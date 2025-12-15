#!/usr/bin/env python3
"""
Build script for FlashFlow Flet Direct Renderer
"""

import subprocess
import sys
import os
from pathlib import Path

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    
    # Install requirements
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def build_executable():
    """Build executable using PyInstaller"""
    print("Building executable...")
    
    try:
        # Install PyInstaller if not present
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], 
                      check=True, capture_output=True)
        
        # Build executable
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--name", "flet-direct-renderer",
            "--hidden-import", "flet",
            "--hidden-import", "yaml",
            "main.py"
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        print("✅ Executable built successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to build executable: {e}")
        return False

def main():
    """Main build function"""
    print("Building FlashFlow Flet Direct Renderer...")
    
    # Change to script directory
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Build executable
    if not build_executable():
        sys.exit(1)
    
    print("\n🎉 Build completed successfully!")
    print("Executable location: dist/flet-direct-renderer")

if __name__ == "__main__":
    main()