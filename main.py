#!/usr/bin/env python3
"""
Overseer - Malware Analysis Automation Tool
Unified entry point and configuration management
"""
import os
import sys
import json
import argparse
from dataclasses import dataclass
from typing import List, Optional
from rich.console import Console
from pathlib import Path

console = Console()

def get_overseer_root():
    return Path.home() / "Desktop" / "Tools"

def get_default_config_path():
    # Use the directory of this script for the config file
    return Path(__file__).parent / "sample_config.json"

@dataclass
class ToolConfig:
    name: str
    path: str
    type: str  # 'static' or 'dynamic'
    arguments: List[str]
    working_directory: Optional[str] = None

@dataclass
class OverseerConfig:
    binary_path: str
    tools_folder: str
    tools: List[ToolConfig]

class ConfigManager:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config: Optional[dict] = None

    def load_config(self) -> dict:
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        with open(self.config_path, 'r') as f:
            self.config = json.load(f)
        return self.config

    def save_config(self, config: dict):
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=4)

# --- CLI and GUI Launch ---
def list_tools(config: dict):
    for tool_name, enabled in config.get('static_tools', {}).items():
        console.print(f"[green]{tool_name}[/green] (static)")
    for tool_name, enabled in config.get('dynamic_tools', {}).items():
        console.print(f"[green]{tool_name}[/green] (dynamic)")

def run_cli(config: dict, static: bool, dynamic: bool):
    if static:
        console.print("Running all static analysis tools...")
    elif dynamic:
        console.print("Running all dynamic analysis tools...")
    else:
        console.print("Running all tools...")

def launch_gui(config_path: str):
    from Utils.gui import overseerUI
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = overseerUI(config_path=config_path)
    window.show()
    app.exec()

def main():
    parser = argparse.ArgumentParser(description="Overseer - Malware Analysis Automation Tool")
    parser.add_argument('--config', '-c', default=str(get_default_config_path()), help='Path to configuration file')
    parser.add_argument('--cli', action='store_true', help='Run in CLI mode')
    parser.add_argument('--static', action='store_true', help='Run static analysis tools (CLI mode only)')
    parser.add_argument('--dynamic', action='store_true', help='Run dynamic analysis tools (CLI mode only)')
    parser.add_argument('--list-tools', action='store_true', help='List available tools (CLI mode only)')
    args = parser.parse_args()

    try:
        config_manager = ConfigManager(args.config)
        overseer_config = config_manager.load_config()
    except Exception as e:
        console.print(f"[red]Error loading configuration:[/red] {str(e)}")
        sys.exit(1)

    if args.cli or args.list_tools or args.static or args.dynamic:
        if args.list_tools:
            list_tools(overseer_config)
        else:
            run_cli(overseer_config, args.static, args.dynamic)
    else:
        launch_gui(args.config)

if __name__ == '__main__':
    main()
