#!/usr/bin/env python3
"""
GUI package entry point.
"""

from gui.app import PhotoToolsApp
import customtkinter as ctk

if __name__ == "__main__":
    ctk.set_appearance_mode("system")
    ctk.set_default_color_theme("blue")
    app = PhotoToolsApp()
    app.mainloop()
