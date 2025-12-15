"""
FlashFlow Mobile IDE - A Flet-based mobile development environment
"""

import flet as ft
import os
import json
import subprocess
import sys
from pathlib import Path

class MobileIDE:
    def __init__(self, page: ft.Page, project_dir: str):
        self.page = page
        self.project_dir = Path(project_dir)
        self.current_file = None
        self.file_content = ""
        
        # Configure page
        self.page.title = "📱 FlashFlow Mobile IDE"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        
        # Build UI
        self.build_ui()
        
        # Load project files
        self.load_project_files()
    
    def build_ui(self):
        """Build the mobile IDE user interface"""
        # Header
        header = ft.AppBar(
            title=ft.Text("📱 FlashFlow Mobile IDE"),
            bgcolor="blue",
            color="white"
        )
        
        # Toolbar with navigation buttons
        self.toolbar = ft.Row(
            controls=[
                ft.ElevatedButton("Files", on_click=lambda e: self.switch_view("files")),
                ft.ElevatedButton("Editor", on_click=lambda e: self.switch_view("editor")),
                ft.ElevatedButton("Build", on_click=lambda e: self.switch_view("build")),
                ft.ElevatedButton("Preview", on_click=lambda e: self.switch_view("preview")),
            ],
            spacing=5,
            wrap=True
        )
        
        # File explorer view
        self.file_list = ft.ListView(
            expand=True,
            spacing=10,
            padding=10
        )
        
        self.file_view = ft.Column(
            controls=[
                ft.Text("📁 Project Files", weight=ft.FontWeight.BOLD, size=16),
                ft.ElevatedButton("New File", on_click=self.new_file),
                self.file_list
            ],
            expand=True
        )
        
        # Editor view
        self.editor = ft.TextField(
            multiline=True,
            expand=True,
            hint_text="Select a file to edit or create a new one...",
            on_change=self.on_editor_change
        )
        
        self.editor_toolbar = ft.Row(
            controls=[
                ft.ElevatedButton("Save", on_click=self.save_file),
            ],
            spacing=10
        )
        
        self.editor_view = ft.Column(
            controls=[
                ft.Text("📝 Editor", weight=ft.FontWeight.BOLD, size=16),
                self.editor_toolbar,
                self.editor
            ],
            expand=True
        )
        
        # Build view
        self.build_output = ft.TextField(
            multiline=True,
            expand=True,
            read_only=True,
            hint_text="Build output will appear here..."
        )
        
        self.build_view = ft.Column(
            controls=[
                ft.Text("🔨 Build", weight=ft.FontWeight.BOLD, size=16),
                ft.ElevatedButton("Build Project", on_click=self.build_project, bgcolor="green"),
                ft.Divider(),
                ft.Text("Build Output:", weight=ft.FontWeight.BOLD),
                self.build_output
            ],
            expand=True
        )
        
        # Preview view
        self.preview_info = ft.Column(
            controls=[
                ft.Text("👀 Preview", weight=ft.FontWeight.BOLD, size=16),
                ft.Text("To preview your application:", size=14),
                ft.Text("1. Build your project first", size=12),
                ft.Text("2. Run 'flashflow serve' on your computer", size=12),
                ft.Text("3. Access the preview URL from your computer", size=12),
                ft.Divider(),
                ft.Text("Project Information:", weight=ft.FontWeight.BOLD),
                ft.Text(f"Project Path: {self.project_dir}", size=12),
            ],
            expand=True
        )
        
        self.preview_view = ft.Column(
            controls=[
                self.preview_info
            ],
            expand=True
        )
        
        # Status bar
        self.status_bar = ft.Text("Ready", size=12, color="grey")
        
        # Main layout
        self.main_content = ft.Column(
            controls=[self.file_view],
            expand=True
        )
        
        self.page.add(
            header,
            self.toolbar,
            ft.Divider(),
            self.main_content,
            ft.Container(
                content=self.status_bar,
                padding=10,
                bgcolor="grey300"
            )
        )
    
    def switch_view(self, view_name):
        """Switch between different views"""
        if view_name == "files":
            self.main_content.controls = [self.file_view]
        elif view_name == "editor":
            self.main_content.controls = [self.editor_view]
        elif view_name == "build":
            self.main_content.controls = [self.build_view]
        elif view_name == "preview":
            self.main_content.controls = [self.preview_view]
        
        self.page.update()
    
    def load_project_files(self):
        """Load project files into the file explorer"""
        self.file_list.controls.clear()
        
        try:
            # Add project root files
            for item in self.project_dir.iterdir():
                if not item.name.startswith('.'):  # Skip hidden files
                    file_tile = ft.ListTile(
                        title=ft.Text(f"{'📁' if item.is_dir() else '📄'} {item.name}"),
                        on_click=lambda e, path=item: self.open_file(path)
                    )
                    self.file_list.controls.append(file_tile)
            
            # Add src/flows files specifically
            flows_dir = self.project_dir / "src" / "flows"
            if flows_dir.exists():
                for flow_file in flows_dir.iterdir():
                    if flow_file.suffix == ".flow":
                        file_tile = ft.ListTile(
                            title=ft.Text(f"📄 {flow_file.name}"),
                            on_click=lambda e, path=flow_file: self.open_file(path)
                        )
                        self.file_list.controls.append(file_tile)
            
            self.update_status("Project files loaded")
        except Exception as e:
            self.update_status(f"Error loading files: {str(e)}")
        
        self.page.update()
    
    def open_file(self, file_path: Path):
        """Open a file in the editor"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.file_content = f.read()
            
            self.current_file = file_path
            self.editor.value = self.file_content
            self.editor.label = f"Editing: {file_path.name}"
            self.update_status(f"Opened: {file_path.name}")
            
            # Switch to editor view
            self.switch_view("editor")
        except Exception as e:
            self.update_status(f"Error opening file: {str(e)}")
    
    def on_editor_change(self, e):
        """Handle editor content changes"""
        self.file_content = self.editor.value or ""
    
    def new_file(self, e):
        """Create a new file dialog"""
        self.new_file_name = ft.TextField(label="File Name", hint_text="example.flow")
        
        def create_file(e):
            file_name = self.new_file_name.value
            if not file_name:
                self.update_status("Please enter a file name")
                return
            
            try:
                # Create in src/flows directory by default
                flows_dir = self.project_dir / "src" / "flows"
                flows_dir.mkdir(parents=True, exist_ok=True)
                
                new_file_path = flows_dir / file_name
                with open(new_file_path, 'w', encoding='utf-8') as f:
                    f.write("# FlashFlow Application\n\n// Define your models, pages, and endpoints here\n")
                
                self.update_status(f"Created: {file_name}")
                self.load_project_files()
                self.close_dialog()
                
                # Open the new file
                self.open_file(new_file_path)
            except Exception as ex:
                self.update_status(f"Error creating file: {str(ex)}")
        
        self.dialog = ft.AlertDialog(
            title=ft.Text("Create New File"),
            content=self.new_file_name,
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.close_dialog()),
                ft.TextButton("Create", on_click=create_file),
            ],
        )
        
        self.page.overlay.append(self.dialog)
        self.dialog.open = True
        self.page.update()
    
    def save_file(self, e):
        """Save the current file"""
        if not self.current_file:
            self.update_status("No file selected")
            return
        
        try:
            content_to_write = self.file_content or ""
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(content_to_write)
            self.update_status(f"Saved: {self.current_file.name}")
        except Exception as ex:
            self.update_status(f"Error saving file: {str(ex)}")
    
    def build_project(self, e):
        """Build the FlashFlow project"""
        self.update_status("Building project...")
        self.build_output.value = "Building...\n"
        self.page.update()
        
        try:
            # Run flashflow build command
            process = subprocess.Popen(
                [sys.executable, "-m", "cli.core.main", "build"],
                cwd=self.project_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                self.build_output.value = f"✅ Build completed successfully!\n\nOutput:\n{stdout}"
                self.update_status("✅ Build completed successfully!")
            else:
                self.build_output.value = f"❌ Build failed:\n\nError:\n{stderr}"
                self.update_status("❌ Build failed")
        except Exception as ex:
            self.build_output.value = f"❌ Build error: {str(ex)}"
            self.update_status(f"❌ Build error: {str(ex)}")
        
        self.page.update()
    
    def update_status(self, message: str):
        """Update the status bar"""
        self.status_bar.value = message
        self.page.update()
    
    def close_dialog(self):
        """Close the current dialog"""
        if hasattr(self, 'dialog'):
            self.dialog.open = False
            self.page.update()

def start_mobile_ide(page: ft.Page, project_dir: str = "."):
    """Main entry point for the mobile IDE"""
    MobileIDE(page, project_dir)

if __name__ == "__main__":
    # This would be called from the CLI command
    ft.app(target=lambda page: start_mobile_ide(page, "."))