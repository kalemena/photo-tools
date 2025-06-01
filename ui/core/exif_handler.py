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
        """Get star rating (0-5) from photo. Returns -1 if not set."""
        if not self.supported:
            return -1

        try:
            import pyexiv2
            img = pyexiv2.Image(photo_path)
            xmp_data = img.read_xmp()
            img.close()

            # Check XMP Rating (0-5 stars)
            rating_str = xmp_data.get('Xmp.xmp.Rating', '')
            if rating_str:
                try:
                    rating = int(float(rating_str))
                    return max(0, min(5, rating))  # Clamp to 0-5
                except ValueError:
                    pass

            # Check EXIF ImageRating
            exif_data = self.read_exif(photo_path)
            rating_str = exif_data.get('Exif.Image.Rating', '')
            if rating_str:
                try:
                    rating = int(float(rating_str))
                    return max(0, min(5, rating))
                except ValueError:
                    pass

            return 0  # Default: no rating
        except Exception as e:
            print(f"Error reading rating from {photo_path}: {e}")
            return -1

    def write_rating(self, photo_path: str, rating: int) -> bool:
        """Write star rating (0-5) to photo EXIF data."""
        if not self.supported:
            return False

        rating = max(0, min(5, rating))  # Clamp to 0-5

        try:
            import pyexiv2
            img = pyexiv2.Image(photo_path)

            # Write to both XMP and EXIF for compatibility
            img.modify_xmp({'Xmp.xmp.Rating': str(rating)})
            img.modify_exif({'Exif.Image.Rating': str(rating)})

            img.close()
            return True
        except Exception as e:
            print(f"Error writing rating to {photo_path}: {e}")
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
