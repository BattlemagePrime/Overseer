# Overseer

Overseer is a malware analysis automation tool that can run multiple static and dynamic analysis tools on a target binary.

## Features

- Run multiple analysis tools in sequence
- Support for both static and dynamic analysis tools
- GUI mode for interactive analysis
- CLI mode for automation and scripting
- Configurable via JSON configuration files
- Support for tool-specific working directories and arguments

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\activate
   ```
3. Install the package:
   ```powershell
   pip install -e .
   ```

## Configuration

Create a JSON configuration file with your tools setup. Example:

```json
{
    "binary_path": "path/to/target/binary",
    "tools_folder": "path/to/tools",
    "tools": [
        {
            "name": "strings",
            "path": "tools/strings.exe",
            "type": "static",
            "arguments": ["-a"]
        }
    ]
}
```

## Usage

### GUI Mode (Default)

```powershell
overseer run --config config.json
```

### CLI Mode (Optional)

Run all tools:
```powershell
overseer run --config config.json
```

Run specific tool:
```powershell
overseer run --config config.json --tool strings
```

Run all static analysis tools:
```powershell
overseer run --config config.json --static
```

Run all dynamic analysis tools:
```powershell
overseer run --config config.json --dynamic
```

List available tools:
```powershell
overseer list-tools --config config.json
```

## Building Executable

To create a standalone executable:

```powershell
pyinstaller --onefile overseer\__main__.py --name overseer
```

The executable will be created in the `dist` directory.

## Development

To install development dependencies:

```powershell
pip install -e ".[dev]"
```
