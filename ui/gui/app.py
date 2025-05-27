#!/usr/bin/env python3
"""
Main application window for Photo Tools GUI.
Implements a 3-panel layout with toolbar.
"""

import customtkinter as ctk
from gui.panels.folder_tree import FolderTreePanel
from gui.panels.thumbnail_grid import ThumbnailGridPanel
from gui.panels.preview_pane import PreviewPanePanel


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

    def _configure_grid(self):
        """Configure grid weights for resizable panels."""
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1, minsize=250)  # Folder tree
        self.grid_columnconfigure(1, weight=3, minsize=500)  # Thumbnail grid
        self.grid_columnconfigure(2, weight=2, minsize=350)  # Preview pane

    def _on_sort(self):
        """Handle Sort button click."""
        print("Sort action triggered")

    def _on_deduplicate(self):
        """Handle Deduplicate button click."""
        print("Deduplicate action triggered")

    def _on_edit_exif(self):
        """Handle Edit EXIF button click."""
        print("Edit EXIF action triggered")

    def _on_move_copy(self):
        """Handle Move/Copy button click."""
        print("Move/Copy action triggered")

    def _toggle_appearance(self):
        """Toggle between light and dark mode."""
        if self.appearance_switch.get():
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("light")
