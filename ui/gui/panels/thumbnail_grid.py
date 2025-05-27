#!/usr/bin/env python3
"""
Thumbnail Grid Panel - Center panel for photo thumbnails.
Displays a grid of photo thumbnails with selection support.
"""

import customtkinter as ctk
import os
from pathlib import Path


class ThumbnailGridPanel(ctk.CTkFrame):
    """Center panel containing the thumbnail grid."""

    SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.heic', '.heif'}

    def __init__(self, master):
        super().__init__(master, corner_radius=10)
        self.master_app = master
        self.current_folder = None
        self.thumbnails = []
        self._create_widgets()

    def _create_widgets(self):
        """Create the thumbnail grid widgets."""
        # Header with folder info
        self.header = ctk.CTkFrame(self, fg_color="transparent", height=40)
        self.header.pack(fill="x", padx=10, pady=(10, 5))
        self.header.pack_propagate(False)

        self.folder_label = ctk.CTkLabel(
            self.header, text="No folder selected", font=ctk.CTkFont(size=14, weight="bold")
        )
        self.folder_label.pack(side="left", anchor="w")

        self.count_label = ctk.CTkLabel(
            self.header, text="", font=ctk.CTkFont(size=12)
        )
        self.count_label.pack(side="right", anchor="e")

        # Scrollable frame for thumbnails
        self.scroll_frame = ctk.CTkScrollableFrame(self, label_text="")
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        # Placeholder message
        self.placeholder = ctk.CTkLabel(
            self.scroll_frame,
            text="Select a folder from the tree to view photos",
            font=ctk.CTkFont(size=14),
            text_color=("gray50", "gray70"),
        )
        self.placeholder.pack(expand=True, pady=100)

    def load_folder(self, folder_path):
        """Load photos from the specified folder."""
        self.current_folder = folder_path
        self.folder_label.configure(text=Path(folder_path).name)
        self.thumbnails = []

        # Clear existing thumbnails
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        # Find photo files
        try:
            photo_files = [
                f for f in os.listdir(folder_path)
                if Path(f).suffix.lower() in self.SUPPORTED_EXTENSIONS
            ]
            photo_files.sort()

            if not photo_files:
                self.placeholder = ctk.CTkLabel(
                    self.scroll_frame,
                    text="No photos found in this folder",
                    font=ctk.CTkFont(size=14),
                    text_color=("gray50", "gray70"),
                )
                self.placeholder.pack(expand=True, pady=100)
                self.count_label.configure(text="0 photos")
                return

            self.count_label.configure(text=f"{len(photo_files)} photos")

            # Create thumbnail grid (simple version for Phase 1)
            for i, photo_file in enumerate(photo_files):
                photo_path = os.path.join(folder_path, photo_file)
                self._add_thumbnail_placeholder(photo_path, i)

        except PermissionError:
            error_label = ctk.CTkLabel(
                self.scroll_frame, text="Permission denied", text_color="red"
            )
            error_label.pack(pady=10)
            self.count_label.configure(text="Error")

    def _add_thumbnail_placeholder(self, photo_path, index):
        """Add a placeholder for a thumbnail (full implementation in Phase 2)."""
        # For Phase 1, we just show file names
        frame = ctk.CTkFrame(self.scroll_frame, height=80, corner_radius=5)
        frame.pack(fill="x", pady=(0, 5))
        frame.pack_propagate(False)

        label = ctk.CTkLabel(
            frame, text=Path(photo_path).name, anchor="w"
        )
        label.pack(fill="both", expand=True, padx=10, pady=10)
