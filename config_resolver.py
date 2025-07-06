#!/usr/bin/env python3
"""
Configuration Resolution Helper API for Radio Gaga

This module provides a comprehensive configuration resolution system that:
1. Accepts explicit absolute/relative paths from CLI flags
2. Consults the RADIO_GAGA_CONFIG environment variable
3. Probes XDG-compliant directories on Linux and macOS Application Support
4. Falls back to packaged defaults
5. Creates user configuration templates on first run

Key Features:
- No directory-changing side effects
- Rich error messages with context
- Cross-platform path resolution
- Lazy loading with smart caching
- Comprehensive error handling
"""

import os
import sys
import platform
from pathlib import Path
from typing import Dict, Any, Optional, Union
import json
import shutil

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

# Default configuration structure
DEFAULT_CONFIG = {
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
        "start_paused": True
    }
}

# Configuration file template with comments
CONFIG_TEMPLATE = """# Radio Gaga Configuration File
# This file contains stream definitions and default settings

# Available radio streams
streams:
  - name: NTS1
    url: https://stream-relay-geo.ntslive.net/stream
  - name: NTS2
    url: https://stream-relay-geo.ntslive.net/stream2
  # Add more streams here:
  # - name: Your Stream
  #   url: https://your-stream-url.com/stream

# Default application settings
defaults:
  volume: 1.0          # Default volume (0.0 to 1.0)
  start_paused: true   # Whether to start in paused state
"""

class ConfigurationError(Exception):
    """
    Rich exception for configuration-related errors.
    
    Provides detailed context about configuration resolution failures,
    including search paths attempted and specific error reasons.
    """
    def __init__(self, message: str, search_paths: Optional[list] = None, 
                 original_error: Optional[Exception] = None):
        super().__init__(message)
        self.search_paths = search_paths or []
        self.original_error = original_error
        
    def __str__(self):
        msg = super().__str__()
        if self.search_paths:
            msg += f"\n\nSearched paths:\n"
            for path in self.search_paths:
                msg += f"  - {path}\n"
        if self.original_error:
            msg += f"\nOriginal error: {self.original_error}"
        return msg


def _get_platform_config_dir() -> Path:
    """
    Get the platform-specific configuration directory.
    
    Returns:
        Path: Platform-appropriate config directory
        
    Platform-specific paths:
    - macOS: ~/Library/Application Support/radio-gaga/
    - Linux: ~/.config/radio-gaga/ (XDG_CONFIG_HOME)
    - Windows: %APPDATA%/radio-gaga/
    """
    system = platform.system()
    home = Path.home()
    
    if system == "Darwin":  # macOS
        return home / "Library" / "Application Support" / "radio-gaga"
    elif system == "Linux":
        # Use XDG_CONFIG_HOME if set, otherwise ~/.config
        xdg_config = os.environ.get("XDG_CONFIG_HOME")
        if xdg_config:
            return Path(xdg_config) / "radio-gaga"
        else:
            return home / ".config" / "radio-gaga"
    elif system == "Windows":
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / "radio-gaga"
        else:
            return home / "AppData" / "Roaming" / "radio-gaga"
    else:
        # Fallback for other systems
        return home / ".config" / "radio-gaga"


def _get_packaged_config_path() -> Path:
    """
    Get the path to the packaged default configuration file.
    
    Returns:
        Path: Path to packaged radio.yaml in the application directory
    """
    app_dir = Path(__file__).parent
    return app_dir / "radio.yaml"


def get_config_path(cli_arg: Optional[str] = None) -> Path:
    """
    Resolve configuration file path following the specified search order.
    
    Search order:
    1. CLI argument (explicit path)
    2. RADIO_GAGA_CONFIG environment variable
    3. Platform-specific user config directory
    4. Legacy locations (./radio.yaml, ./radio.json)
    5. Packaged defaults
    
    Args:
        cli_arg: Optional explicit path from CLI argument
        
    Returns:
        Path: Resolved configuration file path
        
    Raises:
        ConfigurationError: If no valid configuration file is found
    """
    search_paths = []
    
    # 1. CLI argument (highest priority)
    if cli_arg:
        cli_path = Path(cli_arg).expanduser().resolve()
        search_paths.append(str(cli_path))
        if cli_path.exists():
            return cli_path
    
    # 2. Environment variable
    env_config = os.environ.get("RADIO_GAGA_CONFIG")
    if env_config:
        env_path = Path(env_config).expanduser().resolve()
        search_paths.append(str(env_path))
        if env_path.exists():
            return env_path
    
    # 3. Platform-specific user directories
    platform_dir = _get_platform_config_dir()
    platform_yaml = platform_dir / "radio.yaml"
    platform_json = platform_dir / "radio.json"
    
    search_paths.extend([str(platform_yaml), str(platform_json)])
    if platform_yaml.exists():
        return platform_yaml
    if platform_json.exists():
        return platform_json
    
    # 4. Legacy locations (current working directory)
    cwd = Path.cwd()
    legacy_yaml = cwd / "radio.yaml"
    legacy_json = cwd / "radio.json"
    
    search_paths.extend([str(legacy_yaml), str(legacy_json)])
    if legacy_yaml.exists():
        return legacy_yaml
    if legacy_json.exists():
        return legacy_json
    
    # 5. Packaged defaults
    packaged_config = _get_packaged_config_path()
    search_paths.append(str(packaged_config))
    if packaged_config.exists():
        return packaged_config
    
    # If we reach here, no configuration file was found
    raise ConfigurationError(
        "No configuration file found in any search location",
        search_paths=search_paths
    )


def load_config(path: Path) -> Dict[str, Any]:
    """
    Load configuration from the specified path.
    
    Supports both YAML and JSON formats, with automatic format detection
    based on file extension.
    
    Args:
        path: Path to configuration file
        
    Returns:
        dict: Parsed configuration data
        
    Raises:
        ConfigurationError: If file cannot be read or parsed
    """
    if not path.exists():
        raise ConfigurationError(f"Configuration file does not exist: {path}")
    
    if not path.is_file():
        raise ConfigurationError(f"Configuration path is not a file: {path}")
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Detect format by extension
        if path.suffix.lower() in ['.yaml', '.yml']:
            if not YAML_AVAILABLE:
                raise ConfigurationError(
                    f"YAML configuration file found but PyYAML is not installed: {path}"
                )
            try:
                config = yaml.safe_load(content)
            except yaml.YAMLError as e:
                raise ConfigurationError(
                    f"Invalid YAML in configuration file: {path}",
                    original_error=e
                )
        elif path.suffix.lower() == '.json':
            try:
                config = json.loads(content)
            except json.JSONDecodeError as e:
                raise ConfigurationError(
                    f"Invalid JSON in configuration file: {path}",
                    original_error=e
                )
        else:
            # Try to auto-detect format
            try:
                config = json.loads(content)
            except json.JSONDecodeError:
                if YAML_AVAILABLE:
                    try:
                        config = yaml.safe_load(content)
                    except yaml.YAMLError as e:
                        raise ConfigurationError(
                            f"Could not parse configuration file as JSON or YAML: {path}",
                            original_error=e
                        )
                else:
                    raise ConfigurationError(
                        f"Configuration file is not valid JSON and PyYAML is not available: {path}"
                    )
        
        # Validate basic structure
        if not isinstance(config, dict):
            raise ConfigurationError(
                f"Configuration file must contain a dictionary/object: {path}"
            )
        
        return config
        
    except IOError as e:
        raise ConfigurationError(
            f"Could not read configuration file: {path}",
            original_error=e
        )


def ensure_user_default() -> Path:
    """
    Ensure a user configuration file exists in the platform-appropriate location.
    
    Creates a commented configuration template if no user config exists.
    Does not overwrite existing configuration files.
    
    Returns:
        Path: Path to the user configuration file (created or existing)
        
    Raises:
        ConfigurationError: If user config directory cannot be created
    """
    platform_dir = _get_platform_config_dir()
    config_path = platform_dir / "radio.yaml"
    
    # If config already exists, return its path
    if config_path.exists():
        return config_path
    
    # Create directory if it doesn't exist
    try:
        platform_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise ConfigurationError(
            f"Could not create configuration directory: {platform_dir}",
            original_error=e
        )
    
    # Create the configuration file with template
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(CONFIG_TEMPLATE)
        
        return config_path
        
    except IOError as e:
        raise ConfigurationError(
            f"Could not create configuration file: {config_path}",
            original_error=e
        )


def resolve_and_load_config(cli_arg: Optional[str] = None) -> tuple[Path, Dict[str, Any]]:
    """
    High-level function to resolve and load configuration.
    
    This is the main entry point that combines path resolution and config loading.
    On first run, it ensures a user default configuration exists.
    
    Args:
        cli_arg: Optional explicit path from CLI argument
        
    Returns:
        tuple: (resolved_path, config_dict)
        
    Raises:
        ConfigurationError: If configuration cannot be resolved or loaded
    """
    # First, try to ensure user default exists (but don't fail if it can't be created)
    try:
        user_config_path = ensure_user_default()
    except ConfigurationError:
        # If we can't create user config, that's okay - we'll try other paths
        user_config_path = None
    
    # Resolve the configuration path
    try:
        config_path = get_config_path(cli_arg)
    except ConfigurationError as e:
        # If no config found anywhere, and we couldn't create user default, 
        # fall back to DEFAULT_CONFIG
        if user_config_path is None:
            return Path("<default>"), DEFAULT_CONFIG
        else:
            raise
    
    # Load the configuration
    try:
        config = load_config(config_path)
        return config_path, config
    except ConfigurationError as e:
        # If the resolved config can't be loaded, try fallback to defaults
        if config_path == _get_packaged_config_path():
            # If even the packaged config fails, use hard-coded defaults
            return Path("<default>"), DEFAULT_CONFIG
        else:
            raise


def get_config_info(cli_arg: Optional[str] = None) -> Dict[str, Any]:
    """
    Get detailed information about configuration resolution.
    
    Useful for debugging and --config-info CLI commands.
    
    Args:
        cli_arg: Optional explicit path from CLI argument
        
    Returns:
        dict: Configuration resolution information
    """
    info = {
        "platform": platform.system(),
        "platform_config_dir": str(_get_platform_config_dir()),
        "packaged_config_path": str(_get_packaged_config_path()),
        "environment_variable": os.environ.get("RADIO_GAGA_CONFIG"),
        "cli_argument": cli_arg,
        "search_paths": [],
        "resolved_path": None,
        "config_exists": False,
        "user_config_exists": False,
        "error": None
    }
    
    # Build search paths
    search_paths = []
    
    if cli_arg:
        search_paths.append(str(Path(cli_arg).expanduser().resolve()))
    
    env_config = os.environ.get("RADIO_GAGA_CONFIG")
    if env_config:
        search_paths.append(str(Path(env_config).expanduser().resolve()))
    
    platform_dir = _get_platform_config_dir()
    search_paths.extend([
        str(platform_dir / "radio.yaml"),
        str(platform_dir / "radio.json")
    ])
    
    cwd = Path.cwd()
    search_paths.extend([
        str(cwd / "radio.yaml"),
        str(cwd / "radio.json")
    ])
    
    search_paths.append(str(_get_packaged_config_path()))
    
    info["search_paths"] = search_paths
    
    # Check if user config exists
    user_yaml = platform_dir / "radio.yaml"
    user_json = platform_dir / "radio.json"
    info["user_config_exists"] = user_yaml.exists() or user_json.exists()
    
    # Try to resolve path
    try:
        resolved_path = get_config_path(cli_arg)
        info["resolved_path"] = str(resolved_path)
        info["config_exists"] = resolved_path.exists()
    except ConfigurationError as e:
        info["error"] = str(e)
    
    return info


# For backward compatibility, provide a simple load_config function
def load_configuration(cli_arg: Optional[str] = None) -> Dict[str, Any]:
    """
    Backward-compatible configuration loading function.
    
    Args:
        cli_arg: Optional explicit path from CLI argument
        
    Returns:
        dict: Loaded configuration
    """
    _, config = resolve_and_load_config(cli_arg)
    return config


if __name__ == "__main__":
    # Test the configuration resolution
    import argparse
    
    parser = argparse.ArgumentParser(description="Test configuration resolution")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--info", action="store_true", help="Show config info")
    args = parser.parse_args()
    
    if args.info:
        info = get_config_info(args.config)
        print("Configuration Resolution Info:")
        print(f"Platform: {info['platform']}")
        print(f"Platform config dir: {info['platform_config_dir']}")
        print(f"Environment variable: {info['environment_variable']}")
        print(f"CLI argument: {info['cli_argument']}")
        print(f"User config exists: {info['user_config_exists']}")
        print(f"Resolved path: {info['resolved_path']}")
        print(f"Config exists: {info['config_exists']}")
        if info['error']:
            print(f"Error: {info['error']}")
        print("\nSearch paths:")
        for path in info['search_paths']:
            exists = Path(path).exists()
            print(f"  {'✓' if exists else '✗'} {path}")
    else:
        try:
            path, config = resolve_and_load_config(args.config)
            print(f"Loaded configuration from: {path}")
            print(f"Streams: {len(config.get('streams', []))}")
            print(f"Defaults: {config.get('defaults', {})}")
        except ConfigurationError as e:
            print(f"Configuration error: {e}")
            sys.exit(1)
