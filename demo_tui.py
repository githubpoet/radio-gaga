#!/usr/bin/env python3
"""
Demo script showing TUI key features without requiring network dependencies
"""

import curses
import time
import threading
import sys

class MockStreamManager:
    """Mock stream manager for demo purposes"""
    def __init__(self):
        self.playing = False
        self.current_stream_id = None
        
    def status(self):
        return {
            'is_playing': self.playing,
            'current_stream_id': self.current_stream_id,
            'current_stream_name': f'NTS{self.current_stream_id + 1}' if self.current_stream_id is not None else None
        }
    
    def play(self, stream_id):
        self.playing = True
        self.current_stream_id = stream_id
        return True
        
    def stop(self):
        self.playing = False
        self.current_stream_id = None
        return True
        
    def switch(self, stream_id):
        self.current_stream_id = stream_id
        return True

class TUIDemo:
    """TUI Demo with mock functionality"""
    
    def __init__(self):
        self.streams = [
            {'name': 'NTS1', 'url': 'mock_url_1'},
            {'name': 'NTS2', 'url': 'mock_url_2'},
            {'name': 'KCRW', 'url': 'mock_url_3'},
        ]
        self.stream_manager = MockStreamManager()
        self.selected_index = 0
        self.running = False
        self.stdscr = None
        
        # Mock now playing data
        self.now_playing_data = {
            'NTS1': {'track_info': {'artist': 'Four Tet', 'title': 'Looking At Your Pager'}},
            'NTS2': {'track_info': {'artist': 'Burial', 'title': 'Archangel'}},
            'KCRW': {'track_info': {'artist': 'Unknown', 'title': 'Unknown'}},
        }
        
        # Color pairs
        self.COLOR_NORMAL = 1
        self.COLOR_SELECTED = 2
        self.COLOR_PLAYING = 3
        self.COLOR_HEADER = 4
        self.COLOR_STATUS = 5
    
    def setup_colors(self):
        """Initialize color pairs"""
        if curses.has_colors():
            curses.start_color()
            curses.use_default_colors()
            curses.init_pair(self.COLOR_NORMAL, curses.COLOR_WHITE, -1)
            curses.init_pair(self.COLOR_SELECTED, curses.COLOR_BLACK, curses.COLOR_WHITE)
            curses.init_pair(self.COLOR_PLAYING, curses.COLOR_GREEN, -1)
            curses.init_pair(self.COLOR_HEADER, curses.COLOR_CYAN, -1)
            curses.init_pair(self.COLOR_STATUS, curses.COLOR_YELLOW, -1)
    
    def get_play_symbol(self, stream_id):
        """Get play symbol for stream"""
        status = self.stream_manager.status()
        if status['is_playing'] and status['current_stream_id'] == stream_id:
            return "▶"
        return "■"
    
    def get_now_playing_text(self, stream_name):
        """Get now playing text"""
        if stream_name not in self.now_playing_data:
            return "Loading..."
        
        track_info = self.now_playing_data[stream_name]['track_info']
        artist = track_info.get('artist', 'Unknown')
        title = track_info.get('title', 'Unknown')
        
        if artist == 'Unknown' and title == 'Unknown':
            return "No info"
        elif artist == 'Unknown':
            return title
        elif title == 'Unknown':
            return artist
        else:
            return f"{artist} - {title}"
    
    def draw_header(self):
        """Draw header"""
        height, width = self.stdscr.getmaxyx()
        
        title = "Radio TUI Demo"
        self.stdscr.addstr(0, (width - len(title)) // 2, title, 
                          curses.color_pair(self.COLOR_HEADER) | curses.A_BOLD)
        
        instructions = "↑/↓ or 1-3: Navigate | Space/Enter: Play/Stop | Q: Quit"
        if len(instructions) <= width - 2:
            self.stdscr.addstr(1, (width - len(instructions)) // 2, instructions,
                              curses.color_pair(self.COLOR_STATUS))
        
        # Status message
        demo_msg = "Demo Mode - No actual audio playback"
        self.stdscr.addstr(2, (width - len(demo_msg)) // 2, demo_msg,
                          curses.color_pair(self.COLOR_STATUS) | curses.A_DIM)
        
        self.stdscr.addstr(3, 0, "─" * width, curses.color_pair(self.COLOR_NORMAL))
    
    def draw_stream_list(self):
        """Draw stream list"""
        height, width = self.stdscr.getmaxyx()
        start_row = 5
        
        for i, stream in enumerate(self.streams):
            if start_row + i >= height - 2:
                break
                
            stream_name = stream['name']
            play_symbol = self.get_play_symbol(i)
            now_playing = self.get_now_playing_text(stream_name)
            
            line = f"[{play_symbol}] {stream_name} | {now_playing}"
            
            if len(line) > width - 2:
                line = line[:width - 5] + "..."
            
            # Color based on state
            if i == self.selected_index:
                color = curses.color_pair(self.COLOR_SELECTED) | curses.A_BOLD
            elif play_symbol == "▶":
                color = curses.color_pair(self.COLOR_PLAYING)
            else:
                color = curses.color_pair(self.COLOR_NORMAL)
            
            self.stdscr.addstr(start_row + i, 1, line, color)
    
    def draw_status_line(self):
        """Draw status line"""
        height, width = self.stdscr.getmaxyx()
        status_row = height - 1
        
        status = self.stream_manager.status()
        if status['is_playing']:
            status_text = f"Playing: {status['current_stream_name']} (Demo Mode)"
        else:
            status_text = "Ready (Demo Mode)"
        
        self.stdscr.addstr(status_row, 1, status_text, curses.color_pair(self.COLOR_STATUS))
        
        current_time = time.strftime("%H:%M:%S")
        if len(current_time) < width - 2:
            self.stdscr.addstr(status_row, width - len(current_time) - 1, current_time,
                              curses.color_pair(self.COLOR_STATUS))
    
    def draw_ui(self):
        """Draw complete UI"""
        self.stdscr.clear()
        self.draw_header()
        self.draw_stream_list()
        self.draw_status_line()
        self.stdscr.refresh()
    
    def handle_input(self, key):
        """Handle keyboard input"""
        if key == ord('q') or key == ord('Q'):
            self.running = False
            return
        
        elif key == curses.KEY_UP:
            self.selected_index = max(0, self.selected_index - 1)
        elif key == curses.KEY_DOWN:
            self.selected_index = min(len(self.streams) - 1, self.selected_index + 1)
        
        elif ord('1') <= key <= ord('9'):
            num = key - ord('1')
            if num < len(self.streams):
                self.selected_index = num
        
        elif key == ord(' ') or key == ord('\n'):
            self.handle_play_stop()
    
    def handle_play_stop(self):
        """Handle play/stop action"""
        stream_id = self.selected_index
        status = self.stream_manager.status()
        
        if status['is_playing']:
            if status['current_stream_id'] == stream_id:
                self.stream_manager.stop()
            else:
                self.stream_manager.switch(stream_id)
        else:
            self.stream_manager.play(stream_id)
    
    def run(self):
        """Main demo loop"""
        try:
            # Initialize curses
            self.stdscr = curses.initscr()
            curses.noecho()
            curses.cbreak()
            self.stdscr.keypad(True)
            curses.curs_set(0)
            
            self.setup_colors()
            self.stdscr.nodelay(True)
            
            self.running = True
            
            # Demo message
            self.stdscr.addstr(0, 0, "Starting Radio TUI Demo...", curses.A_BOLD)
            self.stdscr.refresh()
            time.sleep(1)
            
            while self.running:
                try:
                    self.draw_ui()
                    
                    key = self.stdscr.getch()
                    if key != -1:
                        self.handle_input(key)
                    
                    time.sleep(0.05)  # 20Hz refresh for demo
                    
                except KeyboardInterrupt:
                    break
                except Exception:
                    pass
        
        finally:
            # Cleanup
            if self.stdscr:
                curses.nocbreak()
                self.stdscr.keypad(False)
                curses.echo()
                curses.endwin()

def main():
    """Main demo function"""
    print("Radio TUI Demo")
    print("=" * 40)
    print()
    print("This demo shows the TUI interface without actual audio streaming.")
    print("You can navigate and test the interface controls.")
    print()
    print("Press any key to start the demo...")
    input()
    
    try:
        demo = TUIDemo()
        demo.run()
        print("\nDemo completed! The TUI interface is working correctly.")
        print("\nTo use with real streams:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run: python radio.py")
    except Exception as e:
        print(f"Demo failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
