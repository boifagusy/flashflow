# User Tracking and Push Notifications in FlashFlow

This document provides a comprehensive guide on implementing user tracking functionality and integrating push notification capabilities into FlashFlow applications.

## Overview

FlashFlow now includes built-in support for:
1. **User Activity Tracking** - Monitor and analyze how users interact with your application
2. **Push Notifications** - Send real-time notifications across multiple channels (in-app, email, SMS, push)
3. **Notification Preferences** - Allow users to control which notifications they receive
4. **Analytics** - Generate insights from user behavior data

## Implementation Details

### Backend Services

The implementation consists of two main services:

#### User Activity Service
- Tracks user activities and sessions
- Stores data in SQLite database
- Provides analytics capabilities
- Located in `src/services/user_activity_service.py`

#### Notification Service
- Handles sending notifications across multiple channels
- Manages user notification preferences
- Supports device token registration for push notifications
- Located in `src/services/notification_service.py`

### Data Models

Several data models support the tracking and notification functionality:

- `UserActivity` - Represents individual user actions
- `UserSession` - Tracks user login sessions
- `UserAnalytics` - Stores aggregated user metrics
- `Notification` - Represents individual notifications
- `NotificationPreference` - User-specific notification settings
- `NotificationTemplate` - Reusable notification templates
- `DeviceToken` - Tokens for push notifications

### API Endpoints

RESTful API endpoints are available for all functionality:

- `POST /api/activity/track` - Track user activities
- `POST /api/session/start` - Start user sessions
- `POST /api/session/end/{session_id}` - End user sessions
- `GET /api/analytics/user/{user_id}` - Get user analytics
- `POST /api/notifications/send` - Send notifications
- `POST /api/notifications/preferences` - Update preferences
- `GET /api/notifications/user/{user_id}` - Get user notifications
- `POST /api/notifications/read/{notification_id}` - Mark as read
- `POST /api/devices/register` - Register push notification tokens

### Frontend Components (Flet)

Flet components are provided for cross-platform integration:

- `NotificationBell` - Displays a notification icon with badge count
- `NotificationSettings` - Allows users to manage notification preferences

These components work seamlessly across web, desktop, and mobile platforms using the Flet framework.

## Integration Example

To integrate user tracking and notifications into your FlashFlow application:

1. **Define Models** - Add user tracking and notification fields to your models
2. **Track Activities** - Use the API to track user actions throughout your app
3. **Send Notifications** - Notify users based on their activities
4. **Display Notifications** - Use the Flet frontend components to show notifications
5. **Manage Preferences** - Allow users to control their notification settings

See `examples/user_tracking_notifications.flow` for a complete example.

## Database Structure

The services use SQLite databases with the following tables:

### User Activities Database
- `user_activities` - Individual activity events
- `user_sessions` - User session tracking
- `user_analytics` - Aggregated user metrics

### Notifications Database
- `notifications` - Individual notifications
- `notification_preferences` - User preferences
- `notification_templates` - Notification templates
- `device_tokens` - Push notification tokens

## Configuration

Services can be configured with custom database paths:

```python
user_activity_service = UserActivityService(db_path="my_activities.db")
notification_service = NotificationService(db_path="my_notifications.db")
```

By default, services use `user_activities.db` and `notifications.db`.

## Testing

Tests are provided to verify functionality:
- Run `python test_user_tracking_notifications.py` from the services directory
- See `TESTING.md` for detailed testing instructions

## Documentation

Additional documentation is available:
- `README.md` - Overview of services and usage
- `TESTING.md` - Testing instructions
- `examples/user_tracking_notifications.flow` - Complete integration example

## Getting Started

1. Start the FlashFlow development server: `flashflow serve`
2. The user tracking and notification APIs will be available at the endpoints listed above
3. Integrate the frontend components into your Flet application
4. Begin tracking user activities and sending notifications

For detailed implementation examples, see the `examples/user_tracking_notifications.flow` file.