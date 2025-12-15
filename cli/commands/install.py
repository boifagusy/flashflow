"""
FlashFlow 'install' command - Install dependencies and setup
"""

import click
import subprocess
import sys
import os
from pathlib import Path
import json
import re

@click.command()
@click.argument('target', default='core')
@click.option('--force', '-f', is_flag=True, help='Force reinstallation')
@click.option('--editor', default='vscode', help='Editor for install-editor (vscode, vim, emacs)')
@click.option('--version', '-v', help='Specify package version')
@click.option('--save', is_flag=True, help='Save package to dependencies in flashflow.json')
@click.option('--dev', is_flag=True, help='Install as development dependency')
def install(target, force, editor, version, save, dev):
    """Install FlashFlow dependencies and tools"""
    
    if target == "core":
        install_core_dependencies(force)
    elif target == "editor":
        install_editor_extension(editor, force)
    elif target == "dev":
        install_dev_dependencies(force)
    elif target == "all":
        install_all_dependencies(force)
    else:
        # Try to install as a specific package
        install_specific_package(target, force, version, save, dev)

def install_core_dependencies(force=False):
    """Install core FlashFlow dependencies"""
    
    click.echo("🚀 Installing FlashFlow core dependencies...")
    
    # Check if we're in a FlashFlow project
    if not Path("flashflow.json").exists():
        click.echo("❌ Not in a FlashFlow project directory")
        click.echo("Run 'flashflow new <project_name>' to create a new project first")
        return
    
    # Python dependencies for FlashFlow CLI
    python_deps = [
        "click>=8.0.0",
        "pyyaml>=6.0",
        "jinja2>=3.0.0",
        "requests>=2.28.0",
        "watchdog>=2.1.0",
        "flask>=2.0.0",
        "flask-cors>=4.0.0"
    ]
    
    # Node.js dependencies for frontend generation
    node_deps = [
        "vite",
        "react",
        "react-dom",
        "@types/react",
        "@types/react-dom",
        "typescript",
        "@vitejs/plugin-react"
    ]
    
    try:
        # Install Python dependencies using flashflow install
        click.echo("📦 Installing Python dependencies...")
        for dep in python_deps:
            try:
                # Hide the actual pip install command and show a user-friendly message
                click.echo(f"   ✅ Installing {dep}...")
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", dep
                ], capture_output=True, text=True, check=True)
                click.echo(f"   ✅ {dep} installed successfully")
            except subprocess.CalledProcessError as e:
                click.echo(f"   ❌ Failed to install {dep}")
        
        # Check if Node.js is available
        try:
            result = subprocess.run(["node", "--version"], capture_output=True, text=True, check=True)
            node_version = result.stdout.strip()
            click.echo(f"📦 Found Node.js {node_version}")
            
            # Initialize package.json if it doesn't exist
            if not Path("package.json").exists():
                click.echo("📦 Initializing package.json...")
                package_json = {
                    "name": "flashflow-frontend",
                    "version": "0.1.0",
                    "type": "module",
                    "scripts": {
                        "dev": "vite",
                        "build": "vite build",
                        "preview": "vite preview"
                    },
                    "dependencies": {},
                    "devDependencies": {}
                }
                
                import json
                with open("package.json", "w") as f:
                    json.dump(package_json, f, indent=2)
            
            # Install Node.js dependencies using flashflow install
            click.echo("📦 Installing Node.js dependencies...")
            npm_cmd = "npm"
            if os.name == 'nt':  # Windows
                npm_cmd = "npm.cmd"
            
            for dep in node_deps:
                try:
                    # Hide the actual npm install command and show a user-friendly message
                    click.echo(f"   ✅ Installing {dep}...")
                    result = subprocess.run([
                        npm_cmd, "install", dep
                    ], capture_output=True, text=True, check=True)
                    click.echo(f"   ✅ {dep} installed successfully")
                except subprocess.CalledProcessError as e:
                    click.echo(f"   ❌ Failed to install {dep}")
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            click.echo("⚠️  Node.js not found. Frontend generation will be limited.")
            click.echo("   Install Node.js from https://nodejs.org to enable full functionality")
        
        # Create necessary directories
        dirs_to_create = [
            "dist/backend",
            "dist/frontend", 
            "dist/mobile",
            "database",
            "storage/logs",
            "storage/cache"
        ]
        
        for dir_path in dirs_to_create:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
        
        # Create .env file from .env.example if it doesn't exist
        if Path(".env.example").exists() and not Path(".env").exists():
            click.echo("🔧 Creating .env file from template...")
            import shutil
            shutil.copy(".env.example", ".env")
            click.echo("   ✅ Created .env file (please update with your configuration)")
        
        click.echo("\n✅ FlashFlow core dependencies installed successfully!")
        click.echo("\n🎯 Next steps:")
        click.echo("   flashflow build      # Generate application code")
        click.echo("   flashflow serve --all # Start development server")
        
    except Exception as e:
        click.echo(f"❌ Error installing dependencies: {str(e)}")

def install_dev_dependencies(force=False):
    """Install development dependencies"""
    
    click.echo("🚀 Installing FlashFlow development dependencies...")
    
    # Development dependencies
    dev_deps = [
        "pytest>=6.0.0",
        "pytest-cov>=2.10.0",
        "pytest-mock>=3.3.1",
        "flake8>=3.8.3",
        "black>=21.0.0",
        "mypy>=0.812",
        "sphinx>=4.0.0",
        "mkdocs>=1.2.0"
    ]
    
    try:
        click.echo("📦 Installing development dependencies...")
        for dep in dev_deps:
            try:
                click.echo(f"   ✅ Installing {dep}...")
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", dep
                ], capture_output=True, text=True, check=True)
                click.echo(f"   ✅ {dep} installed successfully")
            except subprocess.CalledProcessError as e:
                click.echo(f"   ❌ Failed to install {dep}")
        
        click.echo("\n✅ FlashFlow development dependencies installed successfully!")
        
    except Exception as e:
        click.echo(f"❌ Error installing development dependencies: {str(e)}")

def install_all_dependencies(force=False):
    """Install all dependencies (core + dev)"""
    
    click.echo("🚀 Installing all FlashFlow dependencies...")
    
    # Install core dependencies
    install_core_dependencies(force)
    
    # Install development dependencies
    install_dev_dependencies(force)
    
    click.echo("\n✅ All FlashFlow dependencies installed successfully!")

def install_specific_package(package_name, force=False, version=None, save=False, dev=False):
    """Install a specific package"""
    
    click.echo(f"🚀 Installing package: {package_name}")
    
    # Map of common packages to their actual names
    package_mapping = {
        "pytest": "pytest>=6.0.0",
        "pytest-cov": "pytest-cov>=2.10.0",
        "pytest-mock": "pytest-mock>=3.3.1",
        "flake8": "flake8>=3.8.3",
        "black": "black>=21.0.0",
        "mypy": "mypy>=0.812",
        "sphinx": "sphinx>=4.0.0",
        "mkdocs": "mkdocs>=1.2.0",
        "requests": "requests>=2.28.0",
        "click": "click>=8.0.0",
        "pyyaml": "pyyaml>=6.0",
        "jinja2": "jinja2>=3.0.0",
        "watchdog": "watchdog>=2.1.0",
        "flask": "flask>=2.0.0",
        "flask-cors": "flask-cors>=4.0.0",
        "pillow": "pillow>=8.0.0",
        "qrcode": "qrcode[pil]>=7.0.0",
        "pytesseract": "pytesseract>=0.3.8",
        "easyocr": "easyocr>=1.4.0",
        "pyzbar": "pyzbar>=0.1.8",
        "opencv-python": "opencv-python>=4.5.0",
        "SpeechRecognition": "SpeechRecognition>=3.8.1",
        "pyaudio": "pyaudio>=0.2.11",
        "openai-whisper": "openai-whisper>=2023.0.0",
        "pre-commit": "pre-commit>=2.15.0",
        "numpy": "numpy>=1.21.0",
        "pandas": "pandas>=1.3.0",
        "matplotlib": "matplotlib>=3.4.0",
        "seaborn": "seaborn>=0.11.0",
        "scikit-learn": "scikit-learn>=1.0.0",
        "tensorflow": "tensorflow>=2.6.0",
        "torch": "torch>=1.9.0",
        "fastapi": "fastapi>=0.68.0",
        "uvicorn": "uvicorn>=0.15.0",
        "sqlalchemy": "sqlalchemy>=1.4.0",
        "psycopg2": "psycopg2>=2.9.0",
        "pymongo": "pymongo>=4.0.0",
        "redis": "redis>=4.0.0",
        "celery": "celery>=5.2.0",
        "docker": "docker>=5.0.0",
        "kubernetes": "kubernetes>=20.0.0"
    }
    
    # Handle version specification
    if version:
        # If version is specified, use it
        actual_package = f"{package_name}=={version}" if not re.match(r'[>=<~]', version) else f"{package_name}{version}"
    else:
        # Get the actual package name from mapping or use as is
        actual_package = package_mapping.get(package_name, package_name)
    
    try:
        click.echo(f"   ✅ Installing {actual_package}...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", actual_package
        ], capture_output=True, text=True, check=True)
        click.echo(f"   ✅ {actual_package} installed successfully")
        
        # Save to flashflow.json if requested
        if save:
            save_package_to_config(package_name, version, dev)
        
    except subprocess.CalledProcessError as e:
        click.echo(f"   ❌ Failed to install {actual_package}")
        click.echo(f"   Error: {e.stderr}")
    except Exception as e:
        click.echo(f"❌ Error installing package {package_name}: {str(e)}")

def save_package_to_config(package_name, version=None, dev=False):
    """Save package to flashflow.json dependencies"""
    
    try:
        # Read current config
        if Path("flashflow.json").exists():
            with open("flashflow.json", "r") as f:
                config = json.load(f)
        else:
            config = {}
        
        # Initialize dependencies section if not exists
        if "dependencies" not in config:
            config["dependencies"] = {}
        if "devDependencies" not in config:
            config["devDependencies"] = {}
        
        # Determine target section
        target_section = "devDependencies" if dev else "dependencies"
        
        # Add package with version
        if version:
            config[target_section][package_name] = version
        else:
            # Try to get installed version
            try:
                result = subprocess.run([
                    sys.executable, "-m", "pip", "show", package_name
                ], capture_output=True, text=True, check=True)
                
                # Parse version from pip show output
                for line in result.stdout.split('\n'):
                    if line.startswith('Version:'):
                        installed_version = line.split(':', 1)[1].strip()
                        config[target_section][package_name] = installed_version
                        break
                else:
                    config[target_section][package_name] = "*"
            except:
                config[target_section][package_name] = "*"
        
        # Write back to file
        with open("flashflow.json", "w") as f:
            json.dump(config, f, indent=2)
        
        click.echo(f"   💾 Saved {package_name} to {target_section} in flashflow.json")
        
    except Exception as e:
        click.echo(f"   ⚠️  Failed to save package to config: {str(e)}")

def install_editor_extension(editor: str = 'vscode', force: bool = False):
    """Install FlashFlow editor extension"""
    
    click.echo(f"🎨 Installing FlashFlow editor extension for {editor}...")
    
    if editor.lower() == 'vscode':
        install_vscode_extension(force)
    elif editor.lower() == 'vim':
        install_vim_extension(force)
    elif editor.lower() == 'emacs':
        install_emacs_extension(force)
    else:
        click.echo(f"❌ Unsupported editor: {editor}")
        click.echo("Supported editors: vscode, vim, emacs")
    
    click.echo("🔧 Installing FlashFlow editor extension...")
    
    # This would install VSCode extension, language server, etc.
    # For now, we'll create a simple syntax highlighting file
    
    try:
        # Create basic .flow syntax definition for common editors
        vscode_dir = Path.home() / ".vscode" / "extensions" / "flashflow-syntax"
        vscode_dir.mkdir(parents=True, exist_ok=True)
        
        # VSCode extension manifest
        extension_manifest = {
            "name": "flashflow-syntax",
            "displayName": "FlashFlow Syntax",
            "description": "Syntax highlighting for .flow files",
            "version": "0.1.0",
            "engines": {
                "vscode": "^1.60.0"
            },
            "categories": ["Programming Languages"],
            "contributes": {
                "languages": [{
                    "id": "flashflow",
                    "aliases": ["FlashFlow", "flow"],
                    "extensions": [".flow", ".testflow"],
                    "configuration": "./language-configuration.json"
                }],
                "grammars": [{
                    "language": "flashflow",
                    "scopeName": "source.flow",
                    "path": "./syntaxes/flow.tmLanguage.json"
                }]
            }
        }
        
        import json
        with open(vscode_dir / "package.json", "w") as f:
            json.dump(extension_manifest, f, indent=2)
        
        # Basic language configuration
        lang_config = {
            "comments": {
                "lineComment": "#"
            },
            "brackets": [
                ["{", "}"],
                ["[", "]"],
                ["(", ")"]
            ],
            "autoClosingPairs": [
                ["{", "}"],
                ["[", "]"],
                ["(", ")"],
                ["\"", "\""],
                ["'", "'"]
            ]
        }
        
        with open(vscode_dir / "language-configuration.json", "w") as f:
            json.dump(lang_config, f, indent=2)
        
        # Create syntaxes directory
        syntaxes_dir = vscode_dir / "syntaxes"
        syntaxes_dir.mkdir(exist_ok=True)
        
        # Basic TextMate grammar
        grammar = {
            "$schema": "https://raw.githubusercontent.com/martinring/tmlanguage/master/tmlanguage.json",
            "name": "FlashFlow",
            "patterns": [
                {
                    "include": "#keywords"
                },
                {
                    "include": "#strings"
                },
                {
                    "include": "#comments"
                }
            ],
            "repository": {
                "keywords": {
                    "patterns": [{
                        "name": "keyword.control.flow",
                        "match": "\\b(model|page|endpoint|authentication|component|theme|test)\\b"
                    }]
                },
                "strings": {
                    "name": "string.quoted.double.flow",
                    "begin": "\"",
                    "end": "\"",
                    "patterns": [{
                        "name": "constant.character.escape.flow",
                        "match": "\\\\."
                    }]
                },
                "comments": {
                    "patterns": [{
                        "name": "comment.line.number-sign.flow",
                        "match": "#.*$"
                    }]
                }
            },
            "scopeName": "source.flow"
        }
        
        with open(syntaxes_dir / "flow.tmLanguage.json", "w") as f:
            json.dump(grammar, f, indent=2)
        
        click.echo("✅ FlashFlow editor extension installed!")
        click.echo("   Restart VS Code to enable .flow syntax highlighting")
        
    except Exception as e:
        click.echo(f"❌ Error installing editor extension: {str(e)}")

def install_vim_extension(force: bool = False):
    """Install Vim extension for FlashFlow"""
    
    click.echo("🔧 Installing Vim FlashFlow extension...")
    
    vim_dir = Path.home() / ".vim"
    if not vim_dir.exists():
        click.echo("❌ Vim configuration directory not found")
        click.echo("Please ensure Vim is installed and ~/.vim directory exists")
        return
    
    try:
        # Create syntax directory
        syntax_dir = vim_dir / "syntax"
        syntax_dir.mkdir(exist_ok=True)
        
        # Create FlashFlow syntax file
        vim_syntax = '''" Vim syntax file
" Language: FlashFlow
" Maintainer: FlashFlow Team
" Latest Revision: 2024

if exists("b:current_syntax")
  finish
endif

" Keywords
syn keyword flowKeyword model page endpoint authentication theme component fields methods handler action liveflow jobflow
syn keyword flowType string integer float boolean date datetime timestamp text json password email url enum

" Comments
syn match flowComment "#.*$"

" Strings
syn region flowString start='"' end='"'

" Highlighting
hi def link flowKeyword Keyword
hi def link flowType Type
hi def link flowComment Comment
hi def link flowString String

let b:current_syntax = "flashflow"
'''
        
        with open(syntax_dir / "flashflow.vim", 'w') as f:
            f.write(vim_syntax)
        
        # Create filetype detection
        ftdetect_dir = vim_dir / "ftdetect"
        ftdetect_dir.mkdir(exist_ok=True)
        
        with open(ftdetect_dir / "flashflow.vim", 'w') as f:
            f.write('au BufRead,BufNewFile *.flow,*.liveflow,*.jobflow,*.testflow set filetype=flashflow\n')
        
        click.echo("   ✅ Vim syntax files installed")
        click.echo("   📝 Restart Vim to activate FlashFlow syntax highlighting")
    
    except Exception as e:
        click.echo(f"❌ Error installing Vim extension: {str(e)}")

def install_emacs_extension(force: bool = False):
    """Install Emacs extension for FlashFlow"""
    
    click.echo("🔧 Installing Emacs FlashFlow extension...")
    
    emacs_dir = Path.home() / ".emacs.d"
    if not emacs_dir.exists():
        click.echo("❌ Emacs configuration directory not found")
        click.echo("Please ensure Emacs is installed and ~/.emacs.d directory exists")
        return
    
    try:
        # Create FlashFlow mode file
        elisp_code = ''';;; flashflow-mode.el --- Major mode for FlashFlow files

;;; Commentary:
;; Major mode for editing FlashFlow .flow files

;;; Code:

(defvar flashflow-mode-keywords
  '(("\\\\b\\\\(model\\\\|page\\\\|endpoint\\\\|authentication\\\\|theme\\\\|component\\\\|fields\\\\|methods\\\\|handler\\\\|action\\\\|liveflow\\\\|jobflow\\\\)\\\\b" . font-lock-keyword-face)
    ("\\\\b\\\\(string\\\\|integer\\\\|float\\\\|boolean\\\\|date\\\\|datetime\\\\|timestamp\\\\|text\\\\|json\\\\|password\\\\|email\\\\|url\\\\|enum\\\\)\\\\b" . font-lock-type-face)
    ("#.*" . font-lock-comment-face)
    ("\\\\".*\\\\"" . font-lock-string-face)))

(define-derived-mode flashflow-mode yaml-mode "FlashFlow"
  "Major mode for editing FlashFlow files."
  (setq font-lock-defaults '((flashflow-mode-keywords))))

(add-to-list 'auto-mode-alist '("\\\\.flow\\\\'" . flashflow-mode))
(add-to-list 'auto-mode-alist '("\\\\.liveflow\\\\'" . flashflow-mode))
(add-to-list 'auto-mode-alist '("\\\\.jobflow\\\\'" . flashflow-mode))
(add-to-list 'auto-mode-alist '("\\\\.testflow\\\\'" . flashflow-mode))

(provide 'flashflow-mode)
;;; flashflow-mode.el ends here
'''
        
        with open(emacs_dir / "flashflow-mode.el", 'w') as f:
            f.write(elisp_code)
        
        click.echo("   ✅ Emacs mode file installed")
        click.echo("   📝 Add (require 'flashflow-mode) to your .emacs or init.el")
        click.echo("   🔄 Restart Emacs to activate FlashFlow mode")
    
    except Exception as e:
        click.echo(f"❌ Error installing Emacs extension: {str(e)}")