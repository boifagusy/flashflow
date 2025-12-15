"""
Flet Timer Manager Demo
A demonstration of the Flet timer manager with persistent storage and notification integration.
"""

import flet as ft
import sys
import os

# Add the src directory to the path so we can import our components
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from components.countdown_timer import create_countdown_timer
from components.timer_manager import create_timer_manager
from components.notification_bell import create_notification_bell
from services.frontend_notification_service import initialize_frontend_notification_service

def main(page: ft.Page):
    page.title = "FlashFlow Timer Manager Demo"
    page.window_width = 800
    page.window_height = 700
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # Initialize the frontend notification service
    notification_service = initialize_frontend_notification_service(page)
    
    # Create notification bell
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
    
    # Timer completion callback
    def on_timer_complete():
        notification_service.show_notification(
            "Timer Complete!", 
            "Your countdown timer has finished!", 
            "success"
        )
    
    # Timer tick callback (trigger notification at 10 seconds remaining)
    def on_timer_tick(remaining_seconds):
        if remaining_seconds == 10:
            notification_service.show_notification(
                "10 Seconds Remaining", 
                "Your timer will complete in 10 seconds", 
                "warning"
            )
    
    # Create simple countdown timers
    work_timer = create_countdown_timer(
        title="Work Timer (25 min)",
        duration=25 * 60,  # 25 minutes
        on_complete=on_timer_complete,
        on_tick=on_timer_tick
    )
    
    break_timer = create_countdown_timer(
        title="Break Timer (5 min)",
        duration=5 * 60,  # 5 minutes
        on_complete=on_timer_complete,
        on_tick=on_timer_tick
    )
    
    # Create timer manager with notification callback
    def timer_notification_callback(title, message, notification_type):
        notification_service.show_notification(title, message, notification_type)
    
    timer_manager = create_timer_manager(
        user_id="user123",
        notification_callback=timer_notification_callback
    )
    
    # Add all components to the page
    page.add(
        ft.AppBar(
            title=ft.Text("FlashFlow Timer Manager Demo"),
            bgcolor=ft.colors.SURFACE_VARIANT,
            actions=[
                notification_bell
            ]
        ),
        ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Timer Components", size=24, weight=ft.FontWeight.BOLD),
                    ft.Text("Integrated with Notification System", size=16, color=ft.colors.GREY_600),
                    ft.Divider(),
                    
                    # Simple timers section
                    ft.Text("Simple Countdown Timers", size=20, weight=ft.FontWeight.BOLD),
                    ft.Text("Predefined timers for common use cases", size=14, color=ft.colors.GREY_600),
                    
                    # Work timer
                    ft.Text("Pomodoro Work Session", size=16, weight=ft.FontWeight.BOLD),
                    work_timer,
                    
                    ft.Divider(height=20),
                    
                    # Break timer
                    ft.Text("Break Timer", size=16, weight=ft.FontWeight.BOLD),
                    break_timer,
                    
                    ft.Divider(height=30),
                    
                    # Timer manager section
                    ft.Text("Persistent Timer Manager", size=20, weight=ft.FontWeight.BOLD),
                    ft.Text("Create and manage custom timers with persistent storage", size=14, color=ft.colors.GREY_600),
                    timer_manager,
                    
                    ft.Divider(),
                    
                    # Instructions
                    ft.Text("Instructions:", size=16, weight=ft.FontWeight.BOLD),
                    ft.Text("1. Simple timers: Use for temporary countdowns", size=14),
                    ft.Text("2. Timer manager: Create persistent timers that survive app restarts", size=14),
                    ft.Text("3. All timers integrate with the notification system", size=14),
                ],
                spacing=15
            ),
            padding=20,
            expand=True
        )
    )

if __name__ == "__main__":
    ft.app(target=main)