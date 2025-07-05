#!/usr/bin/env python3
"""
Now Playing fetcher module for Radio TUI
Periodically fetches current track information from NTS API and ICY metadata fallback.
"""

import threading
import time
import requests
import subprocess
import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime


class NowPlayingFetcher:
    """
    Fetches and caches current track information for radio streams.
    
    Periodically queries:
    1. NTS public JSON endpoint for current track information
    2. Falls back to ICY metadata via ffprobe if NTS API is unavailable
    """
    
    def __init__(self, streams: list, update_interval: int = 15, toast_callback=None):
        """
        Initialize the Now Playing fetcher.
        
        Args:
            streams (list): List of stream dictionaries with 'name' and 'url' keys
            update_interval (int): Update interval in seconds (default: 15)
            toast_callback (callable): Optional callback to show toast messages in UI
        """
        self.streams = {stream['name']: stream for stream in streams}
        self.update_interval = update_interval
        self.cache = {}
        self.lock = threading.Lock()
        self.running = False
        self.thread = None
        self.toast_callback = toast_callback
        self.api_error_shown = False  # Rate limit error notifications
        
        # NTS API endpoint
        self.nts_api_url = "https://www.nts.live/api/v2/live"
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def start(self):
        """Start the periodic fetching thread."""
        if self.running:
            self.logger.warning("Now Playing fetcher is already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._fetch_loop, daemon=True)
        self.thread.start()
        self.logger.info(f"Now Playing fetcher started with {self.update_interval}s interval")
    
    def stop(self):
        """Stop the periodic fetching thread."""
        if not self.running:
            self.logger.warning("Now Playing fetcher is not running")
            return
        
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)
        self.logger.info("Now Playing fetcher stopped")
    
    def _fetch_loop(self):
        """Main fetching loop that runs in a separate thread."""
        while self.running:
            try:
                self._update_all_streams()
            except Exception as e:
                self.logger.error(f"Error in fetch loop: {e}")
            
            # Sleep with checking for stop condition
            for _ in range(self.update_interval):
                if not self.running:
                    break
                time.sleep(1)
    
    def _update_all_streams(self):
        """Update now playing information for all streams."""
        nts_data = self._fetch_nts_api()
        
        with self.lock:
            for stream_name, stream_info in self.streams.items():
                try:
                    # Try NTS API first
                    track_info = self._get_track_from_nts(stream_name, nts_data)
                    
                    # Fallback to ICY metadata if NTS API doesn't have info
                    if not track_info or track_info.get('artist') == 'Unknown':
                        icy_info = self._fetch_icy_metadata(stream_info['url'])
                        if icy_info:
                            track_info = icy_info
                    
                    # Update cache with timestamp, ensuring we always have track_info
                    self.cache[stream_name] = {
                        'track_info': track_info or self._get_unknown_track(),
                        'last_updated': datetime.now().isoformat(),
                        'source': track_info.get('source', 'unknown') if track_info else 'unavailable'
                    }
                    
                except Exception as e:
                    self.logger.error(f"Error updating stream {stream_name}: {e}")
                    # Keep existing cache entry but mark as error
                    if stream_name in self.cache:
                        self.cache[stream_name]['source'] = 'error'
                    else:
                        self.cache[stream_name] = {
                            'track_info': self._get_unknown_track(),
                            'last_updated': datetime.now().isoformat(),
                            'source': 'error'
                        }
    
    def _fetch_nts_api(self) -> Optional[Dict[str, Any]]:
        """
        Fetch live data from NTS API.
        
        Returns:
            dict: NTS API response data, or None if request fails
        """
        try:
            response = requests.get(self.nts_api_url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Network/API error: {e}")
            # Show toast notification for API errors (rate limited)
            if not self.api_error_shown and self.toast_callback:
                self.toast_callback("API error - continuing")
                self.api_error_shown = True
                # Reset flag after 30 seconds to allow new notifications
                threading.Timer(30.0, lambda: setattr(self, 'api_error_shown', False)).start()
            return None
        except Exception as e:
            self.logger.debug(f"NTS API request failed: {e}")
            return None
    
    def _get_track_from_nts(self, stream_name: str, nts_data: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Extract track information for a specific stream from NTS API data.
        
        Args:
            stream_name (str): Name of the stream (e.g., "NTS1", "NTS2")
            nts_data (dict): NTS API response data
            
        Returns:
            dict: Track information, or None if not available
        """
        if not nts_data or 'results' not in nts_data:
            return None
        
        try:
            for channel in nts_data['results']:
                # Map stream names to NTS channel names
                channel_name = channel.get('channel_name', '').upper()
                if (stream_name.upper() == 'NTS1' and channel_name == 'NTS 1') or \
                   (stream_name.upper() == 'NTS2' and channel_name == 'NTS 2'):
                    
                    # Get current broadcast
                    current_broadcast = channel.get('now', {})
                    if not current_broadcast:
                        continue
                    
                    # Extract track information
                    broadcast_title = current_broadcast.get('broadcast_title', 'Unknown Show')
                    location = current_broadcast.get('location', '')
                    
                    # Try to get current track from tracklist
                    current_track = current_broadcast.get('current_track')
                    if current_track:
                        return {
                            'artist': current_track.get('artist', 'Unknown'),
                            'title': current_track.get('title', 'Unknown'),
                            'show': broadcast_title,
                            'location': location,
                            'source': 'nts_api'
                        }
                    else:
                        # No specific track, use show info
                        return {
                            'artist': location if location else 'NTS',
                            'title': broadcast_title,
                            'show': broadcast_title,
                            'location': location,
                            'source': 'nts_api'
                        }
        except Exception as e:
            self.logger.debug(f"Error parsing NTS data for {stream_name}: {e}")
        
        return None
    
    def _fetch_icy_metadata(self, stream_url: str) -> Optional[Dict[str, Any]]:
        """
        Fetch ICY metadata using ffprobe.
        
        Args:
            stream_url (str): Stream URL to probe
            
        Returns:
            dict: Track information from ICY metadata, or None if unavailable
        """
        try:
            # Use ffprobe to get stream metadata
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_entries', 'format_tags=icy-name,icy-title,icy-genre,title',
                '-i', stream_url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                self.logger.debug(f"ffprobe failed for {stream_url}: {result.stderr}")
                return None
            
            # Parse JSON output
            data = json.loads(result.stdout)
            format_tags = data.get('format', {}).get('tags', {})
            
            # Extract relevant fields
            icy_title = format_tags.get('icy-title', format_tags.get('title', ''))
            icy_name = format_tags.get('icy-name', '')
            icy_genre = format_tags.get('icy-genre', '')
            
            if not icy_title:
                return None
            
            # Try to parse artist and title from icy-title
            if ' - ' in icy_title:
                parts = icy_title.split(' - ', 1)
                artist = parts[0].strip()
                title = parts[1].strip()
            else:
                artist = icy_name if icy_name else 'Unknown'
                title = icy_title
            
            # Ensure we always have a meaningful show value
            show = icy_name if icy_name else 'Live Stream'
            
            return {
                'artist': artist,
                'title': title,
                'show': show,
                'genre': icy_genre,
                'source': 'icy_metadata'
            }
            
        except subprocess.TimeoutExpired:
            self.logger.debug(f"ffprobe timeout for {stream_url}")
            return None
        except Exception as e:
            self.logger.debug(f"Error fetching ICY metadata for {stream_url}: {e}")
            return None
    
    def _get_unknown_track(self) -> Dict[str, Any]:
        """
        Get default track information for unknown/unavailable tracks.
        
        Returns:
            dict: Default track information
        """
        return {
            'artist': 'Unknown',
            'title': 'Unknown',
            'show': 'Live Stream',
            'source': 'unknown'
        }
    
    def get_now_playing(self, stream_name: str) -> Dict[str, Any]:
        """
        Get current track information for a specific stream.
        
        Args:
            stream_name (str): Name of the stream
            
        Returns:
            dict: Current track information and metadata
        """
        with self.lock:
            if stream_name not in self.cache:
                return {
                    'track_info': self._get_unknown_track(),
                    'last_updated': None,
                    'source': 'not_cached'
                }
            
            return self.cache[stream_name].copy()
    
    def get_all_now_playing(self) -> Dict[str, Dict[str, Any]]:
        """
        Get current track information for all streams.
        
        Returns:
            dict: Dictionary mapping stream names to track information
        """
        with self.lock:
            return {stream: info.copy() for stream, info in self.cache.items()}
    
    def force_update(self, stream_name: Optional[str] = None):
        """
        Force an immediate update of track information.
        
        Args:
            stream_name (str, optional): Specific stream to update, or None for all streams
        """
        if stream_name and stream_name not in self.streams:
            self.logger.warning(f"Stream {stream_name} not found")
            return
        
        try:
            if stream_name:
                # Update specific stream
                nts_data = self._fetch_nts_api()
                with self.lock:
                    stream_info = self.streams[stream_name]
                    track_info = self._get_track_from_nts(stream_name, nts_data)
                    
                    if not track_info or track_info.get('artist') == 'Unknown':
                        icy_info = self._fetch_icy_metadata(stream_info['url'])
                        if icy_info:
                            track_info = icy_info
                    
                    self.cache[stream_name] = {
                        'track_info': track_info or self._get_unknown_track(),
                        'last_updated': datetime.now().isoformat(),
                        'source': track_info.get('source', 'unknown') if track_info else 'unavailable'
                    }
            else:
                # Update all streams
                self._update_all_streams()
                
        except Exception as e:
            self.logger.error(f"Error in force update: {e}")
    
    def __del__(self):
        """Cleanup on object destruction."""
        self.stop()
