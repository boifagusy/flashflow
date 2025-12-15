"""
User Activity Tracking Models
============================

Models for tracking user activities, sessions, and behavior analytics.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid


@dataclass
class UserActivity:
    """Represents a user activity event"""
    id: str
    user_id: str
    activity_type: str  # login, page_view, button_click, form_submit, etc.
    timestamp: datetime
    session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    referrer: Optional[str] = None
    page_url: Optional[str] = None


@dataclass
class UserSession:
    """Represents a user session"""
    id: str
    user_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: float = 0.0  # in seconds
    pages_visited: List[str] = None
    activities: List[str] = None  # List of activity IDs
    device_info: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None


@dataclass
class UserAnalytics:
    """Represents user analytics data"""
    user_id: str
    total_sessions: int = 0
    total_activities: int = 0
    last_activity: Optional[datetime] = None
    avg_session_duration: float = 0.0
    most_visited_pages: List[str] = None
    favorite_features: List[str] = None
    engagement_score: float = 0.0


def create_user_activity(
    user_id: str,
    activity_type: str,
    session_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    referrer: Optional[str] = None,
    page_url: Optional[str] = None
) -> UserActivity:
    """Create a new user activity record"""
    return UserActivity(
        id=str(uuid.uuid4()),
        user_id=user_id,
        activity_type=activity_type,
        timestamp=datetime.now(),
        session_id=session_id,
        metadata=metadata or {},
        ip_address=ip_address,
        user_agent=user_agent,
        referrer=referrer,
        page_url=page_url
    )


def create_user_session(
    user_id: str,
    ip_address: Optional[str] = None,
    device_info: Optional[Dict[str, Any]] = None
) -> UserSession:
    """Create a new user session"""
    return UserSession(
        id=str(uuid.uuid4()),
        user_id=user_id,
        start_time=datetime.now(),
        pages_visited=[],
        activities=[],
        ip_address=ip_address,
        device_info=device_info or {}
    )