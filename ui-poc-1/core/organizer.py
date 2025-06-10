#!/usr/bin/env python3
"""
Organizer - Move and copy operations for photo organization.
"""

import shutil
from pathlib import Path
from typing import List, Dict
import os


class Organizer:
    """Handles photo move/copy operations."""

    def __init__(self):
        self.operation = "copy"  # "copy" or "move"

    def move_photos(self, photo_paths: List[str], target_folder: str, operation: str = "copy") -> Dict[str, int]:
        """
        Move or copy photos to target folder.

        Args:
            photo_paths: List of photo paths
            target_folder: Destination folder
            operation: "copy" or "move"

        Returns:
            Dict with success/failed counts
        """
        result = {"success": 0, "failed": 0, "skipped": 0}
        target = Path(target_folder)
        target.mkdir(parents=True, exist_ok=True)

        for photo_path in photo_paths:
            try:
                source = Path(photo_path)
                target_path = target / source.name

                # Handle duplicate names
                if target_path.exists():
                    base_name = source.stem
                    ext = source.suffix
                    counter = 1
                    while target_path.exists():
                        new_name = f"{base_name}_{counter}{ext}"
                        target_path = target / new_name
                        counter += 1

                if operation == "move":
                    shutil.move(str(source), str(target_path))
                else:  # copy
                    shutil.copy2(str(source), str(target_path))

                result["success"] += 1

            except Exception as e:
                print(f"Error {'moving' if operation == 'move' else 'copying'} {photo_path}: {e}")
                result["failed"] += 1

        return result

    def create_folder(self, base_path: str, folder_name: str) -> str:
        """Create a new folder and return its path."""
        new_folder = Path(base_path) / folder_name
        new_folder.mkdir(parents=True, exist_ok=True)
        return str(new_folder)

    def list_folders(self, base_path: str) -> List[str]:
        """List subfolders in a path."""
        try:
            path = Path(base_path)
            if not path.exists():
                return []
            return sorted([str(f) for f in path.iterdir() if f.is_dir()])
        except Exception:
            return []

    def get_photo_info(self, photo_path: str) -> Dict:
        """Get basic info about a photo."""
        try:
            stat = os.stat(photo_path)
            return {
                "name": Path(photo_path).name,
                "size": stat.st_size,
                "size_human": self._format_size(stat.st_size),
                "path": photo_path
            }
        except Exception:
            return {}

    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
