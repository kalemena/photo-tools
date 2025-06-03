#!/usr/bin/env python3
"""
Deduplication - Hash-based duplicate photo detection.
"""

import os
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple
import threading


class Deduplication:
    """Handles duplicate photo detection."""

    def __init__(self):
        self.duplicates = {}
        self.scanning = False
        self.progress_callback = None

    def set_progress_callback(self, callback):
        """Set callback for progress updates (callback(percent, message))."""
        self.progress_callback = callback

    def find_duplicates(self, folder_paths: List[str], recursive: bool = False) -> Dict[str, List[str]]:
        """
        Find duplicate photos across folders using SHA-256 hashing.
        
        Returns dict with hash as key and list of duplicate file paths as value.
        Only hashes with 2+ files are returned.
        """
        self.scanning = True
        self.duplicates = {}
        
        # Supported extensions
        SUPPORTED = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.heic', '.heif'}
        
        # Collect all files
        all_files = []
        for folder_path in folder_paths:
            if not os.path.exists(folder_path):
                continue
            
            if os.path.isfile(folder_path):
                # Single file
                if Path(folder_path).suffix.lower() in SUPPORTED:
                    all_files.append(folder_path)
            else:
                # Directory
                if recursive:
                    for root, dirs, files in os.walk(folder_path):
                        for f in files:
                            if Path(f).suffix.lower() in SUPPORTED:
                                all_files.append(os.path.join(root, f))
                else:
                    for f in os.listdir(folder_path):
                        fpath = os.path.join(folder_path, f)
                        if os.path.isfile(fpath) and Path(f).suffix.lower() in SUPPORTED:
                            all_files.append(fpath)
        
        # Calculate hashes
        total = len(all_files)
        hash_map = {}
        
        for i, file_path in enumerate(all_files):
            if not self.scanning:
                break
            
            try:
                file_hash = self._calculate_hash(file_path)
                if file_hash not in hash_map:
                    hash_map[file_hash] = []
                hash_map[file_hash].append(file_path)
                
                if self.progress_callback:
                    percent = int((i + 1) / total * 100)
                    self.progress_callback(percent, f"Scanning: {i+1}/{total}")
                    
            except Exception as e:
                print(f"Error hashing {file_path}: {e}")
        
        # Filter to only duplicates (2+ files)
        self.duplicates = {h: files for h, files in hash_map.items() if len(files) > 1}
        
        self.scanning = False
        return self.duplicates

    def stop_scanning(self):
        """Stop the scanning process."""
        self.scanning = False

    def _calculate_hash(self, file_path: str, chunk_size: int = 8192) -> str:
        """Calculate SHA-256 hash of a file efficiently."""
        sha256_hash = hashlib.sha256()
        
        # Use chunked reading for memory efficiency
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(chunk_size), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()

    def get_duplicate_groups(self) -> List[Tuple[str, List[str]]]:
        """Get list of duplicate groups (hash, file_list) sorted by file count."""
        groups = [(h, files) for h, files in self.duplicates.items()]
        # Sort by number of files (descending), then by file size
        groups.sort(key=lambda x: (-len(x[1]), -os.path.getsize(x[1][0]) if x[1] else 0))
        return groups

    def get_total_duplicates(self) -> int:
        """Get total number of duplicate files (excluding one original)."""
        return sum(len(files) - 1 for files in self.duplicates.values())

    def get_wasted_space(self) -> int:
        """Get total wasted space from duplicates in bytes."""
        total = 0
        for files in self.duplicates.values():
            if len(files) > 1:
                # Add size of all but one file
                for f in files[1:]:
                    try:
                        total += os.path.getsize(f)
                    except:
                        pass
        return total

    def delete_duplicates(self, files_to_delete: List[str], keep_first: bool = True) -> Dict[str, int]:
        """Delete specified duplicate files."""
        result = {"success": 0, "failed": 0}
        
        for file_path in files_to_delete:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    result["success"] += 1
                else:
                    result["failed"] += 1
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")
                result["failed"] += 1
        
        return result