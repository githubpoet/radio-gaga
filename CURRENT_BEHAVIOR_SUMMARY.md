# Current Command-line Behavior and Search Paths

## Current CLI Arguments

Based on `radio.py --help`:

```
usage: radio.py [-h] [--cli] [--config PATH] [--play STREAM_NAME]

Radio Gaga - Terminal-based Radio Streaming

optional arguments:
  -h, --help          show this help message and exit
  --cli               Use command-line interface instead of TUI
  --config PATH       Path to configuration file (radio.json or radio.yaml)
  --play STREAM_NAME  Play specified stream in batch mode (non-interactive)

Examples:
  radio.py                    # Start interactive TUI
  radio.py --cli             # Show CLI interface with stream info
  radio.py --play NTS1       # Play NTS1 stream in batch mode
  radio.py --config /path/to/config.json --play NTS2
```

## Current Configuration Search Behavior

### Default Search (when no `--config` provided)
From `config.py:load_config()`:

1. **Script directory only**: `Path(__file__).parent`
2. **YAML first**: `radio.yaml` (if PyYAML available)
3. **JSON fallback**: `radio.json`
4. **Hard-coded defaults**: `DEFAULT_CONFIG` if no files found

### Custom Config Path (when `--config PATH` provided)
From `radio.py:main()`:

1. **Validate path exists**: `config_path.exists()`
2. **Directory manipulation hack**: `os.chdir(config_path.parent)`
3. **Clear cache**: `config._config_cache = None`
4. **Force reload**: Configuration is loaded from new directory context

### Current Configuration Files Found

- **`/Users/sk/radio_tui/radio.yaml`**: YAML format, 3 streams (NTS1, NTS2, GDS.FM)
- **`/Users/sk/radio_tui/radio.json`**: JSON format, 2 streams (NTS1, NTS2)

## Current Issues

### Problems with `--config` Implementation

1. **Directory side effects**: `os.chdir()` changes working directory globally
2. **Cache invalidation**: Manual cache clearing required
3. **Error prone**: Directory restoration on exception/exit
4. **Thread unsafe**: Global directory change affects entire process

### Problems with Search Paths

1. **Inflexible**: Only looks in script directory
2. **No user config**: Doesn't check user-specific locations
3. **No environment variables**: No `RADIO_GAGA_CONFIG` support
4. **Platform agnostic**: Doesn't follow OS conventions (XDG, macOS, Windows)

### Current Code Flow

```python
# In radio.py
if args.config:
    config_path = Path(args.config)
    original_dir = os.getcwd()
    try:
        os.chdir(config_path.parent)  # HACK: Change directory
        import config
        config._config_cache = None   # HACK: Clear cache
    except Exception as e:
        # Error handling
        
# Later in the code
config = load_config()  # Loads from current directory context

# At the end
if args.config:
    try:
        os.chdir(original_dir)  # HACK: Restore directory
    except:
        pass
```

## Current Test Coverage

### Existing Tests
- **Manual testing**: `quick_manual_test.py` (TUI functionality only)
- **Setup validation**: `setup.py` (dependency checking)
- **No unit tests**: No pytest test files found
- **No integration tests**: No CLI behavior tests

### Test Gaps
- Configuration loading logic
- Search path behavior
- CLI argument parsing
- Error handling
- Custom config path handling
- Cross-platform compatibility

## Current Dependencies

From `requirements.txt`:
- **requests>=2.28.0**: For HTTP requests
- **PyYAML>=6.0.0**: Optional YAML support (falls back to JSON)

## Current Configuration Format

### YAML Format (preferred)
```yaml
streams:
  - name: NTS1
    url: https://stream-relay-geo.ntslive.net/stream
  - name: NTS2
    url: https://stream-relay-geo.ntslive.net/stream2
defaults:
  volume: 1.0
  start_paused: true
```

### JSON Format (fallback)
```json
{
  "streams": [
    {
      "name": "NTS1",
      "url": "https://stream-relay-geo.ntslive.net/stream"
    },
    {
      "name": "NTS2",
      "url": "https://stream-relay-geo.ntslive.net/stream2"
    }
  ],
  "defaults": {
    "volume": 1.0,
    "start_paused": true
  }
}
```

## Directory Structure

```
/Users/sk/radio_tui/
├── config.py              # Configuration loading module
├── radio.py               # Main CLI entry point
├── radio.yaml             # YAML config file
├── radio.json             # JSON config file
├── requirements.txt       # Dependencies
├── utils/
│   ├── __init__.py
│   ├── stream_manager.py  # Stream management
│   └── now_playing.py     # Now playing info
└── ... (other files)
```

This summary captures the current state before refactoring begins.
