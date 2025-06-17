#!/usr/bin/env python3
"""
Settings - Persist application settings between sessions.
"""

import json
import os
from pathlib import Path
import customtkinter as ctk


class Settings:
    """Manages application settings with JSON persistence."""

    DEFAULT_SETTINGS = {
        "appearance_mode": "system",  # "system", "dark", "light"
        "window_geometry": "1400x900",
        "last_folder": "",
        "last_folders": [],  # Recent folders
    }

    def __init__(self):
        self.settings_file = self._get_settings_path()
        self.settings = self._load()

    def _get_settings_path(self) -> Path:
        """Get platform-appropriate settings file path."""
        if os.name == "nt":  # Windows
            config_dir = Path(os.environ.get("APPDATA", "")) / "photo-tools"
        elif os.name == "posix":
            if "XDG_CONFIG_HOME" in os.environ:
                config_dir = Path(os.environ["XDG_CONFIG_HOME"]) / "photo-tools"
            else:
                config_dir = Path.home() / ".config" / "photo-tools"
        else:
            config_dir = Path.home() / ".photo-tools"
        
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / "settings.json"

    def _load(self) -> dict:
        """Load settings from file or return defaults."""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, "r") as f:
                    loaded = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    return {**self.DEFAULT_SETTINGS, **loaded}
        except Exception as e:
            print(f"Error loading settings: {e}")
        
        return self.DEFAULT_SETTINGS.copy()

    def save(self):
        """Save settings to file."""
        try:
            with open(self.settings_file, "w") as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def get(self, key: str, default=None):
        """Get a setting value."""
        return self.settings.get(key, default)

    def set(self, key: str, value):
        """Set a setting value and save."""
        self.settings[key] = value
        self.save()

    def add_recent_folder(self, folder: str):
        """Add a folder to recent folders list."""
        if not folder:
            return
        
        recent = self.settings.get("last_folders", [])
        
        # Remove if already exists
        if folder in recent:
            recent.remove(folder)
        
        # Add to front
        recent.insert(0, folder)
        
        # Keep only last 10
        self.settings["last_folders"] = recent[:10]
        self.save()

    def get_recent_folders(self) -> list:
        """Get list of recent folders."""
        return self.settings.get("last_folders", [])


# Global settings instance
_settings = None


def get_settings() -> Settings:
    """Get the global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings