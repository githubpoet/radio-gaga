# Changelog

All notable changes to Radio TUI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Enhanced metadata display with smart fallback logic for missing track information
- Multi-source integration combining NTS API data with ICY metadata
- Differential screen updates for improved UI performance
- Adaptive refresh rate that throttles updates when no content changes
- Per-row caching to minimize unnecessary screen redraws
- Toast notification system for non-intrusive error messages and status updates
- Environment variable support for configuration:
  - `DEBUG`: Enable debug logging (writes to `debug.log`)
  - `LOG_LEVEL`: Control logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`)
  - `UPDATE_INTERVAL`: Override default metadata update interval (default: 15 seconds)
- Improved logging with structured output and debugging capabilities
- Responsive layout that adapts to terminal size with intelligent text truncation

### Improved
- **UI Performance**: Significantly reduced CPU usage through optimized screen updates
- **Metadata Display**: More robust handling of missing or incomplete track information
- **Error Handling**: Application continues operation even when metadata sources are unavailable
- **User Experience**: Smoother interface with better visual feedback
- **Resource Management**: Thread-safe operations prevent UI interference
- **Graceful Degradation**: Application remains functional during network issues

### Fixed
- Track information no longer shows "Unknown" when partial metadata is available
- Screen updates now only occur when content actually changes
- Background metadata fetching doesn't block UI responsiveness
- Proper cleanup of resources and processes on application exit

### Technical Details
- No new dependencies introduced - maintains compatibility with existing installations
- Backward compatible with existing configuration files
- Enhanced thread safety for concurrent operations
- Improved error recovery and fallback mechanisms

## [Initial Release]

### Added
- Curses-based terminal user interface
- Stream management with play/stop/switch functionality
- Real-time track information from NTS API and ICY metadata
- Keyboard navigation with arrow keys and number shortcuts
- Live UI updates at ~5Hz refresh rate
- Configuration support for YAML and JSON files
- FFmpeg integration for audio playback
- Multi-stream support with visual indicators
- Color-coded interface with status indicators
