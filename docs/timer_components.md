# FlashFlow Timer Components Documentation

## Overview

The FlashFlow application now includes comprehensive timer functionality with two main components:

1. **CountdownTimer** - A simple, lightweight countdown timer component for temporary use
2. **TimerManager** - A full-featured timer management system with persistent storage

Both components integrate seamlessly with the existing notification system to provide timely alerts when timers complete.

## CountdownTimer Component

### Description
A lightweight Flet component for creating temporary countdown timers. Perfect for one-off timers that don't need to persist between application sessions.

### Features
- Visual countdown display with progress bar
- Start, pause, and reset controls
- Customizable duration and title
- Callback support for timer events
- Automatic notification integration

### Usage Example
```python
from components.countdown_timer import create_countdown_timer

# Create a 5-minute timer
timer = create_countdown_timer(
    title="Break Timer",
    duration=300,  # 5 minutes in seconds
    on_complete=lambda: print("Timer finished!"),
    on_tick=lambda remaining: print(f"{remaining} seconds left")
)
```

### Parameters
- `title` (str): Display title for the timer
- `duration` (int): Timer duration in seconds
- `on_complete` (callable): Function to call when timer completes
- `on_tick` (callable): Function to call on each second tick

## TimerManager Component

### Description
A comprehensive timer management system that persists timers to a SQLite database. Users can create, manage, and track multiple timers that survive application restarts.

### Features
- Persistent timer storage
- Multiple concurrent timers
- Timer status tracking (pending, running, paused, completed, cancelled)
- Notification integration
- CRUD operations for timers
- Tagging and categorization support

### Usage Example
```python
from components.timer_manager import create_timer_manager

# Create a timer manager for a user
timer_manager = create_timer_manager(
    user_id="user123",
    notification_callback=handle_notification
)
```

### Parameters
- `user_id` (str): ID of the user who owns the timers
- `notification_callback` (callable): Function to call when timer notifications are triggered

## Timer Model

### Description
Data model representing a countdown timer with all its properties and state.

### Fields
- `id` (str): Unique identifier
- `user_id` (str): Owner of the timer
- `title` (str): Display title
- `duration` (int): Total duration in seconds
- `remaining_time` (int): Current remaining time in seconds
- `status` (str): Current status (pending, running, paused, completed, cancelled)
- `created_at` (datetime): Creation timestamp
- `started_at` (datetime): When the timer was last started
- `completed_at` (datetime): When the timer completed
- `notification_enabled` (bool): Whether to send notifications
- `notification_message` (str): Custom notification message
- `repeat` (bool): Whether the timer should repeat
- `tags` (list): Optional tags for categorization

## Timer Service

### Description
Backend service for managing timer persistence and operations.

### Methods
- `create_timer()`: Create a new timer
- `get_timer()`: Retrieve a timer by ID
- `get_user_timers()`: Get all timers for a user
- `update_timer_status()`: Update timer status
- `update_remaining_time()`: Update remaining time
- `delete_timer()`: Delete a timer

## Frontend Timer Service

### Description
Client-side service for communicating with the timer API endpoints.

### Methods
- `create_timer()`: Create a new timer via API
- `get_timer()`: Retrieve a timer by ID via API
- `get_user_timers()`: Get all timers for a user via API
- `update_timer_status()`: Update timer status via API
- `update_timer_time()`: Update remaining time via API
- `delete_timer()`: Delete a timer via API

## Integration with Notification System

Both timer components integrate with the existing notification system:

- When a timer completes, a notification is automatically sent
- Users can customize notification messages
- Notifications respect user preferences set in notification settings
- All notification channels are supported (in-app, email, push, SMS)

## API Endpoints

### Timer Management
- `POST /api/timers` - Create a new timer
- `GET /api/timers/<timer_id>` - Get a timer by ID
- `GET /api/timers/user/<user_id>` - Get all timers for a user
- `PUT /api/timers/<timer_id>/status` - Update timer status
- `PUT /api/timers/<timer_id>/time` - Update timer remaining time
- `DELETE /api/timers/<timer_id>` - Delete a timer

## Demo Applications

Two demo applications showcase the timer components:

1. `examples/flet_countdown_demo.py` - Demonstrates simple countdown timers
2. `examples/flet_timer_manager_demo.py` - Demonstrates the full timer management system

To run the demos:
```bash
python examples/flet_countdown_demo.py
python examples/flet_timer_manager_demo.py
```

## Example.flow Integration

The timer components are available in the example.flow file:

```flow
# Simple countdown timer
countdown_timer {
  title: "Task Timer"
  duration: 60
  on_complete: "notify_user_timer_complete"
}

# Timer manager
timer_manager {
  user_id: current_user.id
  on_notification: "handle_timer_notification"
}
```

## Best Practices

1. Use `CountdownTimer` for temporary, one-off timers
2. Use `TimerManager` for persistent timers that need to survive app restarts
3. Always provide meaningful titles for timers
4. Consider enabling notifications for important timers
5. Use tags to categorize timers for easier management
6. Handle timer completion events appropriately in your application