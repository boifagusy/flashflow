#!/usr/bin/env python3
"""
FlashFlow Theme Preview Demo
This script demonstrates how to preview .flow files using FlashFlow's theme preview functionality.
"""

import os
import sys
import subprocess
import webbrowser
import time

def main():
    """Main function to run the FlashFlow theme preview demo"""
    
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Change to the FlashFlow project directory
    flashflow_dir = current_dir
    os.chdir(flashflow_dir)
    
    print("FlashFlow Theme Preview Demo")
    print("=" * 40)
    print("Starting FlashFlow theme preview server...")
    print("Demo file: demo.flow")
    print()
    
    try:
        # Start the FlashFlow theme preview server
        print("Starting FlashFlow server with live reloading...")
        print("Use Ctrl+C to stop the server")
        print()
        
        # Run the flashflow serve command
        # This will start the development server with live reloading
        subprocess.run(["flashflow", "serve"], check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"Error running FlashFlow server: {e}")
        print("Make sure FlashFlow is properly installed and accessible in your PATH")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
        sys.exit(0)
    except FileNotFoundError:
        print("Error: 'flashflow' command not found")
        print("Make sure FlashFlow CLI is installed and accessible in your PATH")
        print("You can install it with: pip install -e .")
        sys.exit(1)

if __name__ == "__main__":
    main()