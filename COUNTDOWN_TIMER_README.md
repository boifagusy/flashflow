# FlashFlow Countdown Timer Feature

## Overview

This feature adds countdown timer functionality to the FlashFlow application, allowing users to set and track time-based notifications or reminders. The implementation includes both simple countdown timers and a full-featured timer manager with persistent storage.

## Components

### 1. CountdownTimer
A lightweight Flet component for creating temporary countdown timers.

**Features:**
- Visual countdown display with progress bar
- Start, pause, and reset controls
- Customizable duration and title
- Callback support for timer events
- Automatic notification integration

**Usage:**
```python
from components.countdown_timer import create_countdown_timer

timer = create_countdown_timer(
    title="Work Timer",
    duration=1500,  # 25 minutes
    on_complete=lambda: print("Timer finished!"),
    on_tick=lambda remaining: print(f"{remaining} seconds left")
)
```

### 2. TimerManager
A comprehensive timer management system with persistent storage.

**Features:**
- Persistent timer storage in SQLite database
- Multiple concurrent timers
- Timer status tracking
- Notification integration
- CRUD operations for timers
- Tagging and categorization support

**Usage:**
```python
from components.timer_manager import create_timer_manager

timer_manager = create_timer_manager(
    user_id="user123",
    notification_callback=handle_notification
)
```

## Integration with Notification System

Both timer components integrate seamlessly with the existing notification system:
- Automatic notifications when timers complete
- Customizable notification messages
- Respects user notification preferences
- Supports all notification channels (in-app, email, push, SMS)

## API Endpoints

The timer service provides REST API endpoints:
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
3. `demos/countdown_demo.py` - Simple standalone demo

To run the demos:
```bash
python examples/flet_countdown_demo.py
python examples/flet_timer_manager_demo.py
python demos/countdown_demo.py
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