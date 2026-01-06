"""
Test script for platform-adaptive components
"""

import flet as ft
from components import PlatformAdaptiveComponents, AdaptiveThemeManager, create_adaptive_headline, create_adaptive_input, create_adaptive_button


def main(page: ft.Page):
    print("Starting test components...")
    # Apply theme
    theme = AdaptiveThemeManager.create_theme(
        dominant_60="#1976D2",    # Blue (60%)
        secondary_30="#424242",   # Grey (30%)
        accent_10="#FF4081"       # Pink (10%)
    )
    page.theme = theme
    print("Theme applied")
    
    # Create adaptive components
    headline = create_adaptive_headline(page, "Platform-Adaptive Demo", level=1)
    input_field = create_adaptive_input(page, "Username")
    button = create_adaptive_button(page, "Submit")
    print("Components created")
    
    # Add to page
    page.add(
        ft.Column([
            headline,
            input_field,
            button
        ])
    )
    print("Components added to page")


if __name__ == "__main__":
    print("Starting Flet app...")
    ft.app(target=main)