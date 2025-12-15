"""
Simple Countdown Timer Demo
A standalone demo of the countdown timer component.
"""

import flet as ft
from src.components.countdown_timer import create_countdown_timer

def main(page: ft.Page):
    page.title = "Countdown Timer Demo"
    page.window_width = 400
    page.window_height = 500
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # Create a simple timer
    timer = create_countdown_timer(
        title="Work Timer",
        duration=5,  # 5 seconds for demo
        on_complete=lambda: print("Timer completed!"),
        on_tick=lambda remaining: print(f"Time remaining: {remaining} seconds")
    )
    
    # Add timer to page
    page.add(
        ft.Column(
            controls=[
                ft.Text("Countdown Timer Demo", size=24, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                timer
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )

if __name__ == "__main__":
    ft.app(target=main)