"""
Frontend Notification Service
A Flet-based service for handling notifications in the frontend.
"""

import flet as ft
import json
import logging
from typing import Optional, Callable, Dict, Any
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FrontendNotificationService:
    """Service for handling frontend notifications in Flet applications."""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.base_url = "/api"
        self.on_notification_received = None
        self.is_supported = True
    
    def show_notification(self, title: str, message: str, notification_type: str = "info"):
        """Show a notification using Flet's built-in snack bar."""
        try:
            # Create appropriate icon based on notification type
            if notification_type == "success":
                icon = ft.icons.CHECK_CIRCLE
                bgcolor = ft.colors.GREEN_100
                icon_color = ft.colors.GREEN_600
            elif notification_type == "warning":
                icon = ft.icons.WARNING
                bgcolor = ft.colors.ORANGE_100
                icon_color = ft.colors.ORANGE_600
            elif notification_type == "error":
                icon = ft.icons.ERROR
                bgcolor = ft.colors.RED_100
                icon_color = ft.colors.RED_600
            else:  # info
                icon = ft.icons.INFO
                bgcolor = ft.colors.BLUE_100
                icon_color = ft.colors.BLUE_600
            
            # Create the snack bar content
            content = ft.Row(
                controls=[
                    ft.Icon(icon, color=icon_color),
                    ft.Column(
                        controls=[
                            ft.Text(title, weight=ft.FontWeight.BOLD),
                            ft.Text(message, size=12)
                        ],
                        spacing=2
                    )
                ],
                spacing=10
            )
            
            # Show the snack bar
            self.page.snack_bar = ft.SnackBar(
                content=content,
                bgcolor=bgcolor,
                duration=5000  # 5 seconds
            )
            self.page.snack_bar.open = True
            self.page.update()
            
            logger.info(f"Notification shown: {title} - {message}")
            
        except Exception as e:
            logger.error(f"Failed to show notification: {e}")
    
    def request_permission(self) -> bool:
        """Request notification permission (always granted in Flet)."""
        return True
    
    def register_device_token(self, token: str, platform: str = "flet", device_info: Optional[Dict[str, Any]] = None):
        """Register device token with backend (mock implementation)."""
        try:
            # In a real implementation, this would make an API call to register the token
            logger.info(f"Device token registered: {token} for platform {platform}")
            return True
        except Exception as e:
            logger.error(f"Failed to register device token: {e}")
            return False
    
    def unregister_device_token(self, token: str):
        """Unregister device token with backend (mock implementation)."""
        try:
            # In a real implementation, this would make an API call to unregister the token
            logger.info(f"Device token unregistered: {token}")
            return True
        except Exception as e:
            logger.error(f"Failed to unregister device token: {e}")
            return False
    
    def show_custom_notification(self, title: str, message: str, options: Optional[Dict[str, Any]] = None):
        """Show a custom notification."""
        if options is None:
            options = {}
        
        notification_type = options.get("type", "info")
        duration = options.get("duration", 5000)
        
        self.show_notification(title, message, notification_type)
        
        # Trigger callback if set
        if self.on_notification_received:
            self.on_notification_received({
                "title": title,
                "message": message,
                "options": options,
                "timestamp": datetime.now().isoformat()
            })
    
    def set_on_notification_received(self, callback: Callable):
        """Set callback for when notifications are received."""
        self.on_notification_received = callback
    
    def get_permission_status(self) -> str:
        """Get notification permission status."""
        return "granted" if self.is_supported else "unsupported"

# Global instance
frontend_notification_service = None

def initialize_frontend_notification_service(page: ft.Page) -> FrontendNotificationService:
    """Initialize the frontend notification service."""
    global frontend_notification_service
    if frontend_notification_service is None:
        frontend_notification_service = FrontendNotificationService(page)
    return frontend_notification_service