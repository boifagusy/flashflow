"""
FlashFlow 'mobile' command - Run mobile development server
"""

import click
import subprocess
import os
import sys
from pathlib import Path

@click.command()
@click.option('--port', '-p', default=8080, help='Port to serve the mobile IDE on')
@click.option('--host', '-h', default='0.0.0.0', help='Host to serve the mobile IDE on')
def mobile(port, host):
    """Run mobile development server for coding on Android and iOS devices"""
    
    # Check if we're in a FlashFlow project
    project_dir = Path.cwd()
    flashflow_config = project_dir / "flashflow.json"
    
    if not flashflow_config.exists():
        click.echo("❌ Not in a FlashFlow project directory")
        click.echo("Run 'flashflow new <project_name>' to create a new project first")
        return
    
    try:
        click.echo("📱 Starting FlashFlow Mobile Development IDE...")
        click.echo(f"🌐 Mobile IDE available at: http://{host}:{port}")
        click.echo("📱 Access this URL from your Android or iOS device!")
        click.echo("💡 Tip: Use your computer's IP address to access from mobile devices on the same network")
        click.echo("🛑 Press Ctrl+C to stop the server")
        
        # Import Flet and start the mobile IDE
        import flet as ft
        from cli.commands.mobile.mobile_ide import start_mobile_ide
        
        # Start Flet app
        ft.app(
            target=lambda page: start_mobile_ide(page, str(project_dir)),
            port=port,
            host=host
        )
        
    except KeyboardInterrupt:
        click.echo("\n🛑 Mobile development server stopped")
    except Exception as e:
        click.echo(f"❌ Mobile development server error: {str(e)}")