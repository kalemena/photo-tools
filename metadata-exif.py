from PIL import Image
from PIL.ExifTags import TAGS
from pillow_heif import register_heif_opener
import argparse

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract EXIF DateTime from HEIC file")
    parser.add_argument("--file", required=True, help="Path to HEIC file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print all EXIF tags")
    args = parser.parse_args()

    date_taken = get_date_taken_from_heic(args.file, args.verbose)

    if date_taken:
        print(f"Date Taken: {date_taken}")
    else:
        print("Date Taken not found.")
