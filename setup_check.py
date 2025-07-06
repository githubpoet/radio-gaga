#!/usr/bin/env python3
"""
Setup script for Radio TUI
Checks dependencies and provides setup instructions
"""

import sys
import subprocess
import shutil
import os

def check_python_version():
    """Check if Python version is 3.7+"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print(f"❌ Python 3.7+ required, found {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_ffmpeg():
    """Check if FFmpeg is available"""
    if shutil.which('ffplay'):
        print("✅ FFmpeg (ffplay) is available")
        return True
    else:
        print("❌ FFmpeg not found")
        print("   Install with:")
        print("   - macOS: brew install ffmpeg")
        print("   - Ubuntu/Debian: sudo apt install ffmpeg")
        print("   - Windows: Download from https://ffmpeg.org/")
        return False

def check_dependencies():
    """Check Python dependencies"""
    dependencies = ['requests', 'PyYAML']
    missing = []
    
    for dep in dependencies:
        try:
            __import__(dep.lower().replace('-', '_'))
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep}")
            missing.append(dep)
    
    return missing

def install_dependencies(missing):
    """Install missing dependencies"""
    if not missing:
        return True
    
    print(f"\nInstalling missing dependencies: {', '.join(missing)}")
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install'
        ] + missing)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        print("   Try running: pip install -r requirements.txt")
        return False

def test_curses():
    """Test curses functionality"""
    try:
        import curses
        print(f"✅ Curses library (version {curses.version.decode() if hasattr(curses.version, 'decode') else curses.version})")
        return True
    except ImportError:
        print("❌ Curses library not available")
        return False

def run_demo():
    """Ask user if they want to run the demo"""
    response = input("\nWould you like to run the TUI demo? (y/N): ").lower().strip()
    if response in ['y', 'yes']:
        print("\nStarting TUI demo...")
        try:
            subprocess.call([sys.executable, 'demo_tui.py'])
        except KeyboardInterrupt:
            print("\nDemo interrupted")
        except Exception as e:
            print(f"Demo failed: {e}")

def main():
    """Main setup function"""
    print("Radio TUI Setup Check")
    print("=" * 40)
    print()
    
    # Check requirements
    checks_passed = 0
    total_checks = 4
    
    if check_python_version():
        checks_passed += 1
    
    if check_ffmpeg():
        checks_passed += 1
    
    if test_curses():
        checks_passed += 1
    
    missing_deps = check_dependencies()
    if not missing_deps:
        checks_passed += 1
    
    print(f"\nChecks passed: {checks_passed}/{total_checks}")
    
    if missing_deps:
        install_choice = input(f"\nInstall missing dependencies? (y/N): ").lower().strip()
        if install_choice in ['y', 'yes']:
            if install_dependencies(missing_deps):
                checks_passed += 1
                print(f"\nAll checks passed: {checks_passed}/{total_checks}")
    
    if checks_passed == total_checks:
        print("\n🎉 Setup complete! Radio TUI is ready to use.")
        print("\nNext steps:")
        print("1. Run demo: python demo_tui.py")
        print("2. Configure streams in radio.json")
        print("3. Start TUI: python radio.py")
        
        run_demo()
    else:
        print(f"\n⚠️  Setup incomplete ({checks_passed}/{total_checks} checks passed)")
        print("Please fix the issues above before running Radio TUI")

if __name__ == "__main__":
    main()
