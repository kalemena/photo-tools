#!/usr/bin/env python3
"""
Photo Tools GUI - Main entry point
A CustomTkinter-based photo management application with 3-panel layout.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk
from gui.app import PhotoToolsApp


def main():
    """Main entry point for the Photo Tools GUI application."""
    # Set CustomTkinter appearance
    ctk.set_appearance_mode("system")  # "system", "dark", "light"
    ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"

    # Create and run application
    app = PhotoToolsApp()
    app.mainloop()


if __name__ == "__main__":
    main()
