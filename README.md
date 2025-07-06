# Radio Gaga

A terminal-based radio streaming application with a curses-based user interface.

## Features

- **Curses-based TUI**: Beautiful terminal interface with keyboard navigation
- **Stream Management**: Control multiple radio stations with play/stop/switch functionality  
- **Now Playing Information**: Real-time track information from NTS API and ICY metadata
- **Keyboard Navigation**: Intuitive controls with arrow keys and number shortcuts
- **Live Updates**: UI refreshes at ~5Hz with current playback status
- **Configuration Support**: YAML or JSON configuration files
- **Enhanced Metadata Display**: Improved track information with smart fallback logic
- **Optimized UI Performance**: Smooth rendering with differential screen updates

## TUI Interface

The terminal interface displays:

```
                           Radio Gaga
        ↑/↓ or 1-9: Navigate | Space/Enter: Play/Stop | Q: Quit
────────────────────────────────────────────────────────────────

 [▶] NTS1 | Current Artist - Track Title
 [■] NTS2 | Loading...

Playing: NTS1                                           14:32:15
```

### Key Bindings

- **↑/↓ Arrow Keys**: Navigate up/down through streams
- **1-9 Number Keys**: Jump directly to stream (1-indexed)
- **Space/Enter**: Start/stop/switch streams
- **Q**: Quit the application

### Display Format

Each stream line shows: `[▶/■] Stream Name | Now Playing`
- **▶**: Currently playing stream
- **■**: Stopped/inactive stream
- **Highlighted line**: Currently selected stream
- **Green text**: Playing stream
- **White on black**: Selected stream

## Requirements

- Python 3.7+
- FFmpeg (for audio playback) 
- requests library
- PyYAML (optional, for YAML configuration support)
- Terminal with color support (recommended)

## Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install FFmpeg:
   - macOS: `brew install ffmpeg`
   - Ubuntu/Debian: `sudo apt install ffmpeg`
   - Windows: Download from https://ffmpeg.org/

## Configuration

Create a `radio.yaml` file (or `radio.json` as fallback) with your stream configuration:

```yaml
streams:
  - name: "NTS1"
    url: "https://stream-relay-geo.ntslive.net/stream"
  - name: "NTS2"
    url: "https://stream-relay-geo.ntslive.net/stream2"

defaults:
  volume: 1.0
  start_paused: true
```

## Custom Configuration

Radio Gaga supports flexible configuration through multiple methods and platforms. The application follows a hierarchical configuration resolution system with comprehensive platform support.

### Configuration File Locations

The application searches for configuration files in the following order:

1. **Explicit CLI argument**: `--config /path/to/config.yaml`
2. **Environment variable**: `RADIO_GAGA_CONFIG=/path/to/config.yaml`
3. **Platform-specific user directories**:
   - **Linux**: `~/.config/radio-gaga/radio.yaml`
   - **macOS**: `~/Library/Application Support/radio-gaga/radio.yaml`
   - **Windows**: `%APPDATA%/radio-gaga/radio.yaml`
4. **Current directory**: `./radio.yaml` or `./radio.json`
5. **Packaged defaults**: Built-in configuration

### Platform-Specific Examples

#### Linux (XDG-compliant)
```bash
# Create config directory
mkdir -p ~/.config/radio-gaga

# Create configuration file
cat > ~/.config/radio-gaga/radio.yaml << 'EOF'
# Radio Gaga Configuration
streams:
  - name: "BBC Radio 1"
    url: "http://stream.live.vc.bbcmedia.co.uk/bbc_radio_one"
  - name: "NTS1"
    url: "https://stream-relay-geo.ntslive.net/stream"

defaults:
  volume: 0.8
  start_paused: false
EOF
```

#### macOS
```bash
# Create config directory
mkdir -p ~/Library/Application\ Support/radio-gaga

# Create configuration file
cat > ~/Library/Application\ Support/radio-gaga/radio.yaml << 'EOF'
# Radio Gaga Configuration
streams:
  - name: "KEXP"
    url: "https://kexp-mp3-128.streamguys1.com/kexp128.mp3"
  - name: "NTS2"
    url: "https://stream-relay-geo.ntslive.net/stream2"

defaults:
  volume: 1.0
  start_paused: true
EOF
```

#### Windows
```powershell
# Create config directory
New-Item -ItemType Directory -Force -Path "$env:APPDATA\radio-gaga"

# Create configuration file
@'
# Radio Gaga Configuration
streams:
  - name: "SomaFM"
    url: "https://ice1.somafm.com/groovesalad-256-mp3"
  - name: "NTS1"
    url: "https://stream-relay-geo.ntslive.net/stream"

defaults:
  volume: 0.9
  start_paused: false
'@ | Out-File -FilePath "$env:APPDATA\radio-gaga\radio.yaml" -Encoding UTF8
```

### CLI Configuration Examples

#### Using absolute paths
```bash
# Use specific config file
python radio.py --config /home/user/my-radio-config.yaml

# Use config with different format
python radio.py --config /path/to/config.json
```

#### Using relative paths
```bash
# Use config in current directory
python radio.py --config ./my-config.yaml

# Use config in parent directory
python radio.py --config ../shared-config.yaml
```

#### Combined with other options
```bash
# Use custom config and play specific stream
python radio.py --config ./production.yaml --play "BBC Radio 1"

# Use custom config with CLI interface
python radio.py --config ~/radio-stations.yaml --cli
```

### Environment Variable Examples

#### Linux/macOS
```bash
# Set environment variable for session
export RADIO_GAGA_CONFIG="/home/user/radio-config.yaml"
python radio.py

# Set environment variable for single run
RADIO_GAGA_CONFIG="./custom-config.yaml" python radio.py

# Use with XDG config directory
export RADIO_GAGA_CONFIG="$XDG_CONFIG_HOME/radio-gaga/radio.yaml"
python radio.py
```

#### Windows
```cmd
# Set environment variable for session
set RADIO_GAGA_CONFIG=C:\Users\Username\radio-config.yaml
python radio.py

# Set environment variable for single run
set RADIO_GAGA_CONFIG=.\custom-config.yaml && python radio.py
```

```powershell
# PowerShell syntax
$env:RADIO_GAGA_CONFIG = "C:\Users\Username\radio-config.yaml"
python radio.py

# PowerShell single run
$env:RADIO_GAGA_CONFIG = ".\custom-config.yaml"; python radio.py
```

### Configuration File Formats

#### YAML Format (Recommended)
```yaml
# Full configuration example
streams:
  - name: "NTS1"
    url: "https://stream-relay-geo.ntslive.net/stream"
  - name: "NTS2"
    url: "https://stream-relay-geo.ntslive.net/stream2"
  - name: "BBC Radio 6"
    url: "http://stream.live.vc.bbcmedia.co.uk/bbc_6music"
  - name: "KEXP"
    url: "https://kexp-mp3-128.streamguys1.com/kexp128.mp3"
  - name: "SomaFM Groove Salad"
    url: "https://ice1.somafm.com/groovesalad-256-mp3"

defaults:
  volume: 1.0          # Volume level (0.0 to 1.0)
  start_paused: true   # Start application in paused state
```

#### JSON Format (Alternative)
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

### Configuration Structure

#### Required Fields
- **streams**: Array of stream objects
  - **name**: Display name for the stream (string)
  - **url**: Stream URL (string)

#### Optional Fields
- **defaults**: Default application settings (object)
  - **volume**: Default volume level, 0.0 to 1.0 (float, default: 1.0)
  - **start_paused**: Whether to start in paused state (boolean, default: true)

#### Stream Configuration Examples
```yaml
streams:
  # Basic stream
  - name: "Simple Stream"
    url: "https://example.com/stream.mp3"
  
  # Stream with special characters
  - name: "Café del Mar"
    url: "https://example.com/special-stream"
  
  # Long stream names are automatically truncated in UI
  - name: "Very Long Stream Name That Will Be Truncated"
    url: "https://example.com/long-name-stream"
```

### CLI Flags Reference

| Flag | Description | Example |
|------|-------------|----------|
| `--config PATH` | Specify configuration file path | `--config /path/to/config.yaml` |
| `--cli` | Use command-line interface instead of TUI | `--cli` |
| `--play STREAM` | Play specific stream in batch mode | `--play "NTS1"` |
| `--help` | Show help message | `--help` |

### Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|----------|
| `RADIO_GAGA_CONFIG` | Path to configuration file | `/home/user/radio.yaml` |
| `DEBUG` | Enable debug logging | `1` |
| `LOG_LEVEL` | Set logging verbosity | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `UPDATE_INTERVAL` | Metadata update interval in seconds | `30` |
| `XDG_CONFIG_HOME` | XDG config directory (Linux) | `/home/user/.config` |

### Advanced Configuration Examples

#### Development Setup
```bash
# Create development config
cat > dev-config.yaml << 'EOF'
streams:
  - name: "Local Test Stream"
    url: "http://localhost:8000/stream"
  - name: "NTS1"
    url: "https://stream-relay-geo.ntslive.net/stream"

defaults:
  volume: 0.5
  start_paused: false
EOF

# Run with development config and debug logging
DEBUG=1 python radio.py --config dev-config.yaml
```

#### Production Setup
```bash
# Create production config in standard location
mkdir -p ~/.config/radio-gaga
cat > ~/.config/radio-gaga/radio.yaml << 'EOF'
streams:
  - name: "BBC Radio 1"
    url: "http://stream.live.vc.bbcmedia.co.uk/bbc_radio_one"
  - name: "BBC Radio 6"
    url: "http://stream.live.vc.bbcmedia.co.uk/bbc_6music"
  - name: "KEXP"
    url: "https://kexp-mp3-128.streamguys1.com/kexp128.mp3"
  - name: "SomaFM"
    url: "https://ice1.somafm.com/groovesalad-256-mp3"

defaults:
  volume: 0.8
  start_paused: true
EOF

# Run with automatic config discovery
python radio.py
```

### Configuration Troubleshooting

#### Check Configuration Resolution
```bash
# Test configuration loading
python config.py --info

# Test specific config file
python config.py --config /path/to/config.yaml --info
```

#### Common Issues

1. **"Configuration file not found"**
   - Verify file path and permissions
   - Check environment variable spelling
   - Ensure file has correct extension (`.yaml`, `.yml`, or `.json`)

2. **"Invalid YAML/JSON format"**
   - Validate syntax using online validators
   - Check for proper indentation in YAML
   - Ensure quotes are balanced in JSON

3. **"PyYAML not installed"**
   - Install with `pip install PyYAML`
   - Or use JSON format as alternative

4. **Streams not loading**
   - Verify stream URLs are accessible
   - Check network connectivity
   - Ensure stream names are unique

### Migration from Legacy Configurations

If you have an existing `radio.json` file, you can continue using it or migrate to YAML:

```bash
# Convert JSON to YAML (requires PyYAML)
python -c "
import json, yaml
with open('radio.json') as f:
    data = json.load(f)
with open('radio.yaml', 'w') as f:
    yaml.dump(data, f, default_flow_style=False)
"
```

## Usage

### TUI Mode (Default)

Run the terminal interface:

```bash
python radio.py
```

or directly:

```bash
python tui.py
```

### CLI Mode (Debug)

For debugging or testing without the TUI:

```bash
python radio.py --cli
```

### Testing

Test the TUI functionality:

```bash
python test_tui.py
```

## Project Structure

```
radio_tui/
├── radio.py              # Main application entry point
├── tui.py               # Curses-based TUI implementation
├── config.py            # Configuration loading (YAML/JSON)
├── utils/               # Core utilities package
│   ├── __init__.py      # Package initialization
│   ├── stream_manager.py # Audio stream management
│   └── now_playing.py   # Track information fetching
├── radio.json           # Default stream configuration
├── requirements.txt     # Python dependencies
├── test_tui.py         # TUI functionality test
├── test_*.py           # Unit tests
└── README.md           # This file
```

## Architecture

The application consists of several components:

- **`tui.py`**: Curses-based terminal user interface with navigation and controls
- **`StreamManager`**: Handles audio playback using ffplay subprocess
- **`NowPlayingFetcher`**: Fetches current track information from various sources
- **`config.py`**: Configuration loading with YAML/JSON support
- **`radio.py`**: Main entry point with CLI argument parsing

### TUI Implementation Details

- **Non-blocking Input**: Uses `curses.nodelay()` for responsive UI
- **Background Updates**: Separate thread updates stream status and now playing info
- **Thread Safety**: Locks protect shared data between UI and update threads
- **Graceful Cleanup**: Signal handlers ensure proper cleanup on exit
- **Responsive Design**: Adapts to terminal size with text truncation

## Development

To run tests:

```bash
python test_stream_manager.py
python test_now_playing.py
python test_tui.py
```

## Recent Improvements

### Enhanced Metadata Display

The application now features significantly improved metadata display with:

- **Smart Fallback Logic**: Gracefully handles missing or incomplete track information
- **Multi-Source Integration**: Combines NTS API data with ICY metadata for comprehensive track info
- **Robust Error Handling**: Continues operation even when metadata sources are unavailable
- **Consistent Display Format**: Shows meaningful information even for unknown tracks

### Improved UI Performance

The terminal interface has been optimized for smoother operation:

- **Differential Screen Updates**: Only redraws changed content to reduce CPU usage
- **Adaptive Refresh Rate**: Throttles updates when no content changes to save resources
- **Per-Row Caching**: Minimizes unnecessary screen redraws for better performance
- **Thread-Safe Operations**: Background updates don't interfere with UI responsiveness

### Enhanced User Experience

- **Toast Notifications**: Non-intrusive error messages and status updates
- **Graceful Degradation**: Application continues working even with network issues
- **Improved Logging**: Better debugging capabilities with structured log output
- **Responsive Layout**: Adapts to terminal size with intelligent text truncation

## Environment Variables

The application supports several environment variables for configuration:

- **DEBUG**: Set to `1` to enable debug logging (writes to `debug.log`)
- **LOG_LEVEL**: Control logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`)
- **UPDATE_INTERVAL**: Override default metadata update interval (default: 15 seconds)

### Example Usage

```bash
# Enable debug logging
DEBUG=1 python radio.py

# Set custom update interval
UPDATE_INTERVAL=30 python radio.py

# Combine multiple settings
DEBUG=1 LOG_LEVEL=DEBUG UPDATE_INTERVAL=10 python radio.py
```

## Dependencies

No new dependencies have been introduced. The application continues to use:

- **Python 3.7+**: Core runtime
- **FFmpeg**: Audio playback (external dependency)
- **requests**: HTTP requests for metadata fetching
- **PyYAML**: Optional YAML configuration support (falls back to JSON)

All dependencies remain the same as previous versions, ensuring easy upgrades.

## Troubleshooting

- **No audio**: Ensure FFmpeg is installed and `ffplay` is in your PATH
- **Import errors**: Install dependencies with `pip install -r requirements.txt`
- **Terminal issues**: Try running in a terminal with color support
- **Network issues**: Check internet connection for now playing information
- **Performance issues**: Enable debug logging to identify bottlenecks
- **Metadata not updating**: Check network connectivity and API availability

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
