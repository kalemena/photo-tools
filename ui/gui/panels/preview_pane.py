#!/usr/bin/env python3
"""
Preview Pane Panel - Right panel for photo preview.
Displays a large preview of the selected photo with metadata and controls.
"""

import customtkinter as ctk
from pathlib import Path
from PIL import Image
import os

# Register HEIC/HEIF support with Pillow
try:
    import pillow_heif
    pillow_heif.register_heif_opener()
except ImportError:
    pass


class PreviewPanePanel(ctk.CTkFrame):
    """Right panel containing the photo preview and metadata."""

    def __init__(self, master):
        super().__init__(master, corner_radius=10)
        self.master_app = master
        self.current_photo = None
        self.photo_list = []
        self.current_index = -1
        self.preview_image = None  # CTkImage reference
        self.original_image = None  # Keep original PIL image for resizing
        self._create_widgets()

    def _create_widgets(self):
        """Create the preview pane widgets."""
        # Title
        self.title_label = ctk.CTkLabel(
            self, text="Preview", font=ctk.CTkFont(size=16, weight="bold")
        )
        self.title_label.pack(pady=(10, 5), padx=10, anchor="w")

        # Preview area with scrollable frame
        self.preview_scroll = ctk.CTkScrollableFrame(self, fg_color=("gray90", "gray20"), label_text="")
        self.preview_scroll.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        # Bind to scroll frame resize
        self.preview_scroll.bind("<Configure>", self._on_scroll_resize)

        # Image label (inside scrollable frame)
        self.preview_label = ctk.CTkLabel(
            self.preview_scroll,
            text="Select a photo to preview",
            font=ctk.CTkFont(size=14),
            text_color=("gray50", "gray70"),
        )
        self.preview_label.pack(expand=True, pady=50)

        # Metadata section
        self.metadata_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.metadata_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.metadata_label = ctk.CTkLabel(
            self.metadata_frame,
            text="No photo selected",
            font=ctk.CTkFont(size=12),
            justify="left",
            anchor="w",
        )
        self.metadata_label.pack(fill="x", pady=5)

        # Star rating (placeholder for Phase 3)
        self.rating_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.rating_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.rating_label = ctk.CTkLabel(
            self.rating_frame, text="Rating:", font=ctk.CTkFont(size=12)
        )
        self.rating_label.pack(side="left", padx=(0, 10))

        # Star buttons (placeholder)
        self.star_buttons = []
        for i in range(5):
            star_btn = ctk.CTkButton(
                self.rating_frame,
                text="☆",
                width=30,
                height=30,
                fg_color="transparent",
                command=lambda s=i: self._set_rating(s + 1),
            )
            star_btn.pack(side="left", padx=2)
            self.star_buttons.append(star_btn)

        # Navigation buttons
        self.nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.nav_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.prev_btn = ctk.CTkButton(
            self.nav_frame, text="◀ Previous", width=100, command=self._prev_photo
        )
        self.prev_btn.pack(side="left", padx=(0, 5))

        # Photo counter
        self.counter_label = ctk.CTkLabel(
            self.nav_frame, text="", font=ctk.CTkFont(size=11)
        )
        self.counter_label.pack(side="left", expand=True)

        self.next_btn = ctk.CTkButton(
            self.nav_frame, text="Next ▶", width=100, command=self._next_photo
        )
        self.next_btn.pack(side="right", padx=(5, 0))

    def load_photo(self, photo_path, photo_list=None):
        """Load and display a photo in the preview pane."""
        self.current_photo = photo_path

        # Update photo list if provided
        if photo_list is not None:
            self.photo_list = photo_list
            self.current_index = photo_list.index(photo_path) if photo_path in photo_list else -1
            self._update_nav_buttons()

        # Update UI in thread-safe way
        self.after(0, self._display_photo, photo_path)

    def _display_photo(self, photo_path):
        """Display the photo (runs in UI thread)."""
        try:
            # Load image
            self.original_image = Image.open(photo_path)

            # Handle EXIF orientation
            try:
                from PIL import ImageOps
                self.original_image = ImageOps.exif_transpose(self.original_image)
            except Exception:
                pass

            # Store original dimensions
            self.orig_width, self.orig_height = self.original_image.size

            # Update metadata display
            filename = Path(photo_path).name
            file_size = os.path.getsize(photo_path)
            size_kb = file_size / 1024

            self.metadata_label.configure(
                text=f"File: {filename}\n"
                     f"Size: {size_kb:.1f} KB\n"
                     f"Dimensions: {self.orig_width} x {self.orig_height}\n"
                     f"\n(EXIF data will be displayed in Phase 3)"
            )

            # Update navigation counter
            if self.photo_list:
                self.counter_label.configure(text=f"{self.current_index + 1} / {len(self.photo_list)}")

            # Schedule resize after UI is fully rendered
            self.after(100, self._resize_and_display)

        except Exception as e:
            self.preview_label.configure(
                image=None,
                text=f"Error loading preview:\n{str(e)}",
                text_color=("red", "red")
            )

    def _resize_and_display(self):
        """Resize image to fit preview area and display it."""
        if self.original_image is None:
            return

        # Calculate resize dimensions based on original image aspect ratio
        # Use a reasonable default size that fits well in the panel
        # The CTkImage will handle DPI scaling automatically
        max_width = 500
        max_height = 400

        img = self.original_image.copy()
        img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

        # Create CTkImage for proper DPI scaling
        # size parameter tells CTkImage the desired display size (it handles DPI)
        self.preview_image = ctk.CTkImage(
            light_image=img,
            dark_image=img,
            size=(img.width, img.height)
        )

        # Update label
        self.preview_label.configure(image=self.preview_image, text="")

    def _on_scroll_resize(self, event):
        """Handle scroll frame resize to adapt preview image."""
        if self.original_image is not None:
            self._resize_and_display()

    def _update_nav_buttons(self):
        """Update navigation button states."""
        if not self.photo_list:
            self.prev_btn.configure(state="disabled")
            self.next_btn.configure(state="disabled")
            return

        self.prev_btn.configure(state="normal" if self.current_index > 0 else "disabled")
        self.next_btn.configure(
            state="normal" if self.current_index < len(self.photo_list) - 1 else "disabled"
        )

    def _set_rating(self, rating):
        """Set star rating (placeholder for Phase 3)."""
        print(f"Set rating to {rating} stars")
        # Update star display
        for i, btn in enumerate(self.star_buttons):
            if i < rating:
                btn.configure(text="★")
            else:
                btn.configure(text="☆")

    def _prev_photo(self):
        """Navigate to previous photo."""
        if self.photo_list and self.current_index > 0:
            self.current_index -= 1
            prev_photo = self.photo_list[self.current_index]
            self.load_photo(prev_photo)
            # Notify thumbnail grid to update selection
            if self.master_app and hasattr(self.master_app, 'thumbnail_panel'):
                self.master_app.thumbnail_panel._select_photo(prev_photo)

    def _next_photo(self):
        """Navigate to next photo."""
        if self.photo_list and self.current_index < len(self.photo_list) - 1:
            self.current_index += 1
            next_photo = self.photo_list[self.current_index]
            self.load_photo(next_photo)
            # Notify thumbnail grid to update selection
            if self.master_app and hasattr(self.master_app, 'thumbnail_panel'):
                self.master_app.thumbnail_panel._select_photo(next_photo)
