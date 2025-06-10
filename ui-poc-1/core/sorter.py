#!/usr/bin/env python3
"""
Sorter - Date and metadata-based photo sorting logic.
Uses EXIF DateTimeOriginal for date sorting, falls back to file mtime.
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict, Optional
from core.exif_handler import EXIFHandler


class Sorter:
    """Handles photo sorting operations."""

    def __init__(self):
        self.exif_handler = EXIFHandler()

    def sort_by_date(self, photo_paths: List[str], output_dir: str, organize_by: str = "month") -> Dict[str, int]:
        """
        Sort photos by date into YYYY/MM or YYYY/MM/DD folder structure.

        Args:
            photo_paths: List of photo file paths
            output_dir: Base output directory
            organize_by: "year", "month", or "day"

        Returns:
            Dict with success/failed counts
        """
        result = {"success": 0, "failed": 0, "skipped": 0}

        for photo_path in photo_paths:
            try:
                # Get date from EXIF
                date_str = self.exif_handler.get_date_taken(photo_path)

                if date_str:
                    # Parse EXIF date format: "YYYY:MM:DD HH:MM:SS"
                    date_parts = date_str.split()[0].split(":")
                    year = date_parts[0]
                    month = date_parts[1] if len(date_parts) > 1 else "01"
                    day = date_parts[2] if len(date_parts) > 2 else "01"
                else:
                    # Fall back to file modification time
                    mtime = os.path.getmtime(photo_path)
                    from datetime import datetime
                    dt = datetime.fromtimestamp(mtime)
                    year = str(dt.year)
                    month = f"{dt.month:02d}"
                    day = f"{dt.day:02d}"

                # Build target folder path
                if organize_by == "year":
                    target_folder = Path(output_dir) / year
                elif organize_by == "month":
                    target_folder = Path(output_dir) / year / month
                else:  # day
                    target_folder = Path(output_dir) / year / month / day

                # Create folder if needed
                target_folder.mkdir(parents=True, exist_ok=True)

                # Copy photo
                target_path = target_folder / Path(photo_path).name

                # Skip if already exists
                if target_path.exists():
                    result["skipped"] += 1
                    continue

                shutil.copy2(photo_path, target_path)
                result["success"] += 1

            except Exception as e:
                print(f"Error sorting {photo_path}: {e}")
                result["failed"] += 1

        return result

    def sort_by_metadata(self, photo_paths: List[str], metadata_key: str) -> Dict[str, List[str]]:
        """
        Sort photos by a specific metadata key.
        Returns dict with metadata value as key and list of photo paths as value.
        """
        result = {}

        for photo_path in photo_paths:
            try:
                exif_data = self.exif_handler.read_exif(photo_path)

                # Handle nested keys like "Exif.Image.Make"
                key_parts = metadata_key.split(".")
                value = exif_data.get(metadata_key, "Unknown")

                if value not in result:
                    result[value] = []
                result[value].append(photo_path)

            except Exception as e:
                print(f"Error reading metadata from {photo_path}: {e}")
                if "Error" not in result:
                    result["Error"] = []
                result["Error"].append(photo_path)

        return result

    def get_date_for_photo(self, photo_path: str) -> Optional[str]:
        """Get formatted date string for a photo."""
        date_str = self.exif_handler.get_date_taken(photo_path)
        if date_str:
            return date_str.split()[0].replace(":", "-")  # YYYY-MM-DD
        return None
