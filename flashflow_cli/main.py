#!/usr/bin/env python3
"""
FlashFlow CLI - Main entry point
"""

import click
from flashflow_cli.commands.build import build
from flashflow_cli.commands.serve import serve
from flashflow_cli.commands.new import new
from flashflow_cli.commands.test import test
from flashflow_cli.commands.install import install
from flashflow_cli.commands.deploy import deploy
from flashflow_cli.commands.custom import custom
from flashflow_cli.commands.theme import theme
from flashflow_cli.commands.demo_form import demo_form

import os
import sys
from pathlib import Path

from .commands import new, install, build, serve, test, deploy, migrate, setup, custom
from .core import FlashFlowProject
from .__init__ import __version__

# DEPRECATED: This module has been moved to cli/core/main.py
# This stub will be removed in a future version
import warnings
warnings.warn("flashflow_cli.main is deprecated, use cli.core.main instead", DeprecationWarning, stacklevel=2)

from cli.core.main import *

@click.group()
def cli():
    """FlashFlow CLI - A full-stack framework for building cross-platform applications"""
    pass

cli.add_command(build)
cli.add_command(serve)
cli.add_command(new)
cli.add_command(test)
cli.add_command(install)
cli.add_command(deploy)
cli.add_command(custom)
cli.add_command(theme)
cli.add_command(demo_form)

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