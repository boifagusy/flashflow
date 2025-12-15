"""
Timer Manager Component
An enhanced Flet component for managing multiple countdown timers with persistence.
"""

import flet as ft
import threading
import time
from datetime import datetime
from typing import Optional, Callable, List, Dict, Any

from ..services.timer_service import timer_service
from ..models.timer import Timer

class TimerManager(ft.Control):
    """A component for managing multiple countdown timers"""
    
    def __init__(
        self,
        user_id: str,
        notification_callback: Optional[Callable] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.notification_callback = notification_callback
        self.timers = []  # Local cache of timer objects
        self.timer_controls = {}  # Map timer IDs to UI controls
        self.active_threads = {}  # Track active timer threads
        
        # UI elements
        self.timers_list = None
        self.title_input = None
        self.duration_input = None
        self.create_button = None
    
    def build(self):
        # Inputs for creating new timers
        self.title_input = ft.TextField(
            label="Timer Title",
            width=200
        )
        
        self.duration_input = ft.TextField(
            label="Duration (seconds)",
            keyboard_type=ft.KeyboardType.NUMBER,
            width=150,
            value="60"
        )
        
        self.create_button = ft.ElevatedButton(
            "Create Timer",
            on_click=self.create_new_timer
        )
        
        # Timers list
        self.timers_list = ft.ListView(
            expand=True,
            spacing=10,
            padding=10
        )
        
        # Main layout
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Timer Manager", size=20, weight=ft.FontWeight.BOLD),
                    ft.Row(
                        controls=[
                            self.title_input,
                            self.duration_input,
                            self.create_button
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        spacing=10
                    ),
                    ft.Divider(),
                    ft.Text("Active Timers:", size=16),
                    self.timers_list
                ],
                spacing=10
            ),
            padding=15,
            expand=True
        )
    
    def did_mount(self):
        """Load timers when component is mounted"""
        self.load_user_timers()
    
    def load_user_timers(self):
        """Load all timers for the current user"""
        self.timers = timer_service.get_user_timers(self.user_id)
        self.refresh_timer_list()
    
    def refresh_timer_list(self):
        """Refresh the displayed list of timers"""
        self.timers_list.controls.clear()
        
        for timer in self.timers:
            timer_control = self.create_timer_control(timer)
            self.timers_list.controls.append(timer_control)
            self.timer_controls[timer.id] = timer_control
        
        self.update()
    
    def create_timer_control(self, timer: Timer):
        """Create a UI control for a timer"""
        # Time display
        time_display = ft.Text(
            self.format_time(timer.remaining_time),
            size=18,
            weight=ft.FontWeight.BOLD
        )
        
        # Status indicator
        status_color = {
            "pending": ft.colors.GREY,
            "running": ft.colors.GREEN,
            "paused": ft.colors.ORANGE,
            "completed": ft.colors.BLUE,
            "cancelled": ft.colors.RED
        }.get(timer.status, ft.colors.GREY)
        
        status_indicator = ft.Container(
            width=12,
            height=12,
            border_radius=6,
            bgcolor=status_color
        )
        
        # Control buttons
        start_button = ft.IconButton(
            icon=ft.icons.PLAY_ARROW,
            tooltip="Start Timer",
            on_click=lambda e, tid=timer.id: self.start_timer(tid)
        )
        
        pause_button = ft.IconButton(
            icon=ft.icons.PAUSE,
            tooltip="Pause Timer",
            on_click=lambda e, tid=timer.id: self.pause_timer(tid),
            visible=timer.status == "running"
        )
        
        reset_button = ft.IconButton(
            icon=ft.icons.RESTART_ALT,
            tooltip="Reset Timer",
            on_click=lambda e, tid=timer.id: self.reset_timer(tid)
        )
        
        delete_button = ft.IconButton(
            icon=ft.icons.DELETE,
            tooltip="Delete Timer",
            on_click=lambda e, tid=timer.id: self.delete_timer(tid)
        )
        
        # Update button visibility based on timer status
        start_button.visible = timer.status in ["pending", "paused"]
        pause_button.visible = timer.status == "running"
        
        # Timer row
        timer_row = ft.Row(
            controls=[
                status_indicator,
                ft.Column(
                    controls=[
                        ft.Text(timer.title, size=16, weight=ft.FontWeight.BOLD),
                        time_display,
                        ft.Text(f"Status: {timer.status.capitalize()}", size=12)
                    ],
                    spacing=2
                ),
                ft.Row(
                    controls=[start_button, pause_button, reset_button, delete_button],
                    spacing=5
                )
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )
        
        return ft.Container(
            content=timer_row,
            padding=10,
            border=ft.border.all(1, ft.colors.GREY_300),
            border_radius=5
        )
    
    def format_time(self, seconds: int) -> str:
        """Format seconds into MM:SS or HH:MM:SS format."""
        if seconds >= 3600:  # 1 hour or more
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            minutes = seconds // 60
            secs = seconds % 60
            return f"{minutes:02d}:{secs:02d}"
    
    def create_new_timer(self, e):
        """Create a new timer from input fields"""
        title = self.title_input.value.strip()
        if not title:
            title = "Untitled Timer"
        
        try:
            duration = int(self.duration_input.value)
            if duration <= 0:
                duration = 60  # Default to 1 minute
        except ValueError:
            duration = 60
        
        # Create timer in database
        timer_id = timer_service.create_timer(
            user_id=self.user_id,
            title=title,
            duration=duration
        )
        
        # Reload timers
        self.load_user_timers()
        
        # Clear inputs
        self.title_input.value = ""
        self.duration_input.value = "60"
        self.update()
    
    def start_timer(self, timer_id: str):
        """Start a timer"""
        timer = timer_service.get_timer(timer_id)
        if not timer:
            return
        
        # Update status in database
        timer_service.update_timer_status(timer_id, "running")
        
        # Start background thread for countdown
        thread = threading.Thread(
            target=self._timer_worker,
            args=(timer_id,),
            daemon=True
        )
        self.active_threads[timer_id] = thread
        thread.start()
        
        # Refresh UI
        self.load_user_timers()
    
    def pause_timer(self, timer_id: str):
        """Pause a timer"""
        # Update status in database
        timer_service.update_timer_status(timer_id, "paused")
        
        # Stop background thread if running
        if timer_id in self.active_threads:
            del self.active_threads[timer_id]
        
        # Refresh UI
        self.load_user_timers()
    
    def reset_timer(self, timer_id: str):
        """Reset a timer"""
        timer = timer_service.get_timer(timer_id)
        if not timer:
            return
        
        # Update in database
        timer_service.update_timer_status(timer_id, "pending")
        timer_service.update_remaining_time(timer_id, timer.duration)
        
        # Stop background thread if running
        if timer_id in self.active_threads:
            del self.active_threads[timer_id]
        
        # Refresh UI
        self.load_user_timers()
    
    def delete_timer(self, timer_id: str):
        """Delete a timer"""
        # Delete from database
        timer_service.delete_timer(timer_id)
        
        # Stop background thread if running
        if timer_id in self.active_threads:
            del self.active_threads[timer_id]
        
        # Refresh UI
        self.load_user_timers()
    
    def _timer_worker(self, timer_id: str):
        """Background thread for timer countdown"""
        timer = timer_service.get_timer(timer_id)
        if not timer or timer.status != "running":
            return
        
        remaining = timer.remaining_time
        
        while remaining > 0 and timer_id in self.active_threads:
            time.sleep(1)
            remaining -= 1
            
            # Update remaining time in database
            timer_service.update_remaining_time(timer_id, remaining)
            
            # Update UI periodically
            if remaining % 5 == 0:  # Update every 5 seconds
                self.load_user_timers()
        
        # Timer completed
        if remaining <= 0 and timer_id in self.active_threads:
            timer_service.update_timer_status(timer_id, "completed")
            
            # Send notification if enabled
            timer = timer_service.get_timer(timer_id)
            if timer and timer.notification_enabled and self.notification_callback:
                message = timer.notification_message or f"Timer '{timer.title}' has completed!"
                self.notification_callback("Timer Completed", message, "success")
            
            # Refresh UI
            self.load_user_timers()
            
            # Clean up thread
            if timer_id in self.active_threads:
                del self.active_threads[timer_id]

def create_timer_manager(
    user_id: str,
    notification_callback: Optional[Callable] = None
) -> TimerManager:
    """Create a timer manager component"""
    return TimerManager(
        user_id=user_id,
        notification_callback=notification_callback
    )