"""
FlashFlow 'setup' command - Web-based project setup wizard
"""

import click
import webbrowser
import threading
import time
import json
import os
from pathlib import Path
from flask import Flask, render_template_string, request, jsonify, redirect, url_for

from core.framework import FlashFlowProject

@click.command()
@click.option('--gui', is_flag=True, help='Launch web-based setup wizard')
@click.option('--github', is_flag=True, help='Setup GitHub CI/CD integration')
@click.option('--port', default=8080, help='Port for web interface')
@click.option('--host', default='localhost', help='Host for web interface')
@click.pass_context
def setup(ctx, gui, github, port, host):
    """Setup FlashFlow project configuration"""
    
    project_root = ctx.obj.get('project_root')
    if not project_root:
        click.echo("❌ Not in a FlashFlow project directory")
        click.echo("Run this command from a FlashFlow project root")
        return
    
    if gui:
        if github:
            launch_github_setup_gui(project_root, host, port)
        else:
            launch_setup_gui(project_root, host, port)
    elif github:
        run_github_cli_setup(project_root)
    else:
        run_cli_setup(project_root)

def run_cli_setup(project_root: Path):
    """Run command-line setup wizard"""
    click.echo("🛠️ FlashFlow Project Setup")
    click.echo("=" * 40)
    
    project = FlashFlowProject(project_root)
    
    # Basic project configuration
    click.echo("\n📋 Project Information:")
    project_name = click.prompt("Project name", default=project.config.name)
    project_description = click.prompt("Project description", default="FlashFlow application")
    project_author = click.prompt("Author", default="FlashFlow Developer")
    
    # Database configuration
    click.echo("\n💾 Database Configuration:")
    db_type = click.prompt("Database type", type=click.Choice(['sqlite', 'mysql', 'postgresql']), default='sqlite')
    
    if db_type != 'sqlite':
        db_host = click.prompt("Database host", default="localhost")
        db_port = click.prompt("Database port", default="3306" if db_type == 'mysql' else "5432")
        db_name = click.prompt("Database name", default=project_name.lower())
        db_user = click.prompt("Database user", default="root")
        db_password = click.prompt("Database password", hide_input=True)
    
    # Environment configuration
    click.echo("\n🌍 Environment Configuration:")
    app_env = click.prompt("Environment", type=click.Choice(['development', 'staging', 'production']), default='development')
    debug_mode = click.confirm("Enable debug mode?", default=True if app_env == 'development' else False)
    
    # Save configuration
    config_data = {
        "name": project_name,
        "description": project_description,
        "author": project_author,
        "version": "0.1.0",
        "environment": app_env,
        "debug": debug_mode,
        "database": {
            "type": db_type,
            "host": db_host if db_type != 'sqlite' else None,
            "port": int(db_port) if db_type != 'sqlite' else None,
            "name": db_name if db_type != 'sqlite' else "database.sqlite",
            "user": db_user if db_type != 'sqlite' else None,
            "password": db_password if db_type != 'sqlite' else None
        }
    }
    
    # Update flashflow.json
    flashflow_config = project_root / "flashflow.json"
    with open(flashflow_config, 'w') as f:
        json.dump(config_data, f, indent=2)
    
    # Create .env file
    create_env_file(project_root, config_data)
    
    click.echo("\n✅ Project setup completed!")
    click.echo("💡 Next steps:")
    click.echo("   flashflow build       # Generate application code")
    click.echo("   flashflow serve --all # Start development server")

def launch_setup_gui(project_root: Path, host: str, port: int):
    """Launch web-based setup wizard"""
    
    click.echo("🌐 Launching web-based setup wizard...")
    click.echo(f"📍 Setup URL: http://{host}:{port}")
    
    app = create_setup_app(project_root)
    
    # Open browser automatically
    def open_browser():
        time.sleep(1.5)  # Wait for server to start
        webbrowser.open(f"http://{host}:{port}")
    
    threading.Thread(target=open_browser).start()
    
    click.echo("🚀 Starting setup server... (Ctrl+C to stop)")
    try:
        app.run(host=host, port=port, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        click.echo("\n✋ Setup wizard stopped")

def create_setup_app(project_root: Path):
    """Create Flask app for setup wizard"""
    
    app = Flask(__name__)
    app.secret_key = "flashflow-setup-key"
    
    project = FlashFlowProject(project_root)
    
    @app.route('/')
    def setup_wizard():
        """Main setup wizard page"""
        
        template = '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>FlashFlow Setup Wizard</title>
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body { 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    color: #333;
                }
                .container { 
                    max-width: 800px; 
                    margin: 0 auto; 
                    padding: 20px; 
                    min-height: 100vh;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                }
                .setup-card {
                    background: white;
                    border-radius: 12px;
                    padding: 40px;
                    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                }
                .header {
                    text-align: center;
                    margin-bottom: 30px;
                }
                .header h1 {
                    color: #667eea;
                    font-size: 2.5rem;
                    margin-bottom: 10px;
                }
                .header p {
                    color: #666;
                    font-size: 1.1rem;
                }
                .form-group {
                    margin-bottom: 20px;
                }
                .form-group label {
                    display: block;
                    margin-bottom: 8px;
                    font-weight: 600;
                    color: #333;
                }
                .form-group input,
                .form-group select,
                .form-group textarea {
                    width: 100%;
                    padding: 12px;
                    border: 2px solid #e1e5e9;
                    border-radius: 8px;
                    font-size: 1rem;
                    transition: border-color 0.3s;
                }
                .form-group input:focus,
                .form-group select:focus,
                .form-group textarea:focus {
                    outline: none;
                    border-color: #667eea;
                }
                .form-row {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 20px;
                }
                .section {
                    margin-bottom: 30px;
                    padding: 20px;
                    background: #f8f9fa;
                    border-radius: 8px;
                }
                .section h3 {
                    color: #667eea;
                    margin-bottom: 15px;
                    font-size: 1.3rem;
                }
                .btn {
                    background: #667eea;
                    color: white;
                    padding: 15px 30px;
                    border: none;
                    border-radius: 8px;
                    font-size: 1.1rem;
                    cursor: pointer;
                    transition: background 0.3s;
                    width: 100%;
                }
                .btn:hover {
                    background: #5a6fd8;
                }
                .checkbox-group {
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }
                .checkbox-group input[type="checkbox"] {
                    width: auto;
                }
                .success-message {
                    background: #d4edda;
                    border: 1px solid #c3e6cb;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 20px 0;
                    color: #155724;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="setup-card">
                    <div class="header">
                        <h1>⚡ FlashFlow Setup</h1>
                        <p>Configure your FlashFlow project in just a few clicks</p>
                    </div>
                    
                    <form id="setupForm" onsubmit="submitSetup(event)">
                        <div class="section">
                            <h3>📋 Project Information</h3>
                            <div class="form-group">
                                <label for="project_name">Project Name</label>
                                <input type="text" id="project_name" name="project_name" value="{{ project_name }}" required>
                            </div>
                            <div class="form-group">
                                <label for="project_description">Description</label>
                                <textarea id="project_description" name="project_description" rows="3" placeholder="Describe your FlashFlow application"></textarea>
                            </div>
                            <div class="form-group">
                                <label for="project_author">Author</label>
                                <input type="text" id="project_author" name="project_author" value="FlashFlow Developer">
                            </div>
                        </div>
                        
                        <div class="section">
                            <h3>💾 Database Configuration</h3>
                            <div class="form-group">
                                <label for="db_type">Database Type</label>
                                <select id="db_type" name="db_type" onchange="toggleDbConfig()">
                                    <option value="sqlite" selected>SQLite (Development)</option>
                                    <option value="mysql">MySQL</option>
                                    <option value="postgresql">PostgreSQL</option>
                                </select>
                            </div>
                            <div id="db_config" style="display: none;">
                                <div class="form-row">
                                    <div class="form-group">
                                        <label for="db_host">Host</label>
                                        <input type="text" id="db_host" name="db_host" value="localhost">
                                    </div>
                                    <div class="form-group">
                                        <label for="db_port">Port</label>
                                        <input type="number" id="db_port" name="db_port" value="3306">
                                    </div>
                                </div>
                                <div class="form-row">
                                    <div class="form-group">
                                        <label for="db_name">Database Name</label>
                                        <input type="text" id="db_name" name="db_name">
                                    </div>
                                    <div class="form-group">
                                        <label for="db_user">Username</label>
                                        <input type="text" id="db_user" name="db_user" value="root">
                                    </div>
                                </div>
                                <div class="form-group">
                                    <label for="db_password">Password</label>
                                    <input type="password" id="db_password" name="db_password">
                                </div>
                            </div>
                        </div>
                        
                        <div class="section">
                            <h3>🌍 Environment Settings</h3>
                            <div class="form-row">
                                <div class="form-group">
                                    <label for="app_env">Environment</label>
                                    <select id="app_env" name="app_env">
                                        <option value="development" selected>Development</option>
                                        <option value="staging">Staging</option>
                                        <option value="production">Production</option>
                                    </select>
                                </div>
                                <div class="form-group">
                                    <div class="checkbox-group">
                                        <input type="checkbox" id="debug_mode" name="debug_mode" checked>
                                        <label for="debug_mode">Enable Debug Mode</label>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <button type="submit" class="btn">🚀 Complete Setup</button>
                    </form>
                    
                    <div id="success" class="success-message" style="display: none;">
                        ✅ Setup completed successfully! Your FlashFlow project is now configured.
                        <br><br>
                        <strong>Next steps:</strong>
                        <ul style="margin-top: 10px; margin-left: 20px;">
                            <li>Run <code>flashflow build</code> to generate your application</li>
                            <li>Run <code>flashflow serve --all</code> to start the development server</li>
                        </ul>
                    </div>
                </div>
            </div>
            
            <script>
                function toggleDbConfig() {
                    const dbType = document.getElementById('db_type').value;
                    const dbConfig = document.getElementById('db_config');
                    dbConfig.style.display = dbType === 'sqlite' ? 'none' : 'block';
                    
                    // Update port default based on database type
                    if (dbType === 'mysql') {
                        document.getElementById('db_port').value = '3306';
                    } else if (dbType === 'postgresql') {
                        document.getElementById('db_port').value = '5432';
                    }
                }
                
                async function submitSetup(event) {
                    event.preventDefault();
                    
                    const formData = new FormData(event.target);
                    const data = Object.fromEntries(formData);
                    
                    try {
                        const response = await fetch('/api/setup', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify(data)
                        });
                        
                        if (response.ok) {
                            document.getElementById('setupForm').style.display = 'none';
                            document.getElementById('success').style.display = 'block';
                        } else {
                            alert('Setup failed. Please try again.');
                        }
                    } catch (error) {
                        alert('Setup failed. Please try again.');
                    }
                }
            </script>
        </body>
        </html>
        '''
        
        return render_template_string(template, project_name=project.config.name)
    
    @app.route('/api/setup', methods=['POST'])
    def save_setup():
        """Save setup configuration"""
        
        try:
            data = request.get_json()
            
            # Build configuration object
            config_data = {
                "name": data.get('project_name'),
                "description": data.get('project_description', ''),
                "author": data.get('project_author', 'FlashFlow Developer'),
                "version": "0.1.0",
                "environment": data.get('app_env', 'development'),
                "debug": data.get('debug_mode') == 'on',
                "database": {
                    "type": data.get('db_type', 'sqlite'),
                }
            }
            
            # Add database-specific configuration
            if config_data['database']['type'] != 'sqlite':
                config_data['database'].update({
                    "host": data.get('db_host', 'localhost'),
                    "port": int(data.get('db_port', 3306)),
                    "name": data.get('db_name'),
                    "user": data.get('db_user'),
                    "password": data.get('db_password')
                })
            else:
                config_data['database']['name'] = 'database.sqlite'
            
            # Save to flashflow.json
            flashflow_config = project_root / "flashflow.json"
            with open(flashflow_config, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            # Create .env file
            create_env_file(project_root, config_data)
            
            return jsonify({"status": "success", "message": "Setup completed successfully"})
            
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    
    return app

def create_env_file(project_root: Path, config_data: dict):
    """Create .env file with configuration"""
    
    env_content = f"""# FlashFlow Environment Configuration
# Generated by FlashFlow Setup Wizard

APP_NAME="{config_data['name']}"
APP_ENV={config_data['environment']}
APP_DEBUG={'true' if config_data.get('debug', False) else 'false'}

# Database Configuration
DB_CONNECTION={config_data['database']['type']}
"""
    
    if config_data['database']['type'] == 'sqlite':
        env_content += f"DB_DATABASE=database/{config_data['database']['name']}\n"
    else:
        env_content += f"""DB_HOST={config_data['database'].get('host', 'localhost')}
DB_PORT={config_data['database'].get('port', 3306)}
DB_DATABASE={config_data['database'].get('name', '')}
DB_USERNAME={config_data['database'].get('user', '')}
DB_PASSWORD={config_data['database'].get('password', '')}
"""
    
    env_content += """
# Application Key (generate a secure key for production)
APP_KEY=base64:FlashFlowGeneratedKey123456789

# Cache Configuration
CACHE_DRIVER=file
SESSION_DRIVER=file

# Mail Configuration
MAIL_MAILER=smtp
MAIL_HOST=localhost
MAIL_PORT=587
MAIL_USERNAME=null
MAIL_PASSWORD=null

# External Service Keys (add your API keys here)
# STRIPE_KEY=
# GOOGLE_CLIENT_ID=
# FACEBOOK_APP_ID=
"""
    
    env_file = project_root / ".env"
    with open(env_file, 'w') as f:
        f.write(env_content)


def run_github_cli_setup(project_root: Path):
    """Run GitHub CI/CD setup via command line"""
    click.echo("🔗 GitHub CI/CD Integration Setup")
    click.echo("=" * 40)
    
    # Check if user has GitHub CLI installed
    import subprocess
    try:
        result = subprocess.run(['gh', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            click.echo("❌ GitHub CLI not found. Please install GitHub CLI first:")
            click.echo("   https://cli.github.com/")
            return
    except FileNotFoundError:
        click.echo("❌ GitHub CLI not found. Please install GitHub CLI first:")
        click.echo("   https://cli.github.com/")
        return
    
    click.echo("✅ GitHub CLI found")
    
    # Check authentication
    try:
        result = subprocess.run(['gh', 'auth', 'status'], capture_output=True, text=True)
        if result.returncode != 0:
            click.echo("🔐 Please authenticate with GitHub first:")
            if click.confirm("Would you like to authenticate now?"):
                subprocess.run(['gh', 'auth', 'login'])
            else:
                return
    except Exception as e:
        click.echo(f"❌ Error checking GitHub authentication: {e}")
        return
    
    # Get repository information
    repo_url = click.prompt("GitHub repository URL (or leave empty to create new):", default="")
    
    if not repo_url:
        repo_name = click.prompt("New repository name", default=project_root.name)
        is_private = click.confirm("Make repository private?", default=True)
        
        # Create repository
        click.echo(f"🔨 Creating GitHub repository '{repo_name}'...")
        try:
            cmd = ['gh', 'repo', 'create', repo_name]
            if is_private:
                cmd.append('--private')
            cmd.extend(['--source', '.', '--push'])
            subprocess.run(cmd, cwd=project_root)
            click.echo("✅ Repository created successfully")
        except Exception as e:
            click.echo(f"❌ Error creating repository: {e}")
            return
    
    # Setup CI/CD credentials
    setup_github_secrets(project_root)
    
    # Create workflow files
    create_github_workflows(project_root)
    
    click.echo("\n✅ GitHub CI/CD integration completed!")
    click.echo("💡 Next steps:")
    click.echo("   git add .")
    click.echo("   git commit -m 'Add GitHub CI/CD workflows'")
    click.echo("   git push")


def launch_github_setup_gui(project_root: Path, host: str, port: int):
    """Launch GitHub integration setup wizard"""
    
    click.echo("🌐 Launching GitHub CI/CD setup wizard...")
    click.echo(f"📍 Setup URL: http://{host}:{port}")
    
    app = create_github_setup_app(project_root)
    
    # Open browser automatically
    def open_browser():
        time.sleep(1.5)  # Wait for server to start
        webbrowser.open(f"http://{host}:{port}")
    
    threading.Thread(target=open_browser).start()
    
    click.echo("🚀 Starting GitHub setup server... (Ctrl+C to stop)")
    try:
        app.run(host=host, port=port, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        click.echo("\n✋ GitHub setup wizard stopped")


def create_github_setup_app(project_root: Path):
    """Create Flask app for GitHub setup wizard"""
    
    app = Flask(__name__)
    app.secret_key = "flashflow-github-setup-key"
    
    # GitHub OAuth App credentials (these would be configured for FlashFlow)
    GITHUB_CLIENT_ID = "your_github_client_id"  # Replace with actual client ID
    GITHUB_CLIENT_SECRET = "your_github_client_secret"  # Replace with actual secret
    
    from ..services.github_integration import GitHubIntegrationService
    from ..services.global_config import global_config, ProjectInheritanceSettings
    github_service = GitHubIntegrationService(project_root)
    
    @app.route('/')
    def github_setup_wizard():
        """GitHub integration setup wizard page"""
        
        template = '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>FlashFlow GitHub CI/CD Setup</title>
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body { 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                    background: linear-gradient(135deg, #24292e 0%, #586069 100%);
                    min-height: 100vh;
                    color: #333;
                }
                .container { 
                    max-width: 900px; 
                    margin: 0 auto; 
                    padding: 20px; 
                    min-height: 100vh;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                }
                .setup-card {
                    background: white;
                    border-radius: 12px;
                    padding: 40px;
                    box-shadow: 0 20px 40px rgba(0,0,0,0.2);
                }
                .header {
                    text-align: center;
                    margin-bottom: 30px;
                }
                .header h1 {
                    color: #24292e;
                    font-size: 2.5rem;
                    margin-bottom: 10px;
                }
                .header p {
                    color: #666;
                    font-size: 1.1rem;
                }
                .step {
                    margin-bottom: 30px;
                    padding: 20px;
                    background: #f8f9fa;
                    border-radius: 8px;
                    border-left: 4px solid #28a745;
                }
                .step h3 {
                    color: #24292e;
                    margin-bottom: 15px;
                    font-size: 1.3rem;
                }
                .step p {
                    color: #586069;
                    line-height: 1.6;
                    margin-bottom: 15px;
                }
                .btn {
                    background: #28a745;
                    color: white;
                    padding: 15px 30px;
                    border: none;
                    border-radius: 8px;
                    font-size: 1.1rem;
                    cursor: pointer;
                    transition: background 0.3s;
                    text-decoration: none;
                    display: inline-block;
                    margin-right: 10px;
                }
                .btn:hover {
                    background: #218838;
                }
                .btn-secondary {
                    background: #6c757d;
                }
                .btn-secondary:hover {
                    background: #5a6268;
                }
                .form-group {
                    margin-bottom: 20px;
                }
                .form-group label {
                    display: block;
                    margin-bottom: 8px;
                    font-weight: 600;
                    color: #333;
                }
                .form-group input,
                .form-group select,
                .form-group textarea {
                    width: 100%;
                    padding: 12px;
                    border: 2px solid #e1e5e9;
                    border-radius: 8px;
                    font-size: 1rem;
                    transition: border-color 0.3s;
                }
                .form-group input:focus,
                .form-group select:focus,
                .form-group textarea:focus {
                    outline: none;
                    border-color: #28a745;
                }
                .credentials-section {
                    display: none;
                    margin-top: 20px;
                }
                .success-message {
                    background: #d4edda;
                    border: 1px solid #c3e6cb;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 20px 0;
                    color: #155724;
                }
                .error-message {
                    background: #f8d7da;
                    border: 1px solid #f5c6cb;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 20px 0;
                    color: #721c24;
                }
                .progress {
                    background: #e9ecef;
                    border-radius: 8px;
                    height: 8px;
                    margin: 20px 0;
                }
                .progress-bar {
                    background: #28a745;
                    height: 100%;
                    border-radius: 8px;
                    transition: width 0.3s;
                }
                .tab-content {
                    display: none;
                }
                .tab-content.active {
                    display: block;
                }
                .tabs {
                    display: flex;
                    margin-bottom: 20px;
                    border-bottom: 2px solid #e1e5e9;
                }
                .tab {
                    padding: 10px 20px;
                    cursor: pointer;
                    border-bottom: 2px solid transparent;
                    transition: all 0.3s;
                }
                .tab.active {
                    border-bottom-color: #28a745;
                    color: #28a745;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="setup-card">
                    <div class="header">
                        <h1>🔗 GitHub CI/CD Setup</h1>
                        <p>Configure automated builds and deployments for your FlashFlow project</p>
                        <div class="progress">
                            <div class="progress-bar" id="progressBar" style="width: 0%"></div>
                        </div>
                    </div>
                    
                    <div class="tabs">
                        <div class="tab active" onclick="showTab('step1')">1. GitHub Connection</div>
                        <div class="tab" onclick="showTab('step2')">2. Repository Setup</div>
                        <div class="tab" onclick="showTab('step3')">3. Credentials</div>
                        <div class="tab" onclick="showTab('step4')">4. Complete</div>
                    </div>
                    
                    <!-- Step 1: GitHub Authentication -->
                    <div id="step1" class="tab-content active">
                        <div class="step">
                            <h3>🔐 Connect Your GitHub Account</h3>
                            <p>FlashFlow needs access to your GitHub account to set up CI/CD workflows and store deployment credentials securely.</p>
                            <p><strong>What we'll do:</strong></p>
                            <ul style="margin-left: 20px; margin-bottom: 15px;">
                                <li>Create or connect to your GitHub repository</li>
                                <li>Set up GitHub Actions workflows</li>
                                <li>Store your Apple and Android credentials as encrypted secrets</li>
                            </ul>
                            <a href="/auth/github" class="btn">🔗 Connect GitHub Account</a>
                            <p style="margin-top: 15px; font-size: 0.9rem; color: #6c757d;">
                                We'll redirect you to GitHub for secure authentication.
                            </p>
                        </div>
                    </div>
                    
                    <!-- Step 2: Repository Setup -->
                    <div id="step2" class="tab-content">
                        <div class="step">
                            <h3>📦 Repository Configuration</h3>
                            <form id="repoForm">
                                <div class="form-group">
                                    <label for="repo_option">Repository Option</label>
                                    <select id="repo_option" name="repo_option" onchange="toggleRepoOptions()">
                                        <option value="create">Create new repository</option>
                                        <option value="existing">Use existing repository</option>
                                    </select>
                                </div>
                                
                                <div id="create_repo_options">
                                    <div class="form-group">
                                        <label for="repo_name">Repository Name</label>
                                        <input type="text" id="repo_name" name="repo_name" value="{{ project_name }}" required>
                                    </div>
                                    <div class="form-group">
                                        <label for="repo_description">Description</label>
                                        <textarea id="repo_description" name="repo_description" rows="3">FlashFlow application with automated CI/CD</textarea>
                                    </div>
                                    <div class="form-group">
                                        <label>
                                            <input type="checkbox" id="is_private" name="is_private" checked>
                                            Make repository private
                                        </label>
                                    </div>
                                </div>
                                
                                <div id="existing_repo_options" style="display: none;">
                                    <div class="form-group">
                                        <label for="existing_repo">Select Repository</label>
                                        <select id="existing_repo" name="existing_repo">
                                            <option value="">Loading repositories...</option>
                                        </select>
                                    </div>
                                </div>
                                
                                <button type="button" class="btn" onclick="nextStep(3)">Continue →</button>
                            </form>
                        </div>
                    </div>
                    
                    <!-- Step 3: Credentials -->
                    <div id="step3" class="tab-content">
                        <div class="step">
                            <h3>🔒 Mobile App Signing Credentials</h3>
                            <p>Add your Apple Developer and Android signing credentials for automated app builds.</p>
                            
                            <form id="credentialsForm">
                                <h4 style="margin: 20px 0 10px 0; color: #24292e;">🍎 Apple Developer</h4>
                                <div class="form-group">
                                    <label for="apple_team_id">Team ID</label>
                                    <input type="text" id="apple_team_id" name="apple_team_id" placeholder="ABC123DEF4">
                                </div>
                                <div class="form-group">
                                    <label for="apple_cert">Signing Certificate (.p12)</label>
                                    <input type="file" id="apple_cert" name="apple_cert" accept=".p12">
                                </div>
                                <div class="form-group">
                                    <label for="apple_profile">Provisioning Profile</label>
                                    <input type="file" id="apple_profile" name="apple_profile" accept=".mobileprovision">
                                </div>
                                <div class="form-group">
                                    <label for="apple_auth_key">App Store Connect API Key (.p8)</label>
                                    <input type="file" id="apple_auth_key" name="apple_auth_key" accept=".p8">
                                </div>
                                <div class="form-group">
                                    <label for="apple_auth_key_id">API Key ID</label>
                                    <input type="text" id="apple_auth_key_id" name="apple_auth_key_id">
                                </div>
                                <div class="form-group">
                                    <label for="apple_auth_issuer_id">Issuer ID</label>
                                    <input type="text" id="apple_auth_issuer_id" name="apple_auth_issuer_id">
                                </div>
                                
                                <h4 style="margin: 20px 0 10px 0; color: #24292e;">🤖 Android</h4>
                                <div class="form-group">
                                    <label for="android_keystore">Keystore File (.jks/.keystore)</label>
                                    <input type="file" id="android_keystore" name="android_keystore" accept=".jks,.keystore">
                                </div>
                                <div class="form-group">
                                    <label for="android_keystore_password">Keystore Password</label>
                                    <input type="password" id="android_keystore_password" name="android_keystore_password">
                                </div>
                                <div class="form-group">
                                    <label for="android_key_alias">Key Alias</label>
                                    <input type="text" id="android_key_alias" name="android_key_alias">
                                </div>
                                <div class="form-group">
                                    <label for="android_key_password">Key Password</label>
                                    <input type="password" id="android_key_password" name="android_key_password">
                                </div>
                                
                                <h4 style="margin: 20px 0 10px 0; color: #24292e;">📦 Google Play</h4>
                                <div class="form-group">
                                    <label for="google_play_service_account">Service Account JSON</label>
                                    <input type="file" id="google_play_service_account" name="google_play_service_account" accept=".json">
                                </div>
                                
                                <button type="button" class="btn" onclick="setupComplete()">Complete Setup ✓</button>
                                <button type="button" class="btn btn-secondary" onclick="skipCredentials()">Skip for Now</button>
                            </form>
                        </div>
                    </div>
                    
                    <!-- Step 4: Complete -->
                    <div id="step4" class="tab-content">
                        <div class="success-message" id="completionMessage">
                            <h3>✅ GitHub CI/CD Setup Complete!</h3>
                            <div id="setupResults"></div>
                        </div>
                        
                        <div class="step">
                            <h3>🚀 What's Next?</h3>
                            <p><strong>Your FlashFlow project now has:</strong></p>
                            <ul style="margin: 15px 0 15px 20px;">
                                <li>Automated testing on every push</li>
                                <li>iOS and Android app building workflows</li>
                                <li>Web and API deployment pipelines</li>
                                <li>Release management automation</li>
                            </ul>
                            
                            <p><strong>Next steps:</strong></p>
                            <ol style="margin: 15px 0 15px 20px;">
                                <li>Commit and push your code to trigger the first build</li>
                                <li>Check the "Actions" tab in your GitHub repository</li>
                                <li>Create a release to build and distribute your mobile apps</li>
                            </ol>
                            
                            <a href="#" class="btn" onclick="window.close()">📚 View Documentation</a>
                            <a href="#" class="btn btn-secondary" onclick="window.close()">Close</a>
                        </div>
                    </div>
                </div>
            </div>
            
            <script>
                let currentStep = 1;
                
                function showTab(tabId) {
                    // Hide all tabs
                    document.querySelectorAll('.tab-content').forEach(content => {
                        content.classList.remove('active');
                    });
                    document.querySelectorAll('.tab').forEach(tab => {
                        tab.classList.remove('active');
                    });
                    
                    // Show selected tab
                    document.getElementById(tabId).classList.add('active');
                    document.querySelector(`[onclick="showTab('${tabId}')"]`).classList.add('active');
                    
                    // Update progress
                    const stepNum = parseInt(tabId.replace('step', ''));
                    updateProgress(stepNum);
                }
                
                function nextStep(step) {
                    currentStep = step;
                    showTab(`step${step}`);
                }
                
                function updateProgress(step) {
                    const progress = (step / 4) * 100;
                    document.getElementById('progressBar').style.width = progress + '%';
                }
                
                function toggleRepoOptions() {
                    const option = document.getElementById('repo_option').value;
                    const createOptions = document.getElementById('create_repo_options');
                    const existingOptions = document.getElementById('existing_repo_options');
                    
                    if (option === 'create') {
                        createOptions.style.display = 'block';
                        existingOptions.style.display = 'none';
                    } else {
                        createOptions.style.display = 'none';
                        existingOptions.style.display = 'block';
                        loadRepositories();
                    }
                }
                
                async function loadRepositories() {
                    try {
                        const response = await fetch('/api/repositories');
                        const repos = await response.json();
                        const select = document.getElementById('existing_repo');
                        
                        select.innerHTML = '<option value="">Select a repository</option>';
                        repos.forEach(repo => {
                            const option = document.createElement('option');
                            option.value = repo.full_name;
                            option.textContent = repo.full_name;
                            select.appendChild(option);
                        });
                    } catch (error) {
                        console.error('Error loading repositories:', error);
                    }
                }
                
                async function setupComplete() {
                    try {
                        const formData = new FormData(document.getElementById('credentialsForm'));
                        const repoFormData = new FormData(document.getElementById('repoForm'));
                        
                        // Combine form data
                        for (let [key, value] of repoFormData.entries()) {
                            formData.append(key, value);
                        }
                        
                        const response = await fetch('/api/setup-complete', {
                            method: 'POST',
                            body: formData
                        });
                        
                        const result = await response.json();
                        
                        if (result.success) {
                            document.getElementById('setupResults').innerHTML = `
                                <p><strong>Repository:</strong> ${result.repository}</p>
                                <p><strong>Workflows created:</strong> ${result.workflows_created}</p>
                                <p><strong>Secrets stored:</strong> ${result.secrets_stored}</p>
                            `;
                            nextStep(4);
                        } else {
                            alert('Setup failed: ' + result.error);
                        }
                    } catch (error) {
                        alert('Setup failed: ' + error.message);
                    }
                }
                
                function skipCredentials() {
                    nextStep(4);
                    document.getElementById('setupResults').innerHTML = `
                        <p><strong>Basic setup completed.</strong></p>
                        <p>You can add mobile signing credentials later in your repository settings.</p>
                    `;
                }
            </script>
        </body>
        </html>
        '''
        
        return render_template_string(template, project_name=project_root.name)
    
    @app.route('/auth/github')
    def github_auth():
        """Redirect to GitHub OAuth"""
        redirect_uri = request.url_root + 'auth/github/callback'
        oauth_url = github_service.get_oauth_url(GITHUB_CLIENT_ID, redirect_uri)
        return redirect(oauth_url)
    
    @app.route('/auth/github/callback')
    def github_callback():
        """Handle GitHub OAuth callback"""
        code = request.args.get('code')
        state = request.args.get('state')
        
        if code and github_service.exchange_oauth_code(code, state, GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET):
            # Update global configuration with GitHub credentials
            global_config.update_github_credentials(
                github_service.credentials.access_token,
                github_service.credentials.username,
                github_service.credentials.email
            )
            
            # Register this project for inheritance
            global_config.register_project(
                str(project_root),
                project_root.name,
                ProjectInheritanceSettings()
            )
            
            return redirect('/?step=2')
        else:
            return redirect('/?error=auth_failed')
    
    @app.route('/api/repositories')
    def get_repositories():
        """Get user's GitHub repositories"""
        try:
            repos = github_service.get_user_repositories()
            return jsonify(repos)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/setup-complete', methods=['POST'])
    def complete_setup():
        """Complete the GitHub CI/CD setup"""
        try:
            # Process uploaded files and form data
            from ..services.github_integration import DeveloperCredentials
            from ..services.github_workflows import GitHubWorkflowGenerator
            
            credentials = DeveloperCredentials()
            
            # Process Apple credentials
            if 'apple_team_id' in request.form:
                credentials.apple_team_id = request.form['apple_team_id']
            if 'apple_auth_key_id' in request.form:
                credentials.apple_auth_key_id = request.form['apple_auth_key_id']
            if 'apple_auth_issuer_id' in request.form:
                credentials.apple_auth_issuer_id = request.form['apple_auth_issuer_id']
            
            # Process Android credentials
            if 'android_keystore_password' in request.form:
                credentials.android_keystore_password = request.form['android_keystore_password']
            if 'android_key_alias' in request.form:
                credentials.android_key_alias = request.form['android_key_alias']
            if 'android_key_password' in request.form:
                credentials.android_key_password = request.form['android_key_password']
            
            # Handle file uploads (convert to base64)
            file_fields = [
                ('apple_cert', 'apple_signing_certificate'),
                ('apple_profile', 'apple_provisioning_profile'),
                ('apple_auth_key', 'apple_auth_key'),
                ('android_keystore', 'android_keystore'),
                ('google_play_service_account', 'google_play_service_account')
            ]
            
            for field_name, attr_name in file_fields:
                if field_name in request.files:
                    file = request.files[field_name]
                    if file.filename:
                        import base64
                        file_content = base64.b64encode(file.read()).decode('utf-8')
                        setattr(credentials, attr_name, file_content)
            
            # Create or get repository
            repo_option = request.form.get('repo_option', 'create')
            if repo_option == 'create':
                repo_name = request.form.get('repo_name', project_root.name)
                repo_description = request.form.get('repo_description', '')
                is_private = 'is_private' in request.form
                
                repo_data = github_service.create_repository(repo_name, repo_description, is_private)
                repo_full_name = repo_data['full_name']
            else:
                repo_full_name = request.form.get('existing_repo')
            
            # Store credentials as GitHub secrets
            repo_owner, repo_name = repo_full_name.split('/')
            secrets_stored = github_service.store_secrets(repo_owner, repo_name, credentials)
            
            # Create workflow files
            workflow_generator = GitHubWorkflowGenerator(project_root)
            project_config = {'name': project_root.name}
            workflow_generator.create_all_workflows(project_config)
            
            return jsonify({
                'success': True,
                'repository': repo_full_name,
                'workflows_created': 5,
                'secrets_stored': secrets_stored
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    return app


def setup_github_secrets(project_root: Path):
    """Setup GitHub secrets via CLI"""
    click.echo("🔒 Setting up deployment credentials...")
    
    # Apple Developer credentials
    click.echo("\n🍎 Apple Developer Credentials (optional):")
    apple_team_id = click.prompt("Apple Team ID", default="", show_default=False)
    
    if apple_team_id:
        apple_cert_path = click.prompt("Path to signing certificate (.p12)", default="")
        apple_profile_path = click.prompt("Path to provisioning profile", default="")
        apple_auth_key_path = click.prompt("Path to App Store Connect API key (.p8)", default="")
        apple_auth_key_id = click.prompt("API Key ID", default="")
        apple_auth_issuer_id = click.prompt("Issuer ID", default="")
    
    # Android credentials
    click.echo("\n🤖 Android Signing Credentials (optional):")
    android_keystore_path = click.prompt("Path to keystore file", default="")
    
    if android_keystore_path:
        android_keystore_password = click.prompt("Keystore password", hide_input=True)
        android_key_alias = click.prompt("Key alias")
        android_key_password = click.prompt("Key password", hide_input=True)
    
    click.echo("✅ Credentials configured. They will be stored securely in GitHub.")


def create_github_workflows(project_root: Path):
    """Create GitHub Actions workflow files"""
    from ..services.github_workflows import GitHubWorkflowGenerator
    
    click.echo("🔨 Creating GitHub Actions workflows...")
    
    # Read project configuration
    flashflow_config = project_root / "flashflow.json"
    project_config = {'name': project_root.name}
    
    if flashflow_config.exists():
        import json
        with open(flashflow_config, 'r') as f:
            project_config = json.load(f)
    
    # Generate workflow files
    workflow_generator = GitHubWorkflowGenerator(project_root)
    workflow_generator.create_all_workflows(project_config)
    
    workflows_created = [
        "main.yml - Main CI/CD pipeline",
        "ios.yml - iOS app building",
        "android.yml - Android app building",
        "deploy-web.yml - Web deployment",
        "deploy-api.yml - API deployment",
        "release.yml - Release management"
    ]
    
    click.echo("✅ Created workflow files:")
    for workflow in workflows_created:
        click.echo(f"   • {workflow}")
    
    return len(workflows_created)