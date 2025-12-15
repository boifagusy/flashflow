"""
Button Component
A reusable button component for FlashFlow applications.
"""

import flet as ft
from typing import Callable, Optional
from ..services.theme_service import theme_service

class Button(ft.ElevatedButton):
    """A customizable button component."""
    
    def __init__(
        self,
        text: str,
        on_click: Optional[Callable] = None,
        icon: Optional[str] = None,
        style: str = "primary",
        **kwargs
    ):
        # Get current theme
        current_theme = theme_service.get_theme()
        
        # Set button style based on type and current theme
        if style == "primary":
            bgcolor = current_theme["primary"]
            color = current_theme["text"] if "text" in current_theme else ft.colors.WHITE
        elif style == "secondary":
            bgcolor = current_theme["secondary"]
            color = current_theme["text"] if "text" in current_theme else ft.colors.BLACK
        elif style == "danger":
            bgcolor = current_theme["danger"]
            color = current_theme["text"] if "text" in current_theme else ft.colors.WHITE
        else:
            bgcolor = None
            color = None
            
        # Initialize the ElevatedButton with our properties
        super().__init__(
            text=text,
            on_click=on_click,
            icon=icon,
            bgcolor=bgcolor,
            color=color,
            **kwargs
        )

def create_primary_button(text: str, on_click: Callable) -> Button:
    """Create a primary button."""
    return Button(text=text, on_click=on_click, style="primary")

def create_secondary_button(text: str, on_click: Callable) -> Button:
    """Create a secondary button."""
    return Button(text=text, on_click=on_click, style="secondary")

def create_danger_button(text: str, on_click: Callable) -> Button:
    """Create a danger button."""
    return Button(text=text, on_click=on_click, style="danger")