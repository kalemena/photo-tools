#!/usr/bin/env python3
"""
File Utilities - Common file operations.
"""

import os
from pathlib import Path


def is_photo_file(file_path: str) -> bool:
    """Check if a file is a supported photo format."""
    SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.heic', '.heif'}
    return Path(file_path).suffix.lower() in SUPPORTED_EXTENSIONS


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"
