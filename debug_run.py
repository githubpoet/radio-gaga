#!/usr/bin/env python3
"""
Debug script to run the Radio TUI and capture logs for bug reproduction.
This will help identify:
1. Missing track info bug
2. UI flicker bug
3. draw_ui() frequency measurement
"""

import os
import sys
import time
import subprocess
import signal
import logging

def setup_logging():
    """Setup logging to capture all debug output."""
    log_file = '/Users/sk/radio_tui/debug_session.log'
    
    # Clear previous log
    with open(log_file, 'w') as f:
        f.write(f"DEBUG SESSION STARTED: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*60 + "\n")
    
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def main():
    logger = setup_logging()
    logger.info("Starting Radio TUI debug session...")
    
    # Clear debug log from previous runs
    debug_log = '/Users/sk/radio_tui/debug.log'
    if os.path.exists(debug_log):
        os.remove(debug_log)
    
    try:
        logger.info("Launching Radio TUI in debug mode...")
        logger.info("The TUI will run for 30 seconds to capture bug behavior")
        logger.info("Expected behaviors to observe:")
        logger.info("1. Missing track info (should show 'Loading...' or 'No info')")
        logger.info("2. Screen flicker from excessive draw_ui() calls")
        logger.info("3. Frequency of draw_ui() calls (should be ~5Hz)")
        
        # Start the TUI in a subprocess
        env = os.environ.copy()
        env['PYTHONPATH'] = '/Users/sk/radio_tui'
        
        process = subprocess.Popen(
            [sys.executable, '/Users/sk/radio_tui/radio.py'],
            cwd='/Users/sk/radio_tui',
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        logger.info(f"TUI process started with PID: {process.pid}")
        logger.info("Monitoring for 30 seconds...")
        
        # Let it run for 30 seconds
        start_time = time.time()
        while time.time() - start_time < 30:
            if process.poll() is not None:
                logger.error("TUI process terminated unexpectedly")
                break
            time.sleep(1)
            elapsed = int(time.time() - start_time)
            if elapsed % 5 == 0:
                logger.info(f"Monitoring... {elapsed}s elapsed")
        
        # Terminate the process
        logger.info("Terminating TUI process...")
        try:
            process.terminate()
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            logger.warning("Process didn't terminate gracefully, killing...")
            process.kill()
            process.wait()
        
        logger.info("TUI process terminated")
        
        # Capture any output
        stdout, stderr = process.communicate()
        if stdout:
            logger.info(f"TUI stdout: {stdout}")
        if stderr:
            logger.info(f"TUI stderr: {stderr}")
        
        # Analyze the debug log
        logger.info("Analyzing debug log...")
        if os.path.exists(debug_log):
            with open(debug_log, 'r') as f:
                log_content = f.read()
            
            # Count draw_ui calls
            draw_ui_calls = log_content.count('draw_ui() called')
            if draw_ui_calls > 0:
                logger.info(f"Found {draw_ui_calls} draw_ui() call logs")
                
                # Extract frequency information
                frequencies = []
                for line in log_content.split('\n'):
                    if 'frequency:' in line:
                        try:
                            freq_str = line.split('frequency: ')[1].split(' Hz')[0]
                            frequencies.append(float(freq_str))
                        except:
                            pass
                
                if frequencies:
                    avg_freq = sum(frequencies) / len(frequencies)
                    max_freq = max(frequencies)
                    min_freq = min(frequencies)
                    logger.info(f"Draw frequency stats: avg={avg_freq:.2f}Hz, max={max_freq:.2f}Hz, min={min_freq:.2f}Hz")
                    
                    if avg_freq > 10:
                        logger.warning("FLICKER BUG DETECTED: Average frequency > 10Hz indicates excessive repainting")
                    elif avg_freq < 3:
                        logger.warning("Performance issue: Average frequency < 3Hz, UI may feel sluggish")
                    else:
                        logger.info("Draw frequency appears normal (3-10Hz)")
            
            # Check for missing track info bugs
            missing_track_bugs = log_content.count('Missing track info bug:')
            if missing_track_bugs > 0:
                logger.warning(f"MISSING TRACK INFO BUG DETECTED: Found {missing_track_bugs} instances")
                
                # Show some examples
                examples = []
                for line in log_content.split('\n'):
                    if 'Missing track info bug:' in line:
                        examples.append(line.strip())
                        if len(examples) >= 3:
                            break
                
                for example in examples:
                    logger.info(f"Example: {example}")
            else:
                logger.info("No missing track info bugs detected")
            
            logger.info(f"Full debug log saved to: {debug_log}")
        else:
            logger.warning("No debug log file found")
        
        logger.info("Debug session completed successfully")
        
    except KeyboardInterrupt:
        logger.info("Debug session interrupted by user")
        if 'process' in locals() and process.poll() is None:
            process.terminate()
    except Exception as e:
        logger.error(f"Error during debug session: {e}")
        if 'process' in locals() and process.poll() is None:
            process.terminate()

if __name__ == "__main__":
    main()
