#!/usr/bin/env python3
"""
Functional CLI tests for radio-gaga with temporary configuration files

This module specifically tests the radio-gaga CLI functionality by:
- Creating temporary YAML/JSON configuration files
- Invoking the CLI with these configs
- Ensuring station lists load correctly
- Testing error handling scenarios
"""

import subprocess
import sys
import tempfile
import yaml
import json
from pathlib import Path
import pytest


class TestCLIFunctional:
    """Functional tests for CLI with temporary config files"""
    
    def test_radio_gaga_cli_with_yaml_config(self, tmp_path):
        """Test radio-gaga CLI with temporary YAML config loads station list"""
        # Create temporary YAML config
        config_file = tmp_path / "test_radio.yaml"
        config_data = {
            "streams": [
                {"name": "Test_Station_1", "url": "http://test1.example.com/stream"},
                {"name": "Test_Station_2", "url": "http://test2.example.com/stream"},
                {"name": "BBC_Radio_1", "url": "http://bbc.co.uk/radio1/stream"}
            ],
            "defaults": {
                "volume": 0.8,
                "start_paused": True
            }
        }
        
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        # Test CLI with the config
        cmd = [sys.executable, "radio.py", "--config", str(config_file), "--cli"]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd="/Users/sk/radio_tui",
            timeout=10
        )
        
        # Verify successful execution
        assert result.returncode == 0, f"CLI failed with stderr: {result.stderr}"
        
        # Verify station list loads correctly
        assert "Test_Station_1" in result.stdout
        assert "Test_Station_2" in result.stdout  
        assert "BBC_Radio_1" in result.stdout
        assert "Available streams (3)" in result.stdout
        
        # Verify default settings are displayed
        assert "Volume: 0.8" in result.stdout
        assert "Start paused: True" in result.stdout
    
    def test_radio_gaga_cli_with_json_config(self, tmp_path):
        """Test radio-gaga CLI with temporary JSON config loads station list"""
        # Create temporary JSON config
        config_file = tmp_path / "test_radio.json"
        config_data = {
            "streams": [
                {"name": "JSON_Station", "url": "http://json.example.com/stream"},
                {"name": "Another_JSON_Station", "url": "http://json2.example.com/stream"}
            ],
            "defaults": {
                "volume": 1.0,
                "start_paused": False
            }
        }
        
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        # Test CLI with the config
        cmd = [sys.executable, "radio.py", "--config", str(config_file), "--cli"]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd="/Users/sk/radio_tui",
            timeout=10
        )
        
        # Verify successful execution
        assert result.returncode == 0, f"CLI failed with stderr: {result.stderr}"
        
        # Verify station list loads correctly
        assert "JSON_Station" in result.stdout
        assert "Another_JSON_Station" in result.stdout
        assert "Available streams (2)" in result.stdout
        
        # Verify default settings
        assert "Volume: 1.0" in result.stdout
        assert "Start paused: False" in result.stdout
    
    def test_radio_gaga_cli_nonexistent_config_error(self, tmp_path):
        """Test radio-gaga CLI with nonexistent config file returns proper error"""
        nonexistent_config = tmp_path / "does_not_exist.yaml"
        
        cmd = [sys.executable, "radio.py", "--config", str(nonexistent_config), "--cli"]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd="/Users/sk/radio_tui",
            timeout=10
        )
        
        # Should fail with error
        assert result.returncode == 1
        assert "Configuration file not found" in result.stderr
    
    def test_radio_gaga_cli_invalid_yaml_config_error(self, tmp_path):
        """Test radio-gaga CLI with invalid YAML config returns proper error"""
        invalid_config = tmp_path / "invalid.yaml"
        
        # Create invalid YAML
        with open(invalid_config, 'w') as f:
            f.write("invalid: yaml: content: [\n")
        
        cmd = [sys.executable, "radio.py", "--config", str(invalid_config), "--cli"]
        
        result = subprocess.run(
            cmd,
            capture_output=True, 
            text=True,
            cwd="/Users/sk/radio_tui",
            timeout=10
        )
        
        # Should fail with error
        assert result.returncode == 1
        assert ("Invalid YAML" in result.stderr or "Configuration Error" in result.stderr)
    
    def test_radio_gaga_cli_invalid_json_config_error(self, tmp_path):
        """Test radio-gaga CLI with invalid JSON config returns proper error"""
        invalid_config = tmp_path / "invalid.json"
        
        # Create invalid JSON
        with open(invalid_config, 'w') as f:
            f.write('{"invalid": json content}')
        
        cmd = [sys.executable, "radio.py", "--config", str(invalid_config), "--cli"]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd="/Users/sk/radio_tui",
            timeout=10
        )
        
        # Should fail with error
        assert result.returncode == 1
        assert ("Invalid JSON" in result.stderr or "Configuration Error" in result.stderr)
    
    def test_radio_gaga_play_mode_finds_station(self, tmp_path):
        """Test radio-gaga --play mode can find and attempt to play configured station"""
        # Create config with specific station
        config_file = tmp_path / "play_test.yaml"
        config_data = {
            "streams": [
                {"name": "PlayableStation", "url": "http://example.com/test_stream"}
            ],
            "defaults": {"volume": 0.5}
        }
        
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        # Test play mode (we'll terminate quickly since we can't actually play)
        cmd = [sys.executable, "radio.py", "--config", str(config_file), "--play", "PlayableStation"]
        
        # Start process and terminate quickly to test config loading
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd="/Users/sk/radio_tui"
        )
        
        try:
            # Give it a brief moment to load config and start
            stdout, stderr = process.communicate(timeout=3)
        except subprocess.TimeoutExpired:
            # Expected - terminate the process
            process.terminate()
            stdout, stderr = process.communicate()
        
        # Should have attempted to play (no config errors)
        assert "Configuration Error" not in stderr
        assert "Configuration file not found" not in stderr
        
        # Should have found the station
        if stdout:
            assert ("Playing PlayableStation" in stdout or 
                   "Started playing" in stdout or
                   "PlayableStation" in stdout)
    
    def test_radio_gaga_play_mode_unknown_station_error(self, tmp_path):
        """Test radio-gaga --play mode with unknown station name returns error"""
        # Create config without the station we'll try to play
        config_file = tmp_path / "play_test.yaml"
        config_data = {
            "streams": [
                {"name": "KnownStation", "url": "http://example.com/stream"}
            ],
            "defaults": {"volume": 0.5}
        }
        
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        cmd = [sys.executable, "radio.py", "--config", str(config_file), "--play", "UnknownStation"]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd="/Users/sk/radio_tui",
            timeout=10
        )
        
        # Should fail with appropriate error
        assert result.returncode == 1
        assert "Stream 'UnknownStation' not found" in result.stderr
    
    def test_radio_gaga_config_info_display(self, tmp_path):
        """Test radio-gaga config info functionality with temporary config"""
        # Create temporary config
        config_file = tmp_path / "info_test.yaml"
        config_data = {
            "streams": [{"name": "InfoTest", "url": "http://example.com/stream"}],
            "defaults": {"volume": 0.7}
        }
        
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        # Test config info display
        cmd = [sys.executable, "config.py", "--config", str(config_file), "--info"]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd="/Users/sk/radio_tui",
            timeout=10
        )
        
        # Should succeed and show config info
        assert result.returncode == 0, f"Config info failed with stderr: {result.stderr}"
        assert "Configuration Resolution Info" in result.stdout
        assert str(config_file) in result.stdout


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
