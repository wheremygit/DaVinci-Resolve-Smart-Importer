#!/usr/bin/env python3
import os
import subprocess
from pathlib import Path

try:
    resolve
except NameError:
    import DaVinciResolveScript as dvr_script
    resolve = dvr_script.scriptapp("Resolve")

IGNORE_EXTENSIONS = {'.txt', '.md', '.exe', '.py', '.sh', '.json', '.xml', '.ini', '.db', '.log'}

def get_file_paths_via_linux_gui():
    if subprocess.run(["which", "zenity"], stdout=subprocess.DEVNULL).returncode == 0:
        cmd = ["zenity", "--file-selection", "--multiple", "--separator=|",
               "--title=Select Media Files to Import", "--file-filter=All Files (*.*) | *.*"]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip().split("|")
    elif subprocess.run(["which", "kdialog"], stdout=subprocess.DEVNULL).returncode == 0:
        cmd = ["kdialog", "--getopenfilename", os.path.expanduser("~"), "*.* | All Files", "--multiple", "--separate-output"]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip().split("\n")
    print("Error: Neither 'zenity' nor 'kdialog' found.")
    return []

def get_audio_codec(file_path):
    """Uses ffprobe to find the audio codec name cleanly."""
    cmd = [
        "ffprobe", "-v", "error", "-select_streams", "a:0",
        "-show_entries", "stream=codec_name", "-of", "default=noprint_wrappers=1:nokey=1",
        str(file_path)
    ]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        return result.stdout.strip().lower()
    except Exception:
        return ""

def smart_import():
    project_manager = resolve.GetProjectManager()
    current_project = project_manager.GetCurrentProject()
    if not current_project:
        print("Please open a project before running the script.")
        return

    media_pool = current_project.GetMediaPool()
    file_paths = get_file_paths_via_linux_gui()
    if not file_paths:
        return

    print(f"Processing {len(file_paths)} files...")

    for path_str in file_paths:
        input_file = Path(path_str.strip())
        if not input_file.exists() or input_file.suffix.lower() in IGNORE_EXTENSIONS:
            continue

        output_file = input_file.parent / f"{input_file.stem}_fixed{input_file.suffix}"

        if output_file.exists():
            print(f"Using existing transcode: {output_file.name}")
            media_pool.ImportMedia([str(output_file)])
            continue

        if input_file.suffix.lower() in {'.mp4', '.mkv', '.mov', '.avi', '.m4a'}:
            codec = get_audio_codec(input_file)

            # If it's already flac or pcm, skip transcode entirely
            if "flac" in codec or "pcm" in codec:
                print(f"Audio is already optimized ({codec}). Importing directly: {input_file.name}")
                media_pool.ImportMedia([str(input_file)])
                continue

            print(f"Optimizing audio stream ({codec} -> flac): {input_file.name}")
            cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(input_file), "-c:v", "copy", "-c:a", "flac", str(output_file)]
            try:
                subprocess.run(cmd, check=True)
                print(f"Importing clean container: {output_file.name}")
                media_pool.ImportMedia([str(output_file)])
                continue
            except subprocess.CalledProcessError:
                pass

        print(f"Directly importing asset: {input_file.name}")
        media_pool.ImportMedia([str(input_file)])

    print("Finished processing.")

if __name__ == "__main__":
    smart_import()
