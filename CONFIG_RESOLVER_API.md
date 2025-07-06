# Configuration Resolution Helper API

This document defines the API contract for the radio-gaga configuration resolution system, implemented in `config_resolver.py`.

## Core API Functions

### `get_config_path(cli_arg: str | None) → Path`

Resolves the configuration file path following the specified priority order.

**Parameters:**
- `cli_arg` (optional): Explicit path from CLI argument (highest priority)

**Returns:**
- `Path`: Resolved configuration file path

**Search Order:**
1. CLI argument (explicit absolute/relative path)
2. `RADIO_GAGA_CONFIG` environment variable 
3. Platform-specific user directories:
   - **macOS**: `~/Library/Application Support/radio-gaga/radio.yaml`
   - **Linux**: `~/.config/radio-gaga/radio.yaml` (respects `XDG_CONFIG_HOME`)
   - **Windows**: `%APPDATA%/radio-gaga/radio.yaml`
4. Legacy locations:
   - `./radio.yaml` (current working directory)
   - `./radio.json` (current working directory)
5. Packaged defaults: `<app_dir>/radio.yaml`

**Raises:**
- `ConfigurationError`: No configuration file found in any search location

**Example:**
```python
from config_resolver import get_config_path

# Use default search order
config_path = get_config_path()

# Use explicit path
config_path = get_config_path("./my-config.yaml")
```

### `load_config(path: Path) → dict`

Loads and parses configuration from the specified file path.

**Parameters:**
- `path`: Path to configuration file

**Returns:**
- `dict`: Parsed configuration data

**Supported Formats:**
- YAML (`.yaml`, `.yml`) - requires PyYAML
- JSON (`.json`)
- Auto-detection for files without extensions

**Raises:**
- `ConfigurationError`: File doesn't exist, can't be read, or has invalid format

**Example:**
```python
from config_resolver import load_config
from pathlib import Path

config = load_config(Path("./radio.yaml"))
streams = config.get("streams", [])
```

### `ensure_user_default() → Path`

Creates a user configuration file with commented template if none exists.

**Parameters:** None

**Returns:**
- `Path`: Path to user configuration file (created or existing)

**Behavior:**
- Creates platform-appropriate config directory if needed
- Generates `radio.yaml` with commented template
- Does NOT overwrite existing configuration files
- Uses platform-specific locations (same as `get_config_path`)

**Raises:**
- `ConfigurationError`: Cannot create config directory or file

**Example:**
```python
from config_resolver import ensure_user_default

# Ensure user has a config file
user_config_path = ensure_user_default()
print(f"User config at: {user_config_path}")
```

## High-Level API Functions

### `resolve_and_load_config(cli_arg: str | None) → tuple[Path, dict]`

Main entry point combining path resolution and configuration loading.

**Parameters:**
- `cli_arg` (optional): Explicit path from CLI argument

**Returns:**
- `tuple[Path, dict]`: (resolved_path, config_dict)

**Behavior:**
- Automatically calls `ensure_user_default()` on first run
- Falls back to hard-coded defaults if no config found
- Handles all error cases gracefully

**Example:**
```python
from config_resolver import resolve_and_load_config

# Load configuration with automatic fallbacks
config_path, config = resolve_and_load_config()
print(f"Using config from: {config_path}")

# With CLI argument
config_path, config = resolve_and_load_config("./custom.yaml")
```

### `load_configuration(cli_arg: str | None) → dict`

Backward-compatible simple configuration loading function.

**Parameters:**
- `cli_arg` (optional): Explicit path from CLI argument

**Returns:**
- `dict`: Loaded configuration

**Example:**
```python
from config_resolver import load_configuration

# Simple configuration loading
config = load_configuration()
streams = config.get("streams", [])
```

## Utility Functions

### `get_config_info(cli_arg: str | None) → dict`

Returns detailed information about configuration resolution for debugging.

**Parameters:**
- `cli_arg` (optional): Explicit path from CLI argument

**Returns:**
- `dict`: Configuration resolution information

**Returned Fields:**
```python
{
    "platform": "Darwin",
    "platform_config_dir": "/Users/user/Library/Application Support/radio-gaga",
    "packaged_config_path": "/app/radio.yaml", 
    "environment_variable": None,
    "cli_argument": None,
    "search_paths": [...],
    "resolved_path": "/path/to/config.yaml",
    "config_exists": True,
    "user_config_exists": False,
    "error": None
}
```

**Example:**
```python
from config_resolver import get_config_info

info = get_config_info()
print(f"Platform: {info['platform']}")
print(f"Config directory: {info['platform_config_dir']}")
```

## Error Handling

### `ConfigurationError`

Rich exception providing detailed context about configuration failures.

**Attributes:**
- `message`: Primary error message
- `search_paths`: List of paths that were searched
- `original_error`: Underlying exception (if any)

**Example:**
```python
from config_resolver import resolve_and_load_config, ConfigurationError

try:
    config_path, config = resolve_and_load_config()
except ConfigurationError as e:
    print(f"Configuration error: {e}")
    print(f"Searched paths: {e.search_paths}")
    if e.original_error:
        print(f"Root cause: {e.original_error}")
```

## Environment Variables

### `RADIO_GAGA_CONFIG`

Set this environment variable to override the default configuration search behavior.

**Examples:**
```bash
# Use specific config file
export RADIO_GAGA_CONFIG=/path/to/my-config.yaml
radio.py

# Use relative path
export RADIO_GAGA_CONFIG=./configs/production.yaml
radio.py

# With tilde expansion
export RADIO_GAGA_CONFIG=~/my-radio-config.yaml
radio.py
```

## Platform-Specific Paths

### macOS
- User config: `~/Library/Application Support/radio-gaga/radio.yaml`
- Follows macOS Application Support conventions

### Linux  
- User config: `~/.config/radio-gaga/radio.yaml`
- Respects `XDG_CONFIG_HOME` environment variable
- Falls back to `~/.config` if `XDG_CONFIG_HOME` not set

### Windows
- User config: `%APPDATA%/radio-gaga/radio.yaml`
- Uses Windows Roaming Application Data folder

## Configuration File Format

### Basic Structure
```yaml
# Available radio streams
streams:
  - name: Stream Name
    url: https://stream-url.com/stream

# Default application settings  
defaults:
  volume: 1.0
  start_paused: true
```

### Supported Formats
- **YAML** (preferred): `.yaml`, `.yml` extensions
- **JSON** (legacy): `.json` extension
- **Auto-detection**: Files without extensions try JSON first, then YAML

## Integration Examples

### CLI Integration
```python
import argparse
from config_resolver import resolve_and_load_config

parser = argparse.ArgumentParser()
parser.add_argument("--config", help="Configuration file path")
args = parser.parse_args()

# Load configuration with CLI support
config_path, config = resolve_and_load_config(args.config)
```

### Backward Compatibility
```python
# Drop-in replacement for existing load_config()
from config_resolver import load_configuration as load_config

config = load_config()  # Works exactly like the old API
```

## Key Design Principles

1. **No Directory Side Effects**: Never uses `os.chdir()` or changes working directory
2. **Rich Error Messages**: Provides context about search paths and failure reasons  
3. **Platform Awareness**: Uses appropriate directories for each operating system
4. **Graceful Fallbacks**: Always provides usable configuration, even with errors
5. **Lazy Loading**: Only loads configuration when actually needed
6. **Cache-Free**: No hidden caching that could cause stale data issues

## Testing

The API can be tested using the command-line interface:

```bash
# Show configuration resolution info
python3 config_resolver.py --info

# Test configuration loading
python3 config_resolver.py

# Test with custom config
python3 config_resolver.py --config ./my-config.yaml --info

# Test with environment variable
RADIO_GAGA_CONFIG=./test.yaml python3 config_resolver.py --info
```
