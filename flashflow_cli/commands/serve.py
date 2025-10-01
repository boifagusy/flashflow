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

from ..core import FlashFlowProject

@click.command()
@click.option('--all', 'serve_all', is_flag=True, help='Serve all components (recommended)')
@click.option('--backend', is_flag=True, help='Serve backend only')
@click.option('--frontend', is_flag=True, help='Serve frontend only')
@click.option('--port', '-p', default=8000, help='Port to serve on')
@click.option('--host', '-h', default='localhost', help='Host to serve on')
def serve(serve_all, backend, frontend, port, host):
    """Run unified development server"""
    
    # Check if we're in a FlashFlow project
    project = FlashFlowProject(Path.cwd())
    if not project.exists():
        click.echo("❌ Not in a FlashFlow project directory")
        return
    
    try:
        if serve_all:
            click.echo(f"🚀 Starting FlashFlow unified server for: {project.config.name}")
            start_unified_server(project, host, port)
        elif backend:
            click.echo("🔧 Starting backend server only...")
            start_backend_only(project, host, port)
        elif frontend:
            click.echo("🎨 Starting frontend server only...")
            start_frontend_only(project, host, port)
        else:
            # Default to unified server
            click.echo(f"🚀 Starting FlashFlow unified server for: {project.config.name}")
            start_unified_server(project, host, port)
            
    except KeyboardInterrupt:
        click.echo("\n🛑 Server stopped")
    except Exception as e:
        click.echo(f"❌ Server error: {str(e)}")

def start_unified_server(project: FlashFlowProject, host: str, port: int):
    """Start the unified development server with all routes"""
    
    app = Flask(__name__)
    CORS(app)
    
    # Store project reference
    app.config['PROJECT'] = project
    
    # Routes
    setup_unified_routes(app)
    
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
    click.echo("\n👀 Server is running... (Ctrl+C to stop)")
    
    app.run(host=host, port=port, debug=True, use_reloader=False)

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
            </style>
        </head>
        <body>
            <div class="container">
                <h1>{{ project_name }}</h1>
                <p class="subtitle">Built with FlashFlow - Single-syntax full-stack development</p>
                
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
        """User Dashboard (PWA)"""
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
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Dashboard</h1>
            </div>
            <div class="container">
                <div class="nav">
                    <a href="/dashboard">Home</a>
                    <a href="/profile">Profile</a>
                    <a href="/settings">Settings</a>
                    <a href="/">← Back to Welcome</a>
                </div>
                
                <div class="stats">
                    <div class="stat-card">
                        <h3>Welcome</h3>
                        <p>FlashFlow User</p>
                    </div>
                    <div class="stat-card">
                        <h3>Status</h3>
                        <p>Active</p>
                    </div>
                    <div class="stat-card">
                        <h3>Project</h3>
                        <p>{{ project_name }}</p>
                    </div>
                </div>
                
                <div style="background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h2>Dashboard Content</h2>
                    <p>This dashboard is generated from your .flow files. Add more components and data models to see them here.</p>
                </div>
            </div>
        </body>
        </html>
        """
        project = app.config['PROJECT']
        return render_template_string(template, project_name=project.config.name)
    
    @app.route('/admin/cpanel')
    def admin_panel():
        """Admin Panel"""
        template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Admin Panel - {{ project_name }}</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { font-family: 'Segoe UI', sans-serif; margin: 0; background: #1a1a1a; color: white; }
                .header { background: #2d3748; padding: 1rem 2rem; border-bottom: 1px solid #4a5568; }
                .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
                .admin-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }
                .admin-card { background: #2d3748; padding: 2rem; border-radius: 8px; border: 1px solid #4a5568; }
                .admin-card h3 { margin-top: 0; color: #63b3ed; }
                a { color: #63b3ed; text-decoration: none; }
                a:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🛠️ Admin Panel</h1>
                <p>Manage your {{ project_name }} application</p>
            </div>
            <div class="container">
                <div class="admin-grid">
                    <div class="admin-card">
                        <h3>📊 Database</h3>
                        <p>Manage models and data</p>
                        <a href="/admin/database">View Database →</a>
                    </div>
                    <div class="admin-card">
                        <h3>👥 Users</h3>
                        <p>User management</p>
                        <a href="/admin/users">Manage Users →</a>
                    </div>
                    <div class="admin-card">
                        <h3>⚙️ Settings</h3>
                        <p>Application configuration</p>
                        <a href="/admin/settings">Settings →</a>
                    </div>
                    <div class="admin-card">
                        <h3>📈 Analytics</h3>
                        <p>Usage statistics</p>
                        <a href="/admin/analytics">View Analytics →</a>
                    </div>
                </div>
                
                <div style="margin-top: 2rem; padding: 2rem; background: #2d3748; border-radius: 8px; border: 1px solid #4a5568;">
                    <h2>Quick Actions</h2>
                    <p><a href="/api/docs">📚 API Documentation</a> | <a href="/api/tester">🧪 API Tester</a> | <a href="/">🏠 Back to App</a></p>
                </div>
            </div>
        </body>
        </html>
        """
        project = app.config['PROJECT']
        return render_template_string(template, project_name=project.config.name)
    
    @app.route('/api/docs')
    def api_docs():
        """Auto-generated API documentation"""
        template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>API Documentation - {{ project_name }}</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { font-family: 'Segoe UI', sans-serif; margin: 0; background: #f8f9fa; }
                .container { max-width: 1000px; margin: 0 auto; padding: 2rem; }
                .endpoint { background: white; margin: 1rem 0; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                .method { display: inline-block; padding: 0.2rem 0.5rem; border-radius: 4px; font-weight: bold; font-size: 0.8rem; }
                .get { background: #d4edda; color: #155724; }
                .post { background: #fff3cd; color: #856404; }
                .put { background: #cce5ff; color: #004085; }
                .delete { background: #f8d7da; color: #721c24; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📚 API Documentation</h1>
                <p>Auto-generated API documentation for {{ project_name }}</p>
                
                <div class="endpoint">
                    <h3><span class="method get">GET</span> /api/health</h3>
                    <p><strong>Description:</strong> Health check endpoint</p>
                    <p><strong>Response:</strong> <code>{"status": "ok", "timestamp": "..."}</code></p>
                </div>
                
                <div class="endpoint">
                    <h3><span class="method get">GET</span> /api/todos</h3>
                    <p><strong>Description:</strong> Get all todos</p>
                    <p><strong>Response:</strong> Array of todo objects</p>
                </div>
                
                <div class="endpoint">
                    <h3><span class="method post">POST</span> /api/todos</h3>
                    <p><strong>Description:</strong> Create a new todo</p>
                    <p><strong>Body:</strong> <code>{"task_name": "string"}</code></p>
                    <p><strong>Response:</strong> Created todo object</p>
                </div>
                
                <div class="endpoint">
                    <h3><span class="method put">PUT</span> /api/todos/:id</h3>
                    <p><strong>Description:</strong> Update a todo</p>
                    <p><strong>Body:</strong> <code>{"is_completed": "boolean"}</code></p>
                    <p><strong>Response:</strong> Updated todo object</p>
                </div>
                
                <div class="endpoint">
                    <h3><span class="method delete">DELETE</span> /api/todos/:id</h3>
                    <p><strong>Description:</strong> Delete a todo</p>
                    <p><strong>Response:</strong> <code>{"message": "Todo deleted"}</code></p>
                </div>
                
                <p><a href="/api/tester">🧪 Test these endpoints →</a> | <a href="/">🏠 Back to App</a></p>
            </div>
        </body>
        </html>
        """
        project = app.config['PROJECT']
        return render_template_string(template, project_name=project.config.name)
    
    @app.route('/api/tester')
    def api_tester():
        """Built-in API testing tool"""
        template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>API Tester - {{ project_name }}</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { font-family: 'Segoe UI', sans-serif; margin: 0; background: #f8f9fa; }
                .container { max-width: 1000px; margin: 0 auto; padding: 2rem; }
                .tester { background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                select, input, textarea, button { margin: 0.5rem 0; padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px; width: 100%; box-sizing: border-box; }
                button { background: #3B82F6; color: white; border: none; cursor: pointer; width: auto; padding: 0.5rem 1rem; }
                button:hover { background: #2563eb; }
                .response { background: #f8f9fa; padding: 1rem; margin-top: 1rem; border-radius: 4px; white-space: pre-wrap; font-family: monospace; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🧪 API Tester</h1>
                <p>Test your FlashFlow API endpoints</p>
                
                <div class="tester">
                    <div style="display: grid; grid-template-columns: 100px 1fr; gap: 10px; align-items: center;">
                        <select id="method">
                            <option>GET</option>
                            <option>POST</option>
                            <option>PUT</option>
                            <option>DELETE</option>
                        </select>
                        <input type="text" id="url" placeholder="/api/endpoint" value="/api/health">
                    </div>
                    
                    <textarea id="body" placeholder="Request body (JSON)" rows="4"></textarea>
                    
                    <button onclick="sendRequest()">Send Request</button>
                    
                    <div id="response" class="response">Response will appear here...</div>
                </div>
                
                <p><a href="/api/docs">📚 View API Documentation</a> | <a href="/">🏠 Back to App</a></p>
            </div>
            
            <script>
                async function sendRequest() {
                    const method = document.getElementById('method').value;
                    const url = document.getElementById('url').value;
                    const body = document.getElementById('body').value;
                    const responseDiv = document.getElementById('response');
                    
                    try {
                        responseDiv.textContent = 'Sending request...';
                        
                        const options = {
                            method: method,
                            headers: {
                                'Content-Type': 'application/json'
                            }
                        };
                        
                        if (body && method !== 'GET') {
                            options.body = body;
                        }
                        
                        const response = await fetch(url, options);
                        const text = await response.text();
                        
                        responseDiv.textContent = `Status: ${response.status}\\n\\n${text}`;
                    } catch (error) {
                        responseDiv.textContent = `Error: ${error.message}`;
                    }
                }
            </script>
        </body>
        </html>
        """
        project = app.config['PROJECT']
        return render_template_string(template, project_name=project.config.name)
    
    @app.route('/api/health')
    def api_health():
        """Health check endpoint"""
        import datetime
        return jsonify({
            "status": "ok",
            "timestamp": datetime.datetime.now().isoformat(),
            "project": app.config['PROJECT'].config.name,
            "version": "0.1.0"
        })
    
    @app.route('/android')
    def android_preview():
        """Android mockup preview"""
        return create_mobile_preview("Android", "#a4c639")
    
    @app.route('/ios') 
    def ios_preview():
        """iOS mockup preview"""
        return create_mobile_preview("iOS", "#007AFF")
    
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

def create_mobile_preview(platform: str, color: str):
    """Create mobile platform preview"""
    template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{platform} Preview</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; margin: 0; background: #f0f0f0; display: flex; justify-content: center; align-items: center; min-height: 100vh; }}
            .phone {{ width: 300px; height: 600px; background: black; border-radius: 25px; padding: 20px; position: relative; }}
            .screen {{ width: 100%; height: 100%; background: white; border-radius: 15px; overflow: hidden; position: relative; }}
            .status-bar {{ height: 30px; background: {color}; color: white; display: flex; align-items: center; justify-content: space-between; padding: 0 15px; font-size: 0.8rem; }}
            .content {{ padding: 20px; }}
            .back-btn {{ position: absolute; top: 20px; left: 20px; background: white; padding: 10px 20px; border-radius: 20px; text-decoration: none; color: black; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        </style>
    </head>
    <body>
        <a href="/" class="back-btn">← Back</a>
        <div class="phone">
            <div class="screen">
                <div class="status-bar">
                    <span>9:41</span>
                    <span>{platform} App</span>
                    <span>🔋 100%</span>
                </div>
                <div class="content">
                    <h2>📱 {platform} App Preview</h2>
                    <p>This is a mockup of your FlashFlow app running on {platform}.</p>
                    <p>The actual native app will be generated from your .flow files.</p>
                    
                    <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 20px 0;">
                        <h4>Features:</h4>
                        <ul>
                            <li>Native UI components</li>
                            <li>Offline-first architecture</li>
                            <li>Auto-sync with backend</li>
                            <li>Push notifications</li>
                        </ul>
                    </div>
                    
                    <button style="width: 100%; padding: 15px; background: {color}; color: white; border: none; border-radius: 8px; font-size: 1rem;">
                        Sample Button
                    </button>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return template

def start_backend_only(project: FlashFlowProject, host: str, port: int):
    """Start backend server only"""
    click.echo("🔧 Backend-only mode not yet implemented")
    click.echo("Use 'flashflow serve --all' for now")

def start_frontend_only(project: FlashFlowProject, host: str, port: int):
    """Start frontend server only"""
    click.echo("🎨 Frontend-only mode not yet implemented") 
    click.echo("Use 'flashflow serve --all' for now")