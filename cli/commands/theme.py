"""
FlashFlow 'theme' command - Theme preview system
"""

import click
import json
import os
from pathlib import Path
from flask import Flask, render_template_string, jsonify, send_from_directory
from flask_cors import CORS

# Fix the import to use the correct path
from core.framework import FlashFlowProject
from core.parser.parser import FlowParser

@click.command()
@click.option('--port', '-p', default=8080, help='Port to serve theme preview on')
@click.option('--host', '-h', default='localhost', help='Host to serve theme preview on')
@click.option('--theme', '-t', default=None, help='Specific theme to preview (default: all themes)')
@click.option('--live', '-l', is_flag=True, help='Enable live reloading when .flow files change')
def theme(port, host, theme, live):
    """Preview themes directly within the FlashFlow development environment"""
    
    # Check if we're in a FlashFlow project
    project = FlashFlowProject(Path.cwd())
    if not project.exists():
        click.echo("❌ Not in a FlashFlow project directory")
        return
    
    try:
        click.echo(f"🎨 Starting FlashFlow theme preview server for: {project.config.name}")
        start_theme_preview_server(project, host, port, theme, live)
    except KeyboardInterrupt:
        click.echo("\n🛑 Theme preview server stopped")
    except Exception as e:
        click.echo(f"❌ Theme preview error: {str(e)}")

def start_theme_preview_server(project: FlashFlowProject, host: str, port: int, theme_name: str = None, live_reload: bool = False):
    """Start the theme preview server"""
    
    app = Flask(__name__)
    CORS(app)
    
    # Store project reference
    app.config['PROJECT'] = project
    app.config['THEME_NAME'] = theme_name
    
    # Parse all .flow files to get theme information
    parser = FlowParser()
    ir = parser.parse_project(project.root_path)
    
    # Routes
    setup_theme_preview_routes(app, ir)
    
    click.echo(f"🌈 Theme preview server starting on http://{host}:{port}")
    click.echo("\n📍 Available routes:")
    click.echo(f"   🎨 Theme Gallery:    http://{host}:{port}/")
    click.echo(f"   📊 Theme Details:    http://{host}:{port}/theme/<name>")
    click.echo(f"   🖌️  Theme Preview:    http://{host}:{port}/preview/<name>")
    click.echo(f"   📱 Mobile Preview:   http://{host}:{port}/preview/<name>/mobile")
    click.echo(f"   🖥️  Desktop Preview:  http://{host}:{port}/preview/<name>/desktop")
    click.echo(f"   📦 Theme JSON:       http://{host}:{port}/api/themes")
    click.echo("\n👀 Theme preview server is running... (Ctrl+C to stop)")
    
    app.run(host=host, port=port, debug=True, use_reloader=False)

def setup_theme_preview_routes(app, ir):
    """Setup theme preview routes"""
    
    @app.route('/')
    def theme_gallery():
        """Theme gallery page showing all available themes"""
        project = app.config['PROJECT']
        
        # Extract themes from IR
        themes = []
        if hasattr(ir, 'theme') and ir.theme:
            themes.append({
                'name': ir.theme.get('name', 'Default'),
                'preview_url': f'/preview/{ir.theme.get("name", "default")}',
                'details_url': f'/theme/{ir.theme.get("name", "default")}',
                'colors': ir.theme.get('colors', {}),
                'description': 'Main project theme'
            })
        
        template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Theme Gallery - {{ project_name }}</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { font-family: 'Segoe UI', sans-serif; margin: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
                .container { max-width: 1200px; margin: 0 auto; padding: 40px 20px; }
                h1 { font-size: 2.5rem; margin-bottom: 0.5rem; font-weight: 300; text-align: center; }
                .subtitle { font-size: 1.2rem; opacity: 0.9; margin-bottom: 3rem; text-align: center; }
                .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 30px; margin: 40px 0; }
                .card { background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px; backdrop-filter: blur(10px); transition: transform 0.3s ease; }
                .card:hover { transform: translateY(-5px); }
                .card h3 { margin-top: 0; font-size: 1.5rem; }
                a { color: white; text-decoration: none; font-weight: 500; }
                a:hover { text-decoration: underline; }
                .color-preview { display: flex; flex-wrap: wrap; gap: 10px; margin: 15px 0; }
                .color-swatch { width: 40px; height: 40px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.2); }
                .theme-actions { display: flex; gap: 15px; margin-top: 20px; }
                .btn { padding: 10px 20px; border-radius: 8px; font-weight: 500; text-align: center; transition: all 0.2s ease; }
                .btn-primary { background: rgba(255,255,255,0.2); border: 1px solid rgba(255,255,255,0.3); }
                .btn-primary:hover { background: rgba(255,255,255,0.3); }
                .btn-secondary { background: rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.1); }
                .btn-secondary:hover { background: rgba(0,0,0,0.3); }
                .version { opacity: 0.7; font-size: 0.9rem; margin-top: 2rem; text-align: center; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎨 Theme Gallery</h1>
                <p class="subtitle">Preview themes for {{ project_name }}</p>
                
                {% if themes %}
                <div class="grid">
                    {% for theme in themes %}
                    <div class="card">
                        <h3>{{ theme.name }}</h3>
                        <p>{{ theme.description }}</p>
                        
                        <div class="color-preview">
                            {% for color_name, color_value in theme.colors.items() %}
                                {% if color_value and color_name != 'name' %}
                                <div class="color-swatch" style="background: {{ color_value }};" title="{{ color_name }}: {{ color_value }}"></div>
                                {% endif %}
                            {% endfor %}
                        </div>
                        
                        <div class="theme-actions">
                            <a href="{{ theme.preview_url }}" class="btn btn-primary">Preview</a>
                            <a href="{{ theme.details_url }}" class="btn btn-secondary">Details</a>
                        </div>
                    </div>
                    {% endfor %}
                </div>
                {% else %}
                <div class="card" style="text-align: center; padding: 60px;">
                    <h3>No themes found</h3>
                    <p>Add a theme definition to your .flow files to see it here.</p>
                </div>
                {% endif %}
                
                <div class="version">
                    FlashFlow Theme Preview | Project: {{ project_name }}
                </div>
            </div>
        </body>
        </html>
        """
        
        return render_template_string(template, 
                                    project_name=project.config.name,
                                    themes=themes)
    
    @app.route('/theme/<theme_name>')
    def theme_details(theme_name):
        """Show detailed information about a specific theme"""
        project = app.config['PROJECT']
        
        # Find the theme in IR
        theme_data = {}
        if hasattr(ir, 'theme') and ir.theme:
            if ir.theme.get('name', '').lower() == theme_name.lower() or theme_name.lower() == 'default':
                theme_data = ir.theme
        
        template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>{{ theme_name }} Theme - {{ project_name }}</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { font-family: 'Segoe UI', sans-serif; margin: 0; background: #f8f9fa; }
                .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem; }
                .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
                .theme-info { background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); margin-bottom: 2rem; }
                .color-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }
                .color-card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); text-align: center; }
                .color-swatch-large { width: 80px; height: 80px; border-radius: 12px; margin: 0 auto 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
                .nav { background: white; padding: 1rem 2rem; margin-bottom: 2rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                .nav a { margin-right: 2rem; color: #3B82F6; text-decoration: none; }
                .nav a:hover { text-decoration: underline; }
                pre { background: #2d3748; color: #f7fafc; padding: 1.5rem; border-radius: 8px; overflow-x: auto; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{{ theme_name }} Theme</h1>
                <p>Detailed information for {{ project_name }}</p>
            </div>
            
            <div class="container">
                <div class="nav">
                    <a href="/">← Back to Gallery</a>
                    <a href="/preview/{{ theme_name }}">Live Preview</a>
                </div>
                
                <div class="theme-info">
                    <h2>Theme Details</h2>
                    {% if theme_data %}
                    <h3>Color Palette</h3>
                    <div class="color-grid">
                        {% for color_name, color_value in theme_data.items() %}
                            {% if color_value and color_name != 'name' %}
                            <div class="color-card">
                                <div class="color-swatch-large" style="background: {{ color_value }};"></div>
                                <h4>{{ color_name.replace('_', ' ').title() }}</h4>
                                <p>{{ color_value }}</p>
                            </div>
                            {% endif %}
                        {% endfor %}
                    </div>
                    
                    <h3>Theme Configuration</h3>
                    <pre>{{ theme_data | tojson(indent=2) }}</pre>
                    {% else %}
                    <p>Theme "{{ theme_name }}" not found.</p>
                    {% endif %}
                </div>
            </div>
        </body>
        </html>
        """
        
        return render_template_string(template,
                                    project_name=project.config.name,
                                    theme_name=theme_name,
                                    theme_data=theme_data)
    
    @app.route('/preview/<theme_name>')
    def theme_preview(theme_name):
        """Live preview of a theme applied to sample components"""
        project = app.config['PROJECT']
        
        # Find the theme in IR
        theme_data = {}
        if hasattr(ir, 'theme') and ir.theme:
            if ir.theme.get('name', '').lower() == theme_name.lower() or theme_name.lower() == 'default':
                theme_data = ir.theme
        
        # Extract theme colors
        colors = theme_data.get('colors', {}) if theme_data else {}
        primary_color = colors.get('primary', '#3B82F6')
        secondary_color = colors.get('secondary', '#64748B')
        background_color = colors.get('background', '#ffffff')
        text_color = colors.get('text', '#0F172A')
        
        template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>{{ theme_name }} Preview - {{ project_name }}</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                :root {
                    --primary-color: {{ primary_color }};
                    --secondary-color: {{ secondary_color }};
                    --background-color: {{ background_color }};
                    --text-color: {{ text_color }};
                    --success-color: #10B981;
                    --warning-color: #F59E0B;
                    --danger-color: #EF4444;
                }
                
                body { 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                    margin: 0; 
                    background: var(--background-color);
                    color: var(--text-color);
                    line-height: 1.6;
                }
                
                .header { 
                    background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%); 
                    color: white; 
                    padding: 2rem; 
                    text-align: center;
                }
                
                .container { 
                    max-width: 1200px; 
                    margin: 0 auto; 
                    padding: 2rem; 
                }
                
                .component-grid { 
                    display: grid; 
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
                    gap: 30px; 
                    margin: 40px 0; 
                }
                
                .component-card { 
                    background: white; 
                    padding: 2rem; 
                    border-radius: 12px; 
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1); 
                }
                
                .component-card h3 { 
                    margin-top: 0; 
                    color: var(--primary-color);
                    border-bottom: 2px solid var(--primary-color);
                    padding-bottom: 10px;
                }
                
                .btn { 
                    display: inline-block;
                    padding: 0.75rem 1.5rem; 
                    background: var(--primary-color);
                    color: white; 
                    text-decoration: none; 
                    border: none; 
                    border-radius: 6px; 
                    cursor: pointer; 
                    font-size: 1rem; 
                    font-weight: 500;
                    transition: all 0.3s ease;
                    margin: 5px;
                }
                
                .btn:hover { 
                    opacity: 0.9;
                    transform: translateY(-2px);
                }
                
                .btn-secondary { 
                    background: var(--secondary-color);
                }
                
                .btn-success { 
                    background: var(--success-color);
                }
                
                .btn-warning { 
                    background: var(--warning-color);
                }
                
                .btn-danger { 
                    background: var(--danger-color);
                }
                
                .form-group { 
                    margin-bottom: 1.5rem; 
                }
                
                .form-control { 
                    width: 100%; 
                    padding: 0.75rem; 
                    border: 1px solid #D1D5DB; 
                    border-radius: 6px; 
                    font-size: 1rem; 
                    transition: all 0.2s ease;
                }
                
                .form-control:focus { 
                    outline: none; 
                    border-color: var(--primary-color);
                    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
                }
                
                .nav { 
                    background: white; 
                    padding: 1rem 2rem; 
                    margin-bottom: 2rem; 
                    border-radius: 8px; 
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1); 
                }
                
                .nav a { 
                    margin-right: 2rem; 
                    color: var(--primary-color); 
                    text-decoration: none; 
                }
                
                .nav a:hover { 
                    text-decoration: underline; 
                }
                
                .alert {
                    padding: 1rem;
                    border-radius: 6px;
                    margin: 1rem 0;
                }
                
                .alert-success {
                    background: #D1FAE5;
                    color: #065F46;
                    border-left: 4px solid var(--success-color);
                }
                
                .alert-warning {
                    background: #FEF3C7;
                    color: #92400E;
                    border-left: 4px solid var(--warning-color);
                }
                
                .alert-danger {
                    background: #FEE2E2;
                    color: #991B1B;
                    border-left: 4px solid var(--danger-color);
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎨 {{ theme_name }} Theme Preview</h1>
                <p>Live preview of {{ project_name }} with the {{ theme_name }} theme</p>
            </div>
            
            <div class="container">
                <div class="nav">
                    <a href="/">← Back to Gallery</a>
                    <a href="/theme/{{ theme_name }}">Theme Details</a>
                    <a href="/preview/{{ theme_name }}/mobile">📱 Mobile</a>
                    <a href="/preview/{{ theme_name }}/desktop">🖥️ Desktop</a>
                </div>
                
                <div class="component-grid">
                    <div class="component-card">
                        <h3>Buttons</h3>
                        <button class="btn">Primary Button</button>
                        <button class="btn btn-secondary">Secondary</button>
                        <button class="btn btn-success">Success</button>
                        <button class="btn btn-warning">Warning</button>
                        <button class="btn btn-danger">Danger</button>
                    </div>
                    
                    <div class="component-card">
                        <h3>Form Elements</h3>
                        <div class="form-group">
                            <label for="name">Name</label>
                            <input type="text" id="name" class="form-control" placeholder="Enter your name">
                        </div>
                        <div class="form-group">
                            <label for="email">Email</label>
                            <input type="email" id="email" class="form-control" placeholder="Enter your email">
                        </div>
                        <div class="form-group">
                            <label for="message">Message</label>
                            <textarea id="message" class="form-control" rows="3" placeholder="Enter your message"></textarea>
                        </div>
                    </div>
                    
                    <div class="component-card">
                        <h3>Alerts</h3>
                        <div class="alert alert-success">
                            <strong>Success!</strong> This is a success alert.
                        </div>
                        <div class="alert alert-warning">
                            <strong>Warning!</strong> This is a warning alert.
                        </div>
                        <div class="alert alert-danger">
                            <strong>Error!</strong> This is an error alert.
                        </div>
                    </div>
                    
                    <div class="component-card">
                        <h3>Typography</h3>
                        <h1>Heading 1</h1>
                        <h2>Heading 2</h2>
                        <h3>Heading 3</h3>
                        <p>This is a paragraph with some <strong>bold text</strong> and <em>italic text</em>. The theme colors are applied to all elements for consistent styling.</p>
                        <ul>
                            <li>Unordered list item</li>
                            <li>Another list item</li>
                            <li>Yet another item</li>
                        </ul>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        return render_template_string(template,
                                    project_name=project.config.name,
                                    theme_name=theme_name,
                                    primary_color=primary_color,
                                    secondary_color=secondary_color,
                                    background_color=background_color,
                                    text_color=text_color)
    
    @app.route('/preview/<theme_name>/mobile')
    def mobile_preview(theme_name):
        """Mobile preview of a theme"""
        project = app.config['PROJECT']
        
        # Find the theme in IR
        theme_data = {}
        if hasattr(ir, 'theme') and ir.theme:
            if ir.theme.get('name', '').lower() == theme_name.lower() or theme_name.lower() == 'default':
                theme_data = ir.theme
        
        # Extract theme colors
        colors = theme_data.get('colors', {}) if theme_data else {}
        primary_color = colors.get('primary', '#3B82F6')
        background_color = colors.get('background', '#ffffff')
        
        template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Mobile Preview - {{ theme_name }} Theme</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
            <style>
                :root {{
                    --primary-color: {primary_color};
                    --background-color: {background_color};
                }}
                
                body {{ 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                    margin: 0; 
                    padding: 0;
                    background: #f0f0f0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                }}
                
                .phone {{ 
                    width: 360px; 
                    height: 700px; 
                    background: black; 
                    border-radius: 40px; 
                    padding: 20px; 
                    position: relative; 
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                }}
                
                .screen {{ 
                    width: 100%; 
                    height: 100%; 
                    background: var(--background-color); 
                    border-radius: 30px; 
                    overflow: hidden; 
                    position: relative; 
                }}
                
                .status-bar {{ 
                    height: 40px; 
                    background: var(--primary-color); 
                    color: white; 
                    display: flex; 
                    align-items: center; 
                    justify-content: space-between; 
                    padding: 0 15px; 
                    font-size: 0.8rem; 
                }}
                
                .content {{ 
                    padding: 20px; 
                }}
                
                .back-btn {{ 
                    position: absolute; 
                    top: 25px; 
                    left: 25px; 
                    background: rgba(255,255,255,0.9); 
                    padding: 10px 20px; 
                    border-radius: 20px; 
                    text-decoration: none; 
                    color: black; 
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1); 
                    font-weight: 500;
                    z-index: 10;
                }}
                
                .header {{ 
                    text-align: center; 
                    margin: 20px 0 30px 0;
                }}
                
                .header h2 {{ 
                    margin: 0; 
                    color: var(--primary-color);
                }}
                
                .component {{ 
                    background: white; 
                    border-radius: 12px; 
                    padding: 20px; 
                    margin-bottom: 20px; 
                    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                }}
                
                .btn {{ 
                    display: block;
                    width: 100%;
                    padding: 15px; 
                    background: var(--primary-color);
                    color: white; 
                    border: none; 
                    border-radius: 8px; 
                    font-size: 1rem; 
                    font-weight: 500;
                    margin: 10px 0;
                    cursor: pointer;
                }}
                
                .btn-secondary {{ 
                    background: #6b7280;
                }}
                
                .form-group {{ 
                    margin-bottom: 15px; 
                }}
                
                .form-control {{ 
                    width: 100%; 
                    padding: 12px; 
                    border: 1px solid #D1D5DB; 
                    border-radius: 8px; 
                    font-size: 1rem; 
                }}
            </style>
        </head>
        <body>
            <a href="/preview/{{ theme_name }}" class="back-btn">← Back</a>
            <div class="phone">
                <div class="screen">
                    <div class="status-bar">
                        <span>9:41</span>
                        <span>{{ theme_name }} App</span>
                        <span>🔋 100%</span>
                    </div>
                    <div class="content">
                        <div class="header">
                            <h2>📱 Mobile Preview</h2>
                            <p>{{ project_name }}</p>
                        </div>
                        
                        <div class="component">
                            <h3>Buttons</h3>
                            <button class="btn">Primary Button</button>
                            <button class="btn btn-secondary">Secondary</button>
                        </div>
                        
                        <div class="component">
                            <h3>Login Form</h3>
                            <div class="form-group">
                                <input type="email" class="form-control" placeholder="Email">
                            </div>
                            <div class="form-group">
                                <input type="password" class="form-control" placeholder="Password">
                            </div>
                            <button class="btn">Sign In</button>
                        </div>
                        
                        <div class="component">
                            <h3>Sample Content</h3>
                            <p>This shows how your theme looks on mobile devices. All components are styled with your theme colors.</p>
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        return render_template_string(template,
                                    project_name=project.config.name,
                                    theme_name=theme_name)
    
    @app.route('/preview/<theme_name>/desktop')
    def desktop_preview(theme_name):
        """Desktop preview of a theme"""
        project = app.config['PROJECT']
        
        # Find the theme in IR
        theme_data = {}
        if hasattr(ir, 'theme') and ir.theme:
            if ir.theme.get('name', '').lower() == theme_name.lower() or theme_name.lower() == 'default':
                theme_data = ir.theme
        
        # Extract theme colors
        colors = theme_data.get('colors', {}) if theme_data else {}
        primary_color = colors.get('primary', '#3B82F6')
        background_color = colors.get('background', '#ffffff')
        text_color = colors.get('text', '#0F172A')
        
        template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Desktop Preview - {{ theme_name }} Theme</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                :root {{
                    --primary-color: {primary_color};
                    --background-color: {background_color};
                    --text-color: {text_color};
                }}
                
                body {{ 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                    margin: 0; 
                    padding: 0;
                    background: #2d3748;
                    color: var(--text-color);
                    height: 100vh;
                    display: flex;
                    flex-direction: column;
                }}
                
                .window {{ 
                    flex: 1;
                    margin: 20px;
                    background: var(--background-color);
                    border-radius: 8px;
                    overflow: hidden;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                    display: flex;
                    flex-direction: column;
                }}
                
                .title-bar {{ 
                    height: 30px; 
                    background: #e2e8f0; 
                    display: flex; 
                    align-items: center; 
                    padding: 0 10px; 
                    border-bottom: 1px solid #cbd5e0;
                }}
                
                .window-controls {{ 
                    display: flex; 
                    gap: 8px; 
                    margin-left: auto; 
                }}
                
                .control {{ 
                    width: 12px; 
                    height: 12px; 
                    border-radius: 50%; 
                }}
                
                .close {{ background: #ff5f57; }}
                .minimize {{ background: #febc2e; }}
                .maximize {{ background: #28c840; }}
                
                .menu-bar {{ 
                    background: #f8fafc; 
                    padding: 8px 15px; 
                    border-bottom: 1px solid #e2e8f0;
                    display: flex;
                    gap: 20px;
                }}
                
                .menu-item {{ 
                    font-weight: 500; 
                    color: #4a5568; 
                    cursor: pointer;
                }}
                
                .menu-item:hover {{ 
                    color: var(--primary-color); 
                }}
                
                .content {{ 
                    flex: 1;
                    padding: 30px;
                    overflow: auto;
                }}
                
                .back-btn {{ 
                    position: absolute; 
                    top: 30px; 
                    left: 30px; 
                    background: rgba(0,0,0,0.1); 
                    padding: 8px 16px; 
                    border-radius: 6px; 
                    text-decoration: none; 
                    color: var(--text-color); 
                    font-weight: 500;
                }}
                
                .header {{ 
                    text-align: center; 
                    margin: 20px 0 40px 0;
                }}
                
                .header h1 {{ 
                    margin: 0; 
                    color: var(--primary-color);
                }}
                
                .component-grid {{ 
                    display: grid; 
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
                    gap: 30px; 
                }}
                
                .component-card {{ 
                    background: white; 
                    border-radius: 12px; 
                    padding: 25px; 
                    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
                }}
                
                .btn {{ 
                    padding: 12px 24px; 
                    background: var(--primary-color);
                    color: white; 
                    border: none; 
                    border-radius: 6px; 
                    font-size: 1rem; 
                    font-weight: 500;
                    cursor: pointer;
                    margin: 10px 0;
                }}
                
                .btn:hover {{ 
                    opacity: 0.9;
                }}
                
                .form-group {{ 
                    margin-bottom: 20px; 
                }}
                
                .form-control {{ 
                    width: 100%; 
                    padding: 12px; 
                    border: 1px solid #D1D5DB; 
                    border-radius: 6px; 
                    font-size: 1rem; 
                }}
            </style>
        </head>
        <body>
            <div class="window">
                <div class="title-bar">
                    <div class="window-controls">
                        <div class="control close"></div>
                        <div class="control minimize"></div>
                        <div class="control maximize"></div>
                    </div>
                </div>
                <div class="menu-bar">
                    <div class="menu-item">File</div>
                    <div class="menu-item">Edit</div>
                    <div class="menu-item">View</div>
                    <div class="menu-item">Help</div>
                </div>
                <div class="content">
                    <a href="/preview/{{ theme_name }}" class="back-btn">← Back</a>
                    <div class="header">
                        <h1>🖥️ Desktop Preview</h1>
                        <p>{{ project_name }} with {{ theme_name }} theme</p>
                    </div>
                    
                    <div class="component-grid">
                        <div class="component-card">
                            <h3>Dashboard</h3>
                            <p>This shows how your theme looks in a desktop application. The interface adapts to provide a native desktop experience.</p>
                            <button class="btn">Dashboard Button</button>
                        </div>
                        
                        <div class="component-card">
                            <h3>Settings Form</h3>
                            <div class="form-group">
                                <label>Application Name</label>
                                <input type="text" class="form-control" value="{{ project_name }}">
                            </div>
                            <div class="form-group">
                                <label>Theme</label>
                                <input type="text" class="form-control" value="{{ theme_name }}">
                            </div>
                            <button class="btn">Save Settings</button>
                        </div>
                        
                        <div class="component-card">
                            <h3>Statistics</h3>
                            <p>Your theme colors are applied consistently across all desktop components for a unified experience.</p>
                            <button class="btn">View Reports</button>
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        return render_template_string(template,
                                    project_name=project.config.name,
                                    theme_name=theme_name)
    
    @app.route('/api/themes')
    def api_themes():
        """API endpoint to get all themes as JSON"""
        themes = []
        if hasattr(ir, 'theme') and ir.theme:
            themes.append(ir.theme)
        
        return jsonify({
            'themes': themes,
            'count': len(themes)
        })

if __name__ == '__main__':
    theme()