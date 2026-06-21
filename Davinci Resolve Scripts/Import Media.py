#!/usr/bin/env python3
import os
import subprocess
from pathlib import Path

# Initialize DaVinci Resolve Scripting API
try:
    resolve
except NameError:
    import DaVinciResolveScript as dvr_script
    resolve = dvr_script.scriptapp("Resolve")

# Files to instantly ignore if accidentally selected
IGNORE_EXTENSIONS = {'.txt', '.md', '.exe', '.py', '.sh', '.json', '.xml', '.ini', '.db', '.log'}

def get_file_paths_via_linux_gui():
    """Uses native Linux dialogs to select any files without crashing Resolve."""
    if subprocess.run(["which", "zenity"], stdout=subprocess.DEVNULL).returncode == 0:
        # Using *.* filter so you can choose any media asset type
        cmd = ["zenity", "--file-selection", "--multiple", "--separator=|",
               "--title=Select Media Files to Import",
               "--file-filter=All Files (*.*) | *.*"]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip().split("|")

    elif subprocess.run(["which", "kdialog"], stdout=subprocess.DEVNULL).returncode == 0:
        cmd = ["kdialog", "--getopenfilename", os.path.expanduser("~"),
               "*.* | All Files", "--multiple", "--separate-output"]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip().split("\n")

    print("Error: Neither 'zenity' nor 'kdialog' found.")
    return []

def smart_import():
    project_manager = resolve.GetProjectManager()
    current_project = project_manager.GetCurrentProject()
    if not current_project:
        print("Please open a project before running the script.")
        return

    media_pool = current_project.GetMediaPool()
    file_paths = get_file_paths_via_linux_gui()

    if not file_paths:
        print("No files selected or dialog canceled.")
        return

    print(f"Processing {len(file_paths)} files...")

    for path_str in file_paths:
        input_file = Path(path_str.strip())
        if not input_file.exists() or input_file.suffix.lower() in IGNORE_EXTENSIONS:
            continue

        # Define flat output file path in the same directory
        output_file = input_file.parent / f"{input_file.stem}_fixed{input_file.suffix}"

        # If this file was already processed previously, pull the fixed version instead
        if output_file.exists():
            print(f"Using existing transcode: {output_file.name}")
            media_pool.ImportMedia([str(output_file)])
            continue

        # Only route media through FFmpeg if it's a container format that could hold AAC
        if input_file.suffix.lower() in {'.mp4', '.mkv', '.mov', '.avi', '.m4a'}:
            print(f"Optimizing audio stream: {input_file.name}")
            cmd = [
                "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                "-i", str(input_file),
                "-c:v", "copy",
                "-c:a", "flac",
                str(output_file)
            ]
            try:
                subprocess.run(cmd, check=True)
                print(f"Importing clean container: {output_file.name}")
                media_pool.ImportMedia([str(output_file)])
                continue
            except subprocess.CalledProcessError:
                print(f"FFmpeg bypassed/failed on {input_file.name}. Importing raw original.")

        # Fallthrough: Directly import images, wavs, luts, or any other native assets
        print(f"Directly importing asset: {input_file.name}")
        media_pool.ImportMedia([str(input_file)])

    print("Finished processing.")

if __name__ == "__main__":
    smart_import()
