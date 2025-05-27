#!/usr/bin/env python3
"""
Sort Dialog - Dialog for configuring sort options.
"""

import customtkinter as ctk


class SortDialog(ctk.CTkToplevel):
    """Dialog for configuring photo sorting options."""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Sort Photos")
        self.geometry("400x500")
        self._create_widgets()

    def _create_widgets(self):
        """Create dialog widgets."""
        # Placeholder for Phase 3
        label = ctk.CTkLabel(
            self, text="Sort Dialog\n(Implementation in Phase 3)"
        )
        label.pack(expand=True, pady=50)

        close_btn = ctk.CTkButton(self, text="Close", command=self.destroy)
        close_btn.pack(pady=20)
