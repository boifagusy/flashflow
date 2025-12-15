"""
Theme Service for FlashFlow
Provides dynamic theme management and gradient button components using Flet
"""

import flet as ft
import json
from typing import Dict, Any, List, Optional, Union
from pathlib import Path

class ThemeService:
    """Service for managing dynamic themes in FlashFlow applications"""
    
    def __init__(self):
        self.themes = {}
        self.current_theme = "light"
        self.default_themes = {
            "light": {
                "primary": ft.Colors.BLUE_500,
                "secondary": ft.Colors.GREY_300,
                "success": ft.Colors.GREEN_500,
                "warning": ft.Colors.AMBER_500,
                "danger": ft.Colors.RED_500,
                "background": ft.Colors.WHITE,
                "surface": ft.Colors.GREY_50,
                "text": ft.Colors.BLACK,
                "text_secondary": ft.Colors.GREY_700
            },
            "dark": {
                "primary": ft.Colors.BLUE_400,
                "secondary": ft.Colors.GREY_700,
                "success": ft.Colors.GREEN_400,
                "warning": ft.Colors.AMBER_400,
                "danger": ft.Colors.RED_400,
                "background": ft.Colors.GREY_900,
                "surface": ft.Colors.GREY_800,
                "text": ft.Colors.WHITE,
                "text_secondary": ft.Colors.GREY_300
            }
        }
        self.themes.update(self.default_themes)
    
    def add_theme(self, name: str, theme_config: Dict[str, Any]):
        """Add a new theme to the theme service"""
        self.themes[name] = theme_config
    
    def get_theme(self, name: str = None) -> Dict[str, Any]:
        """Get a theme by name or the current theme"""
        theme_name = name or self.current_theme
        return self.themes.get(theme_name, self.default_themes["light"])
    
    def set_theme(self, name: str) -> bool:
        """Set the current theme"""
        if name in self.themes:
            self.current_theme = name
            return True
        return False
    
    def get_available_themes(self) -> List[str]:
        """Get list of available theme names"""
        return list(self.themes.keys())
    
    def create_gradient(self, colors: List[str], angle: int = 0) -> ft.LinearGradient:
        """Create a linear gradient for use in Flet components"""
        return ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=colors
        )

# Global theme service instance
theme_service = ThemeService()

class GradientButton(ft.ElevatedButton):
    """A customizable button component with gradient background"""
    
    def __init__(
        self,
        text: str,
        on_click=None,
        gradient_colors: List[str] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        icon: Optional[str] = None,
        **kwargs
    ):
        # Set default gradient colors if not provided
        if gradient_colors is None:
            gradient_colors = [ft.Colors.BLUE_500, ft.Colors.BLUE_700]
        
        # Create gradient
        gradient = ft.LinearGradient(
            begin=ft.alignment.top_center,
            end=ft.alignment.bottom_center,
            colors=gradient_colors
        )
        
        # Initialize the ElevatedButton with gradient background
        super().__init__(
            text=text,
            on_click=on_click,
            icon=icon,
            width=width,
            height=height,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.padding.all(15),
                bgcolor=gradient,
                color=ft.colors.WHITE,
                elevation=5,
                animation_duration=200
            ),
            **kwargs
        )

def create_gradient_button(
    text: str, 
    on_click=None, 
    gradient_type: str = "primary",
    width: Optional[int] = None,
    height: Optional[int] = None,
    icon: Optional[str] = None
) -> GradientButton:
    """Create a gradient button with predefined color schemes"""
    
    gradient_presets = {
        "primary": [ft.Colors.BLUE_500, ft.Colors.BLUE_700],
        "secondary": [ft.Colors.GREY_400, ft.Colors.GREY_600],
        "success": [ft.Colors.GREEN_500, ft.Colors.GREEN_700],
        "warning": [ft.Colors.AMBER_500, ft.Colors.AMBER_700],
        "danger": [ft.Colors.RED_500, ft.Colors.RED_700],
        "rainbow": [ft.Colors.PURPLE_500, ft.Colors.BLUE_500, ft.Colors.CYAN_500, ft.Colors.GREEN_500]
    }
    
    colors = gradient_presets.get(gradient_type, gradient_presets["primary"])
    return GradientButton(
        text=text,
        on_click=on_click,
        gradient_colors=colors,
        width=width,
        height=height,
        icon=icon
    )

class ThemeSwitcher(ft.Row):
    """A component for switching between themes"""
    
    def __init__(self, on_theme_change=None, **kwargs):
        super().__init__(**kwargs)
        self.on_theme_change = on_theme_change
        self.theme_buttons = []
        self.build_theme_switcher()
    
    def build_theme_switcher(self):
        """Build the theme switcher UI"""
        self.controls.clear()
        
        # Get available themes
        themes = theme_service.get_available_themes()
        
        # Create a button for each theme
        for theme_name in themes:
            button = ft.ElevatedButton(
                text=theme_name.capitalize(),
                on_click=lambda e, name=theme_name: self.switch_theme(name),
                style=ft.ButtonStyle(
                    bgcolor=ft.colors.BLUE_500 if theme_name == theme_service.current_theme else ft.colors.GREY_300,
                    color=ft.colors.WHITE if theme_name == theme_service.current_theme else ft.colors.BLACK
                )
            )
            self.theme_buttons.append(button)
            self.controls.append(button)
    
    def switch_theme(self, theme_name: str):
        """Switch to a different theme"""
        if theme_service.set_theme(theme_name):
            # Update button styles
            for i, theme in enumerate(theme_service.get_available_themes()):
                if i < len(self.theme_buttons):
                    button = self.theme_buttons[i]
                    button.style = ft.ButtonStyle(
                        bgcolor=ft.colors.BLUE_500 if theme == theme_name else ft.colors.GREY_300,
                        color=ft.colors.WHITE if theme == theme_name else ft.colors.BLACK
                    )
            
            # Notify callback if provided
            if self.on_theme_change:
                self.on_theme_change(theme_name)
            
            # Update UI
            self.update()

def initialize_theme_service(custom_themes: Dict[str, Dict] = None) -> ThemeService:
    """Initialize the theme service with optional custom themes"""
    if custom_themes:
        for name, config in custom_themes.items():
            theme_service.add_theme(name, config)
    
    return theme_service