#!/usr/bin/env python3
"""
Folder Tree Panel - Left panel for directory navigation.
Displays a tree view of the file system for photo folder selection.
"""

import customtkinter as ctk
import os
from pathlib import Path


class FolderTreePanel(ctk.CTkFrame):
    """Left panel containing the folder tree navigation."""

    def __init__(self, master):
        super().__init__(master, corner_radius=10)
        self.master_app = master

        self.current_path = None
        self._create_widgets()

    def _create_widgets(self):
        """Create the folder tree widgets."""
        # Title label
        self.title_label = ctk.CTkLabel(
            self, text="Folders", font=ctk.CTkFont(size=16, weight="bold")
        )
        self.title_label.pack(pady=(10, 5), padx=10, anchor="w")

        # Path entry
        self.path_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.path_frame.pack(fill="x", padx=10, pady=(0, 5))

        self.path_entry = ctk.CTkEntry(
            self.path_frame, placeholder_text="Enter path or browse..."
        )
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.browse_btn = ctk.CTkButton(
            self.path_frame, text="...", width=30, command=self._browse_folder
        )
        self.browse_btn.pack(side="right")

        # Scrollable frame for tree
        self.tree_scroll = ctk.CTkScrollableFrame(self, label_text="")
        self.tree_scroll.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        # Add home directory as default
        self._populate_tree(str(Path.home()))

    def _browse_folder(self):
        """Open folder browser dialog."""
        from tkinter import filedialog

        folder = filedialog.askdirectory(initialdir=self.path_entry.get() or str(Path.home()))
        if folder:
            self._populate_tree(folder)

    def _populate_tree(self, path):
        """Populate the tree with folders from the given path."""
        self.current_path = path
        self.path_entry.delete(0, "end")
        self.path_entry.insert(0, path)

        # Clear existing widgets
        for widget in self.tree_scroll.winfo_children():
            widget.destroy()

        try:
            # Add parent directory
            parent = os.path.dirname(path)
            if parent and parent != path:
                parent_btn = ctk.CTkButton(
                    self.tree_scroll,
                    text="..",
                    anchor="w",
                    fg_color="transparent",
                    hover_color=("gray70", "gray30"),
                    command=lambda: self._populate_tree(parent),
                )
                parent_btn.pack(fill="x", pady=(0, 2))

            # List directories
            dirs = sorted(
                [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
            )

            for d in dirs:
                dir_path = os.path.join(path, d)
                btn = ctk.CTkButton(
                    self.tree_scroll,
                    text=d,
                    anchor="w",
                    fg_color="transparent",
                    hover_color=("gray70", "gray30"),
                    command=lambda p=dir_path: self._on_folder_select(p),
                )
                btn.pack(fill="x", pady=(0, 2))

        except PermissionError:

            error_label = ctk.CTkLabel(
                self.tree_scroll, text="Permission denied", text_color="red"
            )
            error_label.pack(pady=10)

    def _on_folder_select(self, path):
        """Handle folder selection."""
        self._populate_tree(path)
        # Notify other panels about folder change
        if hasattr(self.master_app, 'thumbnail_panel'):
            self.master_app.thumbnail_panel.load_folder(path)
