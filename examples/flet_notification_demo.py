"""
Flet Notification Demo
A demonstration of the Flet notification components.
"""

import flet as ft
import sys
import os

# Add the src directory to the path so we can import our components
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from components.notification_bell import create_notification_bell
from components.notification_settings import create_notification_settings
from services.frontend_notification_service import initialize_frontend_notification_service

def main(page: ft.Page):
    page.title = "FlashFlow Notification Demo"
    page.window_width = 800
    page.window_height = 600
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # Initialize the frontend notification service
    notification_service = initialize_frontend_notification_service(page)
    
    # Create notification components
    notification_bell = create_notification_bell(
        user_id="user123",
        on_notification_click=lambda nid: notification_service.show_notification(
            "Notification Clicked", 
            f"You clicked notification {nid}", 
            "info"
        ),
        on_mark_as_read=lambda: notification_service.show_notification(
            "Success", 
            "All notifications marked as read", 
            "success"
        )
    )
    
    notification_settings = create_notification_settings(
        user_id="user123",
        on_preference_change=lambda nt, ch, enabled: notification_service.show_notification(
            "Preferences Updated",
            f"{'Enabled' if enabled else 'Disabled'} {nt} via {ch}",
            "success"
        )
    )
    
    # Create demo controls
    demo_buttons = ft.Row(
        controls=[
            ft.ElevatedButton(
                "Show Success Notification",
                on_click=lambda e: notification_service.show_notification(
                    "Success!", 
                    "This is a success notification", 
                    "success"
                )
            ),
            ft.ElevatedButton(
                "Show Warning Notification",
                on_click=lambda e: notification_service.show_notification(
                    "Warning!", 
                    "This is a warning notification", 
                    "warning"
                )
            ),
            ft.ElevatedButton(
                "Show Error Notification",
                on_click=lambda e: notification_service.show_notification(
                    "Error!", 
                    "This is an error notification", 
                    "error"
                )
            ),
            ft.ElevatedButton(
                "Show Info Notification",
                on_click=lambda e: notification_service.show_notification(
                    "Information", 
                    "This is an info notification", 
                    "info"
                )
            )
        ],
        wrap=True,
        spacing=10
    )
    
    # Create the main layout
    page.add(
        ft.AppBar(
            title=ft.Text("FlashFlow Notification Demo"),
            bgcolor=ft.colors.SURFACE_VARIANT,
            actions=[
                notification_bell
            ]
        ),
        ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Notification Demo", size=24, weight=ft.FontWeight.BOLD),
                    ft.Text("Click the buttons below to see different types of notifications."),
                    demo_buttons,
                    ft.Divider(),
                    ft.Text("Notification Settings", size=20, weight=ft.FontWeight.BOLD),
                    ft.Text("Manage your notification preferences below."),
                    notification_settings
                ],
                spacing=20
            ),
            padding=20,
            expand=True
        )
    )

if __name__ == "__main__":
    ft.app(target=main)