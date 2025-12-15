"""
Flet Countdown Timer Demo
A demonstration of the Flet countdown timer with notification integration.
"""

import flet as ft
import sys
import os

# Add the src directory to the path so we can import our components
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from components.countdown_timer import create_countdown_timer
from components.notification_bell import create_notification_bell
from services.frontend_notification_service import initialize_frontend_notification_service

def main(page: ft.Page):
    page.title = "FlashFlow Countdown Timer Demo"
    page.window_width = 600
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
    
    # Create multiple countdown timers
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
    
    custom_timer = create_countdown_timer(
        title="Custom Timer",
        duration=60,  # 1 minute
        on_complete=on_timer_complete,
        on_tick=on_timer_tick
    )
    
    # Custom timer controls
    duration_input = ft.TextField(
        label="Duration (seconds)",
        keyboard_type=ft.KeyboardType.NUMBER,
        value="60"
    )
    
    def set_custom_timer(e):
        try:
            seconds = int(duration_input.value)
            if seconds > 0:
                custom_timer.set_duration(seconds)
                notification_service.show_notification(
                    "Timer Updated", 
                    f"Custom timer set to {custom_timer.format_time(seconds)}", 
                    "info"
                )
            else:
                notification_service.show_notification(
                    "Invalid Input", 
                    "Please enter a positive number", 
                    "error"
                )
        except ValueError:
            notification_service.show_notification(
                "Invalid Input", 
                "Please enter a valid number", 
                "error"
            )
    
    set_button = ft.ElevatedButton("Set Timer", on_click=set_custom_timer)
    
    custom_controls = ft.Row(
        controls=[duration_input, set_button],
        alignment=ft.MainAxisAlignment.CENTER
    )
    
    # Add all components to the page
    page.add(
        ft.AppBar(
            title=ft.Text("FlashFlow Countdown Timer Demo"),
            bgcolor=ft.colors.SURFACE_VARIANT,
            actions=[
                notification_bell
            ]
        ),
        ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Countdown Timers", size=24, weight=ft.FontWeight.BOLD),
                    ft.Text("Integrated with Notification System", size=16, color=ft.colors.GREY_600),
                    ft.Divider(),
                    
                    # Work timer
                    ft.Text("Pomodoro Technique", size=20, weight=ft.FontWeight.BOLD),
                    work_timer,
                    
                    ft.Divider(),
                    
                    # Break timer
                    ft.Text("Break Timer", size=20, weight=ft.FontWeight.BOLD),
                    break_timer,
                    
                    ft.Divider(),
                    
                    # Custom timer
                    ft.Text("Custom Timer", size=20, weight=ft.FontWeight.BOLD),
                    custom_controls,
                    custom_timer,
                    
                    ft.Divider(),
                    
                    # Instructions
                    ft.Text("Instructions:", size=16, weight=ft.FontWeight.BOLD),
                    ft.Text("1. Click Play to start a timer", size=14),
                    ft.Text("2. Click Pause to pause a timer", size=14),
                    ft.Text("3. Click Reset to reset a timer", size=14),
                    ft.Text("4. You'll receive notifications when timers complete", size=14),
                ],
                spacing=20
            ),
            padding=20,
            expand=True
        )
    )

if __name__ == "__main__":
    ft.app(target=main)