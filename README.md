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
