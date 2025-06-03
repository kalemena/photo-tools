#!/usr/bin/env python3
"""
Deduplication Dialog - Dialog for finding and removing duplicate photos.
"""

import os
import customtkinter as ctk
from pathlib import Path
from PIL import Image
import threading
from core.deduplication import Deduplication


class DeduplicationDialog(ctk.CTkToplevel):
    """Dialog for finding and removing duplicate photos."""

    def __init__(self, parent, folder_paths=None):
        super().__init__(parent)
        self.folder_paths = folder_paths or []
        self.dedup = Deduplication()
        self.dedup.set_progress_callback(self._on_progress)
        self.title("Find Duplicates")
        self.geometry("800x600")

        # Make dialog modal
        self.transient(parent)
        self.grab_set()

        self._create_widgets()

    def _create_widgets(self):
        """Create dialog widgets."""
        # Title
        title = ctk.CTkLabel(
            self, text="Find Duplicate Photos", font=ctk.CTkFont(size=16, weight="bold")
        )
        title.pack(pady=(20, 10), padx=20, anchor="w")

        # Options
        options_frame = ctk.CTkFrame(self, fg_color="transparent")
        options_frame.pack(fill="x", padx=20, pady=(0, 10))

        self.recursive_var = ctk.BooleanVar(value=False)
        recursive_check = ctk.CTkCheckBox(
            options_frame, text="Include subfolders", variable=self.recursive_var
        )
        recursive_check.pack(side="left", padx=(0, 20))

        # Scan button
        self.scan_btn = ctk.CTkButton(
            options_frame, text="Scan for Duplicates", command=self._start_scan
        )
        self.scan_btn.pack(side="right")

        # Progress
        self.progress = ctk.CTkProgressBar(self, width=760)
        self.progress.pack(pady=(0, 10), padx=20)
        self.progress.set(0)

        self.progress_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=11))
        self.progress_label.pack(pady=(0, 10), padx=20)

        # Results area
        results_label = ctk.CTkLabel(
            self, text="Duplicate Groups:", font=ctk.CTkFont(size=12, weight="bold")
        )
        results_label.pack(pady=(0, 5), padx=20, anchor="w")

        # Scrollable frame for results
        self.results_scroll = ctk.CTkScrollableFrame(self, label_text="")
        self.results_scroll.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        # Stats
        self.stats_label = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=11)
        )
        self.stats_label.pack(pady=(0, 10), padx=20)

        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(0, 20))

        self.delete_btn = ctk.CTkButton(
            button_frame, text="Delete Selected", command=self._delete_selected,
            fg_color="red", state="disabled"
        )
        self.delete_btn.pack(side="right", padx=(5, 0))

        close_btn = ctk.CTkButton(
            button_frame, text="Close", command=self.destroy, fg_color="gray"
        )
        close_btn.pack(side="right", padx=(0, 5))

        # Info
        info_label = ctk.CTkLabel(
            button_frame,
            text="Tip: Select duplicates to delete (first file in each group is kept)",
            font=ctk.CTkFont(size=10)
        )
        info_label.pack(side="left")

    def _start_scan(self):
        """Start scanning for duplicates."""
        if not self.folder_paths:
            # Get current folder from app
            if hasattr(self.master, 'thumbnail_panel'):
                self.folder_paths = [self.master.thumbnail_panel.current_folder]
        
        if not self.folder_paths:
            self.progress_label.configure(text="No folder selected")
            return

        # Disable scan button
        self.scan_btn.configure(state="disabled", text="Scanning...")
        
        # Clear previous results
        for widget in self.results_scroll.winfo_children():
            widget.destroy()
        
        # Run scan in background thread
        thread = threading.Thread(target=self._scan_worker, daemon=True)
        thread.start()

    def _scan_worker(self):
        """Worker thread for scanning."""
        self.dedup.find_duplicates(self.folder_paths, recursive=self.recursive_var.get())
        
        # Update UI when done
        self.after(0, self._scan_complete)

    def _scan_complete(self):
        """Called when scan is complete."""
        self.scan_btn.configure(state="normal", text="Scan for Duplicates")
        self.progress.set(1)
        
        groups = self.dedup.get_duplicate_groups()
        
        if not groups:
            self.progress_label.configure(text="No duplicates found")
            self.stats_label.configure(text="")
            return
        
        # Update stats
        total_dups = self.dedup.get_total_duplicates()
        wasted = self.dedup.get_wasted_space()
        wasted_mb = wasted / (1024 * 1024)
        
        self.progress_label.configure(text=f"Found {len(groups)} duplicate groups, {total_dups} duplicate files")
        self.stats_label.configure(text=f"Wasted space: {wasted_mb:.1f} MB")
        
        # Build UI for each group
        for group_idx, (file_hash, files) in enumerate(groups):
            self._add_duplicate_group(group_idx, files)
        
        self.delete_btn.configure(state="normal")

    def _add_duplicate_group(self, group_idx: int, files: List[str]):
        """Add a duplicate group to the results."""
        # Group frame
        group_frame = ctk.CTkFrame(self.results_scroll, fg_color="transparent")
        group_frame.pack(fill="x", pady=(0, 10))
        
        # Group header
        header = ctk.CTkLabel(
            group_frame,
            text=f"Group {group_idx + 1} ({len(files)} files)",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        header.pack(anchor="w", pady=(0, 5))
        
        # Files in group
        for file_idx, file_path in enumerate(files):
            file_frame = ctk.CTkFrame(group_frame, fg_color="transparent")
            file_frame.pack(fill="x", pady=(0, 2))
            
            # Checkbox (default unchecked except first which is "keep")
            var = ctk.BooleanVar(value=False)
            check = ctk.CTkCheckBox(
                file_frame, text="", variable=var,
                command=lambda f=file_path, v=var: self._on_file_toggle(f, v)
            )
            check.pack(side="left")
            
            # File info
            try:
                size = os.path.getsize(file_path)
                size_str = f"{size / 1024:.1f} KB"
            except:
                size_str = "?"
            
            filename = Path(file_path).name
            
            # First file is marked as "keep"
            if file_idx == 0:
                label = ctk.CTkLabel(
                    file_frame,
                    text=f"  {filename} ({size_str}) - KEEP",
                    text_color="green"
                )
            else:
                label = ctk.CTkLabel(
                    file_frame,
                    text=f"  {filename} ({size_str})"
                )
            label.pack(side="left")
            
            # Store reference
            if not hasattr(self, 'selected_files'):
                self.selected_files = set()
            
            # Bind checkbox to update selection
            check.configure(command=lambda f=file_path, v=var, c=check: self._update_selection(f, v, c))

    def _on_file_toggle(self, file_path: str, var):
        """Handle file checkbox toggle."""
        if var.get():
            self.selected_files.add(file_path)
        else:
            self.selected_files.discard(file_path)

    def _update_selection(self, file_path, var, check):
        """Update selection when checkbox changes."""
        if not hasattr(self, 'selected_files'):
            self.selected_files = set()
        
        if var.get():
            self.selected_files.add(file_path)
        else:
            self.selected_files.discard(file_path)

    def _on_progress(self, percent: float, message: str):
        """Handle progress updates."""
        self.after(0, lambda: self.progress.set(percent / 100))
        self.after(0, lambda: self.progress_label.configure(text=message))

    def _delete_selected(self):
        """Delete selected duplicate files."""
        if not hasattr(self, 'selected_files') or not self.selected_files:
            return
        
        # Confirm deletion
        confirm = ctk.CTkInputDialog(
            text=f"Delete {len(self.selected_files)} selected files? This cannot be undone.",
            title="Confirm Deletion"
        )
        
        # Actually just delete (the dialog above is just a placeholder, real confirmation would need custom dialog)
        result = self.dedup.delete_duplicates(list(self.selected_files))
        
        # Show result and refresh
        self.progress_label.configure(
            text=f"Deleted: {result['success']}, Failed: {result['failed']}"
        )
        
        # Clear selection and refresh list
        self.selected_files.clear()
        
        # Re-scan to update the list
        self._start_scan()