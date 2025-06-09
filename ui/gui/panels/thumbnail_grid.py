#!/usr/bin/env python3
"""
Thumbnail Grid Panel - Center panel for photo thumbnails.
Displays a grid of photo thumbnails with selection support and batch loading.
"""

import customtkinter as ctk
import os
from pathlib import Path
from PIL import Image
from utils.thumbnail_generator import ThumbnailGenerator
from core.exif_handler import EXIFHandler


class ThumbnailGridPanel(ctk.CTkFrame):
    """Center panel containing the thumbnail grid with batch loading."""

    SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.heic', '.heif'}

    def __init__(self, master):
        super().__init__(master, corner_radius=10)
        self.master_app = master
        self.current_folder = None
        self.photo_paths = []
        self.all_photo_paths = []
        self.selected_photos = set()
        self.thumbnail_generator = ThumbnailGenerator()
        self.exif_handler = EXIFHandler()
        self.thumbnail_images = {}
        self.current_filter = {}
        
        # Loading state
        self.loading_index = 0
        self.loading_active = False
        self.thumbnail_frames = {}
        
        self._create_widgets()

    def _create_widgets(self):
        """Create the thumbnail grid widgets."""
        # Header with folder info and selection controls
        self.header = ctk.CTkFrame(self, fg_color="transparent", height=40)
        self.header.pack(fill="x", padx=10, pady=(10, 5))
        self.header.pack_propagate(False)

        self.folder_label = ctk.CTkLabel(
            self.header, text="No folder selected", font=ctk.CTkFont(size=14, weight="bold")
        )
        self.folder_label.pack(side="left", anchor="w")

        self.selection_label = ctk.CTkLabel(
            self.header, text="", font=ctk.CTkFont(size=12)
        )
        self.selection_label.pack(side="left", padx=(10, 0))

        self.count_label = ctk.CTkLabel(
            self.header, text="", font=ctk.CTkFont(size=12)
        )
        self.count_label.pack(side="right", anchor="e")

        # Scrollable frame for thumbnails grid
        self.scroll_frame = ctk.CTkScrollableFrame(self, label_text="")
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        self.grid_columns = 5  # Default to 5 columns for better space usage

        # Placeholder message
        self.placeholder = ctk.CTkLabel(
            self.scroll_frame,
            text="Select a folder from the tree to view photos",
            font=ctk.CTkFont(size=14),
            text_color=("gray50", "gray70"),
        )
        self.placeholder.pack(expand=True, pady=100)

        # Bind resize event after a delay to avoid early resize events
        self.after(1000, self._bind_resize)
        self.last_width = 0

    def _bind_resize(self):
        """Bind resize event after initial load is complete."""
        self.bind("<Configure>", self._on_resize)

    def _on_resize(self, event):
        """Handle panel resize to adjust grid columns."""
        width = event.width
        
        # Don't rebuild during loading
        if self.loading_active:
            return
        
        # Only rebuild if width changed significantly
        if abs(width - self.last_width) < 80:
            return
            
        self.last_width = width
        new_cols = max(3, min(6, width // 160))
        if new_cols != self.grid_columns:
            self.grid_columns = new_cols
            if self.photo_paths:
                self._rebuild_grid()

    def load_folder(self, folder_path):
        """Load photos from the specified folder."""
        # Stop any ongoing loading
        self.loading_active = False
        
        self.current_folder = folder_path
        self.folder_label.configure(text=Path(folder_path).name)
        self.photo_paths = []
        self.all_photo_paths = []
        self.selected_photos.clear()
        self.thumbnail_images.clear()
        self.thumbnail_frames.clear()
        self.current_filter = {}
        self.loading_index = 0

        # Clear existing thumbnails
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        # Find photo files
        try:
            photo_files = [
                f for f in os.listdir(folder_path)
                if Path(f).suffix.lower() in self.SUPPORTED_EXTENSIONS
            ]
            photo_files.sort()

            if not photo_files:
                self.placeholder = ctk.CTkLabel(
                    self.scroll_frame,
                    text="No photos found in this folder",
                    font=ctk.CTkFont(size=14),
                    text_color=("gray50", "gray70"),
                )
                self.placeholder.pack(expand=True, pady=100)
                self.count_label.configure(text="0 photos")
                self.selection_label.configure(text="")
                return

            self.all_photo_paths = [os.path.join(folder_path, f) for f in photo_files]
            self.photo_paths = self.all_photo_paths.copy()
            self.count_label.configure(text=f"Loading...")
            self.selection_label.configure(text="")

            # Create grid frame
            self.grid_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
            self.grid_frame.pack(fill="both", expand=True)

            # Start batch loading after a short delay to let panel size stabilize
            self.after(100, self._start_loading)

        except PermissionError:
            error_label = ctk.CTkLabel(
                self.scroll_frame, text="Permission denied", text_color="red"
            )
            error_label.pack(pady=10)
            self.count_label.configure(text="Error")

    def _start_loading(self):
        """Start loading after panel size has stabilized."""
        # Calculate columns based on actual current width
        current_width = self.winfo_width()
        if current_width > 200:
            self.grid_columns = max(4, min(6, current_width // 160))
            self.last_width = current_width
        else:
            # Fallback to reasonable default if width not available
            self.grid_columns = 5
        
        self.loading_active = True
        self._load_batch()

    def _load_batch(self):
        """Load a batch of thumbnails (called via after() to keep UI responsive)."""
        if not self.loading_active:
            return

        batch_size = 30  # Load 30 thumbnails per batch
        end = min(self.loading_index + batch_size, len(self.photo_paths))

        # Configure ALL grid columns upfront
        for c in range(self.grid_columns):
            self.grid_frame.grid_columnconfigure(c, weight=1)

        for i in range(self.loading_index, end):
            if not self.loading_active:
                return
                
            photo_path = self.photo_paths[i]
            row = i // self.grid_columns
            col = i % self.grid_columns

            # Create frame
            thumb_frame = ctk.CTkFrame(
                self.grid_frame,
                width=150,
                height=180,
                corner_radius=8,
                border_width=2,
                border_color=("gray80", "gray30")
            )
            thumb_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            thumb_frame.grid_propagate(False)
            
            self.thumbnail_frames[photo_path] = thumb_frame

            # Generate thumbnail (cached, so fast for already-generated)
            thumb_path = self.thumbnail_generator.generate_thumbnail(photo_path, size=(150, 150))
            
            if thumb_path and os.path.exists(thumb_path):
                try:
                    img = Image.open(thumb_path)
                    ctk_img = ctk.CTkImage(
                        light_image=img,
                        dark_image=img,
                        size=(img.width, img.height)
                    )
                    self.thumbnail_images[photo_path] = ctk_img

                    img_label = ctk.CTkLabel(thumb_frame, image=ctk_img, text="")
                    img_label.pack(pady=(10, 5))
                    img_label.bind("<Button-1>", lambda e, p=photo_path, f=thumb_frame: self._on_thumbnail_click(p, f))

                    name_label = ctk.CTkLabel(
                        thumb_frame,
                        text=Path(photo_path).name,
                        font=ctk.CTkFont(size=10),
                        wraplength=130
                    )
                    name_label.pack(pady=(0, 5), fill="x", padx=5)
                    name_label.bind("<Button-1>", lambda e, p=photo_path, f=thumb_frame: self._on_thumbnail_click(p, f))

                except Exception:
                    self._add_text_thumbnail_to_frame(thumb_frame, photo_path)
            else:
                self._add_text_thumbnail_to_frame(thumb_frame, photo_path)

        self.loading_index = end

        # Update count
        self.count_label.configure(text=f"{self.loading_index}/{len(self.photo_paths)}")

        # Load next batch if more to go
        if self.loading_index < len(self.photo_paths):
            self.after(10, self._load_batch)  # Small delay to keep UI responsive
        else:
            # All loaded
            self.loading_active = False
            self.count_label.configure(text=f"{len(self.photo_paths)} photos")

    def _add_text_thumbnail_to_frame(self, frame, photo_path):
        """Add text thumbnail to an existing frame."""
        label = ctk.CTkLabel(
            frame, text=Path(photo_path).name, font=ctk.CTkFont(size=10), wraplength=130
        )
        label.pack(expand=True, fill="both", padx=5, pady=10)
        label.bind("<Button-1>", lambda e, p=photo_path, f=frame: self._on_thumbnail_click(p, f))
        frame.bind("<Button-1>", lambda e, p=photo_path, f=frame: self._on_thumbnail_click(p, f))

    def _rebuild_grid(self):
        """Rebuild grid with new column count."""
        if self.photo_paths:
            self.loading_active = False
            self.loading_index = 0
            self.thumbnail_frames.clear()
            self.thumbnail_images.clear()
            
            for widget in self.scroll_frame.winfo_children():
                widget.destroy()
            
            self.grid_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
            self.grid_frame.pack(fill="both", expand=True)
            
            self.loading_active = True
            self._load_batch()

    def _on_thumbnail_click(self, photo_path, frame):
        """Handle thumbnail selection."""
        if photo_path in self.selected_photos:
            self.selected_photos.remove(photo_path)
            frame.configure(border_color=("gray80", "gray30"))
        else:
            self.selected_photos.add(photo_path)
            frame.configure(border_color=("blue", "blue"))

        count = len(self.selected_photos)
        if count == 0:
            self.selection_label.configure(text="")
        else:
            self.selection_label.configure(text=f"{count} selected")

        if self.master_app and hasattr(self.master_app, 'preview_panel'):
            if photo_path in self.selected_photos or count == 1:
                self.master_app.preview_panel.load_photo(photo_path, self.photo_paths)

    def _select_photo(self, photo_path):
        """Programmatically select a photo."""
        self.selected_photos.clear()
        self.selected_photos.add(photo_path)
        self.selection_label.configure(text="1 selected")

        for path, frame in self.thumbnail_frames.items():
            if path == photo_path:
                frame.configure(border_color=("blue", "blue"))
            else:
                frame.configure(border_color=("gray80", "gray30"))

    def apply_filter(self, filters):
        """Apply metadata filter to photos."""
        self.current_filter = filters
        
        if not filters:
            self.photo_paths = self.all_photo_paths.copy()
            self.folder_label.configure(text=Path(self.current_folder).name)
        else:
            filtered = []
            for photo_path in self.all_photo_paths:
                if self._matches_filter(photo_path, filters):
                    filtered.append(photo_path)
            
            self.photo_paths = filtered
            self.folder_label.configure(text=f"{Path(self.current_folder).name} ({len(filtered)}/{len(self.all_photo_paths)})")
        
        self.count_label.configure(text=f"{len(self.photo_paths)} photos")
        
        if self.photo_paths:
            self.loading_active = False
            self.loading_index = 0
            self.thumbnail_frames.clear()
            self.thumbnail_images.clear()
            
            for widget in self.scroll_frame.winfo_children():
                widget.destroy()
            
            self.grid_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
            self.grid_frame.pack(fill="both", expand=True)
            
            self.loading_active = True
            self._load_batch()

    def _matches_filter(self, photo_path, filters):
        """Check if photo matches filter criteria."""
        try:
            if filters.get('rating_min', 0) > 0:
                rating = self.exif_handler.get_rating(photo_path)
                if rating < filters['rating_min']:
                    return False
            
            if filters.get('make'):
                camera = self.exif_handler.get_camera_info(photo_path)
                if camera.get('make') != filters['make']:
                    return False
            
            if filters.get('model'):
                camera = self.exif_handler.get_camera_info(photo_path)
                if camera.get('model') != filters['model']:
                    return False
            
            return True
        except:
            return False
