"""
Debug and Monitoring Services for FlashFlow
Provides intelligent debugging, error tracking, performance monitoring, and admin panel functionality
"""

import os
import json
import time
import logging
import traceback
import psutil
import sqlite3
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict, deque
import hashlib
import threading
import weakref

logger = logging.getLogger(__name__)

@dataclass
class ErrorReport:
    """Error report data structure"""
    id: str
    timestamp: datetime
    error_type: str
    error_message: str
    stack_trace: str
    user_id: Optional[str]
    session_id: Optional[str]
    request_path: Optional[str]
    user_agent: Optional[str]
    severity: str  # critical, error, warning, info
    resolved: bool = False
    tags: List[str] = None

@dataclass
class PerformanceMetric:
    """Performance monitoring data"""
    id: str
    timestamp: datetime
    metric_type: str  # response_time, memory_usage, cpu_usage, db_query
    value: float
    context: Dict[str, Any]
    endpoint: Optional[str] = None

@dataclass
class SystemHealth:
    """System health status"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    active_connections: int
    error_rate: float
    avg_response_time: float
    status: str  # healthy, warning, critical

class ErrorTracker:
    """Error tracking and analysis"""
    
    def __init__(self, db_path: str = "debug.db"):
        self.db_path = db_path
        self.setup_database()
        self.error_cache = deque(maxlen=1000)
    
    def setup_database(self):
        """Initialize error tracking database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Error reports table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS error_reports (
                    id TEXT PRIMARY KEY,
                    timestamp TIMESTAMP,
                    error_type TEXT,
                    error_message TEXT,
                    stack_trace TEXT,
                    user_id TEXT,
                    session_id TEXT,
                    request_path TEXT,
                    user_agent TEXT,
                    severity TEXT,
                    resolved BOOLEAN DEFAULT FALSE,
                    tags TEXT
                )
            ''')
            
            # Performance metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id TEXT PRIMARY KEY,
                    timestamp TIMESTAMP,
                    metric_type TEXT,
                    value REAL,
                    context TEXT,
                    endpoint TEXT
                )
            ''')
            
            # System health table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_health (
                    timestamp TIMESTAMP PRIMARY KEY,
                    cpu_percent REAL,
                    memory_percent REAL,
                    disk_percent REAL,
                    active_connections INTEGER,
                    error_rate REAL,
                    avg_response_time REAL,
                    status TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Debug database initialized")
            
        except Exception as e:
            logger.error(f"Failed to setup debug database: {e}")
            raise
    
    def report_error(self, 
                    error: Exception,
                    user_id: Optional[str] = None,
                    session_id: Optional[str] = None,
                    request_path: Optional[str] = None,
                    user_agent: Optional[str] = None,
                    severity: str = "error",
                    tags: Optional[List[str]] = None) -> str:
        """Report an error with context"""
        try:
            error_id = hashlib.md5(f"{str(error)}{time.time()}".encode()).hexdigest()
            
            error_report = ErrorReport(
                id=error_id,
                timestamp=datetime.now(),
                error_type=type(error).__name__,
                error_message=str(error),
                stack_trace=traceback.format_exc(),
                user_id=user_id,
                session_id=session_id,
                request_path=request_path,
                user_agent=user_agent,
                severity=severity,
                tags=tags or []
            )
            
            # Store in database
            self._store_error_report(error_report)
            
            # Cache for quick access
            self.error_cache.append(error_report)
            
            logger.error(f"Error reported: {error_id} - {error}")
            return error_id
            
        except Exception as e:
            logger.error(f"Failed to report error: {e}")
            return ""
    
    def _store_error_report(self, error_report: ErrorReport):
        """Store error report in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO error_reports 
                (id, timestamp, error_type, error_message, stack_trace, 
                 user_id, session_id, request_path, user_agent, severity, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                error_report.id,
                error_report.timestamp,
                error_report.error_type,
                error_report.error_message,
                error_report.stack_trace,
                error_report.user_id,
                error_report.session_id,
                error_report.request_path,
                error_report.user_agent,
                error_report.severity,
                json.dumps(error_report.tags)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to store error report: {e}")
    
    def get_error_reports(self, 
                         severity: Optional[str] = None,
                         resolved: Optional[bool] = None,
                         limit: int = 100) -> List[ErrorReport]:
        """Get error reports with filters"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT * FROM error_reports WHERE 1=1"
            params = []
            
            if severity:
                query += " AND severity = ?"
                params.append(severity)
            
            if resolved is not None:
                query += " AND resolved = ?"
                params.append(resolved)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            reports = []
            for row in rows:
                reports.append(ErrorReport(
                    id=row[0],
                    timestamp=datetime.fromisoformat(row[1]),
                    error_type=row[2],
                    error_message=row[3],
                    stack_trace=row[4],
                    user_id=row[5],
                    session_id=row[6],
                    request_path=row[7],
                    user_agent=row[8],
                    severity=row[9],
                    resolved=bool(row[10]),
                    tags=json.loads(row[11]) if row[11] else []
                ))
            
            conn.close()
            return reports
            
        except Exception as e:
            logger.error(f"Failed to get error reports: {e}")
            return []
    
    def get_error_analytics(self, days: int = 7) -> Dict[str, Any]:
        """Get error analytics for specified period"""
        try:
            cutoff = datetime.now() - timedelta(days=days)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total errors
            cursor.execute(
                "SELECT COUNT(*) FROM error_reports WHERE timestamp > ?", 
                (cutoff,)
            )
            total_errors = cursor.fetchone()[0]
            
            # Errors by severity
            cursor.execute('''
                SELECT severity, COUNT(*) 
                FROM error_reports 
                WHERE timestamp > ? 
                GROUP BY severity
            ''', (cutoff,))
            errors_by_severity = dict(cursor.fetchall())
            
            # Top error types
            cursor.execute('''
                SELECT error_type, COUNT(*) 
                FROM error_reports 
                WHERE timestamp > ? 
                GROUP BY error_type 
                ORDER BY COUNT(*) DESC 
                LIMIT 10
            ''', (cutoff,))
            top_error_types = dict(cursor.fetchall())
            
            # Error trend (daily)
            cursor.execute('''
                SELECT DATE(timestamp) as date, COUNT(*) 
                FROM error_reports 
                WHERE timestamp > ? 
                GROUP BY DATE(timestamp) 
                ORDER BY date
            ''', (cutoff,))
            error_trend = dict(cursor.fetchall())
            
            conn.close()
            
            return {
                'total_errors': total_errors,
                'errors_by_severity': errors_by_severity,
                'top_error_types': top_error_types,
                'error_trend': error_trend,
                'error_rate': total_errors / max(days, 1)
            }
            
        except Exception as e:
            logger.error(f"Failed to get error analytics: {e}")
            return {}

class PerformanceMonitor:
    """Performance monitoring and metrics collection"""
    
    def __init__(self, db_path: str = "debug.db"):
        self.db_path = db_path
        self.metrics_cache = deque(maxlen=10000)
        self.active_requests = {}
        self.system_monitor_active = False
        self._start_system_monitoring()
    
    def _start_system_monitoring(self):
        """Start background system monitoring"""
        if not self.system_monitor_active:
            self.system_monitor_active = True
            self._monitor_thread = threading.Thread(target=self._monitor_system, daemon=True)
            self._monitor_thread.start()
    
    def _monitor_system(self):
        """Background system monitoring"""
        while self.system_monitor_active:
            try:
                self._collect_system_metrics()
                time.sleep(60)  # Collect every minute
            except Exception as e:
                logger.error(f"System monitoring error: {e}")
    
    def _collect_system_metrics(self):
        """Collect system performance metrics"""
        try:
            # CPU and memory
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Network connections
            connections = len(psutil.net_connections())
            
            # Calculate error rate and response time
            error_rate = self._calculate_error_rate()
            avg_response_time = self._calculate_avg_response_time()
            
            # Determine system status
            status = self._determine_system_status(cpu_percent, memory.percent, error_rate)
            
            health = SystemHealth(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                disk_percent=disk.percent,
                active_connections=connections,
                error_rate=error_rate,
                avg_response_time=avg_response_time,
                status=status
            )
            
            self._store_system_health(health)
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
    
    def record_performance_metric(self, 
                                 metric_type: str,
                                 value: float,
                                 context: Optional[Dict[str, Any]] = None,
                                 endpoint: Optional[str] = None) -> str:
        """Record a performance metric"""
        try:
            metric_id = hashlib.md5(f"{metric_type}{time.time()}".encode()).hexdigest()
            
            metric = PerformanceMetric(
                id=metric_id,
                timestamp=datetime.now(),
                metric_type=metric_type,
                value=value,
                context=context or {},
                endpoint=endpoint
            )
            
            # Store in database
            self._store_performance_metric(metric)
            
            # Cache for quick access
            self.metrics_cache.append(metric)
            
            return metric_id
            
        except Exception as e:
            logger.error(f"Failed to record performance metric: {e}")
            return ""
    
    def _store_performance_metric(self, metric: PerformanceMetric):
        """Store performance metric in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO performance_metrics 
                (id, timestamp, metric_type, value, context, endpoint)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                metric.id,
                metric.timestamp,
                metric.metric_type,
                metric.value,
                json.dumps(metric.context),
                metric.endpoint
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to store performance metric: {e}")
    
    def _store_system_health(self, health: SystemHealth):
        """Store system health data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO system_health 
                (timestamp, cpu_percent, memory_percent, disk_percent, 
                 active_connections, error_rate, avg_response_time, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                health.timestamp,
                health.cpu_percent,
                health.memory_percent,
                health.disk_percent,
                health.active_connections,
                health.error_rate,
                health.avg_response_time,
                health.status
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to store system health: {e}")
    
    def _calculate_error_rate(self) -> float:
        """Calculate current error rate"""
        # Simple implementation - can be enhanced
        return 0.0
    
    def _calculate_avg_response_time(self) -> float:
        """Calculate average response time"""
        # Simple implementation - can be enhanced
        return 100.0
    
    def _determine_system_status(self, cpu: float, memory: float, error_rate: float) -> str:
        """Determine system health status"""
        if cpu > 90 or memory > 90 or error_rate > 10:
            return "critical"
        elif cpu > 70 or memory > 70 or error_rate > 5:
            return "warning"
        else:
            return "healthy"
    
    def get_performance_analytics(self, days: int = 7) -> Dict[str, Any]:
        """Get performance analytics"""
        try:
            cutoff = datetime.now() - timedelta(days=days)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Average metrics by type
            cursor.execute('''
                SELECT metric_type, AVG(value), COUNT(*) 
                FROM performance_metrics 
                WHERE timestamp > ? 
                GROUP BY metric_type
            ''', (cutoff,))
            avg_metrics = {row[0]: {'avg': row[1], 'count': row[2]} for row in cursor.fetchall()}
            
            # System health trend
            cursor.execute('''
                SELECT timestamp, cpu_percent, memory_percent, status 
                FROM system_health 
                WHERE timestamp > ? 
                ORDER BY timestamp
            ''', (cutoff,))
            health_trend = cursor.fetchall()
            
            conn.close()
            
            return {
                'avg_metrics': avg_metrics,
                'health_trend': health_trend,
                'monitoring_period_days': days
            }
            
        except Exception as e:
            logger.error(f"Failed to get performance analytics: {e}")
            return {}

class IntelligentDebugManager:
    """Main debug and monitoring management class"""
    
    def __init__(self, db_path: str = "debug.db"):
        self.db_path = db_path
        self.error_tracker = ErrorTracker(db_path)
        self.performance_monitor = PerformanceMonitor(db_path)
        self.debug_session_active = False
    
    def start_debug_session(self, session_id: str):
        """Start a debug session"""
        self.debug_session_active = True
        self.current_session_id = session_id
        logger.info(f"Debug session started: {session_id}")
    
    def stop_debug_session(self):
        """Stop debug session"""
        self.debug_session_active = False
        logger.info("Debug session stopped")
    
    def generate_debug_report(self, include_performance: bool = True) -> Dict[str, Any]:
        """Generate comprehensive debug report"""
        try:
            report = {
                'timestamp': datetime.now().isoformat(),
                'system_info': self._get_system_info(),
                'error_summary': self.error_tracker.get_error_analytics(),
                'recent_errors': [asdict(error) for error in self.error_tracker.get_error_reports(limit=50)],
            }
            
            if include_performance:
                report['performance_summary'] = self.performance_monitor.get_performance_analytics()
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate debug report: {e}")
            return {}
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        try:
            return {
                'platform': os.name,
                'python_version': os.sys.version,
                'cpu_count': psutil.cpu_count(),
                'memory_total': psutil.virtual_memory().total,
                'disk_total': psutil.disk_usage('/').total,
                'uptime': time.time() - psutil.boot_time()
            }
        except Exception as e:
            logger.error(f"Failed to get system info: {e}")
            return {}

def create_debug_manager(db_path: str = "debug.db") -> IntelligentDebugManager:
    """Factory function to create debug manager"""
    return IntelligentDebugManager(db_path)