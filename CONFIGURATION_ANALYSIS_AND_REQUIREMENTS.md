# Configuration Analysis and Requirements

## Current Implementation Analysis

### Current Configuration System (`config.py`)

#### Current Search Path and Behavior
1. **Hard-coded directory-based search**: Configuration files are searched relative to the script's directory (`Path(__file__).parent`)
2. **Search order**:
   - `radio.yaml` (if PyYAML is available)
   - `radio.json` (fallback)
   - DEFAULT_CONFIG (hard-coded fallback)

#### Current Command-line Interface (`radio.py`)
- **`--config PATH`**: Accepts a path to a configuration file
- **Implicit working-directory hack**: When `--config` is used, the script performs `os.chdir(config_path.parent)` and clears the config cache to force reload
- **Current CLI arguments**:
  - `--cli`: Command-line interface instead of TUI
  - `--config PATH`: Path to configuration file
  - `--play STREAM_NAME`: Play specified stream in batch mode

#### Current Configuration Files
- **`radio.yaml`**: YAML format configuration (preferred if PyYAML available)
- **`radio.json`**: JSON format configuration (fallback)
- **Both contain**:
  - `streams`: Array of stream objects with `name` and `url`
  - `defaults`: Object with `volume` and `start_paused` settings

#### Current Testing Coverage
- **Unit tests**: None identified (no pytest test files found)
- **Integration tests**: None identified
- **Manual tests**: `quick_manual_test.py` exists but focuses on TUI functionality, not configuration
- **Current test gaps**: No tests for configuration loading, search paths, or CLI behavior

### Current Issues and Limitations

1. **Inflexible search paths**: Only looks in script directory
2. **Fragile directory manipulation**: Uses `os.chdir()` hack for custom config paths
3. **No environment variable support**: No `RADIO_GAGA_CONFIG` environment variable
4. **No XDG/platform-specific directories**: Doesn't follow platform conventions
5. **No user config auto-creation**: Only creates defaults in script directory
6. **Limited error handling**: Basic error handling for missing files
7. **Cache invalidation issues**: Manual cache clearing required for config changes

## Desired Configuration System Requirements

### Search Order Specification

The new configuration system should search for configuration files in the following order:

1. **CLI flag**: `--config PATH` (highest priority)
2. **Environment variable**: `RADIO_GAGA_CONFIG` (if set)
3. **Platform-specific user directories**:
   - **macOS**: `~/Library/Application Support/radio-gaga/config.yaml`
   - **Linux**: `~/.config/radio-gaga/config.yaml` (XDG_CONFIG_HOME)
   - **Windows**: `%APPDATA%\radio-gaga\config.yaml`
4. **Legacy location**: `./radio.yaml` (current working directory)
5. **Legacy location**: `./radio.json` (current working directory)
6. **Packaged defaults**: Fall back to DEFAULT_CONFIG

### UX Requirements

#### Command-line Interface
- **Maintain backward compatibility**: Keep existing `--config PATH` behavior
- **Add environment variable support**: `RADIO_GAGA_CONFIG=/path/to/config.yaml radio.py`
- **Remove directory hack**: Eliminate `os.chdir()` manipulation
- **Better error reporting**: Clear messages about config search paths and failures

#### Configuration File Management
- **Auto-creation**: Create user configuration file in platform-appropriate location on first run
- **Migration support**: Detect and offer to migrate existing `./radio.yaml` or `./radio.json` files
- **Format preference**: Default to YAML format for new files, maintain JSON support for compatibility

#### User Experience
- **Help command**: `radio.py --help` should document configuration search order
- **Config location command**: `radio.py --config-info` to show current config file being used
- **Validation**: Better validation of configuration file format and contents

### Technical Implementation Requirements

#### Configuration Loading
- **Immutable search path**: Define search paths at module level, don't modify during runtime
- **Lazy loading**: Load configuration only when needed
- **Cache management**: Smart cache invalidation when files change
- **Error resilience**: Graceful handling of malformed config files

#### Platform Support
- **Cross-platform paths**: Use `pathlib` and appropriate platform conventions
- **Environment variable expansion**: Support `~` and environment variables in paths
- **Permission handling**: Graceful handling of permission errors

#### Testing Requirements
- **Unit tests**: Test configuration loading, search paths, and error conditions
- **Integration tests**: Test CLI argument parsing and config file interactions
- **Mock testing**: Mock file system for testing different scenarios
- **Platform testing**: Test platform-specific directory resolution

### Acceptance Criteria

#### Functional Requirements
1. **Search order**: Configuration files are found in the specified search order
2. **CLI compatibility**: `--config PATH` works exactly as before
3. **Environment variable**: `RADIO_GAGA_CONFIG` overrides default search behavior
4. **Platform directories**: Uses correct platform-specific config directories
5. **Auto-creation**: Creates user config file in appropriate location
6. **Legacy support**: Finds and uses existing `./radio.yaml` and `./radio.json` files
7. **Error handling**: Provides clear error messages for configuration issues

#### Non-functional Requirements
1. **Performance**: Configuration loading should be fast (under 100ms)
2. **Reliability**: No `os.chdir()` manipulation or directory side effects
3. **Maintainability**: Clear, testable code with comprehensive test coverage
4. **Usability**: Clear documentation and help text for users

#### Testing Requirements
1. **Unit test coverage**: 90%+ coverage of configuration module
2. **Integration tests**: CLI argument parsing and file system interactions
3. **Cross-platform tests**: Test on macOS, Linux, and Windows (or simulated)
4. **Edge case tests**: Permission errors, malformed files, missing directories

### Migration Strategy

#### Backward Compatibility
- **Existing behavior**: `--config PATH` continues to work exactly as before
- **Existing files**: `./radio.yaml` and `./radio.json` are still found and used
- **Configuration format**: No changes to configuration file structure

#### Migration Path
1. **Detection**: Detect existing `./radio.yaml` or `./radio.json` files
2. **Notification**: Inform user about new configuration location
3. **Migration**: Offer to copy existing config to new location
4. **Cleanup**: Optionally remove old config files after migration

### Implementation Notes

#### Code Structure
- **config.py**: Refactor to implement new search order and eliminate directory hacks
- **radio.py**: Update CLI argument handling, remove `os.chdir()` calls
- **tests/**: New test directory with comprehensive test coverage
- **utils/**: Update any utilities that depend on configuration

#### Dependencies
- **Existing dependencies**: Maintain existing `requests` and `PyYAML` dependencies
- **New dependencies**: May need `platformdirs` for cross-platform directory resolution
- **Testing dependencies**: Add `pytest` and `pytest-mock` for testing

#### Configuration File Format
- **YAML preferred**: New files created in YAML format
- **JSON supported**: Maintain JSON support for backward compatibility
- **Validation**: Add schema validation for configuration files
- **Documentation**: Include example configuration files and documentation

This specification will serve as the foundation for the configuration system refactor, ensuring all requirements are met while maintaining backward compatibility and improving user experience.
