#!/usr/bin/env python3
"""
Move/Copy Dialog - Dialog for moving/copying photos to named folders.
"""

import customtkinter as ctk


class MoveDialog(ctk.CTkToplevel):
    """Dialog for moving/copying photos to target folders."""

    def __init__(self, parent, selected_photos=None):
        super().__init__(parent)
        self.selected_photos = selected_photos or []
        self.title("Move/Copy Photos")
        self.geometry("500x400")
        self._create_widgets()

    def _create_widgets(self):
        """Create dialog widgets."""
        # Placeholder for Phase 3
        label = ctk.CTkLabel(
            self, text="Move/Copy Dialog\n(Implementation in Phase 3)"
        )
        label.pack(expand=True, pady=50)

        close_btn = ctk.CTkButton(self, text="Close", command=self.destroy)
        close_btn.pack(pady=20)
