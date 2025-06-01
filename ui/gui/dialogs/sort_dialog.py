#!/usr/bin/env python3
"""
Sort Dialog - Dialog for configuring sort options.
Allows sorting photos by date into organized folder structures.
"""

import customtkinter as ctk
from pathlib import Path
from core.sorter import Sorter
import os


class SortDialog(ctk.CTkToplevel):
    """Dialog for configuring photo sorting options."""

    def __init__(self, parent, source_folder):
        super().__init__(parent)
        self.source_folder = source_folder
        self.sorter = Sorter()
        self.title("Sort Photos by Date")
        self.geometry("500x400")
        self.resizable(False, False)

        # Make dialog modal
        self.transient(parent)
        self.grab_set()

        self._create_widgets()

    def _create_widgets(self):
        """Create dialog widgets."""
        # Title
        title = ctk.CTkLabel(
            self, text="Sort Photos by Date", font=ctk.CTkFont(size=16, weight="bold")
        )
        title.pack(pady=(20, 10), padx=20, anchor="w")

        # Source folder
        source_frame = ctk.CTkFrame(self, fg_color="transparent")
        source_frame.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(source_frame, text="Source:", font=ctk.CTkFont(weight="bold")).pack(side="left")
        ctk.CTkLabel(source_frame, text=self.source_folder, font=ctk.CTkFont(size=11)).pack(side="left", padx=(5, 0))

        # Output folder selection
        output_frame = ctk.CTkFrame(self, fg_color="transparent")
        output_frame.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(output_frame, text="Output:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))

        self.output_entry = ctk.CTkEntry(output_frame, placeholder_text="Select output folder...")
        self.output_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

        browse_btn = ctk.CTkButton(
            output_frame, text="Browse", width=70, command=self._browse_output
        )
        browse_btn.pack(side="right")

        # Organization level
        org_frame = ctk.CTkFrame(self, fg_color="transparent")
        org_frame.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(org_frame, text="Organize by:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))

        self.org_var = ctk.StringVar(value="month")

        year_radio = ctk.CTkRadioButton(
            org_frame, text="Year only (YYYY)", variable=self.org_var, value="year"
        )
        year_radio.pack(anchor="w", padx=(0, 0), pady=2)

        month_radio = ctk.CTkRadioButton(
            org_frame, text="Year/Month (YYYY/MM)", variable=self.org_var, value="month"
        )
        month_radio.pack(anchor="w", padx=(0, 0), pady=2)

        day_radio = ctk.CTkRadioButton(
            org_frame, text="Year/Month/Day (YYYY/MM/DD)", variable=self.org_var, value="day"
        )
        day_radio.pack(anchor="w", padx=(0, 0), pady=2)

        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(20, 20))

        sort_btn = ctk.CTkButton(
            button_frame, text="Sort Photos", command=self._sort_photos
        )
        sort_btn.pack(side="right", padx=(5, 0))

        cancel_btn = ctk.CTkButton(
            button_frame, text="Cancel", command=self.destroy, fg_color="gray"
        )
        cancel_btn.pack(side="right", padx=(0, 5))

    def _browse_output(self):
        """Browse for output folder."""
        from tkinter import filedialog
        folder = filedialog.askdirectory(initialdir=self.output_entry.get() or self.source_folder)
        if folder:
            self.output_entry.delete(0, "end")
            self.output_entry.insert(0, folder)

    def _sort_photos(self):
        """Perform the sorting operation."""
        output_dir = self.output_entry.get()

        if not output_dir:
            self._show_message("Please select an output folder.")
            return

        # Get photo files from source
        from gui.panels.thumbnail_grid import ThumbnailGridPanel
        SUPPORTED = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.heic', '.heif'}

        try:
            photo_files = [
                str(Path(self.source_folder) / f)
                for f in os.listdir(self.source_folder)
                if Path(f).suffix.lower() in SUPPORTED
            ]
        except Exception as e:
            self._show_message(f"Error reading source folder: {e}")
            return

        if not photo_files:
            self._show_message("No photos found in source folder.")
            return

        # Sort photos
        result = self.sorter.sort_by_date(
            photo_files, output_dir, organize_by=self.org_var.get()
        )

        # Show result
        message = f"Sorting complete!\n\n"
        message += f"Successfully sorted: {result['success']}\n"
        message += f"Skipped (already exist): {result['skipped']}\n"
        message += f"Failed: {result['failed']}"

        self._show_message(message)
        self.destroy()

    def _show_message(self, message):
        """Show a message dialog."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Sort Results")
        dialog.geometry("400x250")
        dialog.transient(self)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text=message, wraplength=350).pack(expand=True, padx=20)
        ctk.CTkButton(dialog, text="OK", command=dialog.destroy, width=100).pack(pady=(0, 20))
