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
from gui.widgets.status_bar import StatusBar, show_toast
from core.settings import get_settings


class PhotoToolsApp(ctk.CTk):
    """Main application window with 3-panel layout."""

    def __init__(self):
        # Load settings first
        self.settings = get_settings()
        
        # Apply appearance mode before creating window
        appearance = self.settings.get("appearance_mode", "system")
        ctk.set_appearance_mode(appearance)
        
        super().__init__()

        self.title("Photo Tools GUI")
        
        # Apply saved window geometry
        geometry = self.settings.get("window_geometry", "1400x900")
        x = self.settings.get("window_x")
        y = self.settings.get("window_y")
        
        if x is not None and y is not None:
            self.geometry(f"{geometry}+{x}+{y}")
        else:
            self.geometry(geometry)
        
        self.minsize(1000, 700)
        
        # Bind close event to save settings
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self._create_toolbar()
        self._create_panels()
        self._configure_grid()
        self._create_status_bar()
        
        # Load last folder if available
        last_folder = self.settings.get("last_folder", "")
        if last_folder and Path(last_folder).exists():
            self.folder_panel.load_folder(last_folder)
        
        # Set dark mode toggle state
        if appearance == "dark":
            self.appearance_switch.select()
        elif appearance == "light":
            self.appearance_switch.deselect()
        else:
            # System mode - check current mode
            if ctk.get_appearance_mode() == "Dark":
                self.appearance_switch.select()

    def _on_close(self):
        """Save settings before closing."""
        # Save window position and size
        self.settings.set("window_geometry", self.geometry())
        
        # Get current window position
        x = self.winfo_x()
        y = self.winfo_y()
        self.settings.set("window_x", x)
        self.settings.set("window_y", y)
        
        # Save current folder
        if hasattr(self, 'thumbnail_panel') and self.thumbnail_panel.current_folder:
            self.settings.set("last_folder", self.thumbnail_panel.current_folder)
            self.settings.add_recent_folder(self.thumbnail_panel.current_folder)
        
        # Save appearance mode
        if self.appearance_switch.get():
            self.settings.set("appearance_mode", "dark")
        else:
            current = ctk.get_appearance_mode()
            if current == "light":
                self.settings.set("appearance_mode", "light")
            else:
                self.settings.set("appearance_mode", "system")
        
        self.destroy()

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

        # Cache info button
        self.cache_btn = ctk.CTkButton(
            self.toolbar, text="Cache", width=80, command=self._show_cache_info
        )
        self.cache_btn.pack(side="left", padx=(20, 5), pady=10)

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
        self.grid_rowconfigure(0, weight=0)  # Toolbar
        self.grid_rowconfigure(1, weight=1)  # Main panels
        self.grid_rowconfigure(2, weight=0)  # Status bar
        self.grid_columnconfigure(0, weight=1, minsize=250)  # Folder tree
        self.grid_columnconfigure(1, weight=3, minsize=500)  # Thumbnail grid
        self.grid_columnconfigure(2, weight=2, minsize=350)  # Preview pane

    def _create_status_bar(self):
        """Create the status bar at the bottom."""
        self.status_bar = StatusBar(self)
        self.status_bar.grid(row=2, column=0, columnspan=3, sticky="ew")

    def show_toast(self, message, success=True):
        """Show a toast notification."""
        show_toast(self, message, success=success)

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

    def _show_cache_info(self):
        """Show cache information and offer to clear."""
        from utils.thumbnail_generator import ThumbnailGenerator
        gen = ThumbnailGenerator()
        
        cache_size = gen.get_cache_size()
        cache_count = gen.get_cache_count()
        
        # Create a dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Thumbnail Cache")
        dialog.geometry("350x200")
        dialog.transient(self)
        dialog.grab_set()
        
        # Info
        ctk.CTkLabel(
            dialog, text=f"Cache Size: {cache_size}",
            font=ctk.CTkFont(size=14)
        ).pack(pady=(30, 10))
        
        ctk.CTkLabel(
            dialog, text=f"Cached Thumbnails: {cache_count}",
            font=ctk.CTkFont(size=12)
        ).pack(pady=5)
        
        # Buttons
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        clear_btn = ctk.CTkButton(
            btn_frame, text="Clear Cache", fg_color="red",
            command=lambda: self._clear_cache_and_close(dialog)
        )
        clear_btn.pack(side="left", padx=5)
        
        close_btn = ctk.CTkButton(
            btn_frame, text="Close", command=dialog.destroy
        )
        close_btn.pack(side="left", padx=5)

    def _clear_cache_and_close(self, dialog):
        """Clear thumbnail cache and close dialog."""
        from utils.thumbnail_generator import ThumbnailGenerator
        gen = ThumbnailGenerator()
        gen.clear_cache()
        
        cache_size = gen.get_cache_size()
        cache_count = gen.get_cache_count()
        
        # Update the cache info in the dialog
        for widget in dialog.winfo_children():
            if isinstance(widget, ctk.CTkLabel):
                text = widget.cget("text")
                if "Cache Size" in text:
                    widget.configure(text=f"Cache Size: {cache_size}")
                elif "Cached Thumbnails" in text:
                    widget.configure(text=f"Cached Thumbnails: {cache_count}")
        
        self.show_toast("Cache cleared successfully", success=True)

    def _toggle_appearance(self):
        """Toggle between light and dark mode."""
        if self.appearance_switch.get():
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("light")
