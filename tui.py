#!/usr/bin/env python3
"""
Curses-based Terminal User Interface for Radio TUI
Displays streams in a vertical list with navigation and playback controls.
"""

import curses
import time
import sys
from config import get_streams
from utils.stream_manager import StreamManager


def radio_tui(stdscr):
    """Main radio TUI function with proper navigation"""
    # Setup
    curses.curs_set(0)  # Hide cursor
    stdscr.nodelay(True)  # Non-blocking input
    
    # Load configuration
    streams = get_streams()
    stream_manager = StreamManager(streams)
    
    selected_index = 0
    running = True
    
    # Setup colors
    if curses.has_colors():
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_WHITE, -1)  # Normal
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Selected
        curses.init_pair(3, curses.COLOR_GREEN, -1)  # Playing
        curses.init_pair(4, curses.COLOR_CYAN, -1)  # Header
        curses.init_pair(5, curses.COLOR_YELLOW, -1)  # Status
    
    while running:
        # Clear and get dimensions
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        
        # Draw header
        title = "Radio Gaga"
        instructions = "↑/↓ or 1-9: Navigate | Space/Enter: Play/Stop | Q: Quit"
        
        stdscr.addstr(0, (width - len(title)) // 2, title, curses.color_pair(4) | curses.A_BOLD)
        if len(instructions) <= width - 2:
            stdscr.addstr(1, (width - len(instructions)) // 2, instructions, curses.color_pair(5))
        stdscr.addstr(2, 0, "─" * width, curses.color_pair(1))
        
        # Draw streams
        for i, stream in enumerate(streams):
            if i + 4 >= height - 2:  # Leave space for status
                break
                
            # Get status
            status = stream_manager.status()
            is_playing = (status.get('is_playing') and 
                         status.get('current_stream_id') == i)
            play_symbol = "▶" if is_playing else "■"
            
            # Format line
            line = f"[{play_symbol}] {stream['name']}"
            
            # Truncate if too long
            if len(line) > width - 4:
                line = line[:width - 7] + "..."
            
            # Choose color
            if i == selected_index:
                color = curses.color_pair(2) | curses.A_BOLD
            elif is_playing:
                color = curses.color_pair(3)
            else:
                color = curses.color_pair(1)
            
            stdscr.addstr(i + 4, 2, line, color)
        
        # Status line
        status_text = "Ready"
        status = stream_manager.status()
        if status.get('is_playing'):
            current_stream_name = streams[status.get('current_stream_id', 0)]['name']
            status_text = f"Playing: {current_stream_name}"
        
        current_time = time.strftime("%H:%M:%S")
        stdscr.addstr(height - 1, 1, status_text, curses.color_pair(5))
        if len(current_time) < width - 2:
            stdscr.addstr(height - 1, width - len(current_time) - 1, current_time, curses.color_pair(5))
        
        # Refresh screen
        stdscr.refresh()
        
        # Handle input
        try:
            key = stdscr.getch()
            if key != -1:  # Key was pressed
                if key == ord('q') or key == ord('Q'):
                    running = False
                elif key == curses.KEY_UP:
                    selected_index = max(0, selected_index - 1)
                elif key == curses.KEY_DOWN:
                    selected_index = min(len(streams) - 1, selected_index + 1)
                elif ord('1') <= key <= ord('9'):
                    num = key - ord('1')
                    if num < len(streams):
                        selected_index = num
                elif key == ord(' ') or key == ord('\n') or key == curses.KEY_ENTER:
                    # Handle play/stop
                    stream_id = selected_index
                    status = stream_manager.status()
                    
                    if status.get('is_playing'):
                        current_stream_id = status.get('current_stream_id')
                        if current_stream_id == stream_id:
                            stream_manager.stop()
                        else:
                            stream_manager.switch(stream_id)
                    else:
                        stream_manager.play(stream_id)
        except:
            pass
        
        # Small delay
        time.sleep(0.05)  # 20 FPS
    
    # Cleanup
    stream_manager.stop()


def main():
    """Main entry point for the TUI"""
    try:
        curses.wrapper(radio_tui)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
