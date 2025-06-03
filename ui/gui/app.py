#!/usr/bin/env python3
"""
Main application window for Photo Tools GUI.
Implements a 3-panel layout with toolbar.
"""

import customtkinter as ctk
from pathlib import Path
from gui.panels.folder_tree import FolderTreePanel
from gui.panels.thumbnail_grid import ThumbnailGridPanel
from gui.panels.preview_pane import PreviewPanePanel
from gui.dialogs.exif_editor import EXIFEditorDialog
from gui.dialogs.sort_dialog import SortDialog
from gui.dialogs.move_dialog import MoveDialog
from gui.dialogs.deduplication_dialog import DeduplicationDialog
from gui.dialogs.metadata_filter_dialog import MetadataFilterDialog


class PhotoToolsApp(ctk.CTk):
    """Main application window with 3-panel layout."""

    def __init__(self):
        super().__init__()

        self.title("Photo Tools GUI")
        self.geometry("1400x900")
        self.minsize(1000, 700)

        self._create_toolbar()
        self._create_panels()
        self._configure_grid()

    def _create_toolbar(self):
        """Create the top toolbar with action buttons."""
        self.toolbar = ctk.CTkFrame(self, height=50, corner_radius=0)
        self.toolbar.grid(row=0, column=0, columnspan=3, sticky="ew", padx=0, pady=0)

        # Toolbar buttons
        btn_sort = ctk.CTkButton(
            self.toolbar, text="Sort", width=100, command=self._on_sort
        )
        btn_sort.pack(side="left", padx=5, pady=10)

        btn_dedup = ctk.CTkButton(
            self.toolbar, text="Deduplicate", width=100, command=self._on_deduplicate
        )
        btn_dedup.pack(side="left", padx=5, pady=10)

        btn_exif = ctk.CTkButton(
            self.toolbar, text="Edit EXIF", width=100, command=self._on_edit_exif
        )
        btn_exif.pack(side="left", padx=5, pady=10)

        btn_move = ctk.CTkButton(
            self.toolbar, text="Move/Copy", width=100, command=self._on_move_copy
        )
        btn_move.pack(side="left", padx=5, pady=10)

        btn_filter = ctk.CTkButton(
            self.toolbar, text="Filter", width=100, command=self._on_filter
        )
        btn_filter.pack(side="left", padx=5, pady=10)

        # Spacer
        spacer = ctk.CTkLabel(self.toolbar, text="")
        spacer.pack(side="left", expand=True, fill="x")

        # Appearance mode switch
        self.appearance_switch = ctk.CTkSwitch(
            self.toolbar,
            text="Dark Mode",
            command=self._toggle_appearance,
        )
        self.appearance_switch.pack(side="right", padx=10, pady=10)
        # Set initial state based on current mode
        if ctk.get_appearance_mode() == "Dark":
            self.appearance_switch.select()

    def _create_panels(self):
        """Create the three main panels."""
        # Left panel - Folder Tree
        self.folder_panel = FolderTreePanel(self)
        self.folder_panel.grid(row=1, column=0, sticky="nsew", padx=(5, 2), pady=5)

        # Center panel - Thumbnail Grid
        self.thumbnail_panel = ThumbnailGridPanel(self)
        self.thumbnail_panel.grid(row=1, column=1, sticky="nsew", padx=2, pady=5)

        # Right panel - Preview Pane
        self.preview_panel = PreviewPanePanel(self)
        self.preview_panel.grid(row=1, column=2, sticky="nsew", padx=(2, 5), pady=5)

        # Cross-reference panels for communication
        self.thumbnail_panel.master_app = self
        self.preview_panel.master_app = self

    def _configure_grid(self):
        """Configure grid weights for resizable panels."""
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1, minsize=250)  # Folder tree
        self.grid_columnconfigure(1, weight=3, minsize=500)  # Thumbnail grid
        self.grid_columnconfigure(2, weight=2, minsize=350)  # Preview pane

    def _on_sort(self):
        """Handle Sort button click."""
        if hasattr(self.thumbnail_panel, 'current_folder') and self.thumbnail_panel.current_folder:
            dialog = SortDialog(self, self.thumbnail_panel.current_folder)
            dialog.focus()
        else:
            self._show_info("Please select a folder first.")

    def _on_deduplicate(self):
        """Handle Deduplicate button click."""
        folder = None
        if hasattr(self.thumbnail_panel, 'current_folder') and self.thumbnail_panel.current_folder:
            folder = self.thumbnail_panel.current_folder
        
        if folder:
            dialog = DeduplicationDialog(self, [folder])
            dialog.focus()
        else:
            self._show_info("Please select a folder first.")

    def _on_edit_exif(self):
        """Handle Edit EXIF button click."""
        if hasattr(self.thumbnail_panel, 'selected_photos') and self.thumbnail_panel.selected_photos:
            selected = list(self.thumbnail_panel.selected_photos)
            dialog = EXIFEditorDialog(self, selected)
            dialog.focus()
        elif hasattr(self.preview_panel, 'current_photo') and self.preview_panel.current_photo:
            dialog = EXIFEditorDialog(self, [self.preview_panel.current_photo])
            dialog.focus()
        else:
            self._show_info("Please select a photo first.")

    def _on_move_copy(self):
        """Handle Move/Copy button click."""
        if hasattr(self.thumbnail_panel, 'selected_photos') and self.thumbnail_panel.selected_photos:
            selected = list(self.thumbnail_panel.selected_photos)
            dialog = MoveDialog(self, selected)
            dialog.focus()
        elif hasattr(self.preview_panel, 'current_photo') and self.preview_panel.current_photo:
            dialog = MoveDialog(self, [self.preview_panel.current_photo])
            dialog.focus()
        else:
            self._show_info("Please select a photo first.")

    def _on_filter(self):
        """Handle Filter button click."""
        if hasattr(self.thumbnail_panel, 'photo_paths') and self.thumbnail_panel.photo_paths:
            dialog = MetadataFilterDialog(self, self.thumbnail_panel.photo_paths)
            dialog.focus()
        else:
            self._show_info("No photos to filter. Please select a folder first.")

    def apply_metadata_filter(self, filters):
        """Apply metadata filter to thumbnail grid."""
        if hasattr(self.thumbnail_panel, 'apply_filter'):
            self.thumbnail_panel.apply_filter(filters)

    def _show_info(self, message):
        """Show info dialog."""
        dialog = ctk.CTkInputDialog(text=message, title="Info")
        dialog.destroy()  # Just a simple message box equivalent

    def _toggle_appearance(self):
        """Toggle between light and dark mode."""
        if self.appearance_switch.get():
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("light")
