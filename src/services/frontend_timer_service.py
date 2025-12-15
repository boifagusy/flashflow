"""
Frontend Timer Service
Service for handling timer operations in Flet applications via API calls.
"""

import flet as ft
import requests
import json
from typing import Optional, List, Dict, Any

class FrontendTimerService:
    """Service for handling frontend timer operations in Flet applications."""
    
    def __init__(self, page: ft.Page, base_url: str = "/api"):
        self.page = page
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def create_timer(
        self,
        user_id: str,
        title: str,
        duration: int,
        notification_enabled: bool = True,
        notification_message: Optional[str] = None,
        repeat: bool = False,
        tags: Optional[List[str]] = None
    ) -> Optional[str]:
        """Create a new timer via API"""
        try:
            url = f"{self.base_url}/timers"
            payload = {
                "user_id": user_id,
                "title": title,
                "duration": duration,
                "notification_enabled": notification_enabled,
                "notification_message": notification_message,
                "repeat": repeat,
                "tags": tags
            }
            
            response = self.session.post(url, json=payload)
            if response.status_code == 201:
                data = response.json()
                return data.get("timer_id")
            else:
                print(f"Failed to create timer: {response.text}")
                return None
                
        except Exception as e:
            print(f"Error creating timer: {e}")
            return None
    
    def get_timer(self, timer_id: str) -> Optional[Dict[str, Any]]:
        """Get a timer by ID via API"""
        try:
            url = f"{self.base_url}/timers/{timer_id}"
            response = self.session.get(url)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to get timer: {response.text}")
                return None
                
        except Exception as e:
            print(f"Error getting timer: {e}")
            return None
    
    def get_user_timers(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all timers for a user via API"""
        try:
            url = f"{self.base_url}/timers/user/{user_id}?limit={limit}"
            response = self.session.get(url)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to get user timers: {response.text}")
                return []
                
        except Exception as e:
            print(f"Error getting user timers: {e}")
            return []
    
    def update_timer_status(self, timer_id: str, status: str) -> bool:
        """Update timer status via API"""
        try:
            url = f"{self.base_url}/timers/{timer_id}/status"
            payload = {"status": status}
            
            response = self.session.put(url, json=payload)
            return response.status_code == 200
                
        except Exception as e:
            print(f"Error updating timer status: {e}")
            return False
    
    def update_timer_time(self, timer_id: str, remaining_time: int) -> bool:
        """Update timer remaining time via API"""
        try:
            url = f"{self.base_url}/timers/{timer_id}/time"
            payload = {"remaining_time": remaining_time}
            
            response = self.session.put(url, json=payload)
            return response.status_code == 200
                
        except Exception as e:
            print(f"Error updating timer time: {e}")
            return False
    
    def delete_timer(self, timer_id: str) -> bool:
        """Delete a timer via API"""
        try:
            url = f"{self.base_url}/timers/{timer_id}"
            response = self.session.delete(url)
            return response.status_code == 200
                
        except Exception as e:
            print(f"Error deleting timer: {e}")
            return False

def initialize_frontend_timer_service(page: ft.Page, base_url: str = "/api") -> FrontendTimerService:
    """Initialize the frontend timer service"""
    return FrontendTimerService(page, base_url)