#!/usr/bin/env python3
"""
Simple verification script to test that NowPlayingFetcher always provides meaningful strings.
"""

import json
import time
from utils.now_playing import NowPlayingFetcher

def verify_meaningful_strings():
    """Verify that track_info always has meaningful information."""
    
    # Load configuration
    try:
        with open('radio.json', 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return
    
    streams = config.get('streams', [])
    
    # Test _get_unknown_track
    fetcher = NowPlayingFetcher(streams, update_interval=60)
    unknown_track = fetcher._get_unknown_track()
    
    print("=== Testing _get_unknown_track ===")
    print(f"Unknown track: {unknown_track}")
    
    # Check the rule: never both artist and title Unknown unless show/location provided
    if unknown_track['artist'] == 'Unknown' and unknown_track['title'] == 'Unknown':
        show = unknown_track.get('show', 'Unknown')
        location = unknown_track.get('location', '')
        print(f"Both artist and title are Unknown, show: '{show}', location: '{location}'")
        
        if show != 'Unknown' or location != '':
            print("✅ PASS: Show or location provides meaningful info")
        else:
            print("❌ FAIL: No meaningful info when both artist and title are Unknown")
    else:
        print("✅ PASS: At least one of artist or title is not Unknown")
    
    # Test get_now_playing for stream that doesn't exist yet (should return unknown track)
    print("\n=== Testing get_now_playing for non-cached stream ===")
    now_playing = fetcher.get_now_playing('NTS1')
    track_info = now_playing.get('track_info', {})
    
    print(f"Track info: {track_info}")
    
    if track_info['artist'] == 'Unknown' and track_info['title'] == 'Unknown':
        show = track_info.get('show', 'Unknown')
        location = track_info.get('location', '')
        print(f"Both artist and title are Unknown, show: '{show}', location: '{location}'")
        
        if show != 'Unknown' or location != '':
            print("✅ PASS: Show or location provides meaningful info")
        else:
            print("❌ FAIL: No meaningful info when both artist and title are Unknown")
    else:
        print("✅ PASS: At least one of artist or title is not Unknown")
    
    # Test with actual fetching (briefly)
    print("\n=== Testing with actual fetching ===")
    fetcher.start()
    time.sleep(3)  # Give it time to fetch
    
    all_playing = fetcher.get_all_now_playing()
    for stream_name, info in all_playing.items():
        track_info = info.get('track_info', {})
        if track_info:
            print(f"\n{stream_name}: {track_info}")
            
            if track_info['artist'] == 'Unknown' and track_info['title'] == 'Unknown':
                show = track_info.get('show', 'Unknown')
                location = track_info.get('location', '')
                print(f"  Both artist and title are Unknown, show: '{show}', location: '{location}'")
                
                if show != 'Unknown' or location != '':
                    print("  ✅ PASS: Show or location provides meaningful info")
                else:
                    print("  ❌ FAIL: No meaningful info when both artist and title are Unknown")
            else:
                print("  ✅ PASS: At least one of artist or title is not Unknown")
    
    fetcher.stop()
    print("\n=== Verification Complete ===")

if __name__ == "__main__":
    verify_meaningful_strings()
