#!/usr/bin/env python3
"""
EXIF Handler - Read and write EXIF metadata using pyexiv2.
"""

import os
from pathlib import Path
from typing import Dict, Optional


class EXIFHandler:
    """Handles reading and writing EXIF metadata."""

    def __init__(self):
        self.supported = False
        self._check_dependencies()

    def _check_dependencies(self):
        """Check if required EXIF libraries are available."""
        try:
            import pyexiv2
            self.supported = True
        except ImportError:
            try:
                import exiftool
                self.supported = True
            except ImportError:
                self.supported = False

    def read_exif(self, photo_path: str) -> Dict:
        """Read EXIF data from a photo."""
        if not self.supported:
            return {}

        try:
            import pyexiv2
            img = pyexiv2.Image(photo_path)
            exif_data = img.read_exif()
            xmp_data = img.read_xmp()
            img.close()

            # Combine EXIF and XMP data
            data = {}
            data.update(exif_data)
            data.update(xmp_data)

            return data
        except Exception as e:
            print(f"Error reading EXIF from {photo_path}: {e}")
            return {}

    def get_rating(self, photo_path: str) -> int:
        """Get star rating (0-5) from photo. Returns 0 if not set or error."""
        if not self.supported:
            return 0

        try:
            import pyexiv2
            img = pyexiv2.Image(photo_path)

            # Try to read XMP data (may fail for HEIC)
            rating = 0
            try:
                xmp_data = img.read_xmp()

                # Check XMP Rating (0-5 stars)
                rating_str = xmp_data.get('Xmp.xmp.Rating', '')
                if rating_str:
                    try:
                        rating = int(float(rating_str))
                        rating = max(0, min(5, rating))  # Clamp to 0-5
                    except ValueError:
                        pass
            except Exception as xmp_error:
                # XMP reading failed (common for HEIC), try EXIF only
                pass

            img.close()

            # If no XMP rating found, check EXIF ImageRating
            if rating == 0:
                exif_data = self.read_exif(photo_path)
                rating_str = exif_data.get('Exif.Image.Rating', '')
                if rating_str:
                    try:
                        rating = int(float(rating_str))
                        rating = max(0, min(5, rating))
                    except ValueError:
                        pass

            return rating
        except Exception as e:
            print(f"Error reading rating from {photo_path}: {e}")
            return 0

    def write_rating(self, photo_path: str, rating: int) -> bool:
        """Write star rating (0-5) to photo EXIF data."""
        if not self.supported:
            return False

        rating = max(0, min(5, rating))  # Clamp to 0-5
        ext = Path(photo_path).suffix.lower()

        # For HEIC/HEIF files, use exiftool (pyexiv2 doesn't support writing to BMFF)
        if ext in ['.heic', '.heif']:
            return self._write_with_exiftool(photo_path, rating)

        # For other formats, use pyexiv2
        try:
            import pyexiv2
            img = pyexiv2.Image(photo_path)

            # Write EXIF rating
            img.modify_exif({'Exif.Image.Rating': str(rating)})

            # Write XMP rating
            try:
                img.modify_xmp({'Xmp.xmp.Rating': str(rating)})
            except Exception as xmp_error:
                print(f"Note: Could not write XMP rating: {xmp_error}")

            img.close()
            return True
        except Exception as e:
            print(f"Error writing rating to {photo_path}: {e}")
            return False

    def _write_with_exiftool(self, photo_path: str, rating: int) -> bool:
        """Use exiftool to write rating for formats not supported by pyexiv2 (e.g., HEIC)."""
        try:
            import subprocess
            # Write both EXIF and XMP rating
            result = subprocess.run(
                ['exiftool', '-overwrite_original',
                 f'-Exif:ImageRating={rating}',
                 f'-XMP:Rating={rating}',
                 photo_path],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                print(f"exiftool error: {result.stderr}")
                return False
            return True
        except Exception as e:
            print(f"exiftool failed: {e}")
            return False

    def get_date_taken(self, photo_path: str) -> Optional[str]:
        """Get the date when photo was taken (EXIF DateTimeOriginal)."""
        exif_data = self.read_exif(photo_path)

        # Try different date fields in order of preference
        date_fields = [
            'Exif.Photo.DateTimeOriginal',
            'Exif.Image.DateTimeOriginal',
            'Exif.Photo.DateTimeDigitized',
            'Exif.Image.DateTime',
        ]

        for field in date_fields:
            if field in exif_data and exif_data[field]:
                return exif_data[field]

        return None

    def get_camera_info(self, photo_path: str) -> Dict:
        """Get camera information from EXIF."""
        exif_data = self.read_exif(photo_path)

        return {
            'make': exif_data.get('Exif.Image.Make', 'Unknown'),
            'model': exif_data.get('Exif.Image.Model', 'Unknown'),
            'lens': exif_data.get('Exif.Photo.LensModel', 'Unknown'),
            'iso': exif_data.get('Exif.Photo.ISOSpeedRatings', 'Unknown'),
            'aperture': exif_data.get('Exif.Photo.FNumber', 'Unknown'),
            'focal_length': exif_data.get('Exif.Photo.FocalLength', 'Unknown'),
        }
