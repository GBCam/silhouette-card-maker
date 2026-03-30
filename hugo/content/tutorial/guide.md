---
title: 'Cutting Guide'
weight: 20
---

Before starting, please join our [Discord server](https://discord.gg/jhsKmAgbXc).

It can be overwhelming to learn how to use the scripts and the cutting machine. I set up the Discord server to build a community around cutting cards with Silhouette cutting machines so we can all help each other.

If you get stuck or have questions or just want to learn more before diving in, the best place to ask is in the [Discord server](https://discord.gg/jhsKmAgbXc).

## Prerequisites

### Printer alignment

If you plan on having card backs and if you plan on making double faced cards, then you need to ensure that printer can print with good front and back alignment. Otherwise, your card fronts and backs may have an offset.

Your printer may have built-in tools for calibration and alignment adjustment. However, it doesn't, you can use [`offset_pdf.py`]({{% ref "../docs/offset.md" %}}) to compensate for the printer's offset.

### Cutting settings

Silhouette Studio provides a number of cutting settings to control your cutting machine.

![Cutting settings](/images/cutting_settings.png)

There are 4 main cutting settings:
* **Force** - how hard the machine will push the blade into the material.
* **Speed** - how fast the machine will move the blade.
* **Depth** - how much of the blade the machine will expose.
* **Passes** - how many times the machine will go around a cutting path.

Before starting, you must determine the cutting settings that are best suited for your materials. Failing to do so can result in at best, poorly cut cards or at worse, holes in the your cutting mat.

My recommendations for determining cutting settings:
1) Create a simple cutting template in Silhouette Studio.

![Simple cutting template](/images/cutting_template_simple.png)

2) Click the `Send` tab to show the cutting settings.
1) Set the force, speed, and depth to something reasonable. To start, try 25, 25, and 7.
1) Set passes to 1. By repeating the cutting job, you can determine the required passes.
1) Load your test sheet the press the `Send` button to start the cutting job.
1) When the job finishes, **do not eject** the mat. Lift the corner of the test sheet and check the cut. If the cut is clean, you're done. If not, restart the cutting job as many times as necessary. This will determine required passes.
1) Repeat the entire process. Change the cutting template to cut a different part of your test sheet and experiment with the cutting settings.

Unfortunately, there's no easy way to get around this. You must experiment. You should not copy someone else's settings. Even if we have the same machine, same blade, and same cutting materials, we will need different cutting settings. Learning to adjust cutting settings is a part of using cutting machines.

As a reference, here are my settings for my Cameo 5 with an autoblade and the recommended cardstock and laminate from the [supply list]({{% ref "supplies.md" %}}):
* Force: 35
* Speed: 25
* Depth: 7
* Passes: 4

You can try these settings but you'll likely need to make adjustments for your set up. If you'd like to see settings for other machines and other setups, you can search for them in our [Discord server](https://discord.gg/jhsKmAgbXc).

Here are some other tips:
* Instead of creating a simple cutting template, you can also use one from [cutting_templates/](https://github.com/Alan-Cha/silhouette-card-maker/tree/main/cutting_templates). However, I recommend disabling registration marks and cutting one card at a time. This way, you can do multiple tests with one sheet. To disable registration marks, open the `Print & Cut` sidebar panel and uncheck `Enable Registration Marks`. To cut one card at a time, manually select and delete all other cutting paths.
* You may be tempted to use max force and/or max speed to cut as quickly as possible. You can certainly work up to it and try but your machine may start skipping. If your machine skips, you need to power cycle it so it can rehome.
* You may think that increasing depth will help you cut deeper but that's rarely the case. Depth is just a max limit to how deep your machine can cut. Here is an analogy: it does not matter whether you have a 3-inch knife or a 3-foot katana if you only have the strength to cut 1 inch deep. In this case, the blade length is depth and strength is force, speed, and passes.
* To go with the previous point, I would prioritize the cutting settings in the following order: passes, force, speed, and depth.
* If the edges of your laminated cards are rippled, try reducing force. This happens when the blade is too dull or the machine is pushing the blade too hard and the lamination is ripped through instead of sliced through.

## Instructions

If you run into any issues, you can get help in our [Discord server](https://discord.gg/jhsKmAgbXc). Please ask in the `#troubleshooting` channel and include pictures and videos.

I also recommend searching for your issue in the chat history. There are hundreds of resolved `#troubleshooting` posts so it's likely that someone has encoutered your problem before and fixed it.

### Set up environment

[Install Silhouette Studio](https://www.silhouetteamerica.com/silhouette-studio).

Download the `silhouette-card-makers` code by cloning the [repo](https://github.com/Alan-Cha/silhouette-card-maker) or clicking [here](https://github.com/Alan-Cha/silhouette-card-maker/archive/refs/heads/main.zip). Unzip the code if necessary.

If you're on macOS or Linux, open **Terminal**. If you're on Windows, open **PowerShell**.

### Check if Python is installed

```sh
python --version
```

If it doesn't work, try `python3` as well. If that works, replace the following Python commands with `python3`.

If you don't have Python, install it by clicking [here](https://www.python.org/downloads/). In the installer, check the box to **"Add python.exe to PATH"**.

![Python installer](/images/python_installer.png)

After installation, close **Terminal**/**PowerShell**, reopen it, and verify again.

### Upgrade pip

```sh
python -m pip install --upgrade pip
```

### Navigate to the code

For the following command, replace `<path to the code>` with the file path to the code.

```sh
cd <path to the code>
```

> [!TIP]
> For example, if the code in the `Downloads` folder, then use the following:
> ```sh
> cd Downloads/silhouette-card-maker-main/silhouette-card-maker-main
> ```

### Create a Python virtual environment

A virtual environment ensures that the Python packages you install in the next step will not affect the rest of your computer.

Create a new virtual environment:

```sh
python -m venv venv
```

Then, activate the environment:

{{< tabs items="macOS/Linux,Windows" defaultIndex="0" >}}

  {{< tab >}}
```sh
. venv/bin/activate
```
  {{< /tab >}}
  {{< tab >}}
```powershell
.\venv\Scripts\Activate.ps1
```

> [!TIP]
> If you see a **security error**, run the following, then try activating the environment again.
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
> ```
  {{< /tab >}}

{{< /tabs >}}

You will know if the virtual environment has been activated when `(venv)` appears in the prompt.

### Install Python packages

```sh
pip install -r requirements.txt
```

### Create the PDF

Put card front images into the `game/front/` folder. Then, put a card back image into the `game/back/` folder.

> [!TIP]
> You can use the game, Zero sumZ, as an example. Simply move the [game assets](https://github.com/Alan-Cha/silhouette-card-maker/tree/main/examples/ZERO%20SUMZ) to the appropriate image folders.
>
> You can also use a [plugin]({{% ref "../plugins" %}}) to populate the image folders. Many games, including [Magic: The Gathering]({{% ref "../plugins/mtg.md" %}}), [Pokemon]({{% ref "../plugins/pokemon.md" %}}), [Yu-Gi-Oh!]({{% ref "../plugins/yugioh.md" %}}), [Riftbound]({{% ref "../plugins/riftbound.md" %}}), [One Piece]({{% ref "../plugins/one_piece.md" %}}), and [Lorcana]({{% ref "../plugins/lorcana.md" %}}), are currently supported.

Generate the PDF with the following:

{{< tabs items="Letter size paper,A4 size paper" defaultIndex="0" >}}

  {{< tab >}}
```sh
python create_pdf.py
```
  {{< /tab >}}
  {{< tab >}}
```sh
python create_pdf.py --paper_size a4
```
  {{< /tab >}}

{{< /tabs >}}

> [!TIP]
>`create_pdf.py` has many options such as **paper and card size** and **double-sided cards**. To learn more, see [here]({{% ref "../docs/create.md" %}}).

You can find the PDF in `game/output/game.pdf` and it should look similar to the following:

![PDF output](/images/create_pdf.png)

### Prepare the sheets

Print out the PDF and laminate the sheets. Because cardstock is thicker than printer paper, you may need to use a higher setting on your laminator. If not, you may have cloudy lamination or delamination issues.

> [!TIP]
> You are not limited to making laminated cards. You can cut whatever you want, including plain cardstock, vinyl stickers, and foil on cardstock.

![Print](/images/lamination.jpg)
![Into the lamination pouch](/images/lamination2.jpg)
![Into the laminator](/images/lamination3.jpg)

### Cut the sheets

Open the `letter-standard-<version>.studio3` cutting template in Silhouette Studio. Cutting templates can be found in the [`cutting_templates/`](https://github.com/Alan-Cha/silhouette-card-maker/tree/main/cutting_templates) folder.

![Cutting template](/images/cutting_template_standard.png)

Make sure that your machine is selected.

![Select machine](/images/select_machine.png)
![Select machine](/images/select_machine2.png)

Put a sheet on the cutting mat. The position of the sheet must match the cutting template. Note that for this template, the sheet must be in the **top left of the cutting mat grid**. Note that the **black square registration mark is the top left** as well.

![Notice the grid](/images/sheet_placement.jpg)
![Notice the black square](/images/sheet_placement2.jpg)

Use a Post-It note to **cover the bottom left card**. Because the card is so close to the bottom left L registration mark, the machine sometimes gets the two confused; covering the card will reduce registration issues. You can also use masking tape or a piece of paper with tape on it.

![Bottom left card](/images/registration_fix.jpg)
![Bottom left card covered](/images/registration_fix2.jpg)

The machine's pinch rollers grip and move the mat. Ensure that they are set to the right position for your mat. The should grip both sides of your mat.

![Pinch roller](/images/pinch_roller.jpg)
![Pinch roller close up](/images/pinch_roller2.jpg)

Insert the mat into the machine. The left edge of the mat should be aligned with the notch on the machine. Then, click the media load button on the machine.

![Notch](/images/mat_placement.jpg)
![Mat touching notch](/images/mat_placement2.jpg)
![Notch close up](/images/mat_placement_close.jpg)
![Mat touching notch close up](/images/mat_placement_close2.jpg)

Put your [cutting settings](#cutting-settings) into Silhouette Studio.

![Cutting settings](/images/cutting_template_settings.png)

Start the cutting job. Remember to remove the Post-It note after registration.

![Starting job](/images/starting_job.jpg)

### Finish the cards

Click the media eject button on the machine to remove the mat.

Peel off the cards and remove the excess.

![Cut cards](/images/peel.jpg)
![The peel](/images/peel2.jpg)
![Free cards](/images/peel3.jpg)

Because the cutting process may cause the card edges to delaminate, put the cards through the laminator a second time.

![Relaminating](/images/relamination.jpg)

Now you're ready to play with your cards!

![Card fan](/images/card_fan.jpg)

## Next Steps

Share your success in our [Discord server](https://discord.gg/jhsKmAgbXc)! While you're there, go to the `Channels & Roles` tab and give yourself the `SCM Graduate` role for completing the tutorial! Please share pictures in `#photo-showcase` as well!

As mentioned previously, the `create_pdf.py` script offers many [configuration options]({{% ref "../docs/create.md" %}}). `create_pdf.py` can make double-sided cards, use different paper sizes, cut various card sizes, and more!

If you're interested in making proxies for TCGs, try using a [plugin]({{% ref "../plugins" %}}). Currently, we have support for many games including [Magic: The Gathering]({{% ref "../plugins/mtg.md" %}}), [Pokemon]({{% ref "../plugins/pokemon.md" %}}), [Yu-Gi-Oh!]({{% ref "../plugins/yugioh.md" %}}), [Riftbound]({{% ref "../plugins/riftbound.md" %}}), [One Piece]({{% ref "../plugins/one_piece.md" %}}), and [Lorcana]({{% ref "../plugins/lorcana.md" %}}). All you need to do is provide a decklist and the plugin will automatically fetch the images for you!

Thanks and have fun cutting cards!