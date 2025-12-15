"""
Home Page
The main landing page for the application.
"""

import flet as ft
from ..components.button import Button

class HomePage:
    """Home page implementation."""
    
    def build(self, page: ft.Page) -> ft.View:
        """Build the home page view."""
        return ft.View(
            "/",
            [
                ft.AppBar(
                    title=ft.Text("FlashFlow Application"),
                    bgcolor=ft.colors.SURFACE_VARIANT
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Welcome to FlashFlow", size=32, weight=ft.FontWeight.BOLD),
                        ft.Text("This is a sample home page demonstrating the project structure.", size=16),
                        ft.Divider(),
                        ft.Text("Getting Started", size=24, weight=ft.FontWeight.BOLD),
                        ft.Text("Explore the navigation to see different parts of the application."),
                        Button(
                            "Create Post",
                            on_click=lambda _: page.go("/posts/create"),
                            icon=ft.icons.ADD
                        )
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=20,
                    expand=True
                )
            ]
        )