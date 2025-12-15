"""
Theme Demo Application
Demonstrates dynamic themes and gradient buttons in FlashFlow
"""

import flet as ft
import sys
import os

# Add the src directory to the path so we can import our components
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from components.button import Button, create_primary_button, create_secondary_button, create_danger_button
from src.services.theme_service import initialize_theme_service, theme_service, create_gradient_button, ThemeSwitcher

def main(page: ft.Page):
    page.title = "FlashFlow Theme Demo"
    page.window_width = 800
    page.window_height = 600
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # Initialize theme service with custom themes
    custom_themes = {
        "ocean": {
            "primary": ft.colors.CYAN_500,
            "secondary": ft.colors.TEAL_300,
            "success": ft.colors.GREEN_500,
            "warning": ft.colors.YELLOW_500,
            "danger": ft.colors.RED_500,
            "background": ft.colors.CYAN_50,
            "surface": ft.colors.BLUE_100,
            "text": ft.colors.BLUE_900,
            "text_secondary": ft.colors.BLUE_700
        },
        "sunset": {
            "primary": ft.colors.ORANGE_500,
            "secondary": ft.colors.PINK_300,
            "success": ft.colors.GREEN_500,
            "warning": ft.colors.AMBER_500,
            "danger": ft.colors.RED_500,
            "background": ft.colors.ORANGE_50,
            "surface": ft.colors.ORANGE_100,
            "text": ft.colors.ORANGE_900,
            "text_secondary": ft.colors.ORANGE_700
        }
    }
    
    initialize_theme_service(custom_themes)
    
    # Theme change callback
    def on_theme_change(theme_name):
        # Update page theme based on selected theme
        current_theme = theme_service.get_theme(theme_name)
        
        # Apply theme to page
        page.bgcolor = current_theme["background"]
        page.update()
    
    # Create theme switcher
    theme_switcher = ThemeSwitcher(on_theme_change=on_theme_change)
    
    # Create gradient buttons
    primary_gradient_btn = create_gradient_button(
        text="Primary Gradient Button",
        on_click=lambda e: print("Primary gradient button clicked!"),
        gradient_type="primary"
    )
    
    success_gradient_btn = create_gradient_button(
        text="Success Gradient Button",
        on_click=lambda e: print("Success gradient button clicked!"),
        gradient_type="success"
    )
    
    rainbow_gradient_btn = create_gradient_button(
        text="Rainbow Gradient Button",
        on_click=lambda e: print("Rainbow gradient button clicked!"),
        gradient_type="rainbow"
    )
    
    # Create regular buttons for comparison
    primary_btn = create_primary_button(
        text="Primary Button",
        on_click=lambda e: print("Primary button clicked!")
    )
    
    secondary_btn = create_secondary_button(
        text="Secondary Button",
        on_click=lambda e: print("Secondary button clicked!")
    )
    
    danger_btn = create_danger_button(
        text="Danger Button",
        on_click=lambda e: print("Danger button clicked!")
    )
    
    # Add all components to the page
    page.add(
        ft.AppBar(
            title=ft.Text("FlashFlow Theme Demo"),
            bgcolor=ft.colors.SURFACE_VARIANT,
            actions=[
                theme_switcher
            ]
        ),
        ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Dynamic Themes & Gradient Buttons", size=24, weight=ft.FontWeight.BOLD),
                    ft.Text("FlashFlow now supports dynamic themes and gradient buttons!", size=16, color=ft.colors.GREY_600),
                    ft.Divider(),
                    
                    # Theme switcher section
                    ft.Text("Theme Switcher", size=20, weight=ft.FontWeight.BOLD),
                    ft.Text("Click buttons below to switch themes:", size=14),
                    # Note: We're using the theme_switcher created above
                    
                    ft.Divider(),
                    
                    # Gradient buttons section
                    ft.Text("Gradient Buttons", size=20, weight=ft.FontWeight.BOLD),
                    ft.Text("Beautiful gradient buttons with smooth animations:", size=14),
                    primary_gradient_btn,
                    success_gradient_btn,
                    rainbow_gradient_btn,
                    
                    ft.Divider(),
                    
                    # Regular buttons section
                    ft.Text("Regular Buttons", size=20, weight=ft.FontWeight.BOLD),
                    ft.Text("Standard buttons for comparison:", size=14),
                    primary_btn,
                    secondary_btn,
                    danger_btn,
                    
                    ft.Divider(),
                    
                    # Instructions
                    ft.Text("Instructions:", size=16, weight=ft.FontWeight.BOLD),
                    ft.Text("1. Use the theme switcher in the app bar to change themes", size=14),
                    ft.Text("2. Gradient buttons have smooth animations and beautiful gradients", size=14),
                    ft.Text("3. All components automatically adapt to the current theme", size=14),
                ],
                spacing=15
            ),
            padding=20,
            expand=True
        )
    )

if __name__ == "__main__":
    ft.app(target=main)