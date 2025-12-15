# Testing User Tracking and Notification Services

This document explains how to test the user tracking and notification services.

## Running Tests

To run the tests, navigate to the services directory and execute the test script:

```bash
cd src/services
python test_user_tracking_notifications.py
```

Or from the project root:

```bash
python -m src.services.test_user_tracking_notifications
```

## Test Overview

The test script performs the following checks:

1. **Data Model Tests**
   - Creates user activity objects
   - Creates notification objects

2. **User Activity Service Tests**
   - Tracks user activities
   - Manages user sessions
   - Retrieves user analytics

3. **Notification Service Tests**
   - Sends notifications
   - Manages notification templates
   - Registers device tokens
   - Updates notification preferences
   - Retrieves and manages user notifications

## Manual Testing

You can also test the API endpoints manually using curl or a tool like Postman:

### Track User Activity
```bash
curl -X POST http://localhost:8000/api/activity/track \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "activity_type": "page_view",
    "page_url": "/dashboard"
  }'
```

### Send Notification
```bash
curl -X POST http://localhost:8000/api/notifications/send \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "title": "Test Notification",
    "message": "This is a test notification",
    "notification_type": "test",
    "channel": "in_app"
  }'
```

### Get User Notifications
```bash
curl http://localhost:8000/api/notifications/user/user123
```

## Test Databases

The tests create temporary SQLite databases:
- `test_activities.db` - For user activity data
- `test_notifications.db` - For notification data

These databases are automatically cleaned up after the tests run.