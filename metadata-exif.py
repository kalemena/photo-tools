from PIL import Image
from PIL.ExifTags import TAGS
from pillow_heif import register_heif_opener
import argparse
import subprocess
import re
from datetime import datetime
from pathlib import Path


def get_date_taken_from_heic(heic_file_path, verbose=False):
    """
    Extracts the 'Date Taken' (DateTimeOriginal) from a HEIC file.

    Args:
        heic_file_path (str): The path to the HEIC file.
        verbose (bool): If True, print all EXIF tags.

    Returns:
        str or None: The date and time string if found, otherwise None.
    """
    try:
        register_heif_opener()

        with Image.open(heic_file_path) as img:
            exif_data = img.getexif()

            if exif_data:
                if verbose:
                    for key, value in exif_data.items():
                        tag_name = TAGS.get(key, key)
                        print(f"Tag: {tag_name}, Value: {value}")

                for tag_id, value in exif_data.items():
                    tag_name = TAGS.get(tag_id, tag_id)
                    if tag_name == 'DateTime':
                        return value
            return None
    except Exception as e:
        print(f"Error processing {heic_file_path}: {e}")
        return None


def get_date_taken_from_video(video_file_path, verbose=False):
    """
    Extracts the 'Date Taken' from MOV/MP4 video file using exiftool.

    Args:
        video_file_path (str): The path to the video file.
        verbose (bool): If True, print all metadata.

    Returns:
        str or None: The date and time string if found, otherwise None.
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

        date_tags = [
            'Media Create Date',
            'Track Create Date',
            'Create Date',
            'Date/Time Original',
        ]

        for line in output.split('\n'):
            for tag in date_tags:
                match = re.match(rf'^{re.escape(tag)}\s*:\s*(.+)$', line)
                if match:
                    return match.group(1).strip()

        return None
    except FileNotFoundError:
        print("exiftool not found. Install with: brew install exiftool")
        return None
    except Exception as e:
        print(f"Error processing {video_file_path}: {e}")
        return None


def get_date_taken(file_path, verbose=False):
    """Extract date taken from image or video file, returns ISO format string."""
    file_path = str(file_path)
    ext = file_path.lower().split('.')[-1]

    if ext in ('mov', 'mp4', 'm4v', 'avi'):
        date_str = get_date_taken_from_video(file_path, verbose)
    else:
        date_str = get_date_taken_from_heic(file_path, verbose)

    if not date_str:
        return None

    date_str = date_str.strip()

    date_str = re.sub(r'[+-]\d{2}:\d{2}$', '', date_str)

    formats = [
        '%Y:%m:%d %H:%M:%S',
        '%Y-%m-%d %H:%M:%S',
        '%Y/%m/%d %H:%M:%S',
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.isoformat()
        except ValueError:
            continue

    return date_str


def get_media_files(folder_path):
    """Get list of media files in folder."""
    import os
    media_extensions = {
        '.jpg', '.jpeg', '.png', '.heic', '.heif', '.raw', '.dng', '.tiff', '.tif',
        '.mov', '.mp4', '.m4v', '.avi'
    }
    folder = Path(folder_path)
    files = []
    for f in os.listdir(folder):
        if Path(f).suffix.lower() in media_extensions:
            files.append(folder / f)
    return sorted(files)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract EXIF DateTime from media file(s)")
    parser.add_argument("--file", help="Path to media file")
    parser.add_argument("--folder", help="Path to folder containing media files")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print all EXIF tags")
    parser.add_argument("--limit", "-l", type=int, help="Limit number of files to process")
    args = parser.parse_args()

    if not args.file and not args.folder:
        parser.error("Either --file or --folder must be specified")

    files = []
    if args.file:
        files = [Path(args.file)]
    else:
        files = get_media_files(args.folder)
        if args.limit:
            files = files[:args.limit]

    for file_path in files:
        date_taken = get_date_taken(file_path, args.verbose)
        if date_taken:
            print(f"{file_path.name}: {date_taken}")
        else:
            print(f"{file_path.name}: Date Taken not found.")
