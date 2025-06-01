#!/usr/bin/env python3
"""
Move/Copy Dialog - Dialog for moving/copying photos to named folders.
"""

import customtkinter as ctk
from pathlib import Path
from core.organizer import Organizer
import os


class MoveDialog(ctk.CTkToplevel):
    """Dialog for moving/copying photos to target folders."""

    def __init__(self, parent, photo_paths):
        super().__init__(parent)
        self.photo_paths = photo_paths
        self.organizer = Organizer()
        self.title(f"Move/Copy {len(photo_paths)} Photo(s)")
        self.geometry("500x500")
        self.resizable(False, False)

        # Make dialog modal
        self.transient(parent)
        self.grab_set()

        self._create_widgets()

    def _create_widgets(self):
        """Create dialog widgets."""
        # Title
        title = ctk.CTkLabel(
            self, text=f"Move/Copy {len(self.photo_paths)} Photo(s)",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title.pack(pady=(20, 10), padx=20, anchor="w")

        # Operation type
        op_frame = ctk.CTkFrame(self, fg_color="transparent")
        op_frame.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(op_frame, text="Operation:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))

        self.op_var = ctk.StringVar(value="copy")

        copy_radio = ctk.CTkRadioButton(
            op_frame, text="Copy (preserves originals)", variable=self.op_var, value="copy"
        )
        copy_radio.pack(anchor="w", pady=2)

        move_radio = ctk.CTkRadioButton(
            op_frame, text="Move (removes from source)", variable=self.op_var, value="move"
        )
        move_radio.pack(anchor="w", pady=2)

        # Target folder
        target_frame = ctk.CTkFrame(self, fg_color="transparent")
        target_frame.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(target_frame, text="Target Folder:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))

        entry_frame = ctk.CTkFrame(target_frame, fg_color="transparent")
        entry_frame.pack(fill="x")

        self.target_entry = ctk.CTkEntry(entry_frame, placeholder_text="Select target folder...")
        self.target_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

        browse_btn = ctk.CTkButton(
            entry_frame, text="Browse", width=70, command=self._browse_target
        )
        browse_btn.pack(side="right")

        # Quick folders (from source parent)
        quick_frame = ctk.CTkFrame(self, fg_color="transparent")
        quick_frame.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(quick_frame, text="Quick Access:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))

        # Add common folder buttons
        self._populate_quick_folders(quick_frame)

        # Create new folder
        new_folder_frame = ctk.CTkFrame(self, fg_color="transparent")
        new_folder_frame.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(new_folder_frame, text="New Folder:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))

        entry_row = ctk.CTkFrame(new_folder_frame, fg_color="transparent")
        entry_row.pack(fill="x")

        self.new_folder_entry = ctk.CTkEntry(entry_row, placeholder_text="Folder name...")
        self.new_folder_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

        create_btn = ctk.CTkButton(
            entry_row, text="Create", width=70, command=self._create_folder
        )
        create_btn.pack(side="right")

        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(20, 20))

        move_btn = ctk.CTkButton(
            button_frame, text="Move/Copy Photos", command=self._move_photos
        )
        move_btn.pack(side="right", padx=(5, 0))

        cancel_btn = ctk.CTkButton(
            button_frame, text="Cancel", command=self.destroy, fg_color="gray"
        )
        cancel_btn.pack(side="right", padx=(0, 5))

    def _populate_quick_folders(self, parent):
        """Populate quick access folder buttons."""
        if not self.photo_paths:
            return

        # Get parent folder of first photo
        parent_folder = str(Path(self.photo_paths[0]).parent)

        try:
            folders = sorted([
                f for f in os.listdir(parent_folder)
                if os.path.isdir(os.path.join(parent_folder, f))
            ])[:5]  # Limit to 5 folders

            if folders:
                for folder in folders:
                    btn = ctk.CTkButton(
                        parent,
                        text=folder,
                        height=28,
                        command=lambda f=folder, pf=parent_folder: self._select_quick_folder(pf, f)
                    )
                    btn.pack(anchor="w", pady=1)
            else:
                ctk.CTkLabel(parent, text="No subfolders found").pack(anchor="w")
        except Exception:
            ctk.CTkLabel(parent, text="Error reading folders").pack(anchor="w")

    def _select_quick_folder(self, parent_folder, folder_name):
        """Select a quick access folder."""
        full_path = str(Path(parent_folder) / folder_name)
        self.target_entry.delete(0, "end")
        self.target_entry.insert(0, full_path)

    def _browse_target(self):
        """Browse for target folder."""
        from tkinter import filedialog
        folder = filedialog.askdirectory(initialdir=self.target_entry.get() or str(Path.home()))
        if folder:
            self.target_entry.delete(0, "end")
            self.target_entry.insert(0, folder)

    def _create_folder(self):
        """Create a new folder."""
        folder_name = self.new_folder_entry.get().strip()
        if not folder_name:
            self._show_message("Please enter a folder name.")
            return

        # Use target entry path or parent of first photo
        base_path = self.target_entry.get() or str(Path(self.photo_paths[0]).parent)

        try:
            new_folder = Path(base_path) / folder_name
            new_folder.mkdir(parents=True, exist_ok=True)

            # Update target entry
            self.target_entry.delete(0, "end")
            self.target_entry.insert(0, str(new_folder))

            # Clear entry
            self.new_folder_entry.delete(0, "end")

            self._show_message(f"Folder created: {new_folder}")
        except Exception as e:
            self._show_message(f"Error creating folder: {e}")

    def _move_photos(self):
        """Perform the move/copy operation."""
        target_folder = self.target_entry.get()

        if not target_folder:
            self._show_message("Please select a target folder.")
            return

        # Perform operation
        result = self.organizer.move_photos(
            self.photo_paths, target_folder, operation=self.op_var.get()
        )

        # Show result
        op_name = "moved" if self.op_var.get() == "move" else "copied"
        message = f"Operation complete!\n\n"
        message += f"Successfully {op_name}: {result['success']}\n"
        message += f"Failed: {result['failed']}"

        self._show_message(message)
        self.destroy()

    def _show_message(self, message):
        """Show a message dialog."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Operation Results")
        dialog.geometry("400x250")
        dialog.transient(self)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text=message, wraplength=350).pack(expand=True, padx=20)
        ctk.CTkButton(dialog, text="OK", command=dialog.destroy, width=100).pack(pady=(0, 20))
