#!/usr/bin/env python3
"""
Test script for user tracking and notification services
"""

import os
import sys
import json
from datetime import datetime

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.user_activity_service import UserActivityService
from services.notification_service import NotificationService
from models.user_activity import create_user_activity
from models.notification import create_notification

def test_user_activity_service():
    """Test the user activity service"""
    print("Testing User Activity Service...")
    
    # Create service instance
    service = UserActivityService("test_activities.db")
    
    # Test tracking an activity
    activity_id = service.track_activity(
        user_id="user123",
        activity_type="login",
        page_url="/login",
        metadata={"ip": "192.168.1.1"}
    )
    print(f"Tracked activity with ID: {activity_id}")
    
    # Test starting a session
    session_id = service.start_session(
        user_id="user123",
        ip_address="192.168.1.1",
        device_info={"browser": "Chrome", "os": "Windows"}
    )
    print(f"Started session with ID: {session_id}")
    
    # Test ending a session
    success = service.end_session(session_id)
    print(f"Ended session: {success}")
    
    # Test getting user analytics
    analytics = service.get_user_analytics("user123")
    print(f"User analytics: {analytics}")
    
    print("User Activity Service tests completed successfully!\n")

def test_notification_service():
    """Test the notification service"""
    print("Testing Notification Service...")
    
    # Create service instance
    service = NotificationService("test_notifications.db")
    
    # Test sending a notification
    notification_id = service.send_notification(
        user_id="user123",
        title="Test Notification",
        message="This is a test notification",
        notification_type="test",
        channel="in_app"
    )
    print(f"Sent notification with ID: {notification_id}")
    
    # Test creating a notification template
    template_id = service.create_notification_template(
        name="welcome_email",
        title_template="Welcome {{user_name}}!",
        message_template="Welcome to our platform, {{user_name}}!",
        channels=["email"],
        category="welcome"
    )
    print(f"Created template with ID: {template_id}")
    
    # Test registering a device token
    device_token_id = service.register_device_token(
        user_id="user123",
        token="test_device_token_123",
        platform="web",
        device_info={"browser": "Chrome", "os": "Windows"}
    )
    print(f"Registered device token with ID: {device_token_id}")
    
    # Test updating notification preference
    success = service.update_notification_preference(
        user_id="user123",
        notification_type="test",
        channel="email",
        enabled=True
    )
    print(f"Updated notification preference: {success}")
    
    # Test getting user notifications
    notifications = service.get_user_notifications("user123")
    print(f"Retrieved {len(notifications)} notifications")
    
    # Test marking notification as read
    if notifications:
        success = service.mark_notification_as_read(notifications[0]['id'])
        print(f"Marked notification as read: {success}")
    
    print("Notification Service tests completed successfully!\n")

def test_models():
    """Test the data models"""
    print("Testing Data Models...")
    
    # Test creating user activity
    activity = create_user_activity(
        user_id="user123",
        activity_type="page_view",
        page_url="/dashboard",
        metadata={"referrer": "https://google.com"}
    )
    print(f"Created user activity: {activity}")
    
    # Test creating notification
    notification = create_notification(
        user_id="user123",
        title="Test",
        message="Test message",
        notification_type="test",
        channel="in_app"
    )
    print(f"Created notification: {notification}")
    
    print("Data Model tests completed successfully!\n")

def main():
    """Run all tests"""
    print("Running User Tracking and Notification Service Tests\n")
    
    try:
        test_models()
        test_user_activity_service()
        test_notification_service()
        
        print("All tests completed successfully! 🎉")
        
        # Clean up test databases
        if os.path.exists("test_activities.db"):
            os.remove("test_activities.db")
        if os.path.exists("test_notifications.db"):
            os.remove("test_notifications.db")
            
        print("Cleaned up test databases")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        # Clean up test databases even if tests fail
        if os.path.exists("test_activities.db"):
            os.remove("test_activities.db")
        if os.path.exists("test_notifications.db"):
            os.remove("test_notifications.db")
        sys.exit(1)

if __name__ == "__main__":
    main()