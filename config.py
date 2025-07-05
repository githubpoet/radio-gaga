#!/usr/bin/env python3
"""
Configuration module for Radio TUI
Loads configuration from radio.yaml with fallback to radio.json if PyYAML is unavailable.
"""

import json
import os
from pathlib import Path
import shutil
from typing import Dict, Any, Optional

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

# Cache for loaded configuration
_config_cache = None

# Default configuration
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

class ConfigError(Exception):
    """Custom exception for configuration errors."""
    pass


def save_default_config(path: Path) -> None:
    """
    Save the default configuration to a JSON file.
    
    Args:
        path (Path): The path to the config file to save
    """
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
            print(f"Default configuration saved to {path}")
    except Exception as e:
        print(f"Failed to save default configuration: {e}")


def load_config():
    """
    Load configuration from radio.yaml or radio.json as fallback.
    
    Returns:
        dict: Configuration dictionary containing streams and defaults
    """
    global _config_cache
    
    # Return cached configuration if available
    if _config_cache is not None:
        return _config_cache
    
    config_dir = Path(__file__).parent
    yaml_path = config_dir / "radio.yaml"
    json_path = config_dir / "radio.json"
    
    # Try to load YAML first if PyYAML is available
    if YAML_AVAILABLE and yaml_path.exists():
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                print(f"Loaded configuration from {yaml_path}")
                _config_cache = config
                return config
        except Exception as e:
            print(f"Error loading YAML config: {e}")
            print("Falling back to JSON configuration...")
    
    # Fallback to JSON configuration
    if json_path.exists():
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                if not YAML_AVAILABLE:
                    print(f"PyYAML not available, loaded configuration from {json_path}")
                else:
                    print(f"Loaded configuration from {json_path}")
                _config_cache = config
                return config
        except Exception as e:
            print(f"Error loading JSON config: {e}")
            raise
    
# If no config files exist, generate default configuration
    print("No configuration files found, generating defaults")
    config = DEFAULT_CONFIG
    _config_cache = config
    save_default_config(json_path)  # Save default config
    return config


def get_streams():
    """
    Get list of available streams from configuration.
    
    Returns:
        list: List of stream dictionaries
    """
    config = load_config()
    return config.get("streams", [])


def get_defaults():
    """
    Get default settings from configuration.
    
    Returns:
        dict: Default settings dictionary
    """
    config = load_config()
    return config.get("defaults", {})


if __name__ == "__main__":
    # Test the configuration loading
    print("Testing configuration loading...")
    config = load_config()
    print(f"Streams: {config.get('streams', [])}")
    print(f"Defaults: {config.get('defaults', {})}")
