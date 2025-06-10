#!/usr/bin/env python3
"""
EXIF Editor Dialog - Dialog for editing EXIF data like star ratings.
"""

import customtkinter as ctk
from pathlib import Path
from core.exif_handler import EXIFHandler


class EXIFEditorDialog(ctk.CTkToplevel):
    """Dialog for editing EXIF metadata."""

    def __init__(self, parent, photo_paths=None):
        super().__init__(parent)
        self.photo_paths = photo_paths if isinstance(photo_paths, list) else [photo_paths]
        self.exif_handler = EXIFHandler()
        self.title(f"Edit EXIF - {len(self.photo_paths)} photo(s)")
        self.geometry("500x600")
        self.resizable(False, False)

        # Make dialog modal
        self.transient(parent)
        self.grab_set()

        self._create_widgets()
        self._load_exif_data()

    def _create_widgets(self):
        """Create dialog widgets."""
        # Main scrollable container
        scroll = ctk.CTkScrollableFrame(self, label_text="")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        # File info
        self.file_label = ctk.CTkLabel(
            scroll,
            text=f"Editing {len(self.photo_paths)} photo(s)",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.file_label.pack(pady=(0, 10), anchor="w")

        # Star Rating section
        rating_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        rating_frame.pack(fill="x", pady=(0, 15))

        rating_label = ctk.CTkLabel(
            rating_frame, text="Star Rating:", font=ctk.CTkFont(size=12, weight="bold")
        )
        rating_label.pack(anchor="w", pady=(0, 5))

        self.star_var = ctk.IntVar(value=0)
        self.star_buttons = []

        stars_frame = ctk.CTkFrame(rating_frame, fg_color="transparent")
        stars_frame.pack(fill="x")

        for i in range(6):  # 0-5 stars
            btn = ctk.CTkButton(
                stars_frame,
                text="☆" if i == 0 else "☆",
                width=40,
                height=40,
                fg_color="transparent",
                text_color=("black", "white"),
                command=lambda s=i: self._set_stars(s)
            )
            btn.pack(side="left", padx=2)
            self.star_buttons.append(btn)

        # Labels for star buttons
        labels_frame = ctk.CTkFrame(rating_frame, fg_color="transparent")
        labels_frame.pack(fill="x")

        for i in range(6):
            label_text = "None" if i == 0 else str(i)
            label = ctk.CTkLabel(labels_frame, text=label_text, font=ctk.CTkFont(size=10))
            label.pack(side="left", padx=2, expand=True)

        # EXIF Date section
        date_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        date_frame.pack(fill="x", pady=(0, 15))

        date_label = ctk.CTkLabel(
            date_frame, text="Date Taken:", font=ctk.CTkFont(size=12, weight="bold")
        )
        date_label.pack(anchor="w", pady=(0, 5))

        self.date_entry = ctk.CTkEntry(date_frame, placeholder_text="YYYY:MM:DD HH:MM:SS")
        self.date_entry.pack(fill="x", pady=(0, 5))

        # Camera Info section (read-only)
        camera_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        camera_frame.pack(fill="x", pady=(0, 15))

        camera_label = ctk.CTkLabel(
            camera_frame, text="Camera Info:", font=ctk.CTkFont(size=12, weight="bold")
        )
        camera_label.pack(anchor="w", pady=(0, 5))

        self.camera_info = ctk.CTkLabel(
            camera_frame, text="", justify="left", anchor="w"
        )
        self.camera_info.pack(fill="x")

        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", padx=10, pady=(0, 10))

        save_btn = ctk.CTkButton(
            button_frame, text="Save", command=self._save
        )
        save_btn.pack(side="right", padx=(5, 0))

        cancel_btn = ctk.CTkButton(
            button_frame, text="Cancel", command=self.destroy, fg_color="gray"
        )
        cancel_btn.pack(side="right", padx=(0, 5))

    def _set_stars(self, rating):
        """Set star rating display."""
        self.star_var.set(rating)
        for i, btn in enumerate(self.star_buttons):
            if i == 0:
                btn.configure(text="✗" if rating == 0 else "☆")
            else:
                btn.configure(text="★" if i <= rating else "☆")

    def _load_exif_data(self):
        """Load EXIF data from the first photo."""
        if not self.photo_paths:
            return

        # Load rating
        rating = self.exif_handler.get_rating(self.photo_paths[0])
        self._set_stars(rating)

        # Load date
        date_taken = self.exif_handler.get_date_taken(self.photo_paths[0])
        if date_taken:
            self.date_entry.delete(0, "end")
            self.date_entry.insert(0, date_taken)

        # Load camera info
        camera = self.exif_handler.get_camera_info(self.photo_paths[0])
        info_text = f"Make: {camera['make']}\n"
        info_text += f"Model: {camera['model']}\n"
        info_text += f"Lens: {camera['lens']}\n"
        info_text += f"ISO: {camera['iso']}\n"
        info_text += f"Aperture: {camera['aperture']}\n"
        info_text += f"Focal Length: {camera['focal_length']}"
        self.camera_info.configure(text=info_text)

    def _save(self):
        """Save EXIF data to photos."""
        rating = self.star_var.get()

        success_count = 0
        fail_count = 0

        for photo_path in self.photo_paths:
            if self.exif_handler.write_rating(photo_path, rating):
                success_count += 1
            else:
                fail_count += 1

        # Show result
        if fail_count == 0:
            print(f"Successfully updated {success_count} photo(s)")
        else:
            print(f"Updated {success_count} photo(s), failed: {fail_count}")

        self.destroy()
