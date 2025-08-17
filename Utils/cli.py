#!/usr/bin/env python3
"""
Overseer - Malware Analysis Automation Tool
Main entry point
"""
import sys
import click
from typing import Optional
from main import ConfigManager, OverseerConfig
from Utils.tools import ToolManager
from rich.console import Console

console = Console()

def load_config(config_path: str) -> OverseerConfig:
    """Load and validate configuration"""
    try:
        config_manager = ConfigManager(config_path)
        return config_manager.load_config()
    except Exception as e:
        console.print(f"[red]Error loading configuration:[/red] {str(e)}")
        sys.exit(1)

def run_cli(config: OverseerConfig, tool: Optional[str] = None, static: bool = False, dynamic: bool = False):
    """Run analysis in CLI mode"""
    tool_manager = ToolManager(config.tools)
    
    if tool:
        try:
            result = tool_manager.run_tool(tool)
            console.print(f"\n=== {result['tool_name']} ===")
            console.print(f"Success: {result['success']}")
            if 'error' in result:
                console.print(f"[red]Error:[/red] {result['error']}")
            else:
                if result['stdout']:
                    console.print(f"\nOutput:\n{result['stdout']}")
                if result['stderr']:
                    console.print(f"\nErrors:\n{result['stderr']}")
        except KeyError:
            console.print(f"[red]Error:[/red] Tool '{tool}' not found")
            sys.exit(1)
    elif static:
        results = tool_manager.run_all_static()
        for result in results:
            console.print(f"\n=== {result['tool_name']} ===")
            console.print(f"Success: {result['success']}")
            if 'error' in result:
                console.print(f"[red]Error:[/red] {result['error']}")
            else:
                if result['stdout']:
                    console.print(f"\nOutput:\n{result['stdout']}")
                if result['stderr']:
                    console.print(f"\nErrors:\n{result['stderr']}")
    elif dynamic:
        results = tool_manager.run_all_dynamic()
        for result in results:
            console.print(f"\n=== {result['tool_name']} ===")
            console.print(f"Success: {result['success']}")
            if 'error' in result:
                console.print(f"[red]Error:[/red] {result['error']}")
            else:
                if result['stdout']:
                    console.print(f"\nOutput:\n{result['stdout']}")
                if result['stderr']:
                    console.print(f"\nErrors:\n{result['stderr']}")
    else:
        results = tool_manager.run_all()
        for result in results:
            console.print(f"\n=== {result['tool_name']} ===")
            console.print(f"Success: {result['success']}")
            if 'error' in result:
                console.print(f"[red]Error:[/red] {result['error']}")
            else:
                if result['stdout']:
                    console.print(f"\nOutput:\n{result['stdout']}")
                if result['stderr']:
                    console.print(f"\nErrors:\n{result['stderr']}")

@click.group()
def cli():
    """Overseer - Malware Analysis Automation Tool"""
    pass

@cli.command()
@click.option('--config', '-c', required=True, help='Path to config JSON file')
@click.option('--cli', is_flag=True, help='Run in CLI mode (default is GUI)')
@click.option('--tool', '-t', help='Run a specific tool')
@click.option('--static', is_flag=True, help='Run all static analysis tools')
@click.option('--dynamic', is_flag=True, help='Run all dynamic analysis tools')
def run(config: str, cli: bool, tool: Optional[str], static: bool, dynamic: bool):
    """Run analysis tools"""
    config_obj = load_config(config)
    
    if not cli:
        # Default to GUI mode
        try:
            from overseer.gui import launch_gui
            launch_gui(config_obj)
        except ImportError as e:
            console.print("[red]Error:[/red] Could not load GUI. Make sure PyQt5 is installed.")
            console.print(f"Error details: {str(e)}")
            sys.exit(1)
    else:
        run_cli(config_obj, tool, static, dynamic)

@cli.command()
@click.option('--config', '-c', required=True, help='Path to config JSON file')
def list_tools(config: str):
    """List available tools"""
    config_obj = load_config(config)
    
    console.print("\n[bold]Available Tools:[/bold]")
    for tool in config_obj.tools:
        console.print(f"\n[bold]{tool.name}[/bold]")
        console.print(f"Type: {tool.type}")
        console.print(f"Path: {tool.path}")
        if tool.arguments:
            console.print(f"Arguments: {' '.join(tool.arguments)}")
        if tool.working_directory:
            console.print(f"Working Directory: {tool.working_directory}")

if __name__ == '__main__':
    cli()
