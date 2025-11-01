#!/usr/bin/env python3
"""
FlashFlow CLI - Main entry point
"""

import click
import os
import sys
from pathlib import Path

# Import commands from cli (new structure)
from cli.commands import build, serve, new, test, install, deploy, custom, theme

# Import commands from flashflow_cli (legacy structure)
from flashflow_cli.commands.demo_form import demo_form
from flashflow_cli.commands.demo_slider import demo_slider

# DEPRECATED: This module has been moved to cli/core/main.py
# This stub will be removed in a future version
import warnings
warnings.warn("flashflow_cli.main is deprecated, use cli.core.main instead", DeprecationWarning, stacklevel=2)

from cli.core.main import *

@click.group()
def cli():
    """FlashFlow CLI - A full-stack framework for building cross-platform applications"""
    pass

# Register commands
cli.add_command(build.build)
cli.add_command(serve.serve)
cli.add_command(new.new)
cli.add_command(test.test)
cli.add_command(install.install)
cli.add_command(deploy.deploy)
cli.add_command(custom.custom)
cli.add_command(theme.theme)
cli.add_command(demo_form)
cli.add_command(demo_slider)

def main():
    """Main entry point for the CLI"""
    try:
        cli()
    except KeyboardInterrupt:
        click.echo("\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)

if __name__ == "__main__":
    main()