#!/usr/bin/env python3
"""
StreamManager module for Radio TUI
Manages audio stream playback using ffplay subprocess.
"""

import subprocess
import signal
import os
from typing import Optional, Dict, Any
from .now_playing import NowPlayingFetcher


class StreamManager:
    """
    Manages audio stream playback using ffplay subprocess.
    
    Ensures only one stream process runs at a time and provides
    methods to control playback.
    """
    
    def __init__(self, streams: list, toast_callback=None):
        """
        Initialize StreamManager with available streams.
        
        Args:
            streams (list): List of stream dictionaries with 'name' and 'url' keys
            toast_callback (callable): Optional callback to show toast messages in UI
        """
        self.streams = {i: stream for i, stream in enumerate(streams)}
        self.current_process: Optional[subprocess.Popen] = None
        self.current_stream_id: Optional[int] = None
        self.toast_callback = toast_callback
        
        # Initialize Now Playing fetcher
        self.now_playing_fetcher = NowPlayingFetcher(streams, toast_callback=toast_callback)
        self.now_playing_fetcher.start()
    
    def play(self, stream_id: int) -> bool:
        """
        Start playing a stream by ID.
        
        Args:
            stream_id (int): ID of the stream to play
            
        Returns:
            bool: True if stream started successfully, False otherwise
        """
        if stream_id not in self.streams:
            print(f"Error: Stream ID {stream_id} not found")
            return False
        
        # Stop current stream if playing
        if self.current_process is not None:
            self.stop()
        
        stream = self.streams[stream_id]
        stream_url = stream['url']
        
        try:
            # Launch ffplay with specified options
            self.current_process = subprocess.Popen([
                'ffplay',
                '-nodisp',           # No video display
                '-autoexit',         # Exit when playback ends
                '-loglevel', 'quiet', # Quiet logging
                stream_url
            ], 
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            preexec_fn=os.setsid if os.name != 'nt' else None  # Create new process group on Unix
            )
            
            self.current_stream_id = stream_id
            print(f"Started playing: {stream['name']}")
            return True
            
        except FileNotFoundError:
            error_msg = "ffplay not found. Please install FFmpeg."
            print(f"Error: {error_msg}")
            if self.toast_callback:
                self.toast_callback("FFplay not found")
            return False
        except Exception as e:
            error_msg = f"Error starting stream: {e}"
            print(error_msg)
            if self.toast_callback:
                self.toast_callback("Stream launch failed")
            return False
    
    def stop(self) -> bool:
        """
        Stop the currently playing stream.
        
        Returns:
            bool: True if stream was stopped, False if no stream was playing
        """
        if self.current_process is None:
            print("No stream is currently playing")
            return False
        
        try:
            # Gracefully terminate the process
            if os.name == 'nt':  # Windows
                self.current_process.terminate()
            else:  # Unix-like systems
                # Send SIGTERM to the process group
                os.killpg(os.getpgid(self.current_process.pid), signal.SIGTERM)
            
            # Wait for process to terminate with timeout
            try:
                self.current_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Force kill if graceful termination fails
                if os.name == 'nt':
                    self.current_process.kill()
                else:
                    os.killpg(os.getpgid(self.current_process.pid), signal.SIGKILL)
                self.current_process.wait()
            
            print("Stream stopped")
            self.current_process = None
            self.current_stream_id = None
            return True
            
        except Exception as e:
            print(f"Error stopping stream: {e}")
            # Clean up references even if there was an error
            self.current_process = None
            self.current_stream_id = None
            return False
    
    def switch(self, stream_id: int) -> bool:
        """
        Switch to a different stream.
        
        Args:
            stream_id (int): ID of the stream to switch to
            
        Returns:
            bool: True if switch was successful, False otherwise
        """
        if stream_id not in self.streams:
            print(f"Error: Stream ID {stream_id} not found")
            return False
        
        if self.current_stream_id == stream_id:
            print(f"Already playing stream: {self.streams[stream_id]['name']}")
            return True
        
        # Stop current stream and start new one
        self.stop()
        return self.play(stream_id)
    
    def status(self) -> Dict[str, Any]:
        """
        Get current playback status.
        
        Returns:
            dict: Status information including current stream and process state
        """
        status_info = {
            'is_playing': False,
            'current_stream_id': None,
            'current_stream_name': None,
            'current_stream_url': None,
            'process_alive': False,
            'available_streams': len(self.streams)
        }
        
        if self.current_process is not None:
            # Check if process is still alive
            poll_result = self.current_process.poll()
            if poll_result is None:  # Process is still running
                status_info['is_playing'] = True
                status_info['process_alive'] = True
            else:
                # Process has terminated, clean up
                print("Stream process has terminated")
                self.current_process = None
                self.current_stream_id = None
        
        if self.current_stream_id is not None:
            stream = self.streams[self.current_stream_id]
            status_info['current_stream_id'] = self.current_stream_id
            status_info['current_stream_name'] = stream['name']
            status_info['current_stream_url'] = stream['url']
        
        return status_info
    
    def get_now_playing(self, stream_name: str) -> Dict[str, Any]:
        """
        Get current track information for a specific stream.
        
        Args:
            stream_name (str): Name of the stream
            
        Returns:
            dict: Current track information and metadata
        """
        return self.now_playing_fetcher.get_now_playing(stream_name)
    
    def get_all_now_playing(self) -> Dict[str, Dict[str, Any]]:
        """
        Get current track information for all streams.
        
        Returns:
            dict: Dictionary mapping stream names to track information
        """
        return self.now_playing_fetcher.get_all_now_playing()
    
    def force_update_now_playing(self, stream_name: Optional[str] = None):
        """
        Force an immediate update of track information.
        
        Args:
            stream_name (str, optional): Specific stream to update, or None for all streams
        """
        self.now_playing_fetcher.force_update(stream_name)
    
    def __del__(self):
        """Cleanup on object destruction."""
        if self.current_process is not None:
            self.stop()
        if hasattr(self, 'now_playing_fetcher'):
            self.now_playing_fetcher.stop()
