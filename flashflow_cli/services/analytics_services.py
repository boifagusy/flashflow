"""
FlashFlow Analytics and Monitoring Services
========================================

Comprehensive analytics and monitoring engine for FlashFlow applications.
Provides user behavior tracking, business metrics, performance monitoring, and real-time insights.
"""

import os
import json
import time
import logging
import sqlite3
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import hashlib
import threading
import uuid

logger = logging.getLogger(__name__)

@dataclass
class Event:
    """Represents a tracked event"""
    id: str
    event_type: str
    user_id: Optional[str]
    session_id: Optional[str]
    properties: Dict[str, Any]
    timestamp: datetime
    page_url: Optional[str] = None
    referrer: Optional[str] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None

@dataclass
class UserSession:
    """Represents a user session"""
    id: str
    user_id: Optional[str]
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: float = 0.0
    pages_visited: List[str] = None
    events: List[str] = None
    device_info: Dict[str, Any] = None
    utm_params: Dict[str, str] = None
    
    def __post_init__(self):
        if self.pages_visited is None:
            self.pages_visited = []
        if self.events is None:
            self.events = []
        if self.device_info is None:
            self.device_info = {}
        if self.utm_params is None:
            self.utm_params = {}

@dataclass
class ConversionEvent:
    """Represents a conversion event"""
    id: str
    user_id: str
    conversion_type: str
    value: float
    currency: str
    properties: Dict[str, Any]
    timestamp: datetime
    campaign_id: Optional[str] = None
    experiment_id: Optional[str] = None

@dataclass
class Experiment:
    """Represents an A/B test experiment"""
    id: str
    name: str
    description: str
    variants: List[str]
    status: str  # active, paused, completed
    start_date: datetime
    end_date: Optional[datetime] = None
    metrics: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metrics is None:
            self.metrics = {}

@dataclass
class ExperimentVariant:
    """Represents a variant in an A/B test"""
    id: str
    experiment_id: str
    variant_name: str
    user_count: int = 0
    conversion_count: int = 0
    conversion_rate: float = 0.0
    revenue: float = 0.0

class AnalyticsEngine:
    """Main analytics engine for tracking user behavior and business metrics"""
    
    def __init__(self, db_path: str = "analytics.db"):
        self.db_path = db_path
        self.setup_database()
        self.event_queue = []
        self.session_cache = {}
        self._flush_thread = None
        self._flush_active = False
        self._start_flush_thread()
    
    def setup_database(self):
        """Initialize analytics database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    id TEXT PRIMARY KEY,
                    event_type TEXT,
                    user_id TEXT,
                    session_id TEXT,
                    properties TEXT,
                    timestamp TIMESTAMP,
                    page_url TEXT,
                    referrer TEXT,
                    user_agent TEXT,
                    ip_address TEXT
                )
            ''')
            
            # User sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    duration REAL,
                    pages_visited TEXT,
                    events TEXT,
                    device_info TEXT,
                    utm_params TEXT
                )
            ''')
            
            # Conversion events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    conversion_type TEXT,
                    value REAL,
                    currency TEXT,
                    properties TEXT,
                    timestamp TIMESTAMP,
                    campaign_id TEXT,
                    experiment_id TEXT
                )
            ''')
            
            # Experiments table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS experiments (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    description TEXT,
                    variants TEXT,
                    status TEXT,
                    start_date TIMESTAMP,
                    end_date TIMESTAMP,
                    metrics TEXT
                )
            ''')
            
            # Experiment variants table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS experiment_variants (
                    id TEXT PRIMARY KEY,
                    experiment_id TEXT,
                    variant_name TEXT,
                    user_count INTEGER,
                    conversion_count INTEGER,
                    conversion_rate REAL,
                    revenue REAL
                )
            ''')
            
            # Page views table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS page_views (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    session_id TEXT,
                    page_url TEXT,
                    referrer TEXT,
                    timestamp TIMESTAMP,
                    duration REAL
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Analytics database initialized")
            
        except Exception as e:
            logger.error(f"Failed to setup analytics database: {e}")
            raise
    
    def track_event(self, 
                   event_type: str,
                   user_id: Optional[str] = None,
                   session_id: Optional[str] = None,
                   properties: Optional[Dict[str, Any]] = None,
                   page_url: Optional[str] = None,
                   referrer: Optional[str] = None,
                   user_agent: Optional[str] = None,
                   ip_address: Optional[str] = None) -> str:
        """Track a user event"""
        try:
            event_id = str(uuid.uuid4())
            
            event = Event(
                id=event_id,
                event_type=event_type,
                user_id=user_id,
                session_id=session_id,
                properties=properties or {},
                timestamp=datetime.now(),
                page_url=page_url,
                referrer=referrer,
                user_agent=user_agent,
                ip_address=ip_address
            )
            
            # Add to queue for batch processing
            self.event_queue.append(event)
            
            logger.debug(f"Event tracked: {event_type} - {event_id}")
            return event_id
            
        except Exception as e:
            logger.error(f"Failed to track event: {e}")
            return ""
    
    def track_page_view(self, 
                       user_id: Optional[str] = None,
                       session_id: Optional[str] = None,
                       page_url: str = "",
                       referrer: Optional[str] = None,
                       duration: float = 0.0) -> str:
        """Track a page view"""
        try:
            view_id = str(uuid.uuid4())
            
            # Store in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO page_views 
                (id, user_id, session_id, page_url, referrer, timestamp, duration)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                view_id,
                user_id,
                session_id,
                page_url,
                referrer,
                datetime.now(),
                duration
            ))
            
            conn.commit()
            conn.close()
            
            logger.debug(f"Page view tracked: {page_url} - {view_id}")
            return view_id
            
        except Exception as e:
            logger.error(f"Failed to track page view: {e}")
            return ""
    
    def start_session(self, 
                     user_id: Optional[str] = None,
                     device_info: Optional[Dict[str, Any]] = None,
                     utm_params: Optional[Dict[str, str]] = None) -> str:
        """Start a new user session"""
        try:
            session_id = str(uuid.uuid4())
            
            session = UserSession(
                id=session_id,
                user_id=user_id,
                start_time=datetime.now(),
                device_info=device_info or {},
                utm_params=utm_params or {}
            )
            
            # Store in cache
            self.session_cache[session_id] = session
            
            logger.debug(f"Session started: {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Failed to start session: {e}")
            return ""
    
    def end_session(self, session_id: str) -> bool:
        """End a user session"""
        try:
            if session_id not in self.session_cache:
                logger.warning(f"Session not found: {session_id}")
                return False
            
            session = self.session_cache[session_id]
            session.end_time = datetime.now()
            session.duration = (session.end_time - session.start_time).total_seconds()
            
            # Store in database
            self._store_session(session)
            
            # Remove from cache
            del self.session_cache[session_id]
            
            logger.debug(f"Session ended: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to end session: {e}")
            return False
    
    def track_conversion(self, 
                        user_id: str,
                        conversion_type: str,
                        value: float = 0.0,
                        currency: str = "USD",
                        properties: Optional[Dict[str, Any]] = None,
                        campaign_id: Optional[str] = None,
                        experiment_id: Optional[str] = None) -> str:
        """Track a conversion event"""
        try:
            conversion_id = str(uuid.uuid4())
            
            conversion = ConversionEvent(
                id=conversion_id,
                user_id=user_id,
                conversion_type=conversion_type,
                value=value,
                currency=currency,
                properties=properties or {},
                timestamp=datetime.now(),
                campaign_id=campaign_id,
                experiment_id=experiment_id
            )
            
            # Store in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO conversions 
                (id, user_id, conversion_type, value, currency, properties, timestamp, campaign_id, experiment_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                conversion.id,
                conversion.user_id,
                conversion.conversion_type,
                conversion.value,
                conversion.currency,
                json.dumps(conversion.properties),
                conversion.timestamp,
                conversion.campaign_id,
                conversion.experiment_id
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Conversion tracked: {conversion_type} - {conversion_id} (${value})")
            return conversion_id
            
        except Exception as e:
            logger.error(f"Failed to track conversion: {e}")
            return ""
    
    def create_experiment(self, 
                         name: str,
                         description: str,
                         variants: List[str],
                         start_date: Optional[datetime] = None) -> str:
        """Create a new A/B test experiment"""
        try:
            experiment_id = str(uuid.uuid4())
            start_date = start_date or datetime.now()
            
            experiment = Experiment(
                id=experiment_id,
                name=name,
                description=description,
                variants=variants,
                status="active",
                start_date=start_date
            )
            
            # Store in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO experiments 
                (id, name, description, variants, status, start_date, end_date, metrics)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                experiment.id,
                experiment.name,
                experiment.description,
                json.dumps(experiment.variants),
                experiment.status,
                experiment.start_date,
                experiment.end_date,
                json.dumps(experiment.metrics)
            ))
            
            # Create variant records
            for variant_name in variants:
                variant_id = str(uuid.uuid4())
                variant = ExperimentVariant(
                    id=variant_id,
                    experiment_id=experiment_id,
                    variant_name=variant_name
                )
                
                cursor.execute('''
                    INSERT INTO experiment_variants 
                    (id, experiment_id, variant_name, user_count, conversion_count, conversion_rate, revenue)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    variant.id,
                    variant.experiment_id,
                    variant.variant_name,
                    variant.user_count,
                    variant.conversion_count,
                    variant.conversion_rate,
                    variant.revenue
                ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Experiment created: {name} - {experiment_id}")
            return experiment_id
            
        except Exception as e:
            logger.error(f"Failed to create experiment: {e}")
            return ""
    
    def assign_variant(self, experiment_id: str, user_id: str) -> str:
        """Assign a user to an experiment variant"""
        try:
            # Get experiment variants
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT variants FROM experiments WHERE id = ?
            ''', (experiment_id,))
            result = cursor.fetchone()
            
            if not result:
                logger.error(f"Experiment not found: {experiment_id}")
                return ""
            
            variants = json.loads(result[0])
            if not variants:
                logger.error(f"No variants found for experiment: {experiment_id}")
                return ""
            
            # Simple hash-based assignment for consistent user-variant mapping
            hash_input = f"{experiment_id}:{user_id}"
            variant_index = int(hashlib.md5(hash_input.encode()).hexdigest(), 16) % len(variants)
            assigned_variant = variants[variant_index]
            
            # Update variant statistics
            cursor.execute('''
                UPDATE experiment_variants 
                SET user_count = user_count + 1 
                WHERE experiment_id = ? AND variant_name = ?
            ''', (experiment_id, assigned_variant))
            
            conn.commit()
            conn.close()
            
            logger.debug(f"User {user_id} assigned to variant {assigned_variant} in experiment {experiment_id}")
            return assigned_variant
            
        except Exception as e:
            logger.error(f"Failed to assign variant: {e}")
            return ""
    
    def record_conversion_for_experiment(self, experiment_id: str, variant_name: str, value: float = 0.0) -> bool:
        """Record a conversion for a specific experiment variant"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE experiment_variants 
                SET conversion_count = conversion_count + 1,
                    revenue = revenue + ?
                WHERE experiment_id = ? AND variant_name = ?
            ''', (value, experiment_id, variant_name))
            
            # Update conversion rate
            cursor.execute('''
                SELECT user_count, conversion_count FROM experiment_variants 
                WHERE experiment_id = ? AND variant_name = ?
            ''', (experiment_id, variant_name))
            result = cursor.fetchone()
            
            if result and result[0] > 0:
                conversion_rate = result[1] / result[0]
                cursor.execute('''
                    UPDATE experiment_variants 
                    SET conversion_rate = ? 
                    WHERE experiment_id = ? AND variant_name = ?
                ''', (conversion_rate, experiment_id, variant_name))
            
            conn.commit()
            conn.close()
            
            logger.debug(f"Conversion recorded for experiment {experiment_id}, variant {variant_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to record conversion for experiment: {e}")
            return False
    
    def get_experiment_results(self, experiment_id: str) -> Dict[str, Any]:
        """Get results for an experiment"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get experiment details
            cursor.execute('''
                SELECT id, name, description, variants, status, start_date, end_date, metrics
                FROM experiments WHERE id = ?
            ''', (experiment_id,))
            exp_result = cursor.fetchone()
            
            if not exp_result:
                return {}
            
            # Get variant results
            cursor.execute('''
                SELECT variant_name, user_count, conversion_count, conversion_rate, revenue
                FROM experiment_variants WHERE experiment_id = ?
            ''', (experiment_id,))
            variant_results = cursor.fetchall()
            
            conn.close()
            
            variants_data = []
            for variant in variant_results:
                variants_data.append({
                    'variant_name': variant[0],
                    'user_count': variant[1],
                    'conversion_count': variant[2],
                    'conversion_rate': variant[3],
                    'revenue': variant[4]
                })
            
            return {
                'id': exp_result[0],
                'name': exp_result[1],
                'description': exp_result[2],
                'variants': json.loads(exp_result[3]),
                'status': exp_result[4],
                'start_date': exp_result[5],
                'end_date': exp_result[6],
                'metrics': json.loads(exp_result[7]) if exp_result[7] else {},
                'results': variants_data
            }
            
        except Exception as e:
            logger.error(f"Failed to get experiment results: {e}")
            return {}
    
    def get_analytics_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive analytics summary"""
        try:
            cutoff = datetime.now() - timedelta(days=days)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total events
            cursor.execute('''
                SELECT COUNT(*) FROM events WHERE timestamp > ?
            ''', (cutoff,))
            total_events = cursor.fetchone()[0]
            
            # Total page views
            cursor.execute('''
                SELECT COUNT(*) FROM page_views WHERE timestamp > ?
            ''', (cutoff,))
            total_page_views = cursor.fetchone()[0]
            
            # Unique users
            cursor.execute('''
                SELECT COUNT(DISTINCT user_id) FROM events WHERE timestamp > ? AND user_id IS NOT NULL
            ''', (cutoff,))
            unique_users = cursor.fetchone()[0]
            
            # Conversions
            cursor.execute('''
                SELECT COUNT(*), SUM(value) FROM conversions WHERE timestamp > ?
            ''', (cutoff,))
            conv_result = cursor.fetchone()
            total_conversions = conv_result[0] or 0
            total_revenue = conv_result[1] or 0.0
            
            # Popular pages
            cursor.execute('''
                SELECT page_url, COUNT(*) as count 
                FROM page_views 
                WHERE timestamp > ? AND page_url IS NOT NULL
                GROUP BY page_url 
                ORDER BY count DESC 
                LIMIT 10
            ''', (cutoff,))
            popular_pages = [{'url': row[0], 'count': row[1]} for row in cursor.fetchall()]
            
            # Popular events
            cursor.execute('''
                SELECT event_type, COUNT(*) as count 
                FROM events 
                WHERE timestamp > ?
                GROUP BY event_type 
                ORDER BY count DESC 
                LIMIT 10
            ''', (cutoff,))
            popular_events = [{'event': row[0], 'count': row[1]} for row in cursor.fetchall()]
            
            # User sessions
            cursor.execute('''
                SELECT COUNT(*), AVG(duration) 
                FROM user_sessions 
                WHERE start_time > ?
            ''', (cutoff,))
            session_result = cursor.fetchone()
            total_sessions = session_result[0] or 0
            avg_session_duration = session_result[1] or 0.0
            
            conn.close()
            
            return {
                'period_days': days,
                'total_events': total_events,
                'total_page_views': total_page_views,
                'unique_users': unique_users,
                'total_sessions': total_sessions,
                'avg_session_duration': round(avg_session_duration, 2),
                'total_conversions': total_conversions,
                'conversion_rate': round((total_conversions / max(unique_users, 1)) * 100, 2) if unique_users > 0 else 0,
                'total_revenue': round(total_revenue, 2),
                'popular_pages': popular_pages,
                'popular_events': popular_events
            }
            
        except Exception as e:
            logger.error(f"Failed to get analytics summary: {e}")
            return {}
    
    def _store_session(self, session: UserSession):
        """Store session in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO user_sessions 
                (id, user_id, start_time, end_time, duration, pages_visited, events, device_info, utm_params)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session.id,
                session.user_id,
                session.start_time,
                session.end_time,
                session.duration,
                json.dumps(session.pages_visited),
                json.dumps(session.events),
                json.dumps(session.device_info),
                json.dumps(session.utm_params)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to store session: {e}")
    
    def _start_flush_thread(self):
        """Start background thread for flushing events"""
        if not self._flush_active:
            self._flush_active = True
            self._flush_thread = threading.Thread(target=self._flush_events, daemon=True)
            self._flush_thread.start()
    
    def _flush_events(self):
        """Background thread to flush events to database"""
        while self._flush_active:
            try:
                if self.event_queue:
                    # Process events in batches
                    batch = self.event_queue[:100]
                    self.event_queue = self.event_queue[100:]
                    
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    
                    for event in batch:
                        cursor.execute('''
                            INSERT INTO events 
                            (id, event_type, user_id, session_id, properties, timestamp, page_url, referrer, user_agent, ip_address)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            event.id,
                            event.event_type,
                            event.user_id,
                            event.session_id,
                            json.dumps(event.properties),
                            event.timestamp,
                            event.page_url,
                            event.referrer,
                            event.user_agent,
                            event.ip_address
                        ))
                    
                    conn.commit()
                    conn.close()
                
                time.sleep(5)  # Flush every 5 seconds
                
            except Exception as e:
                logger.error(f"Failed to flush events: {e}")
                time.sleep(10)  # Wait longer on error
    
    def shutdown(self):
        """Shutdown analytics engine and flush remaining events"""
        self._flush_active = False
        # Flush remaining events
        if self.event_queue:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for event in self.event_queue:
                cursor.execute('''
                    INSERT INTO events 
                    (id, event_type, user_id, session_id, properties, timestamp, page_url, referrer, user_agent, ip_address)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    event.id,
                    event.event_type,
                    event.user_id,
                    event.session_id,
                    json.dumps(event.properties),
                    event.timestamp,
                    event.page_url,
                    event.referrer,
                    event.user_agent,
                    event.ip_address
                ))
            
            conn.commit()
            conn.close()
            self.event_queue = []

def create_analytics_engine(db_path: str = "analytics.db") -> AnalyticsEngine:
    """Factory function to create analytics engine"""
    return AnalyticsEngine(db_path)