"""
Notification Models
==================

Models for handling push notifications, user preferences, and notification templates.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid


@dataclass
class Notification:
    """Represents a notification"""
    id: str
    user_id: str
    title: str
    message: str
    notification_type: str  # info, warning, success, error, etc.
    channel: str  # in_app, email, sms, push, etc.
    status: str = "pending"  # pending, sent, delivered, read
    data: Optional[Dict[str, Any]] = None
    created_at: datetime = None
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    priority: str = "normal"  # low, normal, high, urgent
    scheduled_at: Optional[datetime] = None
    device_tokens: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.data is None:
            self.data = {}


@dataclass
class NotificationPreference:
    """Represents user notification preferences"""
    user_id: str
    notification_type: str
    channel: str
    enabled: bool = True
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()


@dataclass
class NotificationTemplate:
    """Represents a notification template"""
    id: str
    name: str
    title_template: str
    message_template: str
    channels: List[str]
    category: str
    data_schema: Optional[Dict[str, Any]] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.data_schema is None:
            self.data_schema = {}


@dataclass
class DeviceToken:
    """Represents a device token for push notifications"""
    id: str
    user_id: str
    token: str
    platform: str  # ios, android, web
    device_info: Optional[Dict[str, Any]] = None
    created_at: datetime = None
    last_used: Optional[datetime] = None
    is_active: bool = True
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.device_info is None:
            self.device_info = {}


def create_notification(
    user_id: str,
    title: str,
    message: str,
    notification_type: str,
    channel: str,
    data: Optional[Dict[str, Any]] = None,
    priority: str = "normal",
    scheduled_at: Optional[datetime] = None,
    device_tokens: Optional[List[str]] = None
) -> Notification:
    """Create a new notification"""
    return Notification(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title=title,
        message=message,
        notification_type=notification_type,
        channel=channel,
        data=data or {},
        priority=priority,
        scheduled_at=scheduled_at,
        device_tokens=device_tokens
    )


def create_notification_preference(
    user_id: str,
    notification_type: str,
    channel: str,
    enabled: bool = True
) -> NotificationPreference:
    """Create a new notification preference"""
    return NotificationPreference(
        user_id=user_id,
        notification_type=notification_type,
        channel=channel,
        enabled=enabled
    )


def create_notification_template(
    name: str,
    title_template: str,
    message_template: str,
    channels: List[str],
    category: str,
    data_schema: Optional[Dict[str, Any]] = None
) -> NotificationTemplate:
    """Create a new notification template"""
    return NotificationTemplate(
        id=str(uuid.uuid4()),
        name=name,
        title_template=title_template,
        message_template=message_template,
        channels=channels,
        category=category,
        data_schema=data_schema or {}
    )


def create_device_token(
    user_id: str,
    token: str,
    platform: str,
    device_info: Optional[Dict[str, Any]] = None
) -> DeviceToken:
    """Create a new device token"""
    return DeviceToken(
        id=str(uuid.uuid4()),
        user_id=user_id,
        token=token,
        platform=platform,
        device_info=device_info or {}
    )