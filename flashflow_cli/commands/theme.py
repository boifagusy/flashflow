"""
FlashFlow 'theme' command - Theme preview system
"""

import click

@click.command()
def theme():
    """Preview themes directly within the FlashFlow development environment"""
    click.echo("🎨 Theme preview command")
    click.echo("This command allows you to preview themes without building the full application.")

if __name__ == '__main__':
    theme()