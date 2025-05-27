#!/usr/bin/env python3
"""
EXIF Editor Dialog - Dialog for editing EXIF data like star ratings.
"""

import customtkinter as ctk


class EXIFEditorDialog(ctk.CTkToplevel):
    """Dialog for editing EXIF metadata."""

    def __init__(self, parent, photo_path=None):
        super().__init__(parent)
        self.photo_path = photo_path
        self.title("Edit EXIF Data")
        self.geometry("400x500")
        self._create_widgets()

    def _create_widgets(self):
        """Create dialog widgets."""
        # Placeholder for Phase 3
        label = ctk.CTkLabel(
            self, text="EXIF Editor\n(Implementation in Phase 3)"
        )
        label.pack(expand=True, pady=50)

        close_btn = ctk.CTkButton(self, text="Close", command=self.destroy)
        close_btn.pack(pady=20)
