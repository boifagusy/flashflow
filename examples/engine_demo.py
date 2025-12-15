#!/usr/bin/env python3
"""
FlashFlow Engine Demo
This script demonstrates how to use the FlashFlow Engine programmatically
"""

import sys
import os
from pathlib import Path

# Add the python-services directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "python-services" / "flet-direct-renderer"))

from main import FlashFlowEngine

def main():
    """Demo the FlashFlow Engine"""
    print("🚀 FlashFlow Engine Demo")
    print("=" * 50)
    
    # Get the project directory (current directory)
    project_dir = Path(__file__).parent.parent
    
    # Create FlashFlow Engine instance
    print(f"📂 Project directory: {project_dir}")
    print(f"📡 Backend URL: http://localhost:8000")
    
    try:
        # Create engine instance (this won't actually start the server in this demo)
        engine = FlashFlowEngine(str(project_dir), "http://localhost:8000")
        
        print("✅ FlashFlow Engine created successfully!")
        print(f"📄 Flow files directory: {engine.flow_files_dir}")
        print(f"🔗 Registered routes: {list(engine.page_registry.keys())}")
        
        # Show how to make an API request (this is just a demo)
        print("\n🔌 API Integration Demo:")
        print("   GET /api/users     - Retrieve users")
        print("   POST /api/users    - Create new user")
        print("   PUT /api/users/1   - Update user with ID 1")
        print("   DELETE /api/users/1 - Delete user with ID 1")
        
        print("\n💡 To run the actual engine:")
        print("   python python-services/flet-direct-renderer/main.py")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()