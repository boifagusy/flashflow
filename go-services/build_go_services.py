#!/usr/bin/env python3
"""
Build script for FlashFlow Go services
"""

import subprocess
import sys
import os
from pathlib import Path

def build_go_service(service_name, service_path):
    """Build a Go service."""
    print(f"Building {service_name}...")
    
    # Change to the service directory
    original_cwd = Path.cwd()
    os.chdir(service_path)
    
    try:
        # Initialize Go module if it doesn't exist
        if not (service_path / "go.mod").exists():
            print(f"  Initializing Go module for {service_name}...")
            result = subprocess.run(["go", "mod", "init", service_name.lower()], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print(f"  Failed to initialize Go module: {result.stderr}")
                return False
        
        # Get dependencies
        print(f"  Getting dependencies for {service_name}...")
        result = subprocess.run(["go", "get", "github.com/gin-gonic/gin"], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  Warning: Failed to get gin dependency: {result.stderr}")
        
        result = subprocess.run(["go", "get", "gopkg.in/yaml.v2"], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  Warning: Failed to get yaml dependency: {result.stderr}")
        
        # Tidy modules
        print(f"  Tidying modules for {service_name}...")
        result = subprocess.run(["go", "mod", "tidy"], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  Warning: Failed to tidy modules: {result.stderr}")
        
        # Build the service
        output_name = service_name
        if sys.platform == "win32":
            output_name += ".exe"
            
        print(f"  Compiling {service_name}...")
        result = subprocess.run(["go", "build", "-o", output_name, "."], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  Failed to build {service_name}: {result.stderr}")
            return False
            
        print(f"  Successfully built {service_name}")
        return True
        
    finally:
        # Restore original directory
        os.chdir(original_cwd)

def build_python_service(service_name, service_path):
    """Build a Python service."""
    print(f"Setting up {service_name}...")
    
    # Change to the service directory
    original_cwd = Path.cwd()
    os.chdir(service_path)
    
    try:
        # Install dependencies
        print(f"  Installing dependencies for {service_name}...")
        result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  Warning: Failed to install dependencies: {result.stderr}")
        
        print(f"  Successfully set up {service_name}")
        return True
        
    finally:
        # Restore original directory
        os.chdir(original_cwd)

def main():
    """Main function to build all Go services."""
    # Get the go-services directory
    script_dir = Path(__file__).parent.absolute()
    go_services_dir = script_dir
    
    print("Initializing and building all FlashFlow services...")
    print(f"Working directory: {go_services_dir}")
    
    # Services to build
    services = [
        ("build-service", go_services_dir / "build-service"),
        ("dev-server", go_services_dir / "dev-server"),
        ("file-watcher", go_services_dir / "file-watcher"),
        ("cli-wrapper", go_services_dir / "cli-wrapper"),
        ("direct-renderer", go_services_dir / "direct-renderer")
    ]
    
    # Python services
    python_services = [
        ("flet-direct-renderer", go_services_dir.parent / "python-services" / "flet-direct-renderer")
    ]
    
    success_count = 0
    
    for service_name, service_path in services:
        if not service_path.exists():
            print(f"Service directory not found: {service_path}")
            continue
            
        if build_go_service(service_name, service_path):
            success_count += 1
        print()  # Add a blank line for readability
    
    for service_name, service_path in python_services:
        if not service_path.exists():
            print(f"Python service directory not found: {service_path}")
            continue
            
        if build_python_service(service_name, service_path):
            success_count += 1
        print()  # Add a blank line for readability
    
    print(f"Build process completed! {success_count}/{len(services) + len(python_services)} services set up successfully.")

if __name__ == "__main__":
    main()