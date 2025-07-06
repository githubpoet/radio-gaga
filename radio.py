#!/usr/bin/env python3
"""
Radio Gaga - A Terminal User Interface for Radio Streaming
"""

import sys
import argparse
import os
import logging
from pathlib import Path
from config import load_config, get_streams, get_defaults, get_config_path, ConfigurationError, load_config_from_path
from utils import StreamManager
from tui import main as tui_main

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def main():
    """Main entry point for the radio TUI application."""
    parser = argparse.ArgumentParser(
        description="Radio Gaga - Terminal-based Radio Streaming",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  %(prog)s                    # Start interactive TUI
  %(prog)s --cli             # Show CLI interface with stream info
  %(prog)s --play NTS1       # Play NTS1 stream in batch mode
  %(prog)s --config /path/to/config.yaml --play NTS2
  %(prog)s --config ./my-config.json

Configuration Resolution:
  The application looks for configuration files in the following order:
  1. Explicit --config argument (absolute or relative paths supported)
  2. RADIO_GAGA_CONFIG environment variable
  3. Platform-specific user config directory:
     - Linux: ~/.config/radio-gaga/radio.yaml
     - macOS: ~/Library/Application Support/radio-gaga/radio.yaml
     - Windows: %%APPDATA%%/radio-gaga/radio.yaml
  4. Current directory: ./radio.yaml or ./radio.json
  5. Packaged defaults

Supported Formats:
  Both YAML (.yaml, .yml) and JSON (.json) formats are supported.
  YAML format requires PyYAML to be installed.
        """
    )
    parser.add_argument("--cli", action="store_true", 
                       help="Use command-line interface instead of TUI")
    parser.add_argument("--config", type=str, metavar="PATH",
                       help="Path to configuration file (supports both absolute and relative paths, "
                            "YAML and JSON formats). If not specified, uses RADIO_GAGA_CONFIG "
                            "environment variable or searches standard locations.")
    parser.add_argument("--play", type=str, metavar="STREAM_NAME",
                       help="Play specified stream in batch mode (non-interactive)")
    args = parser.parse_args()
    
    # Load configuration with comprehensive error handling
    try:
        # Check if explicit config file was provided and validate it exists
        if args.config:
            config_path = Path(args.config).expanduser().resolve()
            if not config_path.exists():
                raise FileNotFoundError(f"Configuration file not found: {args.config}")
            if not config_path.is_file():
                raise ConfigurationError(f"Configuration path is not a file: {args.config}")
            
        # Resolve the configuration path using the new get_config_path function
        config_path = get_config_path(args.config)
        logging.info(f"Using configuration file: {config_path}")
        
        # Load the configuration - use direct loading for explicit configs to avoid fallback
        if args.config:
            # For explicit config files, use strict loading without fallback
            config = load_config_from_path(config_path)
        else:
            # For automatic discovery, use the fallback-enabled loader
            config = load_config(args.config)
        
        streams = config.get("streams", [])
        defaults = config.get("defaults", {})
        
        # Validate configuration structure
        if not isinstance(streams, list):
            raise ConfigurationError("Configuration 'streams' must be a list")
        if not isinstance(defaults, dict):
            raise ConfigurationError("Configuration 'defaults' must be a dictionary")
            
    except ConfigurationError as e:
        print(f"Configuration Error: {e}", file=sys.stderr)
        if hasattr(e, 'search_paths') and e.search_paths:
            print("\nSearched the following locations:", file=sys.stderr)
            for path in e.search_paths:
                print(f"  - {path}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"Configuration file not found: {e}", file=sys.stderr)
        if args.config:
            print(f"Specified config file does not exist: {args.config}", file=sys.stderr)
        else:
            print("No configuration file found in standard locations.", file=sys.stderr)
            print("Set RADIO_GAGA_CONFIG environment variable or use --config option.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        error_msg = str(e)
        if "yaml" in error_msg.lower():
            print(f"Invalid YAML format in configuration file: {error_msg}", file=sys.stderr)
            print("Please check your YAML syntax and try again.", file=sys.stderr)
        elif "json" in error_msg.lower():
            print(f"Invalid JSON format in configuration file: {error_msg}", file=sys.stderr)
            print("Please check your JSON syntax and try again.", file=sys.stderr)
        else:
            print(f"Error loading configuration: {error_msg}", file=sys.stderr)
        sys.exit(1)
    
    # Handle batch play mode
    if args.play:
        # Find the stream by name
        target_stream = None
        stream_id = None
        
        for i, stream in enumerate(streams):
            if stream['name'].lower() == args.play.lower():
                target_stream = stream
                stream_id = i
                break
        
        if target_stream is None:
            print(f"Error: Stream '{args.play}' not found.", file=sys.stderr)
            if streams:
                print("Available streams:", file=sys.stderr)
                for stream in streams:
                    print(f"  - {stream['name']}", file=sys.stderr)
            else:
                print("No streams are configured.", file=sys.stderr)
            sys.exit(1)
        
        print(f"Playing {target_stream['name']} ({target_stream['url']})...")
        
        # Initialize StreamManager and play the stream
        stream_manager = StreamManager(streams)
        try:
            stream_manager.play(stream_id)
            print(f"Started playing {target_stream['name']}")
            print("Press Ctrl+C to stop...")
            
            # Keep the program running until interrupted
            import time
            while True:
                try:
                    time.sleep(1)
                except KeyboardInterrupt:
                    print("\nStopping playback...")
                    stream_manager.stop()
                    break
        except Exception as e:
            print(f"Error playing stream: {e}", file=sys.stderr)
            logging.error(f"Stream playback failed: {e}")
            sys.exit(1)
    
    elif args.cli:
        # Command-line interface for testing/debugging
        print("Radio Gaga - Terminal-based Radio Streaming")
        print("="*40)
        
        print(f"\nAvailable streams ({len(streams)}):")
        for i, stream in enumerate(streams):
            print(f"  {i}. {stream['name']} - {stream['url']}")
        
        print(f"\nDefault settings:")
        print(f"  Volume: {defaults.get('volume', 'N/A')}")
        print(f"  Start paused: {defaults.get('start_paused', 'N/A')}")
        
        # Initialize StreamManager
        stream_manager = StreamManager(streams)
        
        print("\n[StreamManager initialized and ready for use]")
        print("\nStreamManager methods available:")
        print("  - play(id): Start playing stream by ID")
        print("  - stop(): Stop current stream")
        print("  - switch(id): Switch to different stream")
        print("  - status(): Get current playback status")
        
        print("\n[Use 'python radio.py' without --cli flag to start Radio Gaga TUI]")
    else:
        # Start the TUI
        try:
            tui_main()
        except KeyboardInterrupt:
            print("\nGracefully shutting down...")
        except Exception as e:
            print(f"Error starting TUI: {e}", file=sys.stderr)
            logging.error(f"TUI startup failed: {e}")
            # Try to restore terminal state
            try:
                import curses
                curses.endwin()
            except:
                pass
            sys.exit(1)

if __name__ == "__main__":
    main()
