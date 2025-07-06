# Configuration Resolution Helper API Contract

## Core API Functions

```python
# Main path resolution function
get_config_path(cli_arg: str | None) → Path

# Configuration loading function  
load_config(path: Path) → dict

# User default creation function
ensure_user_default() → Path

# High-level combined function
resolve_and_load_config(cli_arg: str | None) → tuple[Path, dict]
```

## Search Order Implementation

1. **CLI argument** (highest priority)
   - Explicit absolute/relative path from `--config` flag
   
2. **Environment variable** 
   - `RADIO_GAGA_CONFIG` environment variable
   
3. **Platform-specific user directories**
   - **macOS**: `~/Library/Application Support/radio-gaga/radio.yaml`
   - **Linux**: `~/.config/radio-gaga/radio.yaml` (respects XDG_CONFIG_HOME)
   - **Windows**: `%APPDATA%/radio-gaga/radio.yaml`
   
4. **Legacy locations**
   - `./radio.yaml` (current working directory)
   - `./radio.json` (current working directory)
   
5. **Packaged defaults**
   - Falls back to `<app_dir>/radio.yaml`

## Key Requirements Met

✅ **No directory-changing side effects** - Never uses `os.chdir()`  
✅ **Rich error handling** - `ConfigurationError` with context and search paths  
✅ **CLI argument support** - Accepts explicit paths with highest priority  
✅ **Environment variable support** - `RADIO_GAGA_CONFIG` consultation  
✅ **XDG compliance** - Platform-appropriate config directories  
✅ **User template creation** - `ensure_user_default()` creates commented template  
✅ **Graceful fallbacks** - Always returns usable configuration  

## Error Handling

```python
class ConfigurationError(Exception):
    def __init__(self, message: str, search_paths: list = None, 
                 original_error: Exception = None)
```

Rich exception that provides:
- Detailed error message
- List of searched paths  
- Original underlying exception (if any)

## Usage Examples

```python
from config_resolver import resolve_and_load_config, get_config_path, ConfigurationError

# Simple usage - handles everything automatically
try:
    config_path, config = resolve_and_load_config()
    print(f"Loaded from: {config_path}")
except ConfigurationError as e:
    print(f"Config error: {e}")

# With CLI argument
config_path, config = resolve_and_load_config(cli_arg="/path/to/config.yaml")

# Step-by-step usage
path = get_config_path(cli_arg)
config = load_config(path)

# Ensure user config exists
ensure_user_default()
```

## Testing Verification

```bash
# Test all functionality
python3 config_resolver.py --info                          # Show resolution info
python3 config_resolver.py --config ./radio.yaml           # Test CLI priority
RADIO_GAGA_CONFIG=./radio.json python3 config_resolver.py  # Test environment variable
```

## Implementation Status: ✅ COMPLETE

All requirements from the task have been implemented and tested:

1. ✅ Accepts explicit paths from CLI flags
2. ✅ Consults `RADIO_GAGA_CONFIG` environment variable  
3. ✅ Probes XDG directories on Linux, macOS Application Support
4. ✅ Falls back to packaged `radio.yaml`
5. ✅ Calls `ensure_user_default()` to create commented template
6. ✅ Returns discovered path with rich error handling
7. ✅ No directory-changing side effects
