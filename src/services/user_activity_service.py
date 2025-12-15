"""
User Activity Tracking Service
=============================

Service for tracking user activities, managing sessions, and generating analytics.
"""

import sqlite3
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from pathlib import Path

from ..models.user_activity import UserActivity, UserSession, UserAnalytics, create_user_activity, create_user_session

logger = logging.getLogger(__name__)


class UserActivityService:
    """Service for tracking user activities and sessions"""
    
    def __init__(self, db_path: str = "user_activities.db"):
        self.db_path = db_path
        self.setup_database()
    
    def setup_database(self):
        """Initialize the user activity database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create user activities table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_activities (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    activity_type TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    session_id TEXT,
                    metadata TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    referrer TEXT,
                    page_url TEXT
                )
            ''')
            
            # Create user sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP,
                    duration REAL,
                    pages_visited TEXT,
                    activities TEXT,
                    device_info TEXT,
                    ip_address TEXT
                )
            ''')
            
            # Create user analytics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_analytics (
                    user_id TEXT PRIMARY KEY,
                    total_sessions INTEGER DEFAULT 0,
                    total_activities INTEGER DEFAULT 0,
                    last_activity TIMESTAMP,
                    avg_session_duration REAL DEFAULT 0.0,
                    most_visited_pages TEXT,
                    favorite_features TEXT,
                    engagement_score REAL DEFAULT 0.0
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("User activity database initialized")
            
        except Exception as e:
            logger.error(f"Failed to setup user activity database: {e}")
            raise
    
    def track_activity(self, 
                      user_id: str,
                      activity_type: str,
                      session_id: Optional[str] = None,
                      metadata: Optional[Dict[str, Any]] = None,
                      ip_address: Optional[str] = None,
                      user_agent: Optional[str] = None,
                      referrer: Optional[str] = None,
                      page_url: Optional[str] = None) -> str:
        """Track a user activity"""
        try:
            activity = create_user_activity(
                user_id=user_id,
                activity_type=activity_type,
                session_id=session_id,
                metadata=metadata,
                ip_address=ip_address,
                user_agent=user_agent,
                referrer=referrer,
                page_url=page_url
            )
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO user_activities 
                (id, user_id, activity_type, timestamp, session_id, metadata, ip_address, user_agent, referrer, page_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                activity.id,
                activity.user_id,
                activity.activity_type,
                activity.timestamp.isoformat(),
                activity.session_id,
                json.dumps(activity.metadata),
                activity.ip_address,
                activity.user_agent,
                activity.referrer,
                activity.page_url
            ))
            
            conn.commit()
            conn.close()
            
            # Update user analytics
            self._update_user_analytics(user_id, activity)
            
            logger.debug(f"Activity tracked: {activity_type} for user {user_id}")
            return activity.id
            
        except Exception as e:
            logger.error(f"Failed to track activity: {e}")
            raise
    
    def start_session(self, 
                     user_id: str,
                     ip_address: Optional[str] = None,
                     device_info: Optional[Dict[str, Any]] = None) -> str:
        """Start a new user session"""
        try:
            session = create_user_session(
                user_id=user_id,
                ip_address=ip_address,
                device_info=device_info
            )
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO user_sessions 
                (id, user_id, start_time, pages_visited, activities, device_info, ip_address)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                session.id,
                session.user_id,
                session.start_time.isoformat(),
                json.dumps(session.pages_visited),
                json.dumps(session.activities),
                json.dumps(session.device_info),
                session.ip_address
            ))
            
            conn.commit()
            conn.close()
            
            logger.debug(f"Session started: {session.id} for user {user_id}")
            return session.id
            
        except Exception as e:
            logger.error(f"Failed to start session: {e}")
            raise
    
    def end_session(self, session_id: str) -> bool:
        """End a user session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get session data
            cursor.execute('SELECT start_time FROM user_sessions WHERE id = ?', (session_id,))
            result = cursor.fetchone()
            
            if not result:
                logger.warning(f"Session not found: {session_id}")
                conn.close()
                return False
            
            start_time = datetime.fromisoformat(result[0])
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Update session
            cursor.execute('''
                UPDATE user_sessions 
                SET end_time = ?, duration = ?
                WHERE id = ?
            ''', (end_time.isoformat(), duration, session_id))
            
            conn.commit()
            conn.close()
            
            logger.debug(f"Session ended: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to end session: {e}")
            return False
    
    def get_user_analytics(self, user_id: str) -> UserAnalytics:
        """Get analytics for a specific user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM user_analytics WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            
            conn.close()
            
            if result:
                return UserAnalytics(
                    user_id=result[0],
                    total_sessions=result[1] or 0,
                    total_activities=result[2] or 0,
                    last_activity=datetime.fromisoformat(result[3]) if result[3] else None,
                    avg_session_duration=result[4] or 0.0,
                    most_visited_pages=json.loads(result[5]) if result[5] else [],
                    favorite_features=json.loads(result[6]) if result[6] else [],
                    engagement_score=result[7] or 0.0
                )
            else:
                return UserAnalytics(user_id=user_id)
                
        except Exception as e:
            logger.error(f"Failed to get user analytics: {e}")
            return UserAnalytics(user_id=user_id)
    
    def _update_user_analytics(self, user_id: str, activity: UserActivity):
        """Update user analytics based on new activity"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get current analytics
            cursor.execute('SELECT * FROM user_analytics WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            
            if result:
                # Update existing analytics
                total_activities = (result[2] or 0) + 1
                last_activity = activity.timestamp.isoformat()
                
                cursor.execute('''
                    UPDATE user_analytics 
                    SET total_activities = ?, last_activity = ?
                    WHERE user_id = ?
                ''', (total_activities, last_activity, user_id))
            else:
                # Create new analytics record
                cursor.execute('''
                    INSERT INTO user_analytics 
                    (user_id, total_activities, last_activity)
                    VALUES (?, ?, ?)
                ''', (user_id, 1, activity.timestamp.isoformat()))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to update user analytics: {e}")


# Global instance
user_activity_service = UserActivityService()