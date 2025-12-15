# User Tracking and Notification Services

This directory contains the implementation of user activity tracking and push notification capabilities for FlashFlow applications.

## Overview

The user tracking and notification system provides:

1. **User Activity Tracking** - Monitor user interactions with your application
2. **Push Notifications** - Send real-time notifications to users across multiple channels
3. **Notification Preferences** - Allow users to control which notifications they receive
4. **Analytics** - Generate insights from user behavior data

## Components

### Models

- `UserActivity` - Represents a user activity event
- `UserSession` - Tracks user sessions
- `UserAnalytics` - Stores user analytics data
- `Notification` - Represents a notification
- `NotificationPreference` - User notification preferences
- `NotificationTemplate` - Reusable notification templates
- `DeviceToken` - Device tokens for push notifications

### Services

- `UserActivityService` - Tracks user activities and manages sessions
- `NotificationService` - Handles sending notifications and managing preferences

### API Endpoints

- `/api/activity/track` - Track a user activity
- `/api/session/start` - Start a user session
- `/api/session/end/{session_id}` - End a user session
- `/api/analytics/user/{user_id}` - Get user analytics
- `/api/notifications/send` - Send a notification
- `/api/notifications/preferences` - Update notification preferences
- `/api/notifications/user/{user_id}` - Get user notifications
- `/api/notifications/read/{notification_id}` - Mark notification as read
- `/api/devices/register` - Register device token for push notifications

### Frontend Components

- `NotificationBell` - Displays notification bell with badge count
- `NotificationSettings` - Allows users to manage notification preferences

## Usage

### Tracking User Activities

To track user activities in your application:

```javascript
// Track a user activity
fetch('/api/activity/track', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    user_id: 'user123',
    activity_type: 'page_view',
    page_url: '/dashboard',
    metadata: {
      referrer: 'https://google.com',
      utm_source: 'search'
    }
  })
})
.then(response => response.json())
.then(data => console.log('Activity tracked:', data));
```

### Sending Notifications

To send notifications to users:

```javascript
// Send a notification
fetch('/api/notifications/send', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    user_id: 'user123',
    title: 'Welcome!',
    message: 'Thanks for joining our platform',
    notification_type: 'welcome',
    channel: 'in_app',
    priority: 'normal'
  })
})
.then(response => response.json())
.then(data => console.log('Notification sent:', data));
```

### Frontend Integration

To use the notification components in your React application:

```jsx
import NotificationBell from '../components/notification_bell';
import NotificationSettings from '../components/notification_settings';

function App() {
  const userId = 'user123'; // Get from your auth system
  
  return (
    <div>
      <header>
        <h1>My App</h1>
        <NotificationBell userId={userId} />
      </header>
      
      <main>
        {/* Your app content */}
      </main>
      
      <aside>
        <NotificationSettings userId={userId} />
      </aside>
    </div>
  );
}
```

## Database Schema

The services use SQLite databases with the following tables:

### User Activities
- `user_activities` - Stores individual user activity events
- `user_sessions` - Tracks user sessions
- `user_analytics` - Stores aggregated user analytics

### Notifications
- `notifications` - Stores individual notifications
- `notification_preferences` - Stores user notification preferences
- `notification_templates` - Stores notification templates
- `device_tokens` - Stores device tokens for push notifications

## Configuration

The services can be configured by passing a database path to the constructor:

```python
from services.user_activity_service import UserActivityService
from services.notification_service import NotificationService

# Create services with custom database paths
user_activity_service = UserActivityService(db_path="my_activities.db")
notification_service = NotificationService(db_path="my_notifications.db")
```

By default, the services use `user_activities.db` and `notifications.db` in the current directory.