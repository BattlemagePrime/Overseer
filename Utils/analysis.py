import os
import json
from pathlib import Path
from typing import Optional, Callable, Dict, Any, Union
# from main import ToolConfig  # Uncomment if you use ToolConfig in this file


def start_analysis_from_config(
    config: Union[str, Dict[str, Any]],
    status_callback: Optional[Callable[[str], None]] = None
) -> Dict[str, Any]:
    """
    Prepare the analysis environment and return a summary of what will be run.
    - config: path to config file or config dict
    - status_callback: function to call with status messages (for GUI/CLI)
    Returns a dict with summary/results.
    """
    def report(msg):
        if status_callback:
            status_callback(msg)
        else:
            print(msg)

    # Load config if a path is given
    if isinstance(config, str):
        with open(config, 'r') as f:
            config = json.load(f)
    assert isinstance(config, dict), "Config must be a dict after loading."

    # Extract paths
    paths = config.get("paths", {})
    analysis_dir = Path(paths.get("analysis", "./analysis"))
    tools_dir = Path(paths.get("tools", "./tools"))
    binary_dir = Path(paths.get("binary", "./binary"))
    utils_dir = Path(paths.get("utils", "./utils"))
    desktop_dir = Path(paths.get("desktop", "./"))

    # Ensure directories exist
    for d in [analysis_dir, tools_dir, binary_dir, utils_dir, desktop_dir]:
        d.mkdir(parents=True, exist_ok=True)

    # Collect which tools will be run
    static_tools = [tool for tool, enabled in config.get("static_tools", {}).items() if enabled]
    dynamic_tools = [tool for tool, enabled in config.get("dynamic_tools", {}).items() if enabled]

    report("Static tools to run:")
    for tool in static_tools:
        report(f"  - {tool}")

    report("Dynamic tools to run:")
    for tool in dynamic_tools:
        report(f"  - {tool}")

    # Procmon settings
    procmon = config.get("procmon_settings", {})
    if procmon.get("enabled"):
        report(f"Procmon enabled: duration={procmon.get('duration')} disable_timer={procmon.get('disable_timer')}")

    # Binary info
    binary = config.get("binary", {})
    report(f"Binary path: {binary.get('path')}")
    report(f"Run: {binary.get('run')}, As Admin: {binary.get('as_admin')}")

    # VM info (if needed)
    vm = config.get("vm", {})
    if vm:
        report(f"VM type: {vm.get('type')}, Path: {vm.get('path')}, Snapshot: {vm.get('snapshot')}")

    # Here you would add logic to:
    # - Copy the binary to the analysis dir
    # - Launch each enabled tool with the correct arguments
    # - Handle VM automation if needed
    # - Collect and store results in the analysis dir

    report("Analysis environment prepared. Ready to launch tools.")

    # Return a summary for further use (GUI/CLI)
    return {
        "static_tools": static_tools,
        "dynamic_tools": dynamic_tools,
        "procmon": procmon,
        "binary": binary,
        "vm": vm,
        "paths": paths
    }

# Example usage (uncomment to test):
# start_analysis_from_config("sample_config.json")
