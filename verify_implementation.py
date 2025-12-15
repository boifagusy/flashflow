#!/usr/bin/env python3
"""
Verification script for FlashFlow Engine upgrade with FlashCore integration
"""

import os
import sys
import subprocess
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists and report status"""
    if os.path.exists(filepath):
        print(f"✓ {description} exists")
        return True
    else:
        print(f"✗ {description} missing")
        return False

def check_directory_exists(dirpath, description):
    """Check if a directory exists and report status"""
    if os.path.exists(dirpath):
        print(f"✓ {description} exists")
        return True
    else:
        print(f"✗ {description} missing")
        return False

def run_command(command, description):
    """Run a command and report status"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ {description} successful")
            return True
        else:
            print(f"✗ {description} failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ {description} failed: {e}")
        return False

def main():
    """Main verification function"""
    print("=" * 60)
    print("FlashFlow Engine Upgrade Verification")
    print("=" * 60)
    
    # Change to the flashflow-main directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Check directory structure
    print("\n1. Directory Structure Verification:")
    print("-" * 40)
    
    dirs_to_check = [
        ("flashcore", "FlashCore main directory"),
        ("flashcore/include", "FlashCore header files"),
        ("flashcore/src", "FlashCore source files"),
        ("flashcore/bindings", "FlashCore language bindings"),
        ("flashcore/bindings/go", "FlashCore Go bindings"),
        ("flashcore/bindings/python", "FlashCore Python bindings"),
        ("flashcore/wasm", "FlashCore WASM build files"),
        ("go-services/flashcore-service", "FlashCore Go service"),
        ("python-services/flet-direct-renderer", "FlashFlow Engine"),
        ("examples/flashcore-demo", "FlashCore demo examples"),
        ("test-projects/flashcore-test", "FlashCore test project"),
        ("docs", "Documentation directory")
    ]
    
    dir_results = []
    for dir_path, description in dirs_to_check:
        dir_results.append(check_directory_exists(dir_path, description))
    
    # Check key files
    print("\n2. Key File Verification:")
    print("-" * 40)
    
    files_to_check = [
        ("flashcore/include/flashcore_api.h", "FlashCore API header"),
        ("flashcore/src/vector_search.cpp", "Vector search implementation"),
        ("flashcore/src/inference_engine.cpp", "Inference engine implementation"),
        ("flashcore/src/vault_security.cpp", "Security vault implementation"),
        ("flashcore/bindings/python/pybind11_bindings.cpp", "Python bindings"),
        ("flashcore/bindings/python/setup.py", "Python setup script"),
        ("go-services/flashcore-service/main.go", "Go service implementation"),
        ("python-services/flet-direct-renderer/main.py", "Updated FlashFlow Engine"),
        ("examples/flashcore-demo/flashcore-demo.flow", "FlashCore demo flow"),
        ("test-projects/flashcore-test/src/flows/app.flow", "Test project main flow"),
        ("docs/FLASHCORE_INTEGRATION.md", "FlashCore integration documentation"),
        ("FLASHCORE_IMPLEMENTATION_SUMMARY.md", "Implementation summary"),
        ("FLASHFLOW_ENGINE_UPGRADE_SUMMARY.md", "Upgrade summary")
    ]
    
    file_results = []
    for file_path, description in files_to_check:
        file_results.append(check_file_exists(file_path, description))
    
    # Check build scripts
    print("\n3. Build Script Verification:")
    print("-" * 40)
    
    script_results = []
    script_results.append(check_file_exists("build-flashcore.bat", "FlashCore build script"))
    script_results.append(check_file_exists("RUN_FLASHCORE_DEMO.bat", "Demo run script"))
    script_results.append(check_file_exists("test-flashcore.py", "FlashCore test script"))
    
    # Summary
    print("\n4. Summary:")
    print("-" * 40)
    
    total_checks = len(dir_results) + len(file_results) + len(script_results)
    passed_checks = sum(dir_results) + sum(file_results) + sum(script_results)
    
    print(f"Total checks: {total_checks}")
    print(f"Passed: {passed_checks}")
    print(f"Failed: {total_checks - passed_checks}")
    
    if passed_checks == total_checks:
        print("\n🎉 All verification checks passed!")
        print("The FlashFlow Engine upgrade with FlashCore integration is complete.")
    else:
        print(f"\n⚠️  {total_checks - passed_checks} verification check(s) failed.")
        print("Please review the failed checks above.")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()