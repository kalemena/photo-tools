#!/usr/bin/env python3
"""
Thumbnail Generator - Generates and caches photo thumbnails.
"""

import hashlib
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image
import os


class ThumbnailGenerator:
    """Generates and caches photo thumbnails."""

    CACHE_DIR = Path.home() / ".cache" / "photo-tools" / "thumbnails"

    def __init__(self):
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)

    def _get_cache_path(self, photo_path: str, size: Tuple[int, int]) -> Path:
        """Generate cache file path based on photo path and size."""
        photo_hash = hashlib.md5(photo_path.encode()).hexdigest()
        size_str = f"{size[0]}x{size[1]}"
        ext = Path(photo_path).suffix.lower()
        # Use png for caching to avoid recompression
        return self.CACHE_DIR / f"{photo_hash}_{size_str}.png"

    def generate_thumbnail(self, photo_path: str, size: Tuple[int, int] = (200, 200)) -> Optional[str]:
        """Generate a thumbnail for a photo and cache it. Returns path to cached thumbnail."""
        cache_path = self._get_cache_path(photo_path, size)

        # Return cached version if exists
        if cache_path.exists():
            return str(cache_path)

        try:
            # Open and convert HEIC if needed
            img = Image.open(photo_path)

            # Handle EXIF orientation
            try:
                from PIL import ImageOps
                img = ImageOps.exif_transpose(img)
            except Exception:
                pass

            # Convert to RGB if necessary (for PNG with alpha, etc.)
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')

            # Create thumbnail (maintains aspect ratio)
            img.thumbnail(size, Image.Resampling.LANCZOS)

            # Save to cache
            img.save(cache_path, 'PNG', optimize=True)

            return str(cache_path)

        except Exception as e:
            print(f"Error generating thumbnail for {photo_path}: {e}")
            return None

    def clear_cache(self):
        """Clear all cached thumbnails."""
        import shutil
        if self.CACHE_DIR.exists():
            shutil.rmtree(self.CACHE_DIR)
            self.CACHE_DIR.mkdir(parents=True, exist_ok=True)
