"""
Notification Service
===================

Service for sending notifications, managing preferences, and handling device tokens.
"""

import sqlite3
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from pathlib import Path

from ..models.notification import (
    Notification, NotificationPreference, NotificationTemplate, DeviceToken,
    create_notification, create_notification_preference, 
    create_notification_template, create_device_token
)

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for handling notifications"""
    
    def __init__(self, db_path: str = "notifications.db"):
        self.db_path = db_path
        self.setup_database()
    
    def setup_database(self):
        """Initialize the notification database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create notifications table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notifications (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    notification_type TEXT NOT NULL,
                    channel TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    data TEXT,
                    created_at TIMESTAMP NOT NULL,
                    sent_at TIMESTAMP,
                    read_at TIMESTAMP,
                    priority TEXT DEFAULT 'normal',
                    scheduled_at TIMESTAMP,
                    device_tokens TEXT
                )
            ''')
            
            # Create notification preferences table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notification_preferences (
                    user_id TEXT NOT NULL,
                    notification_type TEXT NOT NULL,
                    channel TEXT NOT NULL,
                    enabled BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL,
                    PRIMARY KEY (user_id, notification_type, channel)
                )
            ''')
            
            # Create notification templates table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notification_templates (
                    id TEXT PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    title_template TEXT NOT NULL,
                    message_template TEXT NOT NULL,
                    channels TEXT NOT NULL,
                    category TEXT NOT NULL,
                    data_schema TEXT,
                    created_at TIMESTAMP NOT NULL
                )
            ''')
            
            # Create device tokens table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS device_tokens (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    token TEXT UNIQUE NOT NULL,
                    platform TEXT NOT NULL,
                    device_info TEXT,
                    created_at TIMESTAMP NOT NULL,
                    last_used TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Notification database initialized")
            
        except Exception as e:
            logger.error(f"Failed to setup notification database: {e}")
            raise
    
    def send_notification(self, 
                         user_id: str,
                         title: str,
                         message: str,
                         notification_type: str,
                         channel: str,
                         data: Optional[Dict[str, Any]] = None,
                         priority: str = "normal",
                         scheduled_at: Optional[datetime] = None,
                         device_tokens: Optional[List[str]] = None) -> str:
        """Send a notification to a user"""
        try:
            # Check if user has enabled this notification type for this channel
            if not self._should_send_notification(user_id, notification_type, channel):
                logger.debug(f"Notification suppressed for user {user_id}: {notification_type} via {channel}")
                return ""
            
            notification = create_notification(
                user_id=user_id,
                title=title,
                message=message,
                notification_type=notification_type,
                channel=channel,
                data=data,
                priority=priority,
                scheduled_at=scheduled_at,
                device_tokens=device_tokens
            )
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO notifications 
                (id, user_id, title, message, notification_type, channel, status, data, 
                 created_at, priority, scheduled_at, device_tokens)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                notification.id,
                notification.user_id,
                notification.title,
                notification.message,
                notification.notification_type,
                notification.channel,
                notification.status,
                json.dumps(notification.data),
                notification.created_at.isoformat(),
                notification.priority,
                notification.scheduled_at.isoformat() if notification.scheduled_at else None,
                json.dumps(notification.device_tokens) if notification.device_tokens else None
            ))
            
            conn.commit()
            conn.close()
            
            # Simulate sending the notification (in a real implementation, this would send via external services)
            self._mark_notification_as_sent(notification.id)
            
            logger.debug(f"Notification sent: {notification.id} to user {user_id}")
            return notification.id
            
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            raise
    
    def create_notification_template(self,
                                   name: str,
                                   title_template: str,
                                   message_template: str,
                                   channels: List[str],
                                   category: str,
                                   data_schema: Optional[Dict[str, Any]] = None) -> str:
        """Create a notification template"""
        try:
            template = create_notification_template(
                name=name,
                title_template=title_template,
                message_template=message_template,
                channels=channels,
                category=category,
                data_schema=data_schema
            )
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO notification_templates 
                (id, name, title_template, message_template, channels, category, data_schema, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                template.id,
                template.name,
                template.title_template,
                template.message_template,
                json.dumps(template.channels),
                template.category,
                json.dumps(template.data_schema),
                template.created_at.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            logger.debug(f"Notification template created: {template.name}")
            return template.id
            
        except Exception as e:
            logger.error(f"Failed to create notification template: {e}")
            raise
    
    def register_device_token(self,
                            user_id: str,
                            token: str,
                            platform: str,
                            device_info: Optional[Dict[str, Any]] = None) -> str:
        """Register a device token for push notifications"""
        try:
            # Check if token already exists
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT id FROM device_tokens WHERE token = ?', (token,))
            result = cursor.fetchone()
            
            if result:
                # Update existing token
                device_token_id = result[0]
                cursor.execute('''
                    UPDATE device_tokens 
                    SET user_id = ?, platform = ?, device_info = ?, last_used = ?, is_active = TRUE
                    WHERE token = ?
                ''', (
                    user_id,
                    platform,
                    json.dumps(device_info) if device_info else None,
                    datetime.now().isoformat(),
                    token
                ))
            else:
                # Create new token
                device_token = create_device_token(
                    user_id=user_id,
                    token=token,
                    platform=platform,
                    device_info=device_info
                )
                device_token_id = device_token.id
                
                cursor.execute('''
                    INSERT INTO device_tokens 
                    (id, user_id, token, platform, device_info, created_at, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    device_token.id,
                    device_token.user_id,
                    device_token.token,
                    device_token.platform,
                    json.dumps(device_token.device_info) if device_token.device_info else None,
                    device_token.created_at.isoformat(),
                    device_token.is_active
                ))
            
            conn.commit()
            conn.close()
            
            logger.debug(f"Device token registered: {token} for user {user_id}")
            return device_token_id
            
        except Exception as e:
            logger.error(f"Failed to register device token: {e}")
            raise
    
    def update_notification_preference(self,
                                     user_id: str,
                                     notification_type: str,
                                     channel: str,
                                     enabled: bool) -> bool:
        """Update a user's notification preference"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if preference exists
            cursor.execute('''
                SELECT user_id FROM notification_preferences 
                WHERE user_id = ? AND notification_type = ? AND channel = ?
            ''', (user_id, notification_type, channel))
            
            result = cursor.fetchone()
            
            if result:
                # Update existing preference
                cursor.execute('''
                    UPDATE notification_preferences 
                    SET enabled = ?, updated_at = ?
                    WHERE user_id = ? AND notification_type = ? AND channel = ?
                ''', (
                    enabled,
                    datetime.now().isoformat(),
                    user_id,
                    notification_type,
                    channel
                ))
            else:
                # Create new preference
                preference = create_notification_preference(
                    user_id=user_id,
                    notification_type=notification_type,
                    channel=channel,
                    enabled=enabled
                )
                
                cursor.execute('''
                    INSERT INTO notification_preferences 
                    (user_id, notification_type, channel, enabled, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    preference.user_id,
                    preference.notification_type,
                    preference.channel,
                    preference.enabled,
                    preference.created_at.isoformat(),
                    preference.updated_at.isoformat()
                ))
            
            conn.commit()
            conn.close()
            
            logger.debug(f"Notification preference updated for user {user_id}: {notification_type} via {channel} = {enabled}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update notification preference: {e}")
            return False
    
    def get_user_notifications(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get notifications for a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, title, message, notification_type, channel, status, data, 
                       created_at, sent_at, read_at, priority
                FROM notifications 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (user_id, limit))
            
            results = cursor.fetchall()
            conn.close()
            
            notifications = []
            for row in results:
                notifications.append({
                    'id': row[0],
                    'title': row[1],
                    'message': row[2],
                    'notification_type': row[3],
                    'channel': row[4],
                    'status': row[5],
                    'data': json.loads(row[6]) if row[6] else {},
                    'created_at': row[7],
                    'sent_at': row[8],
                    'read_at': row[9],
                    'priority': row[10]
                })
            
            return notifications
            
        except Exception as e:
            logger.error(f"Failed to get user notifications: {e}")
            return []
    
    def mark_notification_as_read(self, notification_id: str) -> bool:
        """Mark a notification as read"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE notifications 
                SET status = 'read', read_at = ?
                WHERE id = ?
            ''', (datetime.now().isoformat(), notification_id))
            
            conn.commit()
            conn.close()
            
            logger.debug(f"Notification marked as read: {notification_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to mark notification as read: {e}")
            return False
    
    def _should_send_notification(self, user_id: str, notification_type: str, channel: str) -> bool:
        """Check if a notification should be sent based on user preferences"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT enabled FROM notification_preferences 
                WHERE user_id = ? AND notification_type = ? AND channel = ?
            ''', (user_id, notification_type, channel))
            
            result = cursor.fetchone()
            conn.close()
            
            # If no preference is set, default to enabled
            if not result:
                return True
            
            return bool(result[0])
            
        except Exception as e:
            logger.error(f"Failed to check notification preference: {e}")
            # Default to sending if there's an error
            return True
    
    def _mark_notification_as_sent(self, notification_id: str) -> bool:
        """Mark a notification as sent"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE notifications 
                SET status = 'sent', sent_at = ?
                WHERE id = ?
            ''', (datetime.now().isoformat(), notification_id))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to mark notification as sent: {e}")
            return False


# Global instance
notification_service = NotificationService()