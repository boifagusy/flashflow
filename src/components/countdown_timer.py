"""
Countdown Timer Component
A Flet component for creating and managing countdown timers with notifications.
"""

import flet as ft
import threading
import time
from datetime import datetime, timedelta
from typing import Optional, Callable, Dict, Any

class CountdownTimer(ft.Control):
    """A countdown timer component with notification integration."""
    
    def __init__(
        self,
        title: str = "Timer",
        duration: int = 60,  # seconds
        on_complete: Optional[Callable] = None,
        on_tick: Optional[Callable] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.title = title
        self.duration = duration
        self.on_complete = on_complete
        self.on_tick = on_tick
        self.remaining_time = duration
        self.is_running = False
        self.is_paused = False
        self.timer_thread = None
        self.start_time = None
        self.end_time = None
        
        # UI elements
        self.time_display = None
        self.start_button = None
        self.pause_button = None
        self.reset_button = None
        self.progress_bar = None
    
    def build(self):
        # Time display
        self.time_display = ft.Text(
            self.format_time(self.remaining_time),
            size=24,
            weight=ft.FontWeight.BOLD
        )
        
        # Progress bar
        self.progress_bar = ft.ProgressBar(
            value=1.0,
            width=200,
            bar_height=8
        )
        
        # Control buttons
        self.start_button = ft.IconButton(
            icon=ft.icons.PLAY_ARROW,
            tooltip="Start Timer",
            on_click=self.start_timer
        )
        
        self.pause_button = ft.IconButton(
            icon=ft.icons.PAUSE,
            tooltip="Pause Timer",
            on_click=self.pause_timer,
            visible=False
        )
        
        self.reset_button = ft.IconButton(
            icon=ft.icons.RESTART_ALT,
            tooltip="Reset Timer",
            on_click=self.reset_timer
        )
        
        # Timer title
        title_text = ft.Text(self.title, size=16, weight=ft.FontWeight.BOLD)
        
        # Controls row
        controls_row = ft.Row(
            controls=[
                self.start_button,
                self.pause_button,
                self.reset_button
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )
        
        # Main container
        return ft.Container(
            content=ft.Column(
                controls=[
                    title_text,
                    self.time_display,
                    self.progress_bar,
                    controls_row
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10
            ),
            padding=15,
            border_radius=10,
            bgcolor=ft.colors.GREY_100
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
    
    def start_timer(self, e):
        """Start the countdown timer."""
        if not self.is_running:
            self.is_running = True
            self.is_paused = False
            self.start_button.visible = False
            self.pause_button.visible = True
            
            if self.remaining_time == self.duration:  # First start
                self.start_time = datetime.now()
                self.end_time = self.start_time + timedelta(seconds=self.duration)
            elif self.is_paused:  # Resume from pause
                # Calculate remaining time based on original end time
                remaining_delta = self.end_time - datetime.now()
                self.remaining_time = max(0, int(remaining_delta.total_seconds()))
                self.is_paused = False
            
            # Start timer thread
            self.timer_thread = threading.Thread(target=self._timer_worker, daemon=True)
            self.timer_thread.start()
            
            self.update()
    
    def pause_timer(self, e):
        """Pause the countdown timer."""
        if self.is_running and not self.is_paused:
            self.is_running = False
            self.is_paused = True
            self.start_button.visible = True
            self.pause_button.visible = False
            self.update()
    
    def reset_timer(self, e):
        """Reset the countdown timer."""
        self.is_running = False
        self.is_paused = False
        self.remaining_time = self.duration
        self.start_time = None
        self.end_time = None
        self.start_button.visible = True
        self.pause_button.visible = False
        
        if self.time_display:
            self.time_display.value = self.format_time(self.remaining_time)
            self.progress_bar.value = 1.0
            self.update()
    
    def _timer_worker(self):
        """Background thread for timer countdown."""
        while self.is_running and self.remaining_time > 0:
            time.sleep(1)
            if self.is_running:  # Check again in case paused during sleep
                self.remaining_time -= 1
                
                # Update UI on main thread
                self.page.invoke(self._update_ui)
                
                # Call tick callback if provided
                if self.on_tick:
                    self.on_tick(self.remaining_time)
        
        # Timer completed
        if self.remaining_time <= 0 and self.is_running:
            self.page.invoke(self._timer_completed)
    
    def _update_ui(self):
        """Update the UI with current timer state."""
        if self.time_display:
            self.time_display.value = self.format_time(self.remaining_time)
            # Update progress bar (1.0 = complete, 0.0 = finished)
            progress = self.remaining_time / self.duration
            self.progress_bar.value = progress
            self.update()
    
    def _timer_completed(self):
        """Handle timer completion."""
        self.is_running = False
        self.start_button.visible = True
        self.pause_button.visible = False
        self.progress_bar.value = 0.0
        self.update()
        
        # Call completion callback if provided
        if self.on_complete:
            self.on_complete()
    
    def set_duration(self, seconds: int):
        """Set the timer duration."""
        self.duration = seconds
        self.reset_timer(None)
    
    def get_remaining_time(self) -> int:
        """Get the remaining time in seconds."""
        return self.remaining_time
    
    def is_active(self) -> bool:
        """Check if the timer is currently running."""
        return self.is_running

def create_countdown_timer(
    title: str = "Timer",
    duration: int = 60,
    on_complete: Callable = None,
    on_tick: Callable = None
) -> CountdownTimer:
    """Create a countdown timer component."""
    return CountdownTimer(
        title=title,
        duration=duration,
        on_complete=on_complete,
        on_tick=on_tick
    )