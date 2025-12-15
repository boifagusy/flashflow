"""
FlashFlow 'build' command - Generate application code
"""

import click
import os
import json
import subprocess
import sys
from pathlib import Path
from core.framework import FlashFlowProject, FlashFlowIR
from core.parser.parser import FlowParser
# Temporarily remove backend generator import to avoid errors
# from generators.backend.backend import BackendGenerator
from generators.web.flet_frontend import FletFrontendGenerator
from generators.mobile.mobile import MobileGenerator
from generators.desktop.simple_desktop import SimpleDesktopGenerator

def check_go_service_available(service_name):
    """Check if a Go service executable is available."""
    service_path = Path(__file__).parent.parent.parent / "go-services" / service_name / f"{service_name}.exe"
    return service_path.exists()

def run_go_build_service(target, env, watch):
    """Run the Go build service if available."""
    try:
        # Determine the path to the build service executable
        build_service_path = Path(__file__).parent.parent.parent / "go-services" / "build-service" / "build-service.exe"
        
        if not build_service_path.exists():
            return False
            
        # Prepare arguments
        args = [str(build_service_path), str(Path.cwd())]
        if watch:
            args.append("--watch")
            
        # Set environment variables
        env_vars = os.environ.copy()
        env_vars["FLASHFLOW_TARGET"] = target
        env_vars["FLASHFLOW_ENV"] = env
        env_vars["FLASHFLOW_WATCH"] = str(watch).lower()
        
        # Run the Go build service
        result = subprocess.run(args, env=env_vars, capture_output=True, text=True)
        
        if result.returncode == 0:
            click.echo(result.stdout)
            return True
        else:
            click.echo(f"Go build service failed: {result.stderr}")
            return False
            
    except Exception as e:
        click.echo(f"Failed to run Go build service: {str(e)}")
        return False

@click.command()
@click.option('--target', '-t', default='all', help='Build target (all, backend, frontend, mobile, ios, android, desktop, windows, macos, linux)')
@click.option('--env', '-e', default='development', help='Build environment (development, production)')
@click.option('--watch', '-w', is_flag=True, help='Watch for file changes and rebuild')
def build(target, env, watch):
    """Generate application code from .flow files"""
    
    # Check if we're in a FlashFlow project
    project = FlashFlowProject(Path.cwd())
    if not project.exists():
        click.echo("❌ Not in a FlashFlow project directory")
        click.echo("Run 'flashflow new <project_name>' to create a new project first")
        return
    
    # Try to use Go build service if available for better performance
    if check_go_service_available("build-service"):
        click.echo("🚀 Using optimized Go build service for faster builds...")
        if run_go_build_service(target, env, watch):
            return
    
    # Fallback to Python implementation
    try:
        click.echo(f"🔨 Building FlashFlow project: {project.config.name}")
        click.echo(f"📦 Target: {target}")
        click.echo(f"🌍 Environment: {env}")
        
        if watch:
            click.echo("👀 Watch mode enabled - building on file changes...")
            build_with_watch(project, target, env)
        else:
            build_once(project, target, env)
            
    except Exception as e:
        click.echo(f"❌ Build failed: {str(e)}")

def build_once(project: FlashFlowProject, target: str, env: str):
    """Build the project once"""
    
    # Parse all .flow files
    click.echo("📖 Parsing .flow files...")
    parser = FlowParser()
    ir = FlashFlowIR()
    
    flow_files = project.get_flow_files()
    if not flow_files:
        click.echo("⚠️  No .flow files found in src/flows/")
        return
    
    for flow_file in flow_files:
        click.echo(f"   📄 {flow_file.name}")
        try:
            parsed_data = parser.parse_file(flow_file)
            merge_parsed_data_to_ir(ir, parsed_data)
        except Exception as e:
            click.echo(f"   ❌ Error parsing {flow_file.name}: {str(e)}")
            return
    
    click.echo(f"✅ Parsed {len(flow_files)} .flow files")
    
    # Generate code based on target
    if target in ['all', 'backend']:
        generate_backend(project, ir, env)
    
    if target in ['all', 'frontend']:
        generate_frontend(project, ir, env)
    
    if target in ['all', 'mobile', 'ios', 'android']:
        generate_mobile(project, ir, env, target)
    
    if target in ['all', 'desktop', 'windows', 'macos', 'linux']:
        generate_desktop(project, ir, env, target)
    
    click.echo("✅ Build completed successfully!")

def build_with_watch(project: FlashFlowProject, target: str, env: str):
    """Build with file watching"""
    import time
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    
    class FlowFileHandler(FileSystemEventHandler):
        def __init__(self, project, target, env):
            self.project = project
            self.target = target
            self.env = env
            self.last_build = 0
        
        def on_modified(self, event):
            if event.is_directory:
                return
            
            # Only rebuild for .flow files
            if not str(event.src_path).endswith('.flow'):
                return
            
            # Debounce builds (max once per second)
            now = time.time()
            if now - self.last_build < 1:
                return
            
            self.last_build = now
            click.echo(f"\n🔄 File changed: {event.src_path}")
            try:
                build_once(self.project, self.target, self.env)
                click.echo("👀 Watching for changes... (Ctrl+C to stop)")
            except Exception as e:
                click.echo(f"❌ Build error: {str(e)}")
    
    # Initial build
    build_once(project, target, env)
    
    # Setup file watcher
    event_handler = FlowFileHandler(project, target, env)
    observer = Observer()
    observer.schedule(event_handler, str(project.flows_path), recursive=True)
    observer.start()
    
    click.echo("👀 Watching for changes... (Ctrl+C to stop)")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        click.echo("\n🛑 Watch mode stopped")
    
    observer.join()

def merge_parsed_data_to_ir(ir: FlashFlowIR, parsed_data: dict):
    """Merge parsed .flow data into the IR"""
    
    # Add models
    if 'model' in parsed_data:
        model_data = parsed_data['model']
        if isinstance(model_data, dict) and 'name' in model_data:
            ir.add_model(model_data['name'], model_data)
    
    # Add pages
    if 'page' in parsed_data:
        page_data = parsed_data['page']
        if isinstance(page_data, dict):
            path = page_data.get('path', '/')
            ir.add_page(path, page_data)
    
    # Add endpoints
    if 'endpoint' in parsed_data:
        endpoint_data = parsed_data['endpoint']
        if isinstance(endpoint_data, dict):
            path = endpoint_data.get('path', '/api/unknown')
            ir.add_endpoint(path, endpoint_data)
    
    # Add authentication
    if 'authentication' in parsed_data:
        ir.set_auth(parsed_data['authentication'])
    
    # Add theme
    if 'theme' in parsed_data:
        ir.set_theme(parsed_data['theme'])

def generate_backend(project: FlashFlowProject, ir: FlashFlowIR, env: str):
    """Generate backend code"""
    click.echo("🔧 Generating backend...")
    
    try:
        # Import backend generator here to avoid import errors
        from generators.backend.backend import BackendGenerator
        
        backend_gen = BackendGenerator(project, ir, env)
        backend_gen.generate()
        
        click.echo("   ✅ Backend code generated")
    except Exception as e:
        click.echo(f"   ❌ Backend generation failed: {str(e)}")
        click.echo("   ⚠️  Backend generation skipped due to errors")

def generate_frontend(project: FlashFlowProject, ir: FlashFlowIR, env: str):
    """Generate frontend code using Flet"""
    click.echo("🎨 Generating frontend...")
    
    frontend_gen = FletFrontendGenerator(project, ir, env)
    frontend_gen.generate()
    
    click.echo("   ✅ Flet web app generated")
    click.echo("   ✅ Build configuration created")

def generate_mobile(project: FlashFlowProject, ir: FlashFlowIR, env: str, target: str):
    """Generate mobile app code"""
    if target == 'ios':
        click.echo("📱 Generating iOS app...")
    elif target == 'android':
        click.echo("🤖 Generating Android app...")
    else:
        click.echo("📱 Generating mobile apps...")
    
    mobile_gen = MobileGenerator(project, ir, env)
    
    if target in ['all', 'mobile', 'ios']:
        mobile_gen.generate_ios()
        click.echo("   ✅ iOS app generated")
    
    if target in ['all', 'mobile', 'android']:
        mobile_gen.generate_android()
        click.echo("   ✅ Android app generated")

def generate_desktop(project: FlashFlowProject, ir: FlashFlowIR, env: str, target: str):
    """Generate desktop app code"""
    click.echo("🖥️  Generating desktop app...")
    
    desktop_gen = SimpleDesktopGenerator(str(project.root_path), project.config.name)
    desktop_gen.generate(ir.to_dict())
    
    click.echo("   ✅ Desktop app generated")
    click.echo("   ✅ Build scripts created")