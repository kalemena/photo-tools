#!/usr/bin/env python3
"""
Photo Manager - Handles photo indexing and caching.
"""

from pathlib import Path
from typing import List


class PhotoManager:
    """Manages photo indexing and caching."""

    SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.heic', '.heif'}

    def __init__(self):
        self.photos = []
        self.current_folder = None

    def index_folder(self, folder_path: str) -> List[str]:
        """Index all photos in a folder."""
        folder = Path(folder_path)
        if not folder.exists():
            return []

        self.current_folder = folder_path
        self.photos = [
            str(f) for f in folder.iterdir()
            if f.is_file() and f.suffix.lower() in self.SUPPORTED_EXTENSIONS
        ]
        self.photos.sort()
        return self.photos
