#!/usr/bin/env python3
"""
Radio TUI - A Terminal User Interface for Radio Streaming
"""

import sys
import argparse
import os
from pathlib import Path
from config import load_config, get_streams, get_defaults
from utils import StreamManager
from tui import main as tui_main

def main():
    """Main entry point for the radio TUI application."""
    parser = argparse.ArgumentParser(
        description="Radio TUI - Terminal-based Radio Streaming",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  %(prog)s                    # Start interactive TUI
  %(prog)s --cli             # Show CLI interface with stream info
  %(prog)s --play NTS1       # Play NTS1 stream in batch mode
  %(prog)s --config /path/to/config.json --play NTS2
        """
    )
    parser.add_argument("--cli", action="store_true", 
                       help="Use command-line interface instead of TUI")
    parser.add_argument("--config", type=str, metavar="PATH",
                       help="Path to configuration file (radio.json or radio.yaml)")
    parser.add_argument("--play", type=str, metavar="STREAM_NAME",
                       help="Play specified stream in batch mode (non-interactive)")
    args = parser.parse_args()
    
    # Handle custom config path
    if args.config:
        config_path = Path(args.config)
        if not config_path.exists():
            print(f"Error: Configuration file '{args.config}' not found.", file=sys.stderr)
            sys.exit(1)
        
        # Set environment variable or modify config loading to use custom path
        # For now, we'll temporarily change to the config directory
        original_dir = os.getcwd()
        try:
            os.chdir(config_path.parent)
            # Clear config cache to force reload
            import config
            config._config_cache = None
        except Exception as e:
            print(f"Error setting up custom config path: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Load configuration with error handling
    try:
        config = load_config()
        streams = get_streams()
        defaults = get_defaults()
    except Exception as e:
        print(f"Error loading configuration: {e}")
        print("Using default configuration...")
        streams = []
        defaults = {}
    
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
            print("Available streams:")
            for stream in streams:
                print(f"  - {stream['name']}")
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
            sys.exit(1)
    
    elif args.cli:
        # Command-line interface for testing/debugging
        print("Radio TUI - Terminal-based Radio Streaming")
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
        
        print("\n[Use 'python radio.py' without --cli flag to start the TUI]")
    else:
        # Start the TUI
        try:
            tui_main()
        except KeyboardInterrupt:
            print("\nGracefully shutting down...")
        except Exception as e:
            print(f"Error starting TUI: {e}", file=sys.stderr)
            # Try to restore terminal state
            try:
                import curses
                curses.endwin()
            except:
                pass
            sys.exit(1)
    
    # Restore original directory if custom config was used
    if args.config:
        try:
            os.chdir(original_dir)
        except:
            pass

if __name__ == "__main__":
    main()
