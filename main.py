#!/usr/bin/env python3
"""
Overseer - Malware Analysis Automation Tool
Unified entry point and configuration management
"""
import os
import sys
import json
from typing import Optional
from rich.console import Console
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

console = Console()

def get_default_config_path():
    # Use the directory of this script for the config file
    return Path(__file__).parent / "sample_config.json"

class ConfigManager:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config: Optional[dict] = None

    def load_config(self) -> dict:
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        with open(self.config_path, 'r') as f:
            config = json.load(f)
            self.config = config
            return config

    def save_config(self, config: dict):
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=4)

def launch_gui(config_path: str):
    from overseer.gui import overseerUI
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = overseerUI(config_path=config_path)
    window.show()
    app.exec()

def main():
    config_path = str(get_default_config_path())

    try:
        config_manager = ConfigManager(config_path)
        _ = config_manager.load_config()  # Load to validate config
    except Exception as e:
        console.print(f"[red]Error loading configuration:[/red] {str(e)}")
        sys.exit(1)

    launch_gui(config_path)

if __name__ == '__main__':
    main()
