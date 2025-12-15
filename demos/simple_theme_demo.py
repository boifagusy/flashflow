"""
Simple Theme Demo
A standalone demo of the theme and gradient button functionality.
"""

import flet as ft
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Directly import the theme service module
import importlib.util
spec = importlib.util.spec_from_file_location("theme_service", os.path.join(os.path.dirname(__file__), "..", "src", "services", "theme_service.py"))
theme_service_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(theme_service_module)

theme_service = theme_service_module.theme_service
create_gradient_button = theme_service_module.create_gradient_button
ThemeSwitcher = theme_service_module.ThemeSwitcher

def main(page: ft.Page):
    page.title = "Simple Theme Demo"
    page.window_width = 600
    page.window_height = 500
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # Theme change callback
    def on_theme_change(theme_name):
        # Update page theme based on selected theme
        current_theme = theme_service.get_theme(theme_name)
        page.bgcolor = current_theme["background"]
        page.update()
    
    # Create theme switcher
    theme_switcher = ThemeSwitcher(on_theme_change=on_theme_change)
    
    # Create gradient buttons
    primary_btn = create_gradient_button(
        text="Primary Gradient Button",
        on_click=lambda e: print("Primary button clicked!"),
        gradient_type="primary"
    )
    
    success_btn = create_gradient_button(
        text="Success Gradient Button",
        on_click=lambda e: print("Success button clicked!"),
        gradient_type="success"
    )
    
    rainbow_btn = create_gradient_button(
        text="Rainbow Gradient Button",
        on_click=lambda e: print("Rainbow button clicked!"),
        gradient_type="rainbow"
    )
    
    # Add components to page
    page.add(
        ft.AppBar(
            title=ft.Text("Simple Theme Demo"),
            bgcolor=ft.Colors.SURFACE_VARIANT,
            actions=[
                theme_switcher
            ]
        ),
        ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Theme & Gradient Demo", size=24, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    primary_btn,
                    success_btn,
                    rainbow_btn,
                    ft.Divider(),
                    ft.Text("Instructions:", size=16, weight=ft.FontWeight.BOLD),
                    ft.Text("1. Use theme switcher to change themes", size=14),
                    ft.Text("2. Click gradient buttons to see effects", size=14),
                ],
                spacing=20,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            padding=20,
            expand=True
        )
    )

if __name__ == "__main__":
    ft.app(target=main)