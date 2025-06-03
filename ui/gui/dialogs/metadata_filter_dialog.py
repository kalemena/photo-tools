#!/usr/bin/env python3
"""
Metadata Filter Dialog - Dialog for filtering photos by metadata.
"""

import customtkinter as ctk
from pathlib import Path
from core.exif_handler import EXIFHandler
import os


class MetadataFilterDialog(ctk.CTkToplevel):
    """Dialog for filtering photos by metadata."""

    def __init__(self, parent, photo_paths):
        super().__init__(parent)
        self.photo_paths = photo_paths
        self.exif_handler = EXIFHandler()
        self.title("Filter Photos by Metadata")
        self.geometry("450x400")
        self.resizable(False, False)

        # Make dialog modal
        self.transient(parent)
        self.grab_set()

        self._create_widgets()

    def _create_widgets(self):
        """Create dialog widgets."""
        # Title
        title = ctk.CTkLabel(
            self, text="Filter Photos by Metadata",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title.pack(pady=(20, 10), padx=20, anchor="w")

        # Filter options
        filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        filter_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Camera make filter
        make_frame = ctk.CTkFrame(filter_frame, fg_color="transparent")
        make_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(make_frame, text="Camera Make:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        
        self.make_var = ctk.StringVar(value="All")
        self.make_menu = ctk.CTkOptionMenu(make_frame, variable=self.make_var, values=["All"])
        self.make_menu.pack(fill="x")

        # Camera model filter
        model_frame = ctk.CTkFrame(filter_frame, fg_color="transparent")
        model_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(model_frame, text="Camera Model:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        
        self.model_var = ctk.StringVar(value="All")
        self.model_menu = ctk.CTkOptionMenu(model_frame, variable=self.model_var, values=["All"])
        self.model_menu.pack(fill="x")

        # Rating filter
        rating_frame = ctk.CTkFrame(filter_frame, fg_color="transparent")
        rating_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(rating_frame, text="Minimum Rating:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        
        self.rating_var = ctk.StringVar(value="0")
        rating_options = ["0 (Any)", "1+", "2+", "3+", "4+", "5"]
        self.rating_menu = ctk.CTkOptionMenu(rating_frame, variable=self.rating_var, values=rating_options)
        self.rating_menu.pack(fill="x")

        # Populate filter options
        self._populate_filters()

        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(10, 20))

        filter_btn = ctk.CTkButton(
            button_frame, text="Apply Filter", command=self._apply_filter
        )
        filter_btn.pack(side="right", padx=(5, 0))

        clear_btn = ctk.CTkButton(
            button_frame, text="Clear Filter", command=self._clear_filter
        )
        clear_btn.pack(side="right", padx=(0, 5))

    def _populate_filters(self):
        """Populate filter dropdown options based on photo metadata."""
        makes = {"All": 1}
        models = {"All": 1}
        
        for photo_path in self.photo_paths[:50]:  # Limit scan for performance
            try:
                camera = self.exif_handler.get_camera_info(photo_path)
                make = camera.get('make', 'Unknown')
                model = camera.get('model', 'Unknown')
                
                if make != 'Unknown':
                    makes[make] = makes.get(make, 0) + 1
                if model != 'Unknown':
                    models[model] = models.get(model, 0) + 1
            except:
                pass
        
        # Update menus
        self.make_menu.configure(values=list(makes.keys()))
        self.model_menu.configure(values=list(models.keys()))

    def _apply_filter(self):
        """Apply the filter and close dialog."""
        # The actual filtering will be done by the parent app
        filters = {
            'make': self.make_var.get() if self.make_var.get() != "All" else None,
            'model': self.model_var.get() if self.model_var.get() != "All" else None,
            'rating_min': int(self.rating_var.get().replace('+', '').split()[0]) if self.rating_var.get() != "0 (Any)" else 0
        }
        
        # Pass filter back to parent
        if hasattr(self.master, 'apply_metadata_filter'):
            self.master.apply_metadata_filter(filters)
        
        self.destroy()

    def _clear_filter(self):
        """Clear filter and close dialog."""
        if hasattr(self.master, 'apply_metadata_filter'):
            self.master.apply_metadata_filter({})  # Empty filter = show all
        
        self.destroy()