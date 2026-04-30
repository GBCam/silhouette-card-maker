import math
from typing import List, NamedTuple, Tuple

from PIL import Image, ImageDraw
import size_convert
from enums import Orientation, Registration

# Registration mark constraints (in mm)
MAX_REG_LENGTH_MM = 20.0
MAX_REG_THICKNESS_MM = 1.0
MAX_REG_INSET_MM = 86.36
MIN_REG_LENGTH_MM = 5.0
MIN_REG_THICKNESS_MM = 0.5
MIN_REG_INSET_MM = 10.0
REG_PADDING_MM = 1.5  # Extra clearance around registration marks

class CardLayout(NamedTuple):
    card_width_px: int
    card_height_px: int
    paper_width_px: int
    paper_height_px: int
    x_pos: List[int]
    y_pos: List[int]
    max_length_mm: float


def _constrain_reg_params(inset_mm: float, thick_mm: float, len_mm: float) -> tuple[float, float, float]:
    return (
        max(MIN_REG_INSET_MM, min(inset_mm, MAX_REG_INSET_MM)),
        max(MIN_REG_THICKNESS_MM, min(thick_mm, MAX_REG_THICKNESS_MM)),
        max(MIN_REG_LENGTH_MM, min(len_mm, MAX_REG_LENGTH_MM)),
    )


def _l_shape_pts(cx, cy, length, thick, corner):
    h = thick // 2
    e = thick % 2
    _PTS = {
        'top-left': [
            (cx - h, cy - h),
            (cx - h + length, cy - h),
            (cx - h + length, cy + h + e),
            (cx + h + e, cy + h + e),
            (cx + h + e, cy - h + length),
            (cx - h, cy - h + length),
        ],
        'bottom-left': [
            (cx - h, cy + h + e),
            (cx - h + length, cy + h + e),
            (cx - h + length, cy - h),
            (cx + h + e, cy - h),
            (cx + h + e, cy + h + e - length),
            (cx - h, cy + h + e - length),
        ],
        'top-right': [
            (cx + h + e, cy - h),
            (cx + h + e - length, cy - h),
            (cx + h + e - length, cy + h + e),
            (cx - h, cy + h + e),
            (cx - h, cy - h + length),
            (cx + h + e, cy - h + length),
        ],
        'bottom-right': [
            (cx + h + e, cy + h + e),
            (cx + h + e - length, cy + h + e),
            (cx + h + e - length, cy - h),
            (cx - h, cy - h),
            (cx - h, cy + h + e - length),
            (cx + h + e, cy + h + e - length),
        ],
    }
    return _PTS[corner]


def _draw_l_shape(draw, cx, cy, length, thick, corner):
    draw.polygon(_l_shape_pts(cx, cy, length, thick, corner), fill='black')


def draw_reg_mark_pil(
    img: Image.Image,
    inset_px: int,
    thick_px: int,
    length_px: int,
    sq_px: int,
    reg: Registration,
):
    draw = ImageDraw.Draw(img)
    w, h = img.size

    if reg == Registration.THREE:
        half = thick_px // 2
        r = inset_px - half + sq_px
        draw.rectangle([inset_px - half, inset_px - half, r, r], fill='black')
    else:
        _draw_l_shape(draw, inset_px, inset_px, length_px, thick_px, 'top-left')

    _draw_l_shape(draw, inset_px, h - inset_px, length_px, thick_px, 'bottom-left')
    _draw_l_shape(draw, w - inset_px, inset_px, length_px, thick_px, 'top-right')

    if reg == Registration.FOUR:
        _draw_l_shape(draw, w - inset_px, h - inset_px, length_px, thick_px, 'bottom-right')


"""
Card layout computation with strict registration-mark corner exclusion.

This module computes card positions on a page while respecting:
- paper orientation
- bleed spacing between cards
- Silhouette registration mark inset
- square corner exclusion zones where NOTHING may appear
  (neither cards nor bleed)

If no valid layout fits without intruding into corner zones,
layout generation FAILS explicitly.

────────────────────────────────────────────────────────────────────────────
TERMINOLOGY

paper edge
┌─────────────────────────────────────┐
│ inset                               │
│   ┌──────────────┐                  │
│   │ corner zone  │ ← corner_len     │
│   └──────────────┘                  │
│                                     │
│        usable area                  │
│   ┌─────────────────────────────┐   │
│   │   bleed | card | bleed      │   │
│   │   bleed | card | bleed      │   │
│   └─────────────────────────────┘   │
└─────────────────────────────────────┘

Definitions:
- inset: distance from paper edge to registration marks
- corner_len: how far registration marks extend inward
- corner zone: square (corner_len × corner_len) at each corner
- usable area: page minus margins
- grid: cards PLUS surrounding bleed (entire grid must avoid corner zones)
"""

# ─────────────────────────────────────────────────────────────────────────────
# 1. Normalize page size for orientation
# ─────────────────────────────────────────────────────────────────────────────

def normalize_page_size(
    orientation: Orientation,
    paper_width_px: int,
    paper_height_px: int,
) -> Tuple[int, int]:
    """
    layouts.json stores paper sizes as landscape (width > height).
    Portrait swaps width and height; card dimensions are never swapped.
    """
    if orientation == Orientation.PORTRAIT:
        return paper_height_px, paper_width_px
    return paper_width_px, paper_height_px


# ─────────────────────────────────────────────────────────────────────────────
# 2. Compute how many cards fit along one axis
# ─────────────────────────────────────────────────────────────────────────────

def compute_grid_fit(
    usable: int,
    card: int,
    bleed: int,
) -> int:
    """
    Compute how many cards fit along a single dimension.

    | bleed | card | bleed | card | bleed |
      ^---------------------------------^ usable
    
    But bleed can extend beyond the usable area. Only cards must be in the usable area.

    n cards require:
        n * card + (n - 1) * bleed

    so:
        n <= (usable + bleed) / (card + bleed)
    """
    if usable <= 0:
        return 0
    return max(0, math.floor((usable + bleed) / (card + bleed)))


# ─────────────────────────────────────────────────────────────────────────────
# 3. Select margins that avoid corner exclusion zones
# ─────────────────────────────────────────────────────────────────────────────

def select_best_margins(
    page_width: int,
    page_height: int,
    card_width: int,
    card_height: int,
    bleed: int,
    inset: int,
    corner_len: int,
) -> Tuple[int, int, int, int, int, int]:
    """
    Try margin strategies and select the one that:
    - keeps the ENTIRE grid (cards + bleed) out of corner zones
    - fits the maximum number of cards

    Returns:
        (cols, rows, margin_x, margin_y, usable_width, usable_height)

    Failure:
        Raises ValueError if no valid layout exists.

    Corner rule:
    A layout overlaps a corner zone if the grid intrudes within corner_len
    of the inset boundary on BOTH axes simultaneously.
    """

    strategies = [
        (inset, inset),                    # minimal margins
        (inset + corner_len, inset),       # clear corners horizontally
        (inset, inset + corner_len),       # clear corners vertically
    ]

    best = None
    best_count = 0

    for margin_x, margin_y in strategies:
        usable_width = page_width - 2 * margin_x
        usable_height = page_height - 2 * margin_y

        cols = compute_grid_fit(usable_width, card_width, bleed)
        rows = compute_grid_fit(usable_height, card_height, bleed)

        if cols == 0 or rows == 0:
            continue

        # Size of the grid INCLUDING bleed
        grid_width = cols * card_width + (cols + 1) * bleed
        grid_height = rows * card_height + (rows + 1) * bleed

        # Measure clearance between the inset boundary and the LEFT edge
        # of the card grid (INCLUDING bleed).
        #
        # Because the grid is centered, left and right clearances
        # are identical; checking the left side is sufficient.
        #
        # The corner exclusion zone must contain NOTHING — neither
        # cards nor bleed are allowed inside it.
        #
        # Diagram (X axis shown; Y is identical):
        #
        # paper edge
        # │
        # │<── inset ──>│ inset boundary
        # │             │
        # │<── margin_x ────────────────┐
        # │                             │
        # │   gap_x                     │
        # │<───────────>┌──────────────┐│
        # │             │ grid (bleed) ││
        # │             │  bleed card  ││
        # │             └──────────────┘│

        gap_x = margin_x + (usable_width - grid_width) / 2 - inset
        gap_y = margin_y + (usable_height - grid_height) / 2 - inset

        overlaps_corner = gap_x < corner_len and gap_y < corner_len
        if overlaps_corner:
            continue

        count = cols * rows
        if count > best_count:
            best_count = count
            best = (cols, rows, margin_x, margin_y, usable_width, usable_height)

    if best is None:
        raise ValueError(
            "No valid layout fits without intruding into corner exclusion zones."
        )

    return best


# ─────────────────────────────────────────────────────────────────────────────
# 4. Compute centered card positions
# ─────────────────────────────────────────────────────────────────────────────

def compute_card_positions(
    cols: int,
    rows: int,
    card_width: int,
    card_height: int,
    bleed: int,
    margin_x: int,
    margin_y: int,
    usable_width: int,
    usable_height: int,
) -> Tuple[List[int], List[int], int, int]:
    """
    Center the card grid within the usable area and return positions.
    """

    grid_width = cols * card_width + (cols + 1) * bleed
    grid_height = rows * card_height + (rows + 1) * bleed

    start_x = round(margin_x + (usable_width - grid_width) / 2 + bleed)
    start_y = round(margin_y + (usable_height - grid_height) / 2 + bleed)

    x_pos = [start_x + i * (card_width + bleed) for i in range(cols)]
    y_pos = [start_y + j * (card_height + bleed) for j in range(rows)]

    return x_pos, y_pos, start_x, start_y


def generate_layout(
    orientation: Orientation,
    card_width: str,
    card_height: str,
    paper_width: str,
    paper_height: str,
    inset: str,
    length: str,
    ppi: int,
):
    """
    Compute card positions on a page, accounting for margins, bleed,
    orientation, and strict registration mark corner exclusion zones.

    Raises:
        ValueError if no valid layout exists.
    """

    # Equivalent to double the bleed
    CARD_DISTANCE = "1.25mm"

    # Convert all dimensions to pixels
    page_width_px = size_convert.size_to_pixel(paper_width, ppi)
    page_height_px = size_convert.size_to_pixel(paper_height, ppi)
    card_width_px = size_convert.size_to_pixel(card_width, ppi)
    card_height_px = size_convert.size_to_pixel(card_height, ppi)
    card_distance_px = size_convert.size_to_pixel(CARD_DISTANCE, ppi)
    inset_px = size_convert.size_to_pixel(inset, ppi)
    length_px = size_convert.size_to_pixel(length, ppi)

    # Normalize orientation
    page_width_px, page_height_px = normalize_page_size(
        orientation, page_width_px, page_height_px
    )

    # Select margins and grid size (strict — no fallback)
    cols, rows, margin_x, margin_y, usable_w, usable_h = select_best_margins(
        page_width_px,
        page_height_px,
        card_width_px,
        card_height_px,
        card_distance_px,
        inset_px,
        length_px,
    )

    # Compute card positions
    x_pos, y_pos, start_x, start_y = compute_card_positions(
        cols,
        rows,
        card_width_px,
        card_height_px,
        card_distance_px,
        margin_x,
        margin_y,
        usable_w,
        usable_h,
    )

    # Maximum registration mark length that fits with a bleed safety buffer
    max_length_px = max(
        0,
        max(start_x - inset_px, start_y - inset_px) - card_distance_px
    )
    max_length_mm = round(max_length_px * 25.4 / ppi, 2)

    return CardLayout(
        card_width_px=card_width_px,
        card_height_px=card_height_px,
        paper_width_px=page_width_px,
        paper_height_px=page_height_px,
        x_pos=x_pos,
        y_pos=y_pos,
        max_length_mm=max_length_mm,
    )

