#!/usr/bin/env python3
"""
Flet Live Preview Service - Provides real-time preview across all platforms
"""

import flet as ft
import threading
import time
import json
import os
import yaml
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from typing import Dict, Any, List
from flask import Flask, render_template_string

class FletPreviewService:
    """Flet Live Preview Service for cross-platform real-time preview"""
    
    def __init__(self, project_dir: str, port: int = 8082):
        self.project_dir = Path(project_dir)
        self.port = port
        self.current_page = None
        self.observer = None
        self.flow_files = {}
        self._load_flow_files()
        
    def start(self):
        """Start the Flet preview service"""
        # Start file watcher
        self._start_file_watcher()
        
        # Start Flet app
        ft.app(target=self._main, port=self.port)
        
    def start_embedded(self, app: Flask):
        """Start the preview service embedded in a Flask app"""
        # Start file watcher
        self._start_file_watcher()
        
        # Register routes with the Flask app
        self._register_flask_routes(app)
        
    def _register_flask_routes(self, app: Flask):
        """Register Flask routes for the preview service"""
        
        @app.route('/preview/api/flow-files')
        def get_flow_files():
            """API endpoint to get list of flow files"""
            flows_dir = self.project_dir / "src" / "flows"
            flow_files = []
            if flows_dir.exists():
                flow_files = [f.name for f in flows_dir.glob("*.flow")]
            return {"files": flow_files}
        
        @app.route('/preview/api/preview-data')
        def get_preview_data():
            """API endpoint to get preview data from flow files"""
            return {
                "flow_files": self.flow_files,
                "last_updated": time.time()
            }
        
    def _main(self, page: ft.Page):
        """Main Flet application"""
        self.current_page = page
        
        # Configure page
        page.title = "FlashFlow Live Preview"
        page.theme_mode = ft.ThemeMode.LIGHT
        
        # Set up navigation
        self._setup_navigation(page)
        
        # Load initial content
        self._load_preview_content(page)
        
    def _setup_navigation(self, page: ft.Page):
        """Set up navigation for different platform previews"""
        def route_change(e):
            self._load_preview_content(page)
            
        page.on_route_change = route_change
        
    def _load_preview_content(self, page: ft.Page):
        """Load preview content based on current route"""
        page.views.clear()
        
        if page.route == "/":
            view = self._build_welcome_view(page)
        elif page.route == "/web":
            view = self._build_web_preview(page)
        elif page.route == "/mobile":
            view = self._build_mobile_preview(page)
        elif page.route == "/desktop":
            view = self._build_desktop_preview(page)
        else:
            view = self._build_welcome_view(page)
            
        page.views.append(view)
        page.update()
        
    def _build_welcome_view(self, page: ft.Page):
        """Build welcome/selector view"""
        return ft.View(
            "/",
            [
                ft.AppBar(
                    title=ft.Text("FlashFlow Live Preview"),
                    bgcolor="blue",
                    color="white"
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text("FlashFlow Live Preview", size=32, weight=ft.FontWeight.BOLD),
                        ft.Text("Select a platform to preview:", size=16),
                        ft.ElevatedButton(
                            "🌐 Web Preview",
                            on_click=lambda _: page.go("/web"),
                            width=300,
                            height=50
                        ),
                        ft.ElevatedButton(
                            "📱 Mobile Preview",
                            on_click=lambda _: page.go("/mobile"),
                            width=300,
                            height=50
                        ),
                        ft.ElevatedButton(
                            "🖥️ Desktop Preview",
                            on_click=lambda _: page.go("/desktop"),
                            width=300,
                            height=50
                        ),
                        ft.Divider(),
                        ft.Text("Changes to your .flow files will automatically update all previews", 
                               size=12, color="grey")
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20),
                    padding=20,
                    expand=True
                )
            ]
        )
        
    def _build_web_preview(self, page: ft.Page):
        """Build web preview view"""
        content_controls = []
        
        # Generate content from flow files
        for flow_name, flow_data in self.flow_files.items():
            content_controls.extend(self._generate_web_components(flow_data))
        
        # If no components, show default content
        if not content_controls:
            content_controls = [
                ft.Text("Web Application Preview", size=24, weight=ft.FontWeight.BOLD),
                ft.Text("This preview shows your web application generated from .flow files", size=14),
                ft.Container(
                    content=ft.Text("Create .flow files in src/flows to see content here", size=16),
                    padding=20,
                    bgcolor="grey200",
                    border_radius=8,
                    expand=True
                )
            ]
        
        return ft.View(
            "/web",
            [
                ft.AppBar(
                    title=ft.Text("Web Preview"),
                    bgcolor="blue",
                    color="white",
                    leading=ft.IconButton(
                        icon="arrow_back",
                        on_click=lambda _: page.go("/")
                    )
                ),
                ft.Container(
                    content=ft.Column(content_controls, spacing=20),
                    padding=20,
                    expand=True
                )
            ]
        )
        
    def _build_mobile_preview(self, page: ft.Page):
        """Build mobile preview view"""
        content_controls = []
        
        # Generate content from flow files
        for flow_name, flow_data in self.flow_files.items():
            content_controls.extend(self._generate_mobile_components(flow_data))
        
        # If no components, show default content
        if not content_controls:
            content_controls = [
                ft.Text("Mobile Application Preview", size=24, weight=ft.FontWeight.BOLD),
                ft.Text("This preview shows your mobile application generated from .flow files", size=14),
                ft.Container(
                    content=ft.Text("Create .flow files in src/flows to see content here", size=16),
                    padding=20,
                    bgcolor="grey200",
                    border_radius=8,
                    expand=True
                )
            ]
        
        return ft.View(
            "/mobile",
            [
                ft.AppBar(
                    title=ft.Text("Mobile Preview"),
                    bgcolor="green",
                    color="white",
                    leading=ft.IconButton(
                        icon="arrow_back",
                        on_click=lambda _: page.go("/")
                    )
                ),
                ft.Container(
                    content=ft.Column(content_controls, spacing=20),
                    padding=20,
                    expand=True
                )
            ]
        )
        
    def _build_desktop_preview(self, page: ft.Page):
        """Build desktop preview view"""
        content_controls = []
        
        # Generate content from flow files
        for flow_name, flow_data in self.flow_files.items():
            content_controls.extend(self._generate_desktop_components(flow_data))
        
        # If no components, show default content
        if not content_controls:
            content_controls = [
                ft.Text("Desktop Application Preview", size=24, weight=ft.FontWeight.BOLD),
                ft.Text("This preview shows your desktop application generated from .flow files", size=14),
                ft.Container(
                    content=ft.Text("Create .flow files in src/flows to see content here", size=16),
                    padding=20,
                    bgcolor="grey200",
                    border_radius=8,
                    expand=True
                )
            ]
        
        return ft.View(
            "/desktop",
            [
                ft.AppBar(
                    title=ft.Text("Desktop Preview"),
                    bgcolor="purple",
                    color="white",
                    leading=ft.IconButton(
                        icon="arrow_back",
                        on_click=lambda _: page.go("/")
                    )
                ),
                ft.Container(
                    content=ft.Column(content_controls, spacing=20),
                    padding=20,
                    expand=True
                )
            ]
        )
        
    def _generate_web_components(self, flow_data: Dict[Any, Any]) -> List:
        """Generate web components from flow data"""
        components = []
        
        # Handle pages - could be a single page or list of pages
        pages = flow_data.get('page', [])
        if isinstance(pages, dict):
            pages = [pages]
        elif not isinstance(pages, list):
            pages = []
            
        for page in pages:
            body = page.get('body', [])
            for component_def in body:
                if isinstance(component_def, dict):
                    component_type = component_def.get('component', 'text')
                    
                    if component_type == 'hero':
                        components.append(
                            ft.Container(
                                content=ft.Column([
                                    ft.Text(
                                        component_def.get('title', 'Welcome'),
                                        size=32,
                                        weight=ft.FontWeight.BOLD,
                                        text_align=ft.TextAlign.CENTER
                                    ),
                                    ft.Text(
                                        component_def.get('subtitle', 'Built with FlashFlow'),
                                        size=16,
                                        text_align=ft.TextAlign.CENTER
                                    ),
                                    ft.ElevatedButton(
                                        component_def.get('cta', {}).get('text', 'Get Started'),
                                        on_click=lambda _: print("CTA clicked")
                                    )
                                ], 
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                padding=40,
                                bgcolor="blue100",
                                border_radius=10
                            )
                        )
                    
                    elif component_type == 'form':
                        fields = component_def.get('fields', [])
                        field_controls = []
                        
                        for field in fields:
                            # Handle both string fields (field names) and dictionary fields
                            if isinstance(field, str):
                                # String field - create a simple text field
                                field_name = field
                                field_type = 'text'
                                placeholder = field.replace('_', ' ').title()
                            elif isinstance(field, dict):
                                # Dictionary field - extract properties
                                field_name = field.get('name', 'field')
                                field_type = field.get('type', 'text')
                                placeholder = field.get('placeholder', field_name.replace('_', ' ').title())
                            else:
                                # Unknown field type, skip
                                continue
                            
                            if field_type == 'text':
                                field_controls.append(
                                    ft.TextField(
                                        label=placeholder,
                                        hint_text=placeholder
                                    )
                                )
                            elif field_type == 'email':
                                field_controls.append(
                                    ft.TextField(
                                        label=placeholder,
                                        hint_text=placeholder,
                                        keyboard_type=ft.KeyboardType.EMAIL
                                    )
                                )
                            elif field_type == 'password':
                                field_controls.append(
                                    ft.TextField(
                                        label=placeholder,
                                        hint_text=placeholder,
                                        password=True
                                    )
                                )
                        
                        button_text = component_def.get('button_text', 'Submit')
                        field_column = ft.Column(field_controls, spacing=10)
                        
                        components.append(
                            ft.Container(
                                content=ft.Column([
                                    field_column,
                                    ft.ElevatedButton(
                                        button_text,
                                        on_click=lambda e: print("Form submitted")
                                    )
                                ], spacing=10),
                                padding=20,
                                bgcolor="grey100",
                                border_radius=10
                            )
                        )
                    
                    elif component_type == 'list':
                        components.append(
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("Data List", size=20, weight=ft.FontWeight.BOLD),
                                    ft.Text("List items will appear here when connected to data")
                                ]),
                                padding=20,
                                bgcolor="grey100",
                                border_radius=10
                            )
                        )
        
        return components
        
    def _generate_mobile_components(self, flow_data: Dict[Any, Any]) -> List:
        """Generate mobile components from flow data (same as web for now)"""
        return self._generate_web_components(flow_data)
        
    def _generate_desktop_components(self, flow_data: Dict[Any, Any]) -> List:
        """Generate desktop components from flow data (same as web for now)"""
        return self._generate_web_components(flow_data)
        
    def _load_flow_files(self):
        """Load all .flow files from the project"""
        flows_dir = self.project_dir / "src" / "flows"
        if flows_dir.exists():
            for flow_file in flows_dir.glob("*.flow"):
                try:
                    with open(flow_file, 'r') as f:
                        flow_data = yaml.safe_load(f)
                        self.flow_files[flow_file.name] = flow_data
                except Exception as e:
                    print(f"Error loading {flow_file}: {e}")
        
    def _start_file_watcher(self):
        """Start file watcher to monitor .flow file changes"""
        class FlowFileHandler(FileSystemEventHandler):
            def __init__(self, service):
                self.service = service
                
            def on_modified(self, event):
                if event.is_directory:
                    return
                    
                # Check if the file ends with .flow extension
                if Path(str(event.src_path)).suffix == ".flow":
                    print(f"🔄 .flow file changed: {event.src_path}")
                    # Reload flow files and update preview
                    self.service._load_flow_files()
                    self.service._update_preview()
                    
        # Create observer
        self.observer = Observer()
        handler = FlowFileHandler(self)
        
        # Watch src/flows directory
        flows_dir = self.project_dir / "src" / "flows"
        if flows_dir.exists():
            self.observer.schedule(handler, str(flows_dir), recursive=False)
            
        # Watch entire project directory
        self.observer.schedule(handler, str(self.project_dir), recursive=True)
        
        # Start observer
        self.observer.start()
        print(f"👀 Watching for .flow file changes in {self.project_dir}")
        
    def _update_preview(self):
        """Update the preview when files change"""
        if self.current_page:
            print("🔄 Updating preview...")
            # Reload the current view
            self._load_preview_content(self.current_page)
            # Show notification
            self.current_page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text("Preview updated!")
                )
            )
            self.current_page.update()

def start_flet_preview(project_dir: str = ".", port: int = 8082):
    """Start the Flet preview service"""
    service = FletPreviewService(project_dir, port)
    service.start()

if __name__ == "__main__":
    start_flet_preview()