"""
Timer Service
Service for managing countdown timers and scheduling notifications.
"""

import sqlite3
import json
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import threading
import time

from ..models.timer import Timer, create_timer

logger = logging.getLogger(__name__)

class TimerService:
    """Service for managing countdown timers"""
    
    def __init__(self, db_path: str = "timers.db"):
        self.db_path = db_path
        self.active_timers = {}  # Track active timer threads
        self.setup_database()
    
    def setup_database(self):
        """Initialize the timers database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create timers table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS timers (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    duration INTEGER NOT NULL,
                    remaining_time INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    notification_enabled BOOLEAN DEFAULT TRUE,
                    notification_message TEXT,
                    repeat BOOLEAN DEFAULT FALSE,
                    tags TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Timer database initialized")
            
        except Exception as e:
            logger.error(f"Failed to setup timer database: {e}")
            raise
    
    def create_timer(
        self,
        user_id: str,
        title: str,
        duration: int,
        notification_enabled: bool = True,
        notification_message: Optional[str] = None,
        repeat: bool = False,
        tags: Optional[List[str]] = None
    ) -> str:
        """Create a new timer"""
        try:
            timer = create_timer(
                user_id=user_id,
                title=title,
                duration=duration,
                notification_enabled=notification_enabled,
                notification_message=notification_message,
                repeat=repeat,
                tags=tags
            )
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO timers 
                (id, user_id, title, duration, remaining_time, status, created_at, 
                 notification_enabled, notification_message, repeat, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                timer.id,
                timer.user_id,
                timer.title,
                timer.duration,
                timer.remaining_time,
                timer.status,
                timer.created_at.isoformat(),
                timer.notification_enabled,
                timer.notification_message,
                timer.repeat,
                json.dumps(timer.tags) if timer.tags else None
            ))
            
            conn.commit()
            conn.close()
            
            logger.debug(f"Timer created: {timer.title} for user {user_id}")
            return timer.id
            
        except Exception as e:
            logger.error(f"Failed to create timer: {e}")
            raise
    
    def get_timer(self, timer_id: str) -> Optional[Timer]:
        """Get a timer by ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM timers WHERE id = ?', (timer_id,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return Timer(
                    id=result[0],
                    user_id=result[1],
                    title=result[2],
                    duration=result[3],
                    remaining_time=result[4],
                    status=result[5],
                    created_at=datetime.fromisoformat(result[6]),
                    started_at=datetime.fromisoformat(result[7]) if result[7] else None,
                    completed_at=datetime.fromisoformat(result[8]) if result[8] else None,
                    notification_enabled=bool(result[9]) if result[9] is not None else True,
                    notification_message=result[10],
                    repeat=bool(result[11]) if result[11] is not None else False,
                    tags=json.loads(result[12]) if result[12] else []
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get timer: {e}")
            return None
    
    def get_user_timers(self, user_id: str, limit: int = 50) -> List[Timer]:
        """Get all timers for a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM timers 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (user_id, limit))
            
            results = cursor.fetchall()
            conn.close()
            
            timers = []
            for result in results:
                timers.append(Timer(
                    id=result[0],
                    user_id=result[1],
                    title=result[2],
                    duration=result[3],
                    remaining_time=result[4],
                    status=result[5],
                    created_at=datetime.fromisoformat(result[6]),
                    started_at=datetime.fromisoformat(result[7]) if result[7] else None,
                    completed_at=datetime.fromisoformat(result[8]) if result[8] else None,
                    notification_enabled=bool(result[9]) if result[9] is not None else True,
                    notification_message=result[10],
                    repeat=bool(result[11]) if result[11] is not None else False,
                    tags=json.loads(result[12]) if result[12] else []
                ))
            
            return timers
            
        except Exception as e:
            logger.error(f"Failed to get user timers: {e}")
            return []
    
    def update_timer_status(self, timer_id: str, status: str) -> bool:
        """Update timer status"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            timestamp_field = None
            timestamp_value = None
            
            if status == "running":
                timestamp_field = "started_at"
                timestamp_value = datetime.now().isoformat()
            elif status == "completed":
                timestamp_field = "completed_at"
                timestamp_value = datetime.now().isoformat()
            
            if timestamp_field:
                cursor.execute(f'''
                    UPDATE timers 
                    SET status = ?, {timestamp_field} = ?
                    WHERE id = ?
                ''', (status, timestamp_value, timer_id))
            else:
                cursor.execute('''
                    UPDATE timers 
                    SET status = ?
                    WHERE id = ?
                ''', (status, timer_id))
            
            conn.commit()
            conn.close()
            
            logger.debug(f"Timer {timer_id} status updated to {status}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update timer status: {e}")
            return False
    
    def update_remaining_time(self, timer_id: str, remaining_time: int) -> bool:
        """Update timer remaining time"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE timers 
                SET remaining_time = ?
                WHERE id = ?
            ''', (remaining_time, timer_id))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update timer remaining time: {e}")
            return False
    
    def delete_timer(self, timer_id: str) -> bool:
        """Delete a timer"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM timers WHERE id = ?', (timer_id,))
            
            conn.commit()
            conn.close()
            
            # Stop active timer if running
            if timer_id in self.active_timers:
                del self.active_timers[timer_id]
            
            logger.debug(f"Timer deleted: {timer_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete timer: {e}")
            return False

# Global instance
timer_service = TimerService()