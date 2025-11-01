#!/usr/bin/env python3
"""
FlashFlow CLI - Main entry point
"""

import click
from .commands import (
    build, 
    serve, 
    init, 
    demo_slider, 
    demo_theme,
    demo_micro_interactions  # Add this import
)

@click.group()
def cli():
    """FlashFlow CLI - Generate complete applications from .flow files"""
    pass

# Register commands
cli.add_command(build.build)
cli.add_command(serve.serve)
cli.add_command(init.init)
cli.add_command(demo_slider.demo_slider)
cli.add_command(demo_theme.demo_theme)
cli.add_command(demo_micro_interactions.demo_micro_interactions)  # Add this line

if __name__ == '__main__':
    cli()