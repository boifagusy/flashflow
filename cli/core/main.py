#!/usr/bin/env python3
"""
FlashFlow CLI - Main entry point
"""

import click
import os
import sys
from pathlib import Path

# Add the flashflow-main directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    # Updated imports to reflect new structure
    from cli.commands import new, install, build, serve, test, deploy, migrate, setup, custom, theme, preview
    from cli.commands.mobile import serve as mobile_serve
    from core.framework import FlashFlowProject
    from cli.core import __version__
except ImportError as e:
    # Fallback imports for when running from different locations
    from cli.commands import new, install, build, serve, test, deploy, migrate, setup, custom, theme, preview
    from cli.commands.mobile import serve as mobile_serve
    from core.framework import FlashFlowProject
    from cli.core import __version__

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
cli.add_command(custom.custom)
cli.add_command(theme.theme)
cli.add_command(mobile_serve.mobile)
cli.add_command(preview.preview)

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