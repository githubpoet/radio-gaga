#!/usr/bin/env python3
"""
Unit tests for configuration resolution and management

Tests cover:
- get_config_path resolution order with tmp_path fixtures
- Environment variable overrides
- Default file creation on first run
- Functional CLI testing with temporary config files
"""

import os
import pytest
import tempfile
import json
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock
import subprocess
import sys

# Import the modules under test
from config import (
    get_config_path, 
    load_config_from_path, 
    ensure_user_default, 
    resolve_and_load_config,
    get_platform_config_dir,
    ConfigurationError,
    DEFAULT_CONFIG,
    CONFIG_TEMPLATE
)


class TestGetConfigPathResolution:
    """Test get_config_path resolution order using tmp_path fixtures"""
    
    def test_cli_arg_highest_priority(self, tmp_path):
        """Test that CLI argument has highest priority"""
        # Create test config file
        config_file = tmp_path / "custom_config.yaml"
        config_file.write_text("streams: []\ndefaults: {}")
        
        # Create files in other locations that should be ignored
        env_config = tmp_path / "env_config.yaml"
        env_config.write_text("streams: []\ndefaults: {}")
        
        with patch.dict(os.environ, {"RADIO_GAGA_CONFIG": str(env_config)}):
            result = get_config_path(str(config_file))
            assert result == config_file
    
    def test_environment_variable_second_priority(self, tmp_path):
        """Test that RADIO_GAGA_CONFIG environment variable has second priority"""
        env_config = tmp_path / "env_config.yaml"
        env_config.write_text("streams: []\ndefaults: {}")
        
        with patch.dict(os.environ, {"RADIO_GAGA_CONFIG": str(env_config)}):
            result = get_config_path()
            assert result == env_config
    
    def test_platform_config_dir_third_priority(self, tmp_path, monkeypatch):
        """Test that platform-specific config directory has third priority"""
        # Create platform config directory and file
        platform_config = tmp_path / "radio.yaml"
        platform_config.write_text("streams: []\ndefaults: {}")
        
        # Mock get_platform_config_dir to return our tmp_path
        monkeypatch.setattr("config.get_platform_config_dir", lambda: tmp_path)
        
        # Ensure no environment variable is set
        with patch.dict(os.environ, {}, clear=True):
            result = get_config_path()
            assert result == platform_config
    
    def test_platform_config_json_fallback(self, tmp_path, monkeypatch):
        """Test that JSON config is found if YAML doesn't exist"""
        platform_config = tmp_path / "radio.json"
        platform_config.write_text('{"streams": [], "defaults": {}}')
        
        monkeypatch.setattr("config.get_platform_config_dir", lambda: tmp_path)
        
        with patch.dict(os.environ, {}, clear=True):
            result = get_config_path()
            assert result == platform_config
    
    def test_legacy_cwd_locations(self, tmp_path, monkeypatch):
        """Test legacy current working directory locations"""
        # Change to tmp_path directory
        monkeypatch.chdir(tmp_path)
        
        # Create legacy config in current directory
        legacy_config = tmp_path / "radio.yaml"
        legacy_config.write_text("streams: []\ndefaults: {}")
        
        # Mock platform config dir to empty directory
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        monkeypatch.setattr("config.get_platform_config_dir", lambda: empty_dir)
        
        with patch.dict(os.environ, {}, clear=True):
            result = get_config_path()
            assert result == legacy_config
    
    def test_packaged_defaults_lowest_priority(self, tmp_path, monkeypatch):
        """Test that packaged defaults are used as last resort"""
        # Mock all other locations to be empty
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        
        # Create packaged config
        packaged_config = tmp_path / "radio.yaml"
        packaged_config.write_text("streams: []\ndefaults: {}")
        
        monkeypatch.setattr("config.get_platform_config_dir", lambda: empty_dir)
        monkeypatch.setattr("config.get_packaged_config_path", lambda: packaged_config)
        monkeypatch.chdir(empty_dir)
        
        with patch.dict(os.environ, {}, clear=True):
            result = get_config_path()
            assert result == packaged_config
    
    def test_no_config_found_raises_error(self, tmp_path, monkeypatch):
        """Test that ConfigurationError is raised when no config is found"""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        
        monkeypatch.setattr("config.get_platform_config_dir", lambda: empty_dir)
        monkeypatch.setattr("config.get_packaged_config_path", lambda: empty_dir / "nonexistent.yaml")
        monkeypatch.chdir(empty_dir)
        
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ConfigurationError) as exc_info:
                get_config_path()
            
            assert "No configuration file found" in str(exc_info.value)
            assert exc_info.value.search_paths  # Should have search paths listed
    
    def test_cli_arg_nonexistent_file_continues_search(self, tmp_path, monkeypatch):
        """Test that nonexistent CLI arg file continues search to next priority"""
        nonexistent_file = tmp_path / "nonexistent.yaml"
        
        # Create environment config that should be found
        env_config = tmp_path / "env_config.yaml"
        env_config.write_text("streams: []\ndefaults: {}")
        
        with patch.dict(os.environ, {"RADIO_GAGA_CONFIG": str(env_config)}):
            result = get_config_path(str(nonexistent_file))
            assert result == env_config
    
    def test_environment_overrides(self, tmp_path, monkeypatch):
        """Test various environment variable override scenarios"""
        config1 = tmp_path / "config1.yaml"
        config2 = tmp_path / "config2.yaml"
        config1.write_text("streams: []\ndefaults: {}")
        config2.write_text("streams: []\ndefaults: {}")
        
        # Mock all other locations to be empty
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        monkeypatch.setattr("config.get_platform_config_dir", lambda: empty_dir)
        monkeypatch.setattr("config.get_packaged_config_path", lambda: empty_dir / "nonexistent.yaml")
        monkeypatch.chdir(empty_dir)
        
        # Test setting environment variable
        with patch.dict(os.environ, {"RADIO_GAGA_CONFIG": str(config1)}):
            result = get_config_path()
            assert result == config1
        
        # Test changing environment variable
        with patch.dict(os.environ, {"RADIO_GAGA_CONFIG": str(config2)}):
            result = get_config_path()
            assert result == config2
        
        # Test unsetting environment variable
        with patch.dict(os.environ, {}, clear=True):
            # This should fail since no other configs exist
            with pytest.raises(ConfigurationError):
                get_config_path()


class TestDefaultFileCreation:
    """Test creation of default configuration file on first run"""
    
    def test_ensure_user_default_creates_file(self, tmp_path, monkeypatch):
        """Test that ensure_user_default creates a config file"""
        monkeypatch.setattr("config.get_platform_config_dir", lambda: tmp_path)
        
        config_path = ensure_user_default()
        
        assert config_path.exists()
        assert config_path.name == "radio.yaml"
        assert config_path.parent == tmp_path
        
        # Check file content
        content = config_path.read_text()
        assert "Radio Gaga Default Configuration Template" in content
        assert "streams:" in content
        assert "defaults:" in content
    
    def test_ensure_user_default_doesnt_overwrite_existing(self, tmp_path, monkeypatch):
        """Test that existing config files are not overwritten"""
        monkeypatch.setattr("config.get_platform_config_dir", lambda: tmp_path)
        
        # Create existing config
        existing_config = tmp_path / "radio.yaml"
        original_content = "# My custom config\nstreams: []\ndefaults: {}"
        existing_config.write_text(original_content)
        
        config_path = ensure_user_default()
        
        assert config_path == existing_config
        assert config_path.read_text() == original_content
    
    def test_ensure_user_default_finds_json_version(self, tmp_path, monkeypatch):
        """Test that ensure_user_default finds existing JSON config"""
        monkeypatch.setattr("config.get_platform_config_dir", lambda: tmp_path)
        
        # Create existing JSON config
        json_config = tmp_path / "radio.json"
        json_config.write_text('{"streams": [], "defaults": {}}')
        
        config_path = ensure_user_default()
        
        assert config_path == json_config
    
    def test_ensure_user_default_creates_directory(self, tmp_path, monkeypatch):
        """Test that ensure_user_default creates parent directories"""
        config_dir = tmp_path / "nested" / "config" / "radio-gaga"
        monkeypatch.setattr("config.get_platform_config_dir", lambda: config_dir)
        
        config_path = ensure_user_default()
        
        assert config_dir.exists()
        assert config_path.exists()
        assert config_path.parent == config_dir
    
    def test_ensure_user_default_permission_error(self, tmp_path, monkeypatch):
        """Test handling of permission errors when creating config"""
        # Create a directory that can't be written to (simulate permission error)
        readonly_dir = tmp_path / "readonly"
        readonly_dir.mkdir()
        readonly_dir.chmod(0o444)  # Read-only
        
        monkeypatch.setattr("config.get_platform_config_dir", lambda: readonly_dir)
        
        try:
            with pytest.raises((ConfigurationError, PermissionError)) as exc_info:
                ensure_user_default()
            
            # The error could be a ConfigurationError wrapping the permission error
            # or a direct PermissionError depending on when it occurs
            error_str = str(exc_info.value)
            assert ("Could not create configuration file" in error_str or 
                   "Permission denied" in error_str)
        finally:
            # Restore permissions for cleanup
            readonly_dir.chmod(0o755)
    
    def test_first_run_integration(self, tmp_path, monkeypatch):
        """Test complete first-run scenario"""
        monkeypatch.setattr("config.get_platform_config_dir", lambda: tmp_path)
        monkeypatch.setattr("config.get_packaged_config_path", lambda: tmp_path / "nonexistent.yaml")
        
        with patch.dict(os.environ, {}, clear=True):
            # This should create user default and return it
            config_path, config_data = resolve_and_load_config()
            
            # Should have created the user config
            user_config = tmp_path / "radio.yaml"
            assert user_config.exists()
            
            # Should return the newly created config
            assert config_path == user_config
            assert isinstance(config_data, dict)
            assert "streams" in config_data
            assert "defaults" in config_data


class TestConfigFileLoading:
    """Test configuration file loading and validation"""
    
    def test_load_yaml_config(self, tmp_path):
        """Test loading YAML configuration"""
        yaml_config = tmp_path / "config.yaml"
        test_data = {
            "streams": [{"name": "Test", "url": "http://test.com"}],
            "defaults": {"volume": 0.8}
        }
        yaml_config.write_text(yaml.dump(test_data))
        
        result = load_config_from_path(yaml_config)
        assert result == test_data
    
    def test_load_json_config(self, tmp_path):
        """Test loading JSON configuration"""
        json_config = tmp_path / "config.json"
        test_data = {
            "streams": [{"name": "Test", "url": "http://test.com"}],
            "defaults": {"volume": 0.8}
        }
        json_config.write_text(json.dumps(test_data))
        
        result = load_config_from_path(json_config)
        assert result == test_data
    
    def test_invalid_yaml_raises_error(self, tmp_path):
        """Test that invalid YAML raises ConfigurationError"""
        yaml_config = tmp_path / "invalid.yaml"
        yaml_config.write_text("invalid: yaml: content: [")
        
        with pytest.raises(ConfigurationError) as exc_info:
            load_config_from_path(yaml_config)
        
        assert "Invalid YAML" in str(exc_info.value)
    
    def test_invalid_json_raises_error(self, tmp_path):
        """Test that invalid JSON raises ConfigurationError"""
        json_config = tmp_path / "invalid.json"
        json_config.write_text('{"invalid": json content}')
        
        with pytest.raises(ConfigurationError) as exc_info:
            load_config_from_path(json_config)
        
        assert "Invalid JSON" in str(exc_info.value)
    
    def test_nonexistent_file_raises_error(self, tmp_path):
        """Test that nonexistent file raises ConfigurationError"""
        nonexistent = tmp_path / "nonexistent.yaml"
        
        with pytest.raises(ConfigurationError) as exc_info:
            load_config_from_path(nonexistent)
        
        assert "does not exist" in str(exc_info.value)


class TestFunctionalCLI:
    """Functional CLI tests with temporary config files"""
    
    def test_cli_with_custom_config(self, tmp_path):
        """Test CLI with custom config file"""
        # Create test config
        test_config = tmp_path / "test_config.yaml"
        config_data = {
            "streams": [
                {"name": "TestStream1", "url": "http://test1.com/stream"},
                {"name": "TestStream2", "url": "http://test2.com/stream"}
            ],
            "defaults": {"volume": 0.9, "start_paused": False}
        }
        test_config.write_text(yaml.dump(config_data))
        
        # Test the CLI interface
        cmd = [
            sys.executable, "radio.py", 
            "--config", str(test_config),
            "--cli"
        ]
        
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True,
            cwd="/Users/sk/radio_tui"
        )
        
        assert result.returncode == 0
        assert "TestStream1" in result.stdout
        assert "TestStream2" in result.stdout
        assert "Available streams (2)" in result.stdout
    
    def test_cli_with_nonexistent_config(self, tmp_path):
        """Test CLI with nonexistent config file returns error"""
        nonexistent_config = tmp_path / "nonexistent.yaml"
        
        cmd = [
            sys.executable, "radio.py",
            "--config", str(nonexistent_config),
            "--cli"
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd="/Users/sk/radio_tui"
        )
        
        assert result.returncode == 1
        assert "Configuration file not found" in result.stderr
    
    def test_cli_config_validation(self, tmp_path):
        """Test CLI validates config structure"""
        # Create invalid config (streams should be list, not dict)
        invalid_config = tmp_path / "invalid_config.yaml"
        invalid_data = {
            "streams": {"name": "Invalid", "url": "http://test.com"},  # Should be list
            "defaults": {"volume": 0.8}
        }
        invalid_config.write_text(yaml.dump(invalid_data))
        
        cmd = [
            sys.executable, "radio.py",
            "--config", str(invalid_config),
            "--cli"
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd="/Users/sk/radio_tui"
        )
        
        assert result.returncode == 1
        assert "Configuration" in result.stderr
    
    def test_cli_play_mode_with_config(self, tmp_path):
        """Test CLI play mode with custom config"""
        # Create test config with specific stream
        test_config = tmp_path / "play_test.yaml"
        config_data = {
            "streams": [
                {"name": "PlayTestStream", "url": "http://example.com/stream"}
            ],
            "defaults": {"volume": 1.0}
        }
        test_config.write_text(yaml.dump(config_data))
        
        # We can't fully test playback, but we can test that it finds the stream
        # and starts the process before we interrupt it
        cmd = [
            sys.executable, "radio.py",
            "--config", str(test_config),
            "--play", "PlayTestStream"
        ]
        
        # Start the process and quickly terminate it
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd="/Users/sk/radio_tui"
        )
        
        try:
            # Give it a moment to start
            stdout, stderr = process.communicate(timeout=2)
            # If it gets this far without error, the config was loaded successfully
        except subprocess.TimeoutExpired:
            # This is expected - terminate the process
            process.terminate()
            stdout, stderr = process.communicate()
        
        # Should not have configuration errors
        assert "Configuration Error" not in stderr
        assert "Configuration file not found" not in stderr
        
        # Should have attempted to play (check if process got far enough to read config)
        # The key test is that there are no configuration errors


class TestPlatformSpecific:
    """Test platform-specific configuration directory resolution"""
    
    @patch('platform.system')
    def test_macos_config_dir(self, mock_system, tmp_path):
        """Test macOS configuration directory"""
        mock_system.return_value = "Darwin"
        
        with patch('pathlib.Path.home') as mock_home:
            mock_home.return_value = tmp_path
            result = get_platform_config_dir()
            expected = tmp_path / "Library" / "Application Support" / "radio-gaga"
            assert result == expected
    
    @patch('platform.system')
    def test_linux_config_dir(self, mock_system, tmp_path):
        """Test Linux configuration directory"""
        mock_system.return_value = "Linux"
        
        with patch('pathlib.Path.home') as mock_home:
            mock_home.return_value = tmp_path
            
            # Test without XDG_CONFIG_HOME
            with patch.dict(os.environ, {}, clear=True):
                result = get_platform_config_dir()
                expected = tmp_path / ".config" / "radio-gaga"
                assert result == expected
    
    @patch('platform.system')
    def test_linux_config_dir_with_xdg(self, mock_system, tmp_path):
        """Test Linux configuration directory with XDG_CONFIG_HOME"""
        mock_system.return_value = "Linux"
        xdg_config = tmp_path / "xdg_config"
        
        with patch.dict(os.environ, {"XDG_CONFIG_HOME": str(xdg_config)}):
            result = get_platform_config_dir()
            expected = xdg_config / "radio-gaga"
            assert result == expected


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
