"""
Notification Settings Component
A Flet component for managing notification preferences.
"""

import flet as ft
from typing import Optional, Callable, Dict, Any

class NotificationSettings(ft.Control):
    """A component for managing notification preferences."""
    
    def __init__(
        self,
        user_id: str,
        on_preference_change: Optional[Callable] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.on_preference_change = on_preference_change
        self.preferences = {}
        self.loading = False
        self.saving = False
        
        # Define notification types and channels
        self.notification_types = [
            {
                "id": "user_mentioned",
                "name": "User Mentioned",
                "description": "When someone mentions you in a post or comment",
                "channels": ["in_app", "email", "push"]
            },
            {
                "id": "order_shipped",
                "name": "Order Shipped",
                "description": "When your order has been shipped",
                "channels": ["in_app", "email", "sms"]
            },
            {
                "id": "system_maintenance",
                "name": "System Maintenance",
                "description": "Important system announcements and maintenance notices",
                "channels": ["in_app", "email", "slack"]
            },
            {
                "id": "password_reset",
                "name": "Password Reset",
                "description": "Password reset requests (cannot be disabled)",
                "channels": ["email"],
                "required": True
            }
        ]
        
        self.channel_labels = {
            "in_app": "In-App",
            "email": "Email",
            "sms": "SMS",
            "push": "Push",
            "slack": "Slack"
        }
    
    def build(self):
        # Loading indicator
        self.loading_indicator = ft.ProgressBar(visible=False)
        
        # Error message
        self.error_message = ft.Text(
            color=ft.colors.RED_500,
            visible=False
        )
        
        # Saving indicator
        self.saving_indicator = ft.Row(
            controls=[
                ft.ProgressRing(width=16, height=16),
                ft.Text("Saving preferences...")
            ],
            visible=False,
            alignment=ft.MainAxisAlignment.CENTER
        )
        
        # Notification types list
        self.types_list = ft.Column(spacing=20)
        
        # Build the main content
        content = ft.Column(
            controls=[
                self.loading_indicator,
                self.error_message,
                ft.Text("Notification Settings", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                self.types_list,
                self.saving_indicator,
                ft.Text(
                    "Note: Some critical notifications cannot be disabled for security reasons.",
                    size=12,
                    color=ft.colors.GREY_500
                )
            ],
            spacing=10
        )
        
        # Load preferences when component is built
        self.load_preferences()
        
        return content
    
    def load_preferences(self):
        """Load notification preferences (mock implementation)."""
        self.loading = True
        self.loading_indicator.visible = True
        self.update()
        
        # Mock preferences data
        self.preferences = {
            "user_mentioned": {
                "in_app": True,
                "email": True,
                "push": True
            },
            "order_shipped": {
                "in_app": True,
                "email": True,
                "sms": False
            },
            "system_maintenance": {
                "in_app": True,
                "email": True,
                "slack": False
            },
            "password_reset": {
                "email": True
            }
        }
        
        self.loading = False
        self.loading_indicator.visible = False
        self.build_notification_types()
        self.update()
    
    def build_notification_types(self):
        """Build the notification types UI."""
        self.types_list.controls.clear()
        
        for notification_type in self.notification_types:
            # Header section
            header_controls = [
                ft.Column(
                    controls=[
                        ft.Text(
                            notification_type["name"],
                            size=16,
                            weight=ft.FontWeight.BOLD
                        ),
                        ft.Text(
                            notification_type["description"],
                            size=12,
                            color=ft.colors.GREY_600
                        )
                    ],
                    spacing=2
                )
            ]
            
            if notification_type.get("required"):
                header_controls.append(
                    ft.Container(
                        content=ft.Text("Required", size=10, color=ft.colors.ORANGE_800),
                        bgcolor=ft.colors.ORANGE_100,
                        padding=ft.padding.all(4),
                        border_radius=4
                    )
                )
            
            header = ft.Row(
                controls=header_controls,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            )
            
            # Channel preferences
            channel_controls = []
            for channel in notification_type["channels"]:
                is_enabled = self.preferences.get(notification_type["id"], {}).get(channel, True)
                is_disabled = notification_type.get("required", False) and channel == "email" and notification_type["id"] == "password_reset"
                
                checkbox = ft.Checkbox(
                    label=self.channel_labels.get(channel, channel),
                    value=is_enabled,
                    disabled=is_disabled or self.saving,
                    on_change=lambda e, nt=notification_type["id"], ch=channel: self.update_preference(nt, ch, e.control.value)
                )
                
                channel_controls.append(checkbox)
            
            channels_row = ft.Row(
                controls=channel_controls,
                wrap=True,
                spacing=20
            )
            
            # Notification type card
            type_card = ft.Container(
                content=ft.Column(
                    controls=[
                        header,
                        channels_row
                    ],
                    spacing=10
                ),
                padding=15,
                border_radius=8,
                bgcolor=ft.colors.GREY_50
            )
            
            self.types_list.controls.append(type_card)
        
        self.types_list.update()
    
    def update_preference(self, notification_type: str, channel: str, enabled: bool):
        """Update a notification preference."""
        self.saving = True
        self.saving_indicator.visible = True
        self.update()
        
        # Update local preferences
        if notification_type not in self.preferences:
            self.preferences[notification_type] = {}
        self.preferences[notification_type][channel] = enabled
        
        # Update UI
        self.build_notification_types()
        
        # In a real implementation, this would save to the backend
        # For now, we'll just simulate an API call
        import time
        time.sleep(0.5)  # Simulate network delay
        
        self.saving = False
        self.saving_indicator.visible = False
        self.update()
        
        # Call the callback if provided
        if self.on_preference_change:
            self.on_preference_change(notification_type, channel, enabled)
    
    def show_error(self, message: str):
        """Show an error message."""
        self.error_message.value = message
        self.error_message.visible = True
        self.update()

def create_notification_settings(user_id: str, on_preference_change: Callable = None) -> NotificationSettings:
    """Create a notification settings component."""
    return NotificationSettings(
        user_id=user_id,
        on_preference_change=on_preference_change
    )