# Making FlashFlow Available System-Wide

This guide explains how to install FlashFlow globally on your system so that any user can access it from any directory.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Installation Methods](#installation-methods)
   - [Method 1: Using pip (Recommended)](#method-1-using-pip-recommended)
   - [Method 2: Automated Installation Scripts](#method-2-automated-installation-scripts)
   - [Method 3: Direct Installation](#method-3-direct-installation)
   - [Method 4: Creating a System-wide Script](#method-4-creating-a-system-wide-script)
4. [Verification](#verification)
5. [Usage](#usage)
6. [Troubleshooting](#troubleshooting)
7. [Uninstallation](#uninstallation)

## Overview

FlashFlow can be made available system-wide through several methods. The recommended approach is using pip for installation, which automatically handles PATH configuration and makes the `flashflow` command available globally.

## Prerequisites

Before installing FlashFlow system-wide, ensure you have:

1. **Python 3.8 or higher** installed on your system
2. **pip** (Python package installer)
3. **Git** (for cloning the repository)
4. **Node.js** (optional, for frontend development)
5. **Administrative privileges** (for system-wide installation)

### Checking Prerequisites

```bash
# Check Python version
python --version
# or
python3 --version

# Check pip
pip --version
# or
pip3 --version

# Check Git
git --version
```

## Installation Methods

### Method 1: Using pip (Recommended)

This is the easiest and most reliable method for making FlashFlow available system-wide.

#### For Development/Testing

If you want to install FlashFlow in development mode (changes to the source code will be reflected immediately):

```bash
# Clone the repository
git clone https://github.com/yourusername/flashflow.git
cd flashflow

# Install in development mode
pip install -e .
```

#### For Production Use

To install FlashFlow as a regular Python package:

```bash
# Clone the repository
git clone https://github.com/yourusername/flashflow.git
cd flashflow

# Install as a package
pip install .
```

#### For All Users (System-wide)

To make FlashFlow available to all users on the system:

```bash
# Clone the repository
git clone https://github.com/yourusername/flashflow.git
cd flashflow

# Install as a package for all users (requires admin privileges)
sudo pip install .
```

On Windows, run Command Prompt or PowerShell as Administrator:

```cmd
# Clone the repository
git clone https://github.com/yourusername/flashflow.git
cd flashflow

# Install as a package for all users
pip install .
```

### Method 2: Automated Installation Scripts

FlashFlow includes automated installation scripts that simplify the installation process.

#### For Windows

Use the [install_flashflow_windows.bat](file://c:\Users\VineMaster\Desktop\flashflow\install_flashflow_windows.bat) script:

1. Right-click on [install_flashflow_windows.bat](file://c:\Users\VineMaster\Desktop\flashflow\install_flashflow_windows.bat)
2. Select "Run as administrator"
3. Follow the prompts

The script will:
- Check prerequisites
- Clone the FlashFlow repository
- Install FlashFlow system-wide
- Create a system-wide batch script

#### For Linux/macOS

Use the [install_flashflow.sh](file://c:\Users\VineMaster\Desktop\flashflow\install_flashflow.sh) script:

```bash
# Make the script executable
chmod +x install_flashflow.sh

# For system-wide installation (requires sudo)
sudo ./install_flashflow.sh

# For user-only installation
./install_flashflow.sh
```

The script will:
- Check prerequisites
- Clone the FlashFlow repository
- Install FlashFlow
- Create a system-wide script
- Add to PATH if needed

### Method 3: Direct Installation

If you prefer to manually install FlashFlow:

#### 1. Clone the Repository

```bash
# Choose a location for installation (e.g., /opt/flashflow or C:\Program Files\FlashFlow)
git clone https://github.com/yourusername/flashflow.git /opt/flashflow
```

#### 2. Install Dependencies

```bash
cd /opt/flashflow
pip install -r requirements.txt
```

If there's no requirements.txt file, install the dependencies manually:

```bash
pip install click pyyaml jinja2 requests watchdog flask flask-cors
```

#### 3. Create a System-wide Script

Create a script that can be accessed from anywhere:

**On Linux/macOS:**

```bash
# Create a script in a directory that's in PATH
sudo nano /usr/local/bin/flashflow

# Add the following content:
#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, '/opt/flashflow')
from flashflow_cli.main import main
if __name__ == '__main__':
    main()

# Make it executable
sudo chmod +x /usr/local/bin/flashflow
```

**On Windows:**

Create a batch file `flashflow.bat` in a directory that's in your PATH:

```batch
@echo off
python "C:\Program Files\FlashFlow\flashflow_cli\main.py" %*
```

### Method 4: Creating a System-wide Script

This method involves creating a wrapper script that can be placed in a system PATH directory.

#### 1. Determine Your PATH

**On Linux/macOS:**
```bash
echo $PATH
```

**On Windows (PowerShell):**
```powershell
$env:PATH
```

#### 2. Create the Wrapper Script

**On Linux/macOS:**

Create a script in `/usr/local/bin` (or another directory in your PATH):

```bash
sudo nano /usr/local/bin/flashflow
```

Add the following content:

```python
#!/usr/bin/env python3
"""
FlashFlow CLI Wrapper Script
"""

import sys
import os

# Add the FlashFlow installation directory to Python path
# Modify this path to match your FlashFlow installation
FLASHFLOW_PATH = "/opt/flashflow"  # Change this to your installation path

if os.path.exists(FLASHFLOW_PATH):
    sys.path.insert(0, FLASHFLOW_PATH)
    
    try:
        from flashflow_cli.main import main
        if __name__ == '__main__':
            main()
    except ImportError as e:
        print(f"Error importing FlashFlow: {e}")
        print("Please check your installation path.")
        sys.exit(1)
else:
    print(f"FlashFlow installation not found at {FLASHFLOW_PATH}")
    print("Please update the FLASHFLOW_PATH in this script.")
    sys.exit(1)
```

Make the script executable:

```bash
sudo chmod +x /usr/local/bin/flashflow
```

**On Windows:**

Create a PowerShell script `flashflow.ps1` in a directory that's in your PATH:

```powershell
# FlashFlow CLI Wrapper Script

# Modify this path to match your FlashFlow installation
$FLASHFLOW_PATH = "C:\Program Files\FlashFlow"

if (Test-Path $FLASHFLOW_PATH) {
    $env:PYTHONPATH = "$FLASHFLOW_PATH;$env:PYTHONPATH"
    
    try {
        python "$FLASHFLOW_PATH\flashflow_cli\main.py" @args
    }
    catch {
        Write-Host "Error running FlashFlow: $_"
        Write-Host "Please check your installation path."
        exit 1
    }
}
else {
    Write-Host "FlashFlow installation not found at $FLASHFLOW_PATH"
    Write-Host "Please update the FLASHFLOW_PATH in this script."
    exit 1
}
```

## Verification

After installation, verify that FlashFlow is available system-wide:

```bash
# Check if flashflow command is available
flashflow --version

# If using the PowerShell script on Windows
flashflow.ps1 --version
```

You should see output similar to:

```
FlashFlow CLI version 0.1.0
```

## Usage

Once installed system-wide, FlashFlow can be used from any directory:

```bash
# Create a new project from anywhere
flashflow new my-awesome-app

# Navigate to the project
cd my-awesome-app

# Install dependencies
flashflow install core

# Build the application
flashflow build

# Start the development server
flashflow serve --all
```

## Troubleshooting

### Common Issues and Solutions

#### 1. "Command not found" Error

**Problem:** The `flashflow` command is not recognized.

**Solution:**
- Ensure the installation directory is in your PATH
- Restart your terminal/command prompt
- On Windows, try using the full path to the script

#### 2. Permission Denied

**Problem:** You get permission errors during installation.

**Solution:**
- On Linux/macOS, use `sudo` for system-wide installation
- On Windows, run Command Prompt/PowerShell as Administrator

#### 3. Python Path Issues

**Problem:** Python cannot find FlashFlow modules.

**Solution:**
- Verify the installation path in your wrapper script
- Ensure all dependencies are installed
- Check that Python can import the flashflow_cli module

#### 4. PATH Not Updated

**Problem:** The command works in one terminal session but not in others.

**Solution:**
- Add the script directory to your system PATH permanently
- On Linux/macOS, add to `~/.bashrc` or `~/.zshrc`
- On Windows, add to System Environment Variables

### Adding to PATH Permanently

**On Linux/macOS:**

Add to your shell configuration file (`~/.bashrc`, `~/.zshrc`, etc.):

```bash
export PATH="/usr/local/bin:$PATH"
```

Then reload your shell configuration:

```bash
source ~/.bashrc
# or
source ~/.zshrc
```

**On Windows:**

1. Open System Properties
2. Click "Environment Variables"
3. Under "System Variables", find and select "Path", then click "Edit"
4. Click "New" and add the directory containing your flashflow script
5. Click "OK" to save

## Uninstallation

### If Installed with pip

```bash
# Uninstall the package
pip uninstall flashflow-cli
```

### Manual Uninstallation

1. Remove the FlashFlow directory:
   ```bash
   # On Linux/macOS
   sudo rm -rf /opt/flashflow
   
   # On Windows
   rmdir /s "C:\Program Files\FlashFlow"
   ```

2. Remove the wrapper script:
   ```bash
   # On Linux/macOS
   sudo rm /usr/local/bin/flashflow
   
   # On Windows, remove from PATH and delete the script file
   ```

3. Remove any added PATH entries

## Best Practices

### 1. Use Virtual Environments

For development, consider using virtual environments to avoid conflicts:

```bash
# Create a virtual environment
python -m venv flashflow-env

# Activate it
# On Linux/macOS:
source flashflow-env/bin/activate
# On Windows:
flashflow-env\Scripts\activate

# Install FlashFlow
pip install -e .

# Deactivate when done
deactivate
```

### 2. Keep FlashFlow Updated

Regularly update FlashFlow to get the latest features and bug fixes:

```bash
# If installed in development mode
cd /path/to/flashflow
git pull origin main

# If installed as a package
pip install --upgrade flashflow-cli
```

### 3. System-wide vs User Installation

Consider installing for your user only instead of system-wide:

```bash
# Install for current user only
pip install --user .
```

This avoids the need for administrative privileges and keeps the installation user-specific.

### 4. Multiple Versions

If you need multiple versions of FlashFlow:

1. Use virtual environments for different projects
2. Install different versions in different virtual environments
3. Use tools like `pyenv` to manage Python versions

## Advanced Configuration

### Custom Installation Directory

You can install FlashFlow to a custom directory:

```bash
# Clone to custom location
git clone https://github.com/yourusername/flashflow.git /custom/path/flashflow

# Install from custom location
cd /custom/path/flashflow
pip install .
```

### Environment Variables

FlashFlow may use environment variables for configuration. You can set them system-wide:

**On Linux/macOS:**
Add to `~/.bashrc` or `/etc/environment`:
```bash
export FLASHFLOW_HOME="/opt/flashflow"
```

**On Windows:**
Add to System Environment Variables through System Properties.

## Conclusion

By following these instructions, you can make FlashFlow available system-wide on any PC, allowing all users to access it from any directory. The pip installation method is recommended for most users as it handles PATH configuration automatically and provides easy updates and uninstallation.

Remember to:
1. Choose the installation method that best fits your needs
2. Verify the installation works correctly
3. Keep FlashFlow updated for the latest features
4. Follow security best practices when installing system-wide