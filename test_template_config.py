#!/usr/bin/env python3
"""
Test script to verify that the radio_default.yaml template
is properly loaded from package resources.
"""

import sys
import tempfile
import os
from pathlib import Path

# Add current directory to path for testing
sys.path.insert(0, '.')

def test_load_packaged_template():
    """Test loading the packaged template."""
    print("Testing load_packaged_template()...")
    
    from config import load_packaged_template
    
    try:
        template = load_packaged_template()
        print(f"✅ Template loaded successfully (length: {len(template)})")
        
        # Check if it contains expected content
        if "Radio Gaga Default Configuration Template" in template:
            print("✅ Template contains expected header")
        else:
            print("❌ Template missing expected header")
            
        if "streams:" in template and "defaults:" in template:
            print("✅ Template contains expected sections")
        else:
            print("❌ Template missing expected sections")
            
        return True
        
    except Exception as e:
        print(f"❌ Failed to load template: {e}")
        return False

def test_ensure_user_default():
    """Test creating user default configuration."""
    print("\nTesting ensure_user_default()...")
    
    from config import ensure_user_default, get_platform_config_dir
    
    # Create a temporary directory to simulate user config area  
    with tempfile.TemporaryDirectory() as temp_dir:
        # Override the platform config dir for testing
        import config
        original_func = config.get_platform_config_dir
        config.get_platform_config_dir = lambda: Path(temp_dir) / 'test-config'
        
        try:
            config_path = ensure_user_default()
            print(f"✅ Config created at: {config_path}")
            
            if config_path.exists():
                print("✅ Config file exists")
                
                with open(config_path, 'r') as f:
                    content = f.read()
                    
                if "Radio Gaga Default Configuration Template" in content:
                    print("✅ Config contains template content")
                else:
                    print("❌ Config missing template content")
                    
                return True
            else:
                print("❌ Config file was not created")
                return False
                
        except Exception as e:
            print(f"❌ Failed to create user config: {e}")
            return False
        finally:
            # Restore original function
            config.get_platform_config_dir = original_func

def main():
    """Run all tests."""
    print("Testing radio_default.yaml template configuration...")
    print("=" * 50)
    
    success = True
    
    # Test 1: Load packaged template
    success &= test_load_packaged_template()
    
    # Test 2: Create user default config
    success &= test_ensure_user_default()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed!")
    else:
        print("❌ Some tests failed!")
        
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
