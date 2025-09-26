#!/usr/bin/env python3
"""
Version Management for Bongo Cat Application
Provides version information and update checking
"""

import json
from pathlib import Path

class VersionManager:
    """Manages application version information"""

    VERSION = "1.0.0"
    VERSION_FILE = "version.json"

    @staticmethod
    def get_version():
        """Get current application version"""
        return VersionManager.VERSION

    @staticmethod
    def get_version_info():
        """Get detailed version information"""
        return {
            "version": VersionManager.VERSION,
            "major": 1,
            "minor": 0,
            "patch": 0,
            "features": [
                "Basic system monitoring",
                "ESP32 display integration",
                "Advanced hardware monitoring (optional)"
            ]
        }

    @staticmethod
    def save_version_info(filepath=None):
        """Save version information to file"""
        if filepath is None:
            filepath = Path.cwd() / VersionManager.VERSION_FILE

        version_info = VersionManager.get_version_info()
        try:
            with open(filepath, 'w') as f:
                json.dump(version_info, f, indent=2)
            return True
        except Exception as e:
            print(f"❌ Error saving version info: {e}")
            return False

    @staticmethod
    def load_version_info(filepath=None):
        """Load version information from file"""
        if filepath is None:
            filepath = Path.cwd() / VersionManager.VERSION_FILE

        try:
            if filepath.exists():
                with open(filepath, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"❌ Error loading version info: {e}")
        return None