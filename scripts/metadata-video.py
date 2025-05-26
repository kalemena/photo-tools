from pathlib import Path
import argparse
import subprocess
import re
import os
from datetime import datetime


def get_video_metadata(video_file_path, verbose=False):
    """
    Extracts video metadata using exiftool.

    Args:
        video_file_path (str): The path to the video file.
        verbose (bool): If True, print all metadata.

    Returns:
        dict: Dictionary containing video metadata.
    """
    try:
        result = subprocess.run(
            ['exiftool', '-api', 'QuickTimeUTC', video_file_path],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"Error running exiftool: {result.stderr}")
            return None

        output = result.stdout

        if verbose:
            print(output)

        metadata = {}
        for line in output.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip()

        return metadata
    except FileNotFoundError:
        print("exiftool not found. Install with: brew install exiftool")
        return None
    except Exception as e:
        print(f"Error processing {video_file_path}: {e}")
        return None


def format_file_size(size_bytes):
    """Convert bytes to human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def print_video_info(video_path, metadata, verbose=False):
    """Print formatted video metadata."""
    if not metadata:
        print(f"{video_path.name}: No metadata found.")
        return

    print(f"\n{video_path.name}:")

    file_size = Path(video_path).stat().st_size
    print(f"  File Size: {format_file_size(file_size)}")

    info_keys = [
        ('Image Size', 'Resolution'),
        ('Video Codec', 'Codec'),
        ('Audio Codec', 'Audio'),
        ('Duration', 'Duration'),
        ('Frame Rate', 'FPS'),
        ('Bitrate', 'Bitrate'),
        ('Media Create Date', 'Created'),
        ('Rotation', 'Rotation'),
        ('File Type', 'Format'),
    ]

    for exif_key, label in info_keys:
        if exif_key in metadata:
            print(f"  {label}: {metadata[exif_key]}")

    if verbose:
        print("\n  All metadata:")
        for key, value in sorted(metadata.items()):
            print(f"    {key}: {value}")


def get_video_files(folder_path):
    """Get list of video files in folder."""
    video_extensions = {'.mov', '.mp4', '.m4v', '.avi', '.mkv', '.webm'}
    folder = Path(folder_path)
    files = []
    for f in os.listdir(folder):
        if Path(f).suffix.lower() in video_extensions:
            files.append(folder / f)
    return sorted(files)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract video metadata (codec, size, duration, etc.)")
    parser.add_argument("--file", help="Path to video file")
    parser.add_argument("--folder", help="Path to folder containing video files")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print all metadata")
    parser.add_argument("--limit", "-l", type=int, help="Limit number of files to process")
    args = parser.parse_args()

    if not args.file and not args.folder:
        parser.error("Either --file or --folder must be specified")

    files = []
    if args.file:
        files = [Path(args.file)]
    else:
        files = get_video_files(args.folder)
        if args.limit:
            files = files[:args.limit]

    for video_path in files:
        metadata = get_video_metadata(video_path, args.verbose)
        print_video_info(video_path, metadata, args.verbose)
