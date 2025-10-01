#!/usr/bin/env python3
"""
FlashFlow CLI - Main entry point
"""

import click
import os
import sys
from pathlib import Path

from .commands import new, install, build, serve, test, deploy, migrate, setup
from .core import FlashFlowProject
from .__init__ import __version__

@click.group()
@click.version_option(__version__)
@click.pass_context
def cli(ctx):
    """
    FlashFlow - Single-syntax full-stack framework
    
    Build complete applications with landing pages, mobile apps, 
    backend APIs, and databases from a single .flow file.
    """
    ctx.ensure_object(dict)
    
    # Find project root
    current_dir = Path.cwd()
    project_root = None
    
    for parent in [current_dir] + list(current_dir.parents):
        if (parent / "flashflow.json").exists():
            project_root = parent
            break
    
    ctx.obj['project_root'] = project_root
    ctx.obj['current_dir'] = current_dir

# Register commands
cli.add_command(new.new)
cli.add_command(install.install)
cli.add_command(build.build)
cli.add_command(serve.serve)
cli.add_command(test.test)
cli.add_command(deploy.deploy)
cli.add_command(migrate.migrate)
cli.add_command(setup.setup)

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