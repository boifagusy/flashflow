"""
Notification Bell Component
A Flet component that displays a notification bell with badge count and dropdown menu.
"""

import flet as ft
import json
from typing import Optional, Callable, List, Dict, Any

class NotificationBell(ft.Control):
    """A notification bell component with badge count and dropdown."""
    
    def __init__(
        self,
        user_id: str,
        on_notification_click: Optional[Callable] = None,
        on_mark_as_read: Optional[Callable] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.on_notification_click = on_notification_click
        self.on_mark_as_read = on_mark_as_read
        self.notifications = []
        self.unread_count = 0
        self.is_open = False
        
        # UI elements that will be referenced
        self.badge = None
        self.dropdown = None
        self.notification_list = None
    
    def build(self):
        # Create the badge that shows unread count
        self.badge = ft.Container(
            content=ft.Text("0", size=10, color=ft.colors.WHITE),
            width=18,
            height=18,
            bgcolor=ft.colors.RED_500,
            border_radius=9,
            alignment=ft.alignment.center,
            visible=False
        )
        
        # Create the notification bell icon button
        bell_button = ft.IconButton(
            icon=ft.icons.NOTIFICATIONS,
            icon_size=24,
            on_click=self.toggle_dropdown
        )
        
        # Create the badge container
        badge_container = ft.Stack(
            controls=[
                bell_button,
                ft.Container(
                    content=self.badge,
                    right=0,
                    top=0
                )
            ]
        )
        
        # Create notification list container
        self.notification_list = ft.Column(
            spacing=10,
            scroll=ft.ScrollMode.AUTO
        )
        
        # Create dropdown menu
        self.dropdown = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Text("Notifications", size=18, weight=ft.FontWeight.BOLD),
                                ft.IconButton(
                                    icon=ft.icons.CLOSE,
                                    on_click=self.toggle_dropdown
                                )
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        self.notification_list,
                        ft.Divider(),
                        ft.Row(
                            controls=[
                                ft.TextButton(
                                    text="Mark all as read",
                                    on_click=self.mark_all_as_read
                                ),
                                ft.TextButton(
                                    text="View all",
                                    on_click=self.view_all_notifications
                                )
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        )
                    ],
                    spacing=10
                ),
                padding=10,
                width=300,
                height=400
            ),
            visible=False
        )
        
        # Main container
        return ft.Column(
            controls=[
                badge_container,
                self.dropdown
            ],
            spacing=5,
            horizontal_alignment=ft.CrossAxisAlignment.END
        )
    
    def toggle_dropdown(self, e):
        """Toggle the notification dropdown visibility."""
        self.is_open = not self.is_open
        self.dropdown.visible = self.is_open
        if self.is_open:
            self.fetch_notifications()
        self.update()
    
    def fetch_notifications(self):
        """Fetch notifications for the user (mock implementation)."""
        # In a real implementation, this would fetch from the backend API
        # For now, we'll use mock data
        mock_notifications = [
            {
                "id": "1",
                "title": "Welcome to FlashFlow",
                "message": "Thanks for joining our platform!",
                "created_at": "2023-01-01T10:00:00Z",
                "status": "unread",
                "type": "welcome"
            },
            {
                "id": "2",
                "title": "New Feature Available",
                "message": "Check out our new analytics dashboard",
                "created_at": "2023-01-02T14:30:00Z",
                "status": "unread",
                "type": "info"
            }
        ]
        
        self.notifications = mock_notifications
        self.unread_count = len([n for n in mock_notifications if n["status"] == "unread"])
        self.update_notifications_list()
        self.update_badge()
    
    def update_notifications_list(self):
        """Update the notifications list in the dropdown."""
        self.notification_list.controls.clear()
        
        if not self.notifications:
            self.notification_list.controls.append(
                ft.Text("No notifications", color=ft.colors.GREY_500, italic=True)
            )
        else:
            for notification in self.notifications:
                # Create notification item
                notification_item = ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Text(
                                        notification["title"],
                                        weight=ft.FontWeight.BOLD,
                                        size=14
                                    ),
                                    ft.Container(
                                        content=ft.Text("●", size=8),
                                        width=8,
                                        height=8,
                                        bgcolor=ft.colors.RED_500 if notification["status"] == "unread" else ft.colors.TRANSPARENT,
                                        border_radius=4,
                                        visible=notification["status"] == "unread"
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            ),
                            ft.Text(notification["message"], size=12),
                            ft.Row(
                                controls=[
                                    ft.Text(
                                        self.format_time(notification["created_at"]),
                                        size=10,
                                        color=ft.colors.GREY_500
                                    ),
                                    ft.Text(
                                        notification["type"],
                                        size=10,
                                        color=ft.colors.BLUE_500
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ],
                        spacing=5
                    ),
                    padding=10,
                    border_radius=5,
                    bgcolor=ft.colors.GREY_100 if notification["status"] == "unread" else ft.colors.TRANSPARENT,
                    on_click=lambda e, nid=notification["id"]: self.on_notification_clicked(nid)
                )
                
                self.notification_list.controls.append(notification_item)
        
        self.notification_list.update()
    
    def update_badge(self):
        """Update the badge count."""
        if self.unread_count > 0:
            self.badge.content.value = str(self.unread_count) if self.unread_count < 100 else "99+"
            self.badge.visible = True
        else:
            self.badge.visible = False
        self.badge.update()
    
    def format_time(self, timestamp: str) -> str:
        """Format timestamp for display."""
        # Simple time formatting - in a real app, you'd use proper datetime parsing
        return timestamp.split("T")[1][:5]  # Extract HH:MM
    
    def on_notification_clicked(self, notification_id: str):
        """Handle notification click."""
        if self.on_notification_click:
            self.on_notification_click(notification_id)
        
        # Mark as read
        for notification in self.notifications:
            if notification["id"] == notification_id and notification["status"] == "unread":
                notification["status"] = "read"
                self.unread_count -= 1
                self.update_badge()
                self.update_notifications_list()
                break
    
    def mark_all_as_read(self, e):
        """Mark all notifications as read."""
        for notification in self.notifications:
            if notification["status"] == "unread":
                notification["status"] = "read"
        self.unread_count = 0
        self.update_badge()
        self.update_notifications_list()
        
        if self.on_mark_as_read:
            self.on_mark_as_read()
    
    def view_all_notifications(self, e):
        """View all notifications."""
        # In a real implementation, this would navigate to a full notifications page
        print("View all notifications clicked")
        self.toggle_dropdown(None)

def create_notification_bell(user_id: str, on_notification_click: Callable = None, on_mark_as_read: Callable = None) -> NotificationBell:
    """Create a notification bell component."""
    return NotificationBell(
        user_id=user_id,
        on_notification_click=on_notification_click,
        on_mark_as_read=on_mark_as_read
    )