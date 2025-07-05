# StreamManager Implementation

## Overview
The `StreamManager` class provides a robust interface for managing audio stream playback using `ffplay` from the FFmpeg suite. It ensures only one stream process runs at a time and handles graceful termination.

## Features

### Core Methods
- `play(id)`: Start playing a stream by ID
- `stop()`: Stop the currently playing stream
- `switch(id)`: Switch to a different stream (stops current, starts new)
- `status()`: Get current playback status information

### Key Implementation Details

#### FFplay Integration
- Uses `subprocess.Popen` to launch `ffplay` with the following options:
  - `-nodisp`: No video display
  - `-autoexit`: Exit when playback ends
  - `-loglevel quiet`: Suppress verbose output
  - Redirects stdout/stderr to DEVNULL for clean operation

#### Process Management
- Creates new process groups on Unix systems for better process control
- Implements graceful termination with SIGTERM followed by SIGKILL if needed
- 5-second timeout for graceful shutdown
- Automatic cleanup on object destruction

#### Error Handling
- Validates stream IDs before attempting playback
- Handles missing FFmpeg installation gracefully
- Provides informative error messages
- Cleans up state even when errors occur

#### Cross-Platform Support
- Works on both Unix-like systems (Linux, macOS) and Windows
- Uses appropriate termination methods for each platform
- Process group management for Unix systems

## Usage Example

```python
from config import get_streams
from utils import StreamManager

# Initialize with streams from configuration
streams = get_streams()
manager = StreamManager(streams)

# Start playing first stream
manager.play(0)

# Check status
status = manager.status()
print(f"Playing: {status['is_playing']}")
print(f"Current stream: {status['current_stream_name']}")

# Switch to another stream
manager.switch(1)

# Stop playback
manager.stop()
```

## Status Information
The `status()` method returns a dictionary with:
- `is_playing`: Boolean indicating if audio is currently playing
- `current_stream_id`: ID of the current stream (or None)
- `current_stream_name`: Name of the current stream (or None)
- `current_stream_url`: URL of the current stream (or None)
- `process_alive`: Boolean indicating if the ffplay process is alive
- `available_streams`: Total number of available streams

## Requirements
- FFmpeg with `ffplay` command available in PATH
- Python 3.6+ (uses subprocess and typing features)

## Testing
Run the test script to verify functionality:
```bash
python3 test_stream_manager.py
```

This will demonstrate all methods and show the StreamManager working with actual streams from the configuration.
