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

# A comprehensive list of files to exclude from importing
IGNORE_EXTENSIONS = {'.txt', '.md', '.exe', '.py', '.sh', '.json', '.xml', '.ini', '.db', '.log'}

def get_folder_path_via_linux_gui():
    """Uses native Linux dialogs to select a directory safely."""
    if subprocess.run(["which", "zenity"], stdout=subprocess.DEVNULL).returncode == 0:
        cmd = ["zenity", "--file-selection", "--directory",
               "--title=Select Source Folder to Import Asset Bin"]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()

    elif subprocess.run(["which", "kdialog"], stdout=subprocess.DEVNULL).returncode == 0:
        cmd = ["kdialog", "--getexistingdirectory", os.path.expanduser("~"),
               "--title", "Select Source Folder to Import Asset Bin"]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()

    print("Error: Neither 'zenity' nor 'kdialog' found.")
    return None

def smart_bin_import():
    project_manager = resolve.GetProjectManager()
    current_project = project_manager.GetCurrentProject()
    if not current_project:
        print("Error: Please open a project before running the script.")
        return

    media_pool = current_project.GetMediaPool()
    root_folder = media_pool.GetRootFolder()

    # Get chosen input directory
    target_dir_str = get_folder_path_via_linux_gui()
    if not target_dir_str:
        print("No folder selected or dialog canceled.")
        return

    source_dir = Path(target_dir_str)

    # 1. Grab EVERY file except system junk or script files
    try:
        all_files = [
            f for f in source_dir.iterdir()
            if f.is_file()
            and f.suffix.lower() not in IGNORE_EXTENSIONS
            and not f.name.startswith('.')
            and "_fixed" not in f.stem
        ]
    except Exception as e:
        print(f"Error reading folder: {e}")
        return

    if not all_files:
        print(f"No importable assets found in {source_dir}")
        return

    # 2. Setup the target Bin inside Resolve using the OS folder's name
    bin_name = source_dir.name
    print(f"Targeting Bin name: '{bin_name}'")

    target_bin = None
    subfolders = root_folder.GetSubFolderList()
    if subfolders:
        for folder in subfolders:
            if folder.GetName() == bin_name:
                target_bin = folder
                break

    if not target_bin:
        target_bin = media_pool.AddSubFolder(root_folder, bin_name)

    if not target_bin:
        print("Failed to create or access the target Bin.")
        return

    # Force the Media Pool target cursor into this bin
    media_pool.SetCurrentFolder(target_bin)
    print(f"Syncing {len(all_files)} items into Bin '{bin_name}'...")

    # 3. Process files dynamically
    for input_file in all_files:
        output_file = source_dir / f"{input_file.stem}_fixed{input_file.suffix}"

        # If a transcoded version already exists, import that directly
        if output_file.exists():
            print(f"Using existing transcode: {output_file.name}")
            media_pool.ImportMedia([str(output_file)])
            continue

        # Check if the file is a standard video/audio track that could contain problematic audio tracks
        # Extensions like .mp4, .mkv, .mov, .m4a
        if input_file.suffix.lower() in {'.mp4', '.mkv', '.mov', '.avi', '.m4a'}:
            print(f"Optimizing format: {input_file.name}")
            cmd = [
                "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                "-i", str(input_file),
                "-c:v", "copy",
                "-c:a", "flac",
                str(output_file)
            ]
            try:
                subprocess.run(cmd, check=True)
                media_pool.ImportMedia([str(output_file)])
                continue
            except subprocess.CalledProcessError:
                print(f"FFmpeg skipped/failed for {input_file.name}. Importing raw file.")

        # For images (.png, .jpg), clean WAV/MP3 files, or anything else, import directly
        print(f"Directly importing asset: {input_file.name}")
        media_pool.ImportMedia([str(input_file)])

    print("Finished comprehensive folder sync.")

if __name__ == "__main__":
    smart_bin_import()
