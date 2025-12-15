#!/usr/bin/env python3
"""
FlashFlow 'preview' command - Run Flet live preview service
"""

import click
import sys
from pathlib import Path

# Add the flashflow-main directory to the path so we can import the service
sys.path.insert(0, str(Path(__file__).parent.parent / "flashflow-main"))

from services.flet_preview import FletPreviewService
from core.framework import FlashFlowProject

@click.command()
@click.option('--port', '-p', default=8010, help='Port to serve the preview on')
def preview(port):
    """Run Flet live preview service"""
    
    # Check if we're in a FlashFlow project
    project = FlashFlowProject(Path.cwd())
    if not project.exists():
        click.echo("❌ Not in a FlashFlow project directory")
        return
    
    try:
        click.echo(f"📱 Starting Flet Live Preview Service for: {project.config.name}")
        click.echo(f"🌐 Preview available at: http://localhost:{port}")
        click.echo("👀 Watching for .flow file changes...")
        click.echo("❌ Press Ctrl+C to stop")
        
        # Start the Flet preview service
        service = FletPreviewService(str(project.root_path), port)
        service.start()
        
    except KeyboardInterrupt:
        click.echo("\n🛑 Flet Preview Service stopped")
    except Exception as e:
        click.echo(f"❌ Preview service error: {str(e)}")

if __name__ == "__main__":
    preview()