"""
Timer Models
Models for handling countdown timers and scheduled notifications.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

@dataclass
class Timer:
    """Represents a countdown timer"""
    id: str
    user_id: str
    title: str
    duration: int  # in seconds
    remaining_time: int  # in seconds
    status: str  # pending, running, paused, completed, cancelled
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    notification_enabled: bool = True
    notification_message: Optional[str] = None
    repeat: bool = False
    tags: Optional[list] = None

def create_timer(
    user_id: str,
    title: str,
    duration: int,
    notification_enabled: bool = True,
    notification_message: Optional[str] = None,
    repeat: bool = False,
    tags: Optional[list] = None
) -> Timer:
    """Create a new timer"""
    return Timer(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title=title,
        duration=duration,
        remaining_time=duration,
        status="pending",
        created_at=datetime.now(),
        notification_enabled=notification_enabled,
        notification_message=notification_message,
        repeat=repeat,
        tags=tags or []
    )