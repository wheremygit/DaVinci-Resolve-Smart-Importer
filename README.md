# DaVinci Resolve Smart Importer for Linux

> [!NOTE]
> These scripts were inspired by [Andrew Shark's Resolve Scripts](https://gitlab.com/AndrewShark/davinci-resolve-scripts).

> [!CAUTION]
> I don't know any code nor I am a dev thus these scripts were generated using an LLM. Use at your own risk.

A pair of automation scripts for **DaVinci Resolve Studio on Linux** that fixes the infamous "silent AAC audio" issue on import as well integrates with your DE's file picker offerring seemless media importing on the Linux Desktop until [Blackmagic Fixes it themseleves](https://forum.blackmagicdesign.com/viewtopic.php?f=33&t=149142).

Instead of dealing with separate tracks or fragile GUI automation, these scripts pre-process your media files instantly using FFmpeg. They clone the video stream exactly (zero quality loss, lightning-fast) and transcode the audio to lossless **FLAC**, then inject the unified clips directly into your open Resolve project.



https://github.com/user-attachments/assets/c653196b-80b6-43c2-9d0c-ba76d38f16ca



## Features

* **Smart Import:** Multi-select any combination of supported files (videos, audio, images). Videos are optimized on the fly; other assets are imported directly.
* **Smart Bin:** Select an entire directory. The script transcodes any video files inside it and automatically creates a matching, organized Bin (sub-folder) in your Media Pool.
* No separate audio tracks, no extra folders, and no temporary timelines.

---

## Script Dependencies

To run either the **Smart Import** or **Smart Bin** scripts, ensure the following packages are installed on your system.

### Arch Linux Installation

**For KDE Plasma / Qt Users:**

```bash
sudo pacman -S ffmpeg kdialog python

```

**For GNOME / GTK Users:**

```bash
sudo pacman -S ffmpeg zenity python

```

> [!IMPORTANT]
> * **DaVinci Resolve Studio:** Blackmagic Design limits external Python scripting execution to the **Studio (paid)** version on Linux. (Typically installed via the AUR as `davinci-resolve-studio`).
> * **System GUI File Choosers:** The script dynamically checks for `zenity` or `kdialog` to open file/folder dialogs safely without blocking or crashing Resolve's interface thread.
> 
> 

---

## Installation & Setup

### 1. Place the Scripts

Move the `.py` files into DaVinci Resolve's dedicated utility scripts directory:

```bash
mkdir -p ~/.local/share/DaVinciResolve/Fusion/Scripts/Utility/
cp *.py ~/.local/share/DaVinciResolve/Fusion/Scripts/Utility/

```

### 2. Run the Scripts in Resolve

1. Open DaVinci Resolve and open a project.
2. Navigate to the top menu: **Workspace > Scripts**.
3. Select your script to execute it.

> [!TIP]
> ### 3. (Optional) Assign Keyboard Shortcuts
>
> To speed up your workflow, you can map these scripts to keyboard shortcuts:
>
> 1. Go to **DaVinci Resolve > Keyboard Customization**.
> 2. Search for the name of your script (under the *Application > Workspace > Scripts* category).
> 3. Assign your preferred shortcut key bind.

---

> [!WARNING]
> ## Environment & Testing
>
> * **Tested OS:** Arch Linux (KDE Plasma)
> * **Tested Application:** DaVinci Resolve Studio 21
> * **Dependencies Checked:** FFmpeg, KDialog, Python 3.11+
