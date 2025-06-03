#!/usr/bin/env python3
"""
Thumbnail Grid Panel - Center panel for photo thumbnails.
Displays a grid of photo thumbnails with selection support.
"""

import customtkinter as ctk
import os
import threading
from pathlib import Path
from PIL import Image
from utils.thumbnail_generator import ThumbnailGenerator
from core.exif_handler import EXIFHandler


class ThumbnailGridPanel(ctk.CTkFrame):
    """Center panel containing the thumbnail grid."""

    SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.heic', '.heif'}

    def __init__(self, master):
        super().__init__(master, corner_radius=10)
        self.master_app = master
        self.current_folder = None
        self.photo_paths = []
        self.all_photo_paths = []  # Keep all photos before filtering
        self.selected_photos = set()
        self.thumbnail_generator = ThumbnailGenerator()
        self.exif_handler = EXIFHandler()
        self.thumbnail_images = {}  # Keep references to prevent garbage collection
        self.current_filter = {}  # Current filter criteria
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

        # Configure grid columns (will be updated on resize)
        self.grid_columns = 3

        # Placeholder message
        self.placeholder = ctk.CTkLabel(
            self.scroll_frame,
            text="Select a folder from the tree to view photos",
            font=ctk.CTkFont(size=14),
            text_color=("gray50", "gray70"),
        )
        self.placeholder.pack(expand=True, pady=100)

        # Bind resize event
        self.bind("<Configure>", self._on_resize)

    def _on_resize(self, event):
        """Handle panel resize to adjust grid columns."""
        width = event.width
        # Calculate number of columns based on width (each thumbnail ~160px + padding)
        new_cols = max(2, min(6, width // 160))
        if new_cols != self.grid_columns:
            self.grid_columns = new_cols
            if self.photo_paths:
                self._rebuild_grid()

    def load_folder(self, folder_path):
        """Load photos from the specified folder."""
        self.current_folder = folder_path
        self.folder_label.configure(text=Path(folder_path).name)
        self.photo_paths = []
        self.all_photo_paths = []
        self.selected_photos.clear()
        self.thumbnail_images.clear()
        self.current_filter = {}

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
            self.count_label.configure(text=f"{len(photo_files)} photos")
            self.selection_label.configure(text="")

            # Build the grid
            self._build_grid()

        except PermissionError:
            error_label = ctk.CTkLabel(
                self.scroll_frame, text="Permission denied", text_color="red"
            )
            error_label.pack(pady=10)
            self.count_label.configure(text="Error")

    def _build_grid(self):
        """Build the thumbnail grid."""
        # Clear existing
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        # Create grid frame
        self.grid_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.grid_frame.pack(fill="both", expand=True)

        # Generate thumbnails in background thread
        threading.Thread(target=self._generate_thumbnails, daemon=True).start()

    def _rebuild_grid(self):
        """Rebuild grid with new column count."""
        if self.photo_paths:
            self._build_grid()

    def _generate_thumbnails(self):
        """Generate and display thumbnails (runs in background thread)."""
        for i, photo_path in enumerate(self.photo_paths):
            # Generate thumbnail
            thumb_path = self.thumbnail_generator.generate_thumbnail(photo_path, size=(150, 150))

            # Schedule UI update in main thread
            self.after(0, self._add_thumbnail, photo_path, thumb_path, i)

    def _add_thumbnail(self, photo_path, thumb_path, index):
        """Add a thumbnail to the grid (runs in UI thread)."""
        row = index // self.grid_columns
        col = index % self.grid_columns

        # Create thumbnail frame
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

        if thumb_path and os.path.exists(thumb_path):
            try:
                # Load and display image using CTkImage for DPI scaling
                img = Image.open(thumb_path)
                ctk_img = ctk.CTkImage(
                    light_image=img,
                    dark_image=img,
                    size=(img.width, img.height)
                )

                # Keep reference to prevent garbage collection
                self.thumbnail_images[photo_path] = ctk_img

                # Image label
                img_label = ctk.CTkLabel(
                    thumb_frame, image=ctk_img, text=""
                )
                img_label.pack(pady=(10, 5))
                img_label.bind("<Button-1>", lambda e, p=photo_path: self._on_thumbnail_click(p, thumb_frame))

                # File name label
                name_label = ctk.CTkLabel(
                    thumb_frame,
                    text=Path(photo_path).name,
                    font=ctk.CTkFont(size=10),
                    wraplength=130
                )
                name_label.pack(pady=(0, 5), fill="x", padx=5)
                name_label.bind("<Button-1>", lambda e, p=photo_path: self._on_thumbnail_click(p, thumb_frame))

            except Exception as e:
                # Fallback to text if image fails to load
                self._add_text_thumbnail(thumb_frame, photo_path)
        else:
            # No thumbnail available
            self._add_text_thumbnail(thumb_frame, photo_path)

        # Configure grid weights
        for i in range(self.grid_columns):
            self.grid_frame.grid_columnconfigure(i, weight=1)

    def _add_text_thumbnail(self, frame, photo_path):
        """Add a text-based thumbnail as fallback."""
        label = ctk.CTkLabel(
            frame, text=Path(photo_path).name, font=ctk.CTkFont(size=10), wraplength=130
        )
        label.pack(expand=True, fill="both", padx=5, pady=10)
        label.bind("<Button-1>", lambda e, p=photo_path, f=frame: self._on_thumbnail_click(p, f))

        frame.bind("<Button-1>", lambda e, p=photo_path, f=frame: self._on_thumbnail_click(p, f))

    def _on_thumbnail_click(self, photo_path, frame):
        """Handle thumbnail selection."""
        # Toggle selection
        if photo_path in self.selected_photos:
            self.selected_photos.remove(photo_path)
            frame.configure(border_color=("gray80", "gray30"))
        else:
            # If Cmd/Ctrl is not held, clear others
            # For simplicity, we allow multiple selection always
            self.selected_photos.add(photo_path)
            frame.configure(border_color=("blue", "blue"))

        # Update selection label
        count = len(self.selected_photos)
        if count == 0:
            self.selection_label.configure(text="")
        else:
            self.selection_label.configure(text=f"{count} selected")

        # Notify preview pane
        if self.master_app and hasattr(self.master_app, 'preview_panel'):
            if photo_path in self.selected_photos or count == 1:
                self.master_app.preview_panel.load_photo(photo_path, self.photo_paths)

    def _select_photo(self, photo_path):
        """Programmatically select a photo (used by preview pane navigation)."""
        # Clear previous selections
        self.selected_photos.clear()
        self.selected_photos.add(photo_path)

        # Update selection label
        self.selection_label.configure(text="1 selected")

        # Update border colors - find and update the frame
        for widget in self.grid_frame.winfo_children():
            if hasattr(widget, 'cget') and widget.cget('text') != '':
                # This is a rough way - in production, maintain a dict mapping paths to frames
                pass

        # Just reload the grid with updated selection
        if self.photo_paths:
            self._build_grid()

    def apply_filter(self, filters):
        """Apply metadata filter to photos."""
        self.current_filter = filters
        
        if not filters:
            # Clear filter - show all photos
            self.photo_paths = self.all_photo_paths.copy()
            self.folder_label.configure(text=Path(self.current_folder).name)
        else:
            # Apply filter
            filtered = []
            for photo_path in self.all_photo_paths:
                if self._matches_filter(photo_path, filters):
                    filtered.append(photo_path)
            
            self.photo_paths = filtered
            
            # Update label to show filtered count
            self.folder_label.configure(text=f"{Path(self.current_folder).name} ({len(filtered)}/{len(self.all_photo_paths)})")
        
        self.count_label.configure(text=f"{len(self.photo_paths)} photos")
        
        # Rebuild grid
        if self.photo_paths:
            self._build_grid()

    def _matches_filter(self, photo_path, filters):
        """Check if photo matches filter criteria."""
        try:
            # Check rating
            if filters.get('rating_min', 0) > 0:
                rating = self.exif_handler.get_rating(photo_path)
                if rating < filters['rating_min']:
                    return False
            
            # Check camera make
            if filters.get('make'):
                camera = self.exif_handler.get_camera_info(photo_path)
                if camera.get('make') != filters['make']:
                    return False
            
            # Check camera model
            if filters.get('model'):
                camera = self.exif_handler.get_camera_info(photo_path)
                if camera.get('model') != filters['model']:
                    return False
            
            return True
        except:
            return False
