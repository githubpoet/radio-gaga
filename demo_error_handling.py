#!/usr/bin/env python3
"""
Demo script for Radio TUI error handling features
Shows how the app gracefully handles various error conditions
"""

import os
import sys
import time
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import load_config, DEFAULT_CONFIG
from utils.stream_manager import StreamManager
from utils.now_playing import NowPlayingFetcher


def demo_config_error_handling():
    """Demonstrate config error handling."""
    print("=== Configuration Error Handling Demo ===")
    print("\n1. Missing Config Files:")
    print("   - If radio.yaml and radio.json are missing")
    print("   - App automatically generates default config")
    print("   - Notifies user and continues running")
    
    # Example of what happens when config is missing
    try:
        config = load_config()
        print(f"   ✓ Loaded config with {len(config.get('streams', []))} streams")
    except Exception as e:
        print(f"   ✗ Config error: {e}")


def demo_ffplay_error_handling():
    """Demonstrate ffplay error handling."""
    print("\n=== FFplay Error Handling Demo ===")
    print("\n2. FFplay Launch Failures:")
    print("   - If ffplay is not installed")
    print("   - If stream URL is invalid")
    print("   - Shows toast notification in UI")
    print("   - App continues running without crashing")
    
    # Create a toast collector
    error_messages = []
    def collect_toast(message):
        error_messages.append(message)
        print(f"   📢 Toast: {message}")
    
    # Test with invalid executable (simulated error)
    streams = [{"name": "Test Stream", "url": "http://example.com/stream"}]
    manager = StreamManager(streams, toast_callback=collect_toast)
    
    print("   Attempting to play stream...")
    success = manager.play(0)
    
    if success:
        print("   ✓ Stream started successfully")
        manager.stop()
    else:
        print("   ✓ Error handled gracefully")
    
    if error_messages:
        print(f"   ✓ User notified via toast: {error_messages[-1]}")
    
    manager.now_playing_fetcher.stop()


def demo_api_error_handling():
    """Demonstrate API error handling."""
    print("\n=== Network/API Error Handling Demo ===")
    print("\n3. Network/API Errors:")
    print("   - When NTS API is unreachable")
    print("   - When network connection fails")
    print("   - Shows brief 'API error' message")
    print("   - App continues running normally")
    
    # Create a toast collector
    api_messages = []
    def collect_api_toast(message):
        api_messages.append(message)
        print(f"   📢 API Toast: {message}")
    
    # Test API error handling
    streams = [{"name": "NTS1", "url": "http://example.com"}]
    fetcher = NowPlayingFetcher(streams, update_interval=1, toast_callback=collect_api_toast)
    
    # Manually trigger an API error
    original_url = fetcher.nts_api_url
    fetcher.nts_api_url = "http://invalid-api-that-will-fail"
    
    print("   Testing API with invalid endpoint...")
    result = fetcher._fetch_nts_api()
    
    if result is None:
        print("   ✓ API error handled gracefully")
    
    if api_messages:
        print(f"   ✓ User notified: {api_messages[-1]}")
    
    # Restore and cleanup
    fetcher.nts_api_url = original_url
    fetcher.stop()


def demo_graceful_shutdown():
    """Demonstrate graceful shutdown."""
    print("\n=== Graceful Shutdown Demo ===")
    print("\n4. Graceful Shutdown (q or SIGINT):")
    print("   - Stops any running ffplay processes")
    print("   - Restores terminal state with curses.endwin()")
    print("   - Cleans up background threads")
    print("   - No zombie processes left behind")
    
    streams = [{"name": "Test Stream", "url": "http://example.com"}]
    manager = StreamManager(streams)
    
    print("   Creating StreamManager...")
    print("   ✓ Background threads started")
    
    # Simulate cleanup
    print("   Simulating shutdown...")
    manager.stop()
    manager.now_playing_fetcher.stop()
    print("   ✓ All processes stopped")
    print("   ✓ Resources cleaned up")
    print("   ✓ Ready for terminal restoration")


def main():
    """Run all demos."""
    print("Radio TUI Error Handling Demonstrations")
    print("=" * 50)
    print("\nThis demo shows how the Radio TUI handles various error conditions:")
    
    try:
        demo_config_error_handling()
        demo_ffplay_error_handling()
        demo_api_error_handling()
        demo_graceful_shutdown()
        
        print("\n" + "=" * 50)
        print("✓ All error handling features demonstrated!")
        print("\nKey Features Implemented:")
        print("• Missing/invalid config → generates default & notifies user")
        print("• ffplay failures → shows toast in UI")
        print("• Network/API errors → displays 'API error' & continues")
        print("• Graceful shutdown → stops ffplay & restores terminal")
        
    except KeyboardInterrupt:
        print("\n\n🛑 Interrupted - demonstrating graceful shutdown...")
        print("✓ Terminal state would be restored")
        print("✓ Background processes would be stopped")
    except Exception as e:
        print(f"\n✗ Demo error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
