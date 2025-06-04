#!/usr/bin/env python3
"""
Status Bar - Bottom status bar for user feedback and operations.
"""

import customtkinter as ctk
import threading
import time


class StatusBar(ctk.CTkFrame):
    """Bottom status bar with progress and messages."""

    def __init__(self, master):
        super().__init__(master, height=30, corner_radius=0)
        
        # Status message
        self.status_label = ctk.CTkLabel(
            self, text="Ready", font=ctk.CTkFont(size=11)
        )
        self.status_label.pack(side="left", padx=10)
        
        # Progress bar (hidden by default)
        self.progress = ctk.CTkProgressBar(self, width=200, height=10)
        self.progress.pack(side="right", padx=10)
        self.progress.pack_forget()
        
        # Progress label
        self.progress_label = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=10)
        )
        self.progress_label.pack(side="right", padx=(0, 5))
        self.progress_label.pack_forget()
        
        # Operation running flag
        self.operation_running = False

    def set_status(self, message):
        """Set status message."""
        self.status_label.configure(text=message)

    def show_progress(self, show=True):
        """Show or hide progress bar."""
        if show:
            self.progress.pack(side="right", padx=10)
            self.progress_label.pack(side="right", padx=(0, 5))
        else:
            self.progress.pack_forget()
            self.progress_label.pack_forget()

    def set_progress(self, value, message=""):
        """Set progress value (0.0-1.0) and optional message."""
        self.progress.set(value)
        if message:
            self.progress_label.configure(text=message)

    def start_operation(self, message="Processing..."):
        """Start an operation with progress."""
        self.operation_running = True
        self.set_status(message)
        self.show_progress(True)
        self.set_progress(0)

    def end_operation(self, message="Ready", success=True):
        """End an operation."""
        self.operation_running = False
        self.set_status(message)
        self.show_progress(False)
        
        # Auto-reset to "Ready" after 3 seconds
        def reset_status():
            if not self.operation_running:
                self.set_status("Ready")
        
        self.after(3000, reset_status)


class ToastNotification(ctk.CTkFrame):
    """Toast notification popup."""

    def __init__(self, parent, message, duration=3000, success=True):
        super().__init__(parent, corner_radius=10)
        
        # Position at top-right
        self.place(relx=0.98, rely=0.02, anchor="ne")
        
        # Style based on success/failure
        fg_color = ("green", "#1a5c1a") if success else ("red", "#5c1a1a")
        self.configure(fg_color=fg_color, border_width=1, border_color=fg_color)
        
        # Message
        label = ctk.CTkLabel(
            self, text=message, font=ctk.CTkFont(size=12),
            text_color=("white", "white"), wraplength=300
        )
        label.pack(padx=15, pady=10)
        
        # Schedule removal
        self.after(duration, self.destroy)


def show_toast(parent, message, duration=3000, success=True):
    """Show a toast notification."""
    toast = ToastNotification(parent, message, duration, success)
    return toast