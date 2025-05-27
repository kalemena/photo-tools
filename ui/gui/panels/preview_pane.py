#!/usr/bin/env python3
"""
Preview Pane Panel - Right panel for photo preview.
Displays a large preview of the selected photo with metadata and controls.
"""

import customtkinter as ctk
from pathlib import Path


class PreviewPanePanel(ctk.CTkFrame):
    """Right panel containing the photo preview and metadata."""

    def __init__(self, master):
        super().__init__(master, corner_radius=10)
        self.master_app = master
        self.current_photo = None
        self._create_widgets()

    def _create_widgets(self):
        """Create the preview pane widgets."""
        # Title
        self.title_label = ctk.CTkLabel(
            self, text="Preview", font=ctk.CTkFont(size=16, weight="bold")
        )
        self.title_label.pack(pady=(10, 5), padx=10, anchor="w")

        # Preview area (placeholder for Phase 1)
        self.preview_frame = ctk.CTkFrame(self, fg_color=("gray90", "gray20"))
        self.preview_frame.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        self.preview_label = ctk.CTkLabel(
            self.preview_frame,
            text="Select a photo to preview",
            font=ctk.CTkFont(size=14),
            text_color=("gray50", "gray70"),
        )
        self.preview_label.pack(expand=True)

        # Metadata section
        self.metadata_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.metadata_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.metadata_label = ctk.CTkLabel(
            self.metadata_frame,
            text="No photo selected",
            font=ctk.CTkFont(size=12),
            justify="left",
            anchor="w",
        )
        self.metadata_label.pack(fill="x", pady=5)

        # Star rating (placeholder for Phase 3)
        self.rating_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.rating_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.rating_label = ctk.CTkLabel(
            self.rating_frame, text="Rating:", font=ctk.CTkFont(size=12)
        )
        self.rating_label.pack(side="left", padx=(0, 10))

        # Star buttons (placeholder)
        for i in range(5):
            star_btn = ctk.CTkButton(
                self.rating_frame,
                text="☆",
                width=30,
                height=30,
                fg_color="transparent",
                command=lambda s=i: self._set_rating(s + 1),
            )
            star_btn.pack(side="left", padx=2)

        # Navigation buttons
        self.nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.nav_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.prev_btn = ctk.CTkButton(
            self.nav_frame, text="◀ Previous", width=100, command=self._prev_photo
        )
        self.prev_btn.pack(side="left", padx=(0, 5))

        self.next_btn = ctk.CTkButton(
            self.nav_frame, text="Next ▶", width=100, command=self._next_photo
        )
        self.next_btn.pack(side="right", padx=(5, 0))

    def load_photo(self, photo_path):
        """Load and display a photo in the preview pane."""
        self.current_photo = photo_path

        # Update metadata display
        filename = Path(photo_path).name
        self.metadata_label.configure(text=f"File: {filename}\n\n(EXIF data will be displayed in Phase 3)")

        # Update preview (placeholder for Phase 2)
        self.preview_label.configure(text=f"Preview: {filename}\n\n(Full preview in Phase 2)")

    def _set_rating(self, rating):
        """Set star rating (placeholder for Phase 3)."""
        print(f"Set rating to {rating} stars")

    def _prev_photo(self):
        """Navigate to previous photo (placeholder)."""
        print("Previous photo")

    def _next_photo(self):
        """Navigate to next photo (placeholder)."""
        print("Next photo")
