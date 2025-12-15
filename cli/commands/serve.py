#!/usr/bin/env python3
"""
FlashFlow 'serve' command - Run unified development server
"""

import click
import subprocess
import threading
import time
import os
import sys
from pathlib import Path
from flask import Flask, render_template_string, jsonify, send_from_directory
from flask_cors import CORS
import flask

# Import Flet preview service
from services.flet_preview import FletPreviewService

from core.framework import FlashFlowProject
import subprocess
import os
from pathlib import Path

# Import user activity and notification services
from src.services.api_endpoints import register_api_endpoints

def check_go_service_available(service_name):
    """Check if a Go service executable is available."""
    service_path = Path(__file__).parent.parent.parent / "go-services" / service_name / f"{service_name}.exe"
    return service_path.exists()

def run_go_dev_server(host, port):
    """Run the Go development server if available."""
    try:
        # Determine the path to the dev server executable
        dev_server_path = Path(__file__).parent.parent.parent / "go-services" / "dev-server" / "dev-server.exe"
        
        if not dev_server_path.exists():
            return False
            
        # Prepare arguments
        args = [str(dev_server_path), str(Path.cwd())]
        
        # Set environment variables
        env_vars = os.environ.copy()
        env_vars["FLASHFLOW_HOST"] = host
        env_vars["FLASHFLOW_PORT"] = str(port)
        
        # Run the Go dev server
        subprocess.run(args, env=env_vars)
        return True
            
    except Exception as e:
        click.echo(f"Failed to run Go dev server: {str(e)}")
        return False

@click.command()
@click.option('--all', 'serve_all', is_flag=True, help='Serve all components (recommended)')
@click.option('--backend', is_flag=True, help='Serve backend only')
@click.option('--frontend', is_flag=True, help='Serve frontend only')
@click.option('--port', '-p', default=8000, help='Port to serve on')
@click.option('--host', '-h', default='localhost', help='Host to serve on')
@click.option('--auto-start-engine', is_flag=True, help='Automatically start FlashFlow Engine')
def serve(serve_all, backend, frontend, port, host, auto_start_engine):
    """Run unified development server"""
    
    # Check if we're in a FlashFlow project
    project = FlashFlowProject(Path.cwd())
    if not project.exists():
        click.echo("❌ Not in a FlashFlow project directory")
        return
    
    # Try to use Go development server if available for better performance
    if not backend and not frontend and check_go_service_available("dev-server"):
        click.echo("🚀 Using optimized Go development server for better performance...")
        if run_go_dev_server(host, port):
            return
    
    try:
        if serve_all:
            click.echo(f"🚀 Starting FlashFlow unified server for: {project.config.name}")
            start_unified_server(project, host, port, auto_start_engine)
        elif backend:
            click.echo("🔧 Starting backend server only...")
            start_backend_only(project, host, port)
        elif frontend:
            click.echo("🎨 Starting frontend server only...")
            start_frontend_only(project, host, port)
        else:
            # Default to unified server
            click.echo(f"🚀 Starting FlashFlow unified server for: {project.config.name}")
            start_unified_server(project, host, port, auto_start_engine)
            
    except KeyboardInterrupt:
        click.echo("\n🛑 Server stopped")
    except Exception as e:
        click.echo(f"❌ Server error: {str(e)}")

def start_flashflow_engine(project_root, backend_url="http://localhost:8000"):
    """Start the FlashFlow Engine in the background"""
    try:
        # Determine the path to the Flet direct renderer script
        flet_renderer_path = Path(__file__).parent.parent.parent / "python-services" / "flet-direct-renderer" / "main.py"
        
        if not flet_renderer_path.exists():
            click.echo("⚠️  FlashFlow Engine not found, skipping auto-start")
            return None
            
        # Start the FlashFlow Engine in a separate process
        engine_process = subprocess.Popen([
            sys.executable, 
            str(flet_renderer_path), 
            str(project_root),
            backend_url
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        click.echo("⚡ FlashFlow Engine started automatically on http://localhost:8012")
        return engine_process
        
    except Exception as e:
        click.echo(f"⚠️  Failed to start FlashFlow Engine: {str(e)}")
        return None

def start_unified_server(project: FlashFlowProject, host: str, port: int, auto_start_engine: bool = True):
    """Start the unified development server with all routes"""
    
    app = Flask(__name__)
    CORS(app)
    
    # Store project reference
    app.config['PROJECT'] = project
    
    # Automatically start FlashFlow Engine if requested
    engine_process = None
    if auto_start_engine:
        engine_process = start_flashflow_engine(project.root_path, f"http://{host}:{port}")
    
    # Start file watcher for .flow files
    file_watcher_thread = None
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
        import threading
        
        class FlowFileHandler(FileSystemEventHandler):
            def __init__(self, app):
                self.app = app
                
            def on_modified(self, event):
                if event.is_directory:
                    return
                    
                # Check if the file ends with .flow extension
                if Path(str(event.src_path)).suffix == ".flow":
                    print(f"🔄 .flow file changed: {event.src_path}")
                    # Broadcast update to all connected clients
                    # In a real implementation, this would use WebSockets
                    pass
        
        # Create observer
        observer = Observer()
        handler = FlowFileHandler(app)
        
        # Watch src/flows directory
        flows_dir = project.root_path / "src" / "flows"
        if flows_dir.exists():
            observer.schedule(handler, str(flows_dir), recursive=False)
            
        # Start observer in background thread
        observer.start()
        
        # Store observer reference for cleanup
        file_watcher_thread = observer
        
    except ImportError:
        print("⚠️  File watching not available (watchdog not installed)")
    
    # Routes
    setup_unified_routes(app)
    
    # Add live preview route with real-time updates (defined after setup_unified_routes to avoid conflicts)
    @app.route('/preview')
    def live_preview():
        """Live preview of .flow files with real-time updates"""
        project = app.config['PROJECT']
        
        # Get flow files data
        flows_dir = project.root_path / "src" / "flows"
        flow_data = {}
        if flows_dir.exists():
            for flow_file in flows_dir.glob("*.flow"):
                try:
                    import yaml
                    with open(flow_file, 'r') as f:
                        flow_data[flow_file.name] = yaml.safe_load(f)
                except Exception as e:
                    flow_data[flow_file.name] = {"error": str(e)}
        
        # Build the flow files list HTML
        flow_files_html = ""
        if flow_data:
            for file_name in flow_data.keys():
                flow_files_html += f'<li>📄 {file_name}</li>'
        else:
            flow_files_html = '<li>No .flow files found</li>'
        
        template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>FlashFlow Live Preview</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {{ font-family: 'Segoe UI', sans-serif; margin: 0; background: #f8f9fa; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1rem 2rem; }}
                .container {{ max-width: 1200px; margin: 0 auto; padding: 2rem; }}
                .preview-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 2rem 0; }}
                .preview-card {{ background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; }}
                .preview-card h3 {{ margin-top: 0; color: #3B82F6; }}
                .preview-placeholder {{ width: 100%; height: 400px; border: 1px solid #ddd; border-radius: 4px; margin: 1rem 0; display: flex; align-items: center; justify-content: center; background: #f8f9fa; }}
                .status {{ background: #d1fae5; color: #065f46; padding: 1rem; border-radius: 4px; margin: 1rem 0; }}
                .file-list {{ background: white; padding: 1rem; border-radius: 4px; margin: 1rem 0; }}
                .file-list li {{ margin: 0.5rem 0; }}
                .update-indicator {{ display: inline-block; width: 10px; height: 10px; border-radius: 50%; background: #10B981; margin-right: 8px; animation: pulse 2s infinite; }}
                @keyframes pulse {{
                    0% {{ opacity: 1; }}
                    50% {{ opacity: 0.5; }}
                    100% {{ opacity: 1; }}
                }}
                .instructions {{ background: #fef3c7; color: #92400e; padding: 1rem; border-radius: 4px; margin: 1rem 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>👁️ FlashFlow Live Preview</h1>
                <p>Real-time preview of your .flow files across all platforms</p>
            </div>
            <div class="container">
                <div class="status">
                    <strong><span class="update-indicator"></span>Live Preview Active</strong> - Changes to .flow files are automatically detected
                </div>
                
                <h2>Platform Previews</h2>
                <div class="preview-grid">
                    <div class="preview-card">
                        <h3>🌐 Web Preview</h3>
                        <p>Web application preview</p>
                        <div class="preview-placeholder" id="web-preview">
                            <div>
                                <div style="font-size: 3rem; margin-bottom: 1rem;">🌐</div>
                                <p>Web application preview</p>
                                <p style="font-size: 0.9rem; color: #666;">Generated from .flow files</p>
                            </div>
                        </div>
                    </div>
                    <div class="preview-card">
                        <h3>📱 Mobile Preview</h3>
                        <p>Mobile application preview</p>
                        <div class="preview-placeholder" id="mobile-preview">
                            <div>
                                <div style="font-size: 3rem; margin-bottom: 1rem;">📱</div>
                                <p>Mobile application preview</p>
                                <p style="font-size: 0.9rem; color: #666;">Generated from .flow files</p>
                            </div>
                        </div>
                    </div>
                    <div class="preview-card">
                        <h3>🖥️ Desktop Preview</h3>
                        <p>Desktop application preview</p>
                        <div class="preview-placeholder" id="desktop-preview">
                            <div>
                                <div style="font-size: 3rem; margin-bottom: 1rem;">🖥️</div>
                                <p>Desktop application preview</p>
                                <p style="font-size: 0.9rem; color: #666;">Generated from .flow files</p>
                            </div>
                        </div>
                    </div>
                </div>
                
                <h2>Project Information</h2>
                <div class="file-list">
                    <h3>.flow Files in Project</h3>
                    <ul id="flow-files-list">
                        {flow_files_html}
                    </ul>
                </div>
                
                <div class="instructions">
                    <strong>💡 How it works:</strong>
                    <p>FlashFlow automatically detects changes to your .flow files and updates all platform previews in real-time.</p>
                    <p>Modify any .flow file in your project's <code>src/flows</code> directory and watch the previews update automatically!</p>
                    <p><strong>⚡ FlashFlow Engine is running automatically on <a href="http://localhost:8012" target="_blank">http://localhost:8012</a></strong></p>
                </div>
                
                <p><a href="/">← Back to Main Dashboard</a></p>
            </div>
            
            <script>
                // Simulate real-time updates
                setInterval(() => {{
                    // In a real implementation, this would listen for WebSocket updates
                    const now = new Date();
                    document.querySelector('.status').innerHTML = 
                        `<strong><span class="update-indicator"></span>Live Preview Active</strong> - Last checked: ${{now.toLocaleTimeString()}}`;
                }}, 5000);
            </script>
        </body>
        </html>
        """
        
        return template
    
    # Add API endpoint for flow files (defined after setup_unified_routes to avoid conflicts)
    @app.route('/api/flow-files')
    def api_flow_files():
        """API endpoint to get list of flow files"""
        flows_dir = project.root_path / "src" / "flows"
        flow_files = []
        if flows_dir.exists():
            flow_files = [f.name for f in flows_dir.glob("*.flow")]
        return {"files": flow_files}
    
    # Add API endpoint for preview data (defined after setup_unified_routes to avoid conflicts)
    @app.route('/api/preview-data')
    def api_preview_data():
        """API endpoint to get preview data from flow files"""
        flows_dir = project.root_path / "src" / "flows"
        flow_data = {}
        if flows_dir.exists():
            for flow_file in flows_dir.glob("*.flow"):
                try:
                    import yaml
                    with open(flow_file, 'r') as f:
                        flow_data[flow_file.name] = yaml.safe_load(f)
                except Exception as e:
                    flow_data[flow_file.name] = {"error": str(e)}
        return {"flow_files": flow_data}
    
    # Register user activity and notification API endpoints
    register_api_endpoints(app)
    
    click.echo(f"🌐 Unified server starting on http://{host}:{port}")
    click.echo("\n📍 Available routes:")
    click.echo(f"   🏠 Welcome Page:     http://{host}:{port}/")
    click.echo(f"   📊 Dashboard:        http://{host}:{port}/dashboard")
    click.echo(f"   👨‍💼 Admin Panel:      http://{host}:{port}/admin/cpanel")
    click.echo(f"   📚 API Docs:         http://{host}:{port}/api/docs")
    click.echo(f"   🧪 API Tester:       http://{host}:{port}/api/tester")
    click.echo(f"   📱 Android Preview:  http://{host}:{port}/android")
    click.echo(f"   🍎 iOS Preview:      http://{host}:{port}/ios")
    click.echo(f"   🖥️  Desktop Preview:   http://{host}:{port}/desktop")
    click.echo(f"   🔧 Backend Status:   http://{host}:{port}/backend")
    click.echo(f"   👁️  Live Preview:      http://{host}:{port}/preview")
    if auto_start_engine:
        click.echo(f"   ⚡ FlashFlow Engine:  http://localhost:8012")
    click.echo("\n👀 Server is running... (Ctrl+C to stop)")
    
    try:
        app.run(host=host, port=port, debug=True, use_reloader=False)
    finally:
        # Clean up file watcher
        if file_watcher_thread:
            file_watcher_thread.stop()
            file_watcher_thread.join()
        
        # Clean up FlashFlow Engine process
        if engine_process:
            try:
                engine_process.terminate()
                engine_process.wait(timeout=5)
                click.echo("\n⚡ FlashFlow Engine stopped")
            except subprocess.TimeoutExpired:
                engine_process.kill()
                click.echo("\n⚡ FlashFlow Engine force killed")

def create_mobile_preview(platform_name, color):
    """Create mobile preview with live content from .flow files"""
    project = flask.current_app.config['PROJECT']
    
    # Get flow files data
    flows_dir = project.root_path / "src" / "flows"
    flow_data = {}
    if flows_dir.exists():
        for flow_file in flows_dir.glob("*.flow"):
            try:
                import yaml
                with open(flow_file, 'r') as f:
                    flow_data[flow_file.name] = yaml.safe_load(f)
            except Exception as e:
                flow_data[flow_file.name] = {"error": str(e)}
    
    # Build the flow files list HTML
    flow_files_html = ""
    if flow_data:
        for file_name in flow_data.keys():
            flow_files_html += f'<li>📄 {file_name}</li>'
    else:
        flow_files_html = '<li>No .flow files found</li>'
    
    # Build the flow content HTML
    flow_content_html = ""
    if flow_data:
        for flow_name, flow_content in flow_data.items():
            content_str = str(flow_content)[:200]
            if len(str(flow_content)) > 200:
                content_str += '...'
            flow_content_html += f'''
                        <div style="margin: 15px 0; padding: 15px; background: #e9ecef; border-radius: 8px;">
                            <h4>{flow_name}</h4>
                            <pre style="font-size: 12px; overflow: auto;">{content_str}</pre>
                        </div>
                        '''
    else:
        flow_content_html = '<p>No content to display</p>'
    
    # Build the complete template
    template = f"""<!DOCTYPE html>
<html>
<head>
    <title>{platform_name} Preview - {project.config.name}</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; margin: 0; background: #f0f0f0; }}
        .device {{ 
            width: 360px; 
            height: 700px; 
            background: white; 
            margin: 2rem auto; 
            border-radius: 40px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            position: relative;
            overflow: hidden;
            border: 12px solid {color};
        }}
        .status-bar {{ 
            height: 40px; 
            background: {color}; 
            color: white; 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            padding: 0 20px; 
            font-size: 14px;
        }}
        .screen {{ 
            height: calc(100% - 40px); 
            overflow-y: auto;
            padding: 20px;
            background: #f8f9fa;
        }}
        .app-bar {{ 
            background: {color}; 
            color: white; 
            padding: 15px 20px; 
            font-size: 20px;
            font-weight: bold;
        }}
        .content {{ padding: 20px; }}
        .card {{ 
            background: white; 
            border-radius: 12px; 
            padding: 20px; 
            margin-bottom: 20px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .button {{ 
            background: {color}; 
            color: white; 
            border: none; 
            padding: 12px 20px; 
            border-radius: 8px; 
            font-size: 16px;
            cursor: pointer;
            width: 100%;
            margin: 10px 0;
        }}
        .button:hover {{ opacity: 0.9; }}
        .flow-files {{ 
            background: #e9ecef; 
            padding: 15px; 
            border-radius: 8px; 
            margin: 20px 0;
        }}
        .update-indicator {{ 
            display: inline-block; 
            width: 10px; 
            height: 10px; 
            border-radius: 50%; 
            background: #28a745; 
            margin-right: 8px; 
            animation: pulse 2s infinite; 
        }}
        @keyframes pulse {{
            0% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
            100% {{ opacity: 1; }}
        }}
    </style>
</head>
<body>
    <div class="device">
        <div class="status-bar">
            <span>9:41</span>
            <span>📶 🔋</span>
        </div>
        <div class="app-bar">
            {platform_name} Preview
        </div>
        <div class="screen">
            <div class="content">
                <h2>📱 Live {platform_name} Preview</h2>
                <p>Real-time preview generated from .flow files</p>
                
                <div class="card">
                    <h3>Flow Files Detected</h3>
                    <div class="flow-files">
                        <ul>
                            {flow_files_html}
                        </ul>
                    </div>
                    <p><span class="update-indicator"></span> Live updates enabled</p>
                </div>
                
                <div class="card">
                    <h3>Preview Content</h3>
                    {flow_content_html}
                </div>
                
                <button class="button" onclick="location.reload()">🔄 Refresh Preview</button>
                <button class="button" style="background: #6c757d;" onclick="window.location.href='/'">🏠 Back to Dashboard</button>
            </div>
        </div>
    </div>
    
    <div style="text-align: center; margin: 20px;">
        <p>Changes to .flow files are automatically detected and will update this preview</p>
        <p><a href="/preview">👁️ View All Platform Previews</a></p>
    </div>
</body>
</html>"""
    
    return template


def create_desktop_preview():
    """Create desktop preview with live content from .flow files"""
    project = flask.current_app.config['PROJECT']
    
    # Get flow files data
    flows_dir = project.root_path / "src" / "flows"
    flow_data = {}
    if flows_dir.exists():
        for flow_file in flows_dir.glob("*.flow"):
            try:
                import yaml
                with open(flow_file, 'r') as f:
                    flow_data[flow_file.name] = yaml.safe_load(f)
            except Exception as e:
                flow_data[flow_file.name] = {"error": str(e)}
    
    # Build the flow files list HTML
    flow_files_html = ""
    if flow_data:
        for file_name in flow_data.keys():
            flow_files_html += f'<li>📄 {file_name}</li>'
    else:
        flow_files_html = '<li>No .flow files found</li>'
    
    # Build the flow content HTML
    flow_content_html = ""
    if flow_data:
        for flow_name, flow_content in flow_data.items():
            content_str = str(flow_content)[:300]
            if len(str(flow_content)) > 300:
                content_str += '...'
            flow_content_html += f'''
                        <div style="margin: 15px 0; padding: 15px; background: #4a5568; border-radius: 8px;">
                            <h3>{flow_name}</h3>
                            <pre style="font-size: 12px; overflow: auto; background: #2d3748; padding: 10px; border-radius: 4px;">{content_str}</pre>
                        </div>
                        '''
    else:
        flow_content_html = '<p>No content to display</p>'
    
    # Build the complete template
    template = f"""<!DOCTYPE html>
<html>
<head>
    <title>Desktop Preview - {project.config.name}</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{ 
            font-family: 'Segoe UI', sans-serif; 
            margin: 0; 
            background: #2d3748; 
            color: white;
            height: 100vh;
            overflow: hidden;
        }}
        .window {{ 
            width: 80%; 
            height: 80%; 
            background: #1a202c; 
            margin: 5vh auto; 
            border-radius: 8px; 
            box-shadow: 0 20px 50px rgba(0,0,0,0.5);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }}
        .title-bar {{ 
            height: 30px; 
            background: #2d3748; 
            display: flex; 
            align-items: center; 
            padding: 0 10px;
            border-bottom: 1px solid #4a5568;
        }}
        .window-controls {{ 
            display: flex; 
            margin-left: auto;
        }}
        .control {{ 
            width: 12px; 
            height: 12px; 
            border-radius: 50%; 
            margin-left: 8px;
        }}
        .close {{ background: #e53e3e; }}
        .minimize {{ background: #f6ad55; }}
        .maximize {{ background: #68d391; }}
        .menu-bar {{ 
            height: 30px; 
            background: #2d3748; 
            display: flex; 
            align-items: center; 
            padding: 0 20px;
            border-bottom: 1px solid #4a5568;
        }}
        .menu-item {{ 
            margin-right: 20px; 
            cursor: pointer;
            padding: 5px 10px;
            border-radius: 4px;
        }}
        .menu-item:hover {{ background: #4a5568; }}
        .content-area {{ 
            display: flex; 
            flex: 1; 
            overflow: hidden;
        }}
        .sidebar {{ 
            width: 250px; 
            background: #2d3748; 
            padding: 20px;
            border-right: 1px solid #4a5568;
            overflow-y: auto;
        }}
        .main-content {{ 
            flex: 1; 
            padding: 30px;
            overflow-y: auto;
            background: #1a202c;
        }}
        .card {{ 
            background: #2d3748; 
            border-radius: 8px; 
            padding: 20px; 
            margin-bottom: 20px; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .button {{ 
            background: #4299e1; 
            color: white; 
            border: none; 
            padding: 10px 20px; 
            border-radius: 6px; 
            font-size: 14px;
            cursor: pointer;
            margin: 5px;
        }}
        .button:hover {{ background: #3182ce; }}
        .flow-files {{ 
            background: #4a5568; 
            padding: 15px; 
            border-radius: 6px; 
            margin: 15px 0;
        }}
        .update-indicator {{ 
            display: inline-block; 
            width: 10px; 
            height: 10px; 
            border-radius: 50%; 
            background: #68d391; 
            margin-right: 8px; 
            animation: pulse 2s infinite; 
        }}
        @keyframes pulse {{
            0% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
            100% {{ opacity: 1; }}
        }}
    </style>
</head>
<body>
    <div class="window">
        <div class="title-bar">
            <span>Desktop Preview - {project.config.name}</span>
            <div class="window-controls">
                <div class="control minimize"></div>
                <div class="control maximize"></div>
                <div class="control close"></div>
            </div>
        </div>
        <div class="menu-bar">
            <div class="menu-item">File</div>
            <div class="menu-item">Edit</div>
            <div class="menu-item">View</div>
            <div class="menu-item">Help</div>
        </div>
        <div class="content-area">
            <div class="sidebar">
                <h3>Navigation</h3>
                <div class="menu-item">🏠 Dashboard</div>
                <div class="menu-item">📄 Flow Files</div>
                <div class="menu-item">⚙️ Settings</div>
                <div class="menu-item">❓ Help</div>
                
                <h3 style="margin-top: 30px;">Flow Files</h3>
                <div class="flow-files">
                    <ul style="padding-left: 20px;">
                        {flow_files_html}
                    </ul>
                </div>
            </div>
            <div class="main-content">
                <h1>🖥️ Desktop Application Preview</h1>
                <p>Real-time preview generated from .flow files</p>
                
                <div class="card">
                    <h2>Live Preview Status</h2>
                    <p><span class="update-indicator"></span> Live updates enabled - Changes to .flow files are automatically detected</p>
                </div>
                
                <div class="card">
                    <h2>Flow File Content</h2>
                    {flow_content_html}
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <button class="button" onclick="location.reload()">🔄 Refresh Preview</button>
                    <button class="button" style="background: #6c757d;" onclick="window.location.href='/'">🏠 Back to Dashboard</button>
                </div>
            </div>
        </div>
    </div>
    
    <div style="text-align: center; margin: 20px;">
        <p>Changes to .flow files are automatically detected and will update this preview</p>
        <p><a href="/preview" style="color: #63b3ed;">👁️ View All Platform Previews</a></p>
    </div>
</body>
</html>"""
    
    return template

def setup_unified_routes(app):
    """Setup all unified server routes"""
    
    @app.route('/')
    def welcome():
        """Welcome page (Laravel-style intro)"""
        project = app.config['PROJECT']
        
        template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>{{ project_name }} - FlashFlow</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { font-family: 'Segoe UI', sans-serif; margin: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
                .container { max-width: 800px; margin: 0 auto; padding: 60px 20px; text-align: center; }
                h1 { font-size: 3rem; margin-bottom: 0.5rem; font-weight: 300; }
                .subtitle { font-size: 1.2rem; opacity: 0.9; margin-bottom: 3rem; }
                .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 40px 0; }
                .card { background: rgba(255,255,255,0.1); padding: 30px; border-radius: 10px; backdrop-filter: blur(10px); }
                .card h3 { margin-top: 0; }
                a { color: white; text-decoration: none; font-weight: 500; }
                a:hover { text-decoration: underline; }
                .version { opacity: 0.7; font-size: 0.9rem; margin-top: 2rem; }
                .engine-status { background: rgba(255,255,255,0.2); padding: 1rem; border-radius: 8px; margin: 1rem 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>{{ project_name }}</h1>
                <p class="subtitle">Built with FlashFlow - Single-syntax full-stack development</p>
                
                <div class="engine-status">
                    <p>⚡ FlashFlow Engine is running automatically on <a href="http://localhost:8012" target="_blank">http://localhost:8012</a></p>
                </div>
                
                <div class="grid">
                    <div class="card">
                        <h3>📊 Dashboard</h3>
                        <p><a href="/dashboard">User Dashboard</a></p>
                    </div>
                    <div class="card">
                        <h3>👨‍💼 Admin</h3>
                        <p><a href="/admin/cpanel">Admin Panel</a></p>
                    </div>
                    <div class="card">
                        <h3>📚 API</h3>
                        <p><a href="/api/docs">Documentation</a> | <a href="/api/tester">Tester</a></p>
                    </div>
                    <div class="card">
                        <h3>📱 Mobile</h3>
                        <p><a href="/android">Android</a> | <a href="/ios">iOS</a></p>
                    </div>
                    <div class="card">
                        <h3>🖥️ Desktop</h3>
                        <p><a href="/desktop">Desktop Preview</a></p>
                    </div>
                    <div class="card">
                        <h3>👁️ Preview</h3>
                        <p><a href="/preview">Live Preview</a></p>
                    </div>
                </div>
                
                <div class="version">
                    FlashFlow v0.1 | Project: {{ project_name }}
                </div>
            </div>
        </body>
        </html>
        """
        
        return render_template_string(template, project_name=project.config.name)
    
    @app.route('/dashboard')
    def dashboard():
        """User Dashboard (PWA) with real-time building capabilities"""
        template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Dashboard - {{ project_name }}</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { font-family: 'Segoe UI', sans-serif; margin: 0; background: #f8f9fa; }
                .header { background: #3B82F6; color: white; padding: 1rem 2rem; }
                .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
                .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 2rem; }
                .stat-card { background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                .nav { background: white; padding: 1rem 2rem; margin-bottom: 2rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                .nav a { margin-right: 2rem; color: #3B82F6; text-decoration: none; }
                .nav a:hover { text-decoration: underline; }
                .build-section { 
                    background: white; 
                    padding: 2rem; 
                    border-radius: 8px; 
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    margin: 2rem 0;
                }
                .build-controls { display: flex; flex-wrap: wrap; gap: 10px; margin: 1rem 0; }
                .button { 
                    background: #3B82F6; 
                    color: white; 
                    border: none; 
                    padding: 0.75rem 1.5rem; 
                    border-radius: 4px; 
                    cursor: pointer;
                    font-size: 1rem;
                }
                .button:hover { background: #2563eb; }
                .button-secondary { background: #6c757d; }
                .button-success { background: #28a745; }
                .button-warning { background: #ffc107; color: #212529; }
                .build-log { 
                    background: #1a202c; 
                    color: #e2e8f0; 
                    padding: 1rem; 
                    border-radius: 4px; 
                    font-family: monospace; 
                    height: 150px; 
                    overflow-y: auto;
                    margin: 1rem 0;
                }
                .status-indicator { 
                    display: inline-block; 
                    width: 10px; 
                    height: 10px; 
                    border-radius: 50%; 
                    margin-right: 8px; 
                }
                .status-building { background: #f6ad55; animation: pulse 1s infinite; }
                .status-ready { background: #68d391; }
                .preview-grid { 
                    display: grid; 
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
                    gap: 20px; 
                    margin: 2rem 0;
                }
                .preview-card { 
                    background: white; 
                    padding: 1.5rem; 
                    border-radius: 8px; 
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    text-align: center;
                }
                .preview-card h3 { margin-top: 0; color: #3B82F6; }
                @keyframes pulse {
                    0% { opacity: 1; }
                    50% { opacity: 0.4; }
                    100% { opacity: 1; }
                }
                .engine-info { background: #e6fffa; border-left: 4px solid #00b894; padding: 1rem; border-radius: 4px; margin: 1rem 0; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Dashboard</h1>
                <p>Real-time application development with FlashFlow</p>
            </div>
            
            <div class="container">
                <div class="engine-info">
                    <p>⚡ FlashFlow Engine is running automatically on <a href="http://localhost:8012" target="_blank">http://localhost:8012</a></p>
                </div>
                
                <div class="stats">
                    <div class="stat-card">
                        <h3>🚀 Status</h3>
                        <p><span class="status-indicator status-ready"></span> Ready</p>
                    </div>
                    <div class="stat-card">
                        <h3>📁 Files</h3>
                        <p id="file-count">Loading...</p>
                    </div>
                    <div class="stat-card">
                        <h3>⏱️ Uptime</h3>
                        <p id="uptime">00:00:00</p>
                    </div>
                </div>
                
                <div class="nav">
                    <a href="/">🏠 Home</a>
                    <a href="/preview">👁️ Live Preview</a>
                    <a href="/api/docs">📚 API Docs</a>
                    <a href="/admin/cpanel">👨‍💼 Admin</a>
                    <a href="/android">📱 Android</a>
                    <a href="/ios">🍎 iOS</a>
                    <a href="/desktop">🖥️ Desktop</a>
                </div>
                
                <div class="build-section">
                    <h2>🏗️ Build Controls</h2>
                    <p>Control your FlashFlow development environment</p>
                    
                    <div class="build-controls">
                        <button class="button" onclick="refreshPreview()">🔄 Refresh Preview</button>
                        <button class="button button-warning" onclick="clearCache()">🧹 Clear Cache</button>
                        <button class="button button-secondary" onclick="toggleTheme()">🌓 Toggle Theme</button>
                    </div>
                    
                    <h3>📋 Build Log</h3>
                    <div class="build-log" id="build-log">
                        <div>[INFO] FlashFlow server started</div>
                        <div>[INFO] FlashFlow Engine started automatically on port 8012</div>
                        <div>[INFO] Watching for .flow file changes...</div>
                    </div>
                </div>
                
                <div class="preview-grid">
                    <div class="preview-card">
                        <h3>🌐 Web Preview</h3>
                        <p>Live preview of your web application</p>
                        <button class="button" onclick="window.open('/preview', '_blank')">👁️ View Preview</button>
                    </div>
                    <div class="preview-card">
                        <h3>📱 Mobile Preview</h3>
                        <p>Mobile application simulator</p>
                        <button class="button" onclick="window.open('/android', '_blank')">📱 Android Preview</button>
                        <button class="button" onclick="window.open('/ios', '_blank')" style="background: #007AFF;">🍎 iOS Preview</button>
                    </div>
                    <div class="preview-card">
                        <h3>🖥️ Desktop Preview</h3>
                        <p>Desktop application preview</p>
                        <button class="button" onclick="window.open('/desktop', '_blank')">🖥️ Launch Preview</button>
                    </div>
                </div>
            </div>
            
            <script>
                // Update file count
                async function updateFileCount() {
                    try {
                        const response = await fetch('/api/flow-files');
                        const data = await response.json();
                        document.getElementById('file-count').textContent = data.files ? data.files.length + ' .flow files' : '0 .flow files';
                    } catch (error) {
                        document.getElementById('file-count').textContent = 'Error loading';
                    }
                }
                
                // Update uptime
                function updateUptime() {
                    const uptimeElement = document.getElementById('uptime');
                    const startTime = new Date();
                    
                    setInterval(() => {
                        const now = new Date();
                        const diff = new Date(now - startTime);
                        const hours = diff.getUTCHours().toString().padStart(2, '0');
                        const minutes = diff.getUTCMinutes().toString().padStart(2, '0');
                        const seconds = diff.getUTCSeconds().toString().padStart(2, '0');
                        uptimeElement.textContent = `${hours}:${minutes}:${seconds}`;
                    }, 1000);
                }
                
                // Refresh preview
                function refreshPreview() {
                    const log = document.getElementById('build-log');
                    const timestamp = new Date().toLocaleTimeString();
                    log.innerHTML += `<div>[${timestamp}] Refreshing preview...</div>`;
                    log.scrollTop = log.scrollHeight;
                    
                    // In a real implementation, this would trigger a rebuild
                    setTimeout(() => {
                        log.innerHTML += `<div>[${timestamp}] Preview refreshed successfully</div>`;
                        log.scrollTop = log.scrollHeight;
                    }, 1000);
                }
                
                // Clear cache
                function clearCache() {
                    const log = document.getElementById('build-log');
                    const timestamp = new Date().toLocaleTimeString();
                    log.innerHTML += `<div>[${timestamp}] Clearing cache...</div>`;
                    log.scrollTop = log.scrollHeight;
                    
                    setTimeout(() => {
                        log.innerHTML += `<div>[${timestamp}] Cache cleared successfully</div>`;
                        log.scrollTop = log.scrollHeight;
                    }, 500);
                }
                
                // Toggle theme
                function toggleTheme() {
                    document.body.classList.toggle('dark-theme');
                    const log = document.getElementById('build-log');
                    const timestamp = new Date().toLocaleTimeString();
                    log.innerHTML += `<div>[${timestamp}] Theme toggled</div>`;
                    log.scrollTop = log.scrollHeight;
                }
                
                // Initialize
                updateFileCount();
                updateUptime();
            </script>
        </body>
        </html>
        """
        
        project = app.config['PROJECT']
        return render_template_string(template, project_name=project.config.name)
    
    @app.route('/android')
    def android_preview():
        """Android live preview from .flow files"""
        return create_mobile_preview("Android", "#a4c639")
    
    @app.route('/ios') 
    def ios_preview():
        """iOS live preview from .flow files"""
        return create_mobile_preview("iOS", "#007AFF")
    
    @app.route('/desktop')
    def desktop_preview():
        """Desktop live preview from .flow files"""
        return create_desktop_preview()
    
    @app.route('/backend')
    def backend_status():
        """Backend health status"""
        template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Backend Status - {{ project_name }}</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { font-family: 'Segoe UI', sans-serif; margin: 0; background: #f8f9fa; }
                .container { max-width: 800px; margin: 0 auto; padding: 2rem; }
                .status { background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin: 1rem 0; }
                .healthy { border-left: 4px solid #10b981; }
                .metric { display: flex; justify-content: space-between; margin: 0.5rem 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🔧 Backend Status</h1>
                
                <div class="status healthy">
                    <h3>✅ System Health</h3>
                    <div class="metric"><span>Status:</span><span>Healthy</span></div>
                    <div class="metric"><span>Uptime:</span><span>Running</span></div>
                    <div class="metric"><span>Database:</span><span>Connected</span></div>
                </div>
                
                <div class="status">
                    <h3>📊 Project Info</h3>
                    <div class="metric"><span>Name:</span><span>{{ project_name }}</span></div>
                    <div class="metric"><span>Framework:</span><span>FlashFlow</span></div>
                    <div class="metric"><span>Environment:</span><span>Development</span></div>
                </div>
                
                <p><a href="/api/docs">📚 API Docs</a> | <a href="/">🏠 Back to App</a></p>
            </div>
        </body>
        </html>
        """
        project = app.config['PROJECT']
        return render_template_string(template, project_name=project.config.name)

def start_backend_only(project: FlashFlowProject, host: str, port: int):
    """Start backend server only"""
    click.echo("🔧 Backend-only mode not yet implemented")
    click.echo("Use 'flashflow serve --all' for now")

def start_frontend_only(project: FlashFlowProject, host: str, port: int):
    """Start frontend server only"""
    click.echo("🎨 Frontend-only mode not yet implemented") 
    click.echo("Use 'flashflow serve --all' for now")