"""
FlashFlow Cron Services
=====================

Comprehensive cron job scheduling and management services for FlashFlow applications.
Provides scheduled task execution, monitoring, and management.
"""

import os
import json
import time
import logging
import threading
import schedule
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import sqlite3
import secrets

logger = logging.getLogger(__name__)

@dataclass
class CronJob:
    """Represents a scheduled cron job"""
    id: str
    name: str
    description: str
    schedule: str  # cron expression or human-readable schedule
    enabled: bool
    last_run: Optional[datetime]
    next_run: Optional[datetime]
    success_count: int = 0
    failure_count: int = 0
    last_error: Optional[str] = None
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

@dataclass
class JobExecutionLog:
    """Represents a job execution log entry"""
    id: str
    job_id: str
    started_at: datetime
    finished_at: Optional[datetime]
    status: str  # success, failed, running
    output: Optional[str]
    error: Optional[str]

class CronJobManager:
    """Main cron job manager for FlashFlow applications"""
    
    def __init__(self, db_path: str = "cron.db"):
        self.db_path = db_path
        self.jobs: Dict[str, CronJob] = {}
        self.job_functions: Dict[str, Callable] = {}
        self.running = False
        self.scheduler_thread = None
        self.setup_database()
        self.load_jobs()
    
    def setup_database(self):
        """Initialize cron database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Cron jobs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cron_jobs (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    description TEXT,
                    schedule TEXT,
                    enabled BOOLEAN,
                    last_run TIMESTAMP,
                    next_run TIMESTAMP,
                    success_count INTEGER DEFAULT 0,
                    failure_count INTEGER DEFAULT 0,
                    last_error TEXT,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP
                )
            ''')
            
            # Job execution logs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS job_execution_logs (
                    id TEXT PRIMARY KEY,
                    job_id TEXT,
                    started_at TIMESTAMP,
                    finished_at TIMESTAMP,
                    status TEXT,
                    output TEXT,
                    error TEXT,
                    FOREIGN KEY (job_id) REFERENCES cron_jobs (id)
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Cron database initialized")
            
        except Exception as e:
            logger.error(f"Failed to setup cron database: {e}")
            raise
    
    def load_jobs(self):
        """Load jobs from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, name, description, schedule, enabled, last_run, next_run, 
                       success_count, failure_count, last_error, created_at, updated_at
                FROM cron_jobs
            ''')
            rows = cursor.fetchall()
            
            conn.close()
            
            for row in rows:
                job = CronJob(
                    id=row[0],
                    name=row[1],
                    description=row[2],
                    schedule=row[3],
                    enabled=row[4],
                    last_run=datetime.fromisoformat(row[5]) if row[5] else None,
                    next_run=datetime.fromisoformat(row[6]) if row[6] else None,
                    success_count=row[7],
                    failure_count=row[8],
                    last_error=row[9],
                    created_at=datetime.fromisoformat(row[10]) if row[10] else None,
                    updated_at=datetime.fromisoformat(row[11]) if row[11] else None
                )
                self.jobs[job.id] = job
            
            logger.info(f"Loaded {len(self.jobs)} cron jobs from database")
            
        except Exception as e:
            logger.error(f"Error loading jobs: {e}")
    
    def add_job(self, name: str, schedule: str, func: Callable, description: str = "", enabled: bool = True) -> str:
        """Add a new cron job"""
        try:
            job_id = secrets.token_urlsafe(16)
            
            job = CronJob(
                id=job_id,
                name=name,
                description=description,
                schedule=schedule,
                enabled=enabled,
                last_run=None,
                next_run=None
            )
            
            # Store job function
            self.job_functions[job_id] = func
            
            # Save to database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO cron_jobs 
                (id, name, description, schedule, enabled, last_run, next_run, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                job.id,
                job.name,
                job.description,
                job.schedule,
                job.enabled,
                job.last_run,
                job.next_run,
                job.created_at,
                job.updated_at
            ))
            
            conn.commit()
            conn.close()
            
            # Add to memory
            self.jobs[job_id] = job
            
            logger.info(f"Added cron job: {name} with schedule: {schedule}")
            return job_id
            
        except Exception as e:
            logger.error(f"Error adding job: {e}")
            raise
    
    def remove_job(self, job_id: str) -> bool:
        """Remove a cron job"""
        try:
            if job_id not in self.jobs:
                return False
            
            # Remove from schedule
            if self.running:
                schedule.clear(job_id)
            
            # Remove from database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM job_execution_logs WHERE job_id = ?', (job_id,))
            cursor.execute('DELETE FROM cron_jobs WHERE id = ?', (job_id,))
            
            conn.commit()
            conn.close()
            
            # Remove from memory
            if job_id in self.jobs:
                del self.jobs[job_id]
            if job_id in self.job_functions:
                del self.job_functions[job_id]
            
            logger.info(f"Removed cron job: {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error removing job: {e}")
            return False
    
    def update_job(self, job_id: str, **kwargs) -> bool:
        """Update a cron job"""
        try:
            if job_id not in self.jobs:
                return False
            
            job = self.jobs[job_id]
            
            # Update fields
            if 'name' in kwargs:
                job.name = kwargs['name']
            if 'description' in kwargs:
                job.description = kwargs['description']
            if 'schedule' in kwargs:
                job.schedule = kwargs['schedule']
            if 'enabled' in kwargs:
                job.enabled = kwargs['enabled']
            
            job.updated_at = datetime.now()
            
            # Update in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE cron_jobs 
                SET name = ?, description = ?, schedule = ?, enabled = ?, updated_at = ?
                WHERE id = ?
            ''', (
                job.name,
                job.description,
                job.schedule,
                job.enabled,
                job.updated_at,
                job.id
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Updated cron job: {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating job: {e}")
            return False
    
    def get_jobs(self) -> List[CronJob]:
        """Get all cron jobs"""
        return list(self.jobs.values())
    
    def get_job(self, job_id: str) -> Optional[CronJob]:
        """Get a specific cron job"""
        return self.jobs.get(job_id)
    
    def enable_job(self, job_id: str) -> bool:
        """Enable a cron job"""
        return self.update_job(job_id, enabled=True)
    
    def disable_job(self, job_id: str) -> bool:
        """Disable a cron job"""
        return self.update_job(job_id, enabled=False)
    
    def start_scheduler(self):
        """Start the cron job scheduler"""
        if self.running:
            logger.warning("Scheduler is already running")
            return
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        
        # Schedule all enabled jobs
        for job in self.jobs.values():
            if job.enabled:
                self._schedule_job(job)
        
        logger.info("Cron job scheduler started")
    
    def stop_scheduler(self):
        """Stop the cron job scheduler"""
        if not self.running:
            logger.warning("Scheduler is not running")
            return
        
        self.running = False
        schedule.clear()
        
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        
        logger.info("Cron job scheduler stopped")
    
    def _scheduler_loop(self):
        """Main scheduler loop"""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                time.sleep(5)  # Wait before retrying
    
    def _schedule_job(self, job: CronJob):
        """Schedule a job using the schedule library"""
        if not job.enabled:
            return
        
        try:
            # Parse schedule and create job
            # This is a simplified implementation - in a real system, you'd parse cron expressions
            if job.schedule == "every_minute":
                schedule.every().minute.do(self._execute_job, job.id).tag(job.id)
            elif job.schedule == "every_hour":
                schedule.every().hour.do(self._execute_job, job.id).tag(job.id)
            elif job.schedule == "every_day":
                schedule.every().day.do(self._execute_job, job.id).tag(job.id)
            elif job.schedule == "every_week":
                schedule.every().week.do(self._execute_job, job.id).tag(job.id)
            elif job.schedule.startswith("every_") and job.schedule.endswith("_minutes"):
                minutes = int(job.schedule.split("_")[1])
                schedule.every(minutes).minutes.do(self._execute_job, job.id).tag(job.id)
            elif job.schedule.startswith("every_") and job.schedule.endswith("_hours"):
                hours = int(job.schedule.split("_")[1])
                schedule.every(hours).hours.do(self._execute_job, job.id).tag(job.id)
            else:
                # Default to every hour if schedule not recognized
                schedule.every().hour.do(self._execute_job, job.id).tag(job.id)
            
            logger.info(f"Scheduled job: {job.name} with schedule: {job.schedule}")
            
        except Exception as e:
            logger.error(f"Error scheduling job {job.name}: {e}")
    
    def _execute_job(self, job_id: str):
        """Execute a scheduled job"""
        if job_id not in self.jobs or job_id not in self.job_functions:
            logger.warning(f"Job {job_id} not found")
            return
        
        job = self.jobs[job_id]
        if not job.enabled:
            return
        
        logger.info(f"Executing job: {job.name}")
        
        # Log execution start
        log_id = secrets.token_urlsafe(16)
        execution_log = JobExecutionLog(
            id=log_id,
            job_id=job_id,
            started_at=datetime.now(),
            finished_at=None,
            status="running",
            output=None,
            error=None
        )
        
        self._log_execution(execution_log)
        
        try:
            # Execute job function
            func = self.job_functions[job_id]
            output = func()
            
            # Update job stats
            job.success_count += 1
            job.last_run = datetime.now()
            job.last_error = None
            
            # Update execution log
            execution_log.finished_at = datetime.now()
            execution_log.status = "success"
            execution_log.output = str(output) if output is not None else None
            
            logger.info(f"Job {job.name} executed successfully")
            
        except Exception as e:
            # Update job stats
            job.failure_count += 1
            job.last_run = datetime.now()
            job.last_error = str(e)
            
            # Update execution log
            execution_log.finished_at = datetime.now()
            execution_log.status = "failed"
            execution_log.error = str(e)
            
            logger.error(f"Job {job.name} failed: {e}")
        
        finally:
            # Save job updates
            self._update_job_stats(job)
            # Update execution log
            self._log_execution(execution_log)
    
    def _log_execution(self, execution_log: JobExecutionLog):
        """Log job execution to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO job_execution_logs 
                (id, job_id, started_at, finished_at, status, output, error)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                execution_log.id,
                execution_log.job_id,
                execution_log.started_at,
                execution_log.finished_at,
                execution_log.status,
                execution_log.output,
                execution_log.error
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error logging execution: {e}")
    
    def _update_job_stats(self, job: CronJob):
        """Update job statistics in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE cron_jobs 
                SET last_run = ?, success_count = ?, failure_count = ?, last_error = ?, updated_at = ?
                WHERE id = ?
            ''', (
                job.last_run,
                job.success_count,
                job.failure_count,
                job.last_error,
                datetime.now(),
                job.id
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error updating job stats: {e}")
    
    def get_execution_logs(self, job_id: str = None, limit: int = 100) -> List[JobExecutionLog]:
        """Get execution logs"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if job_id:
                cursor.execute('''
                    SELECT id, job_id, started_at, finished_at, status, output, error
                    FROM job_execution_logs 
                    WHERE job_id = ?
                    ORDER BY started_at DESC 
                    LIMIT ?
                ''', (job_id, limit))
            else:
                cursor.execute('''
                    SELECT id, job_id, started_at, finished_at, status, output, error
                    FROM job_execution_logs 
                    ORDER BY started_at DESC 
                    LIMIT ?
                ''', (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            logs = []
            for row in rows:
                log = JobExecutionLog(
                    id=row[0],
                    job_id=row[1],
                    started_at=datetime.fromisoformat(row[2]),
                    finished_at=datetime.fromisoformat(row[3]) if row[3] else None,
                    status=row[4],
                    output=row[5],
                    error=row[6]
                )
                logs.append(log)
            
            return logs
            
        except Exception as e:
            logger.error(f"Error retrieving execution logs: {e}")
            return []
    
    def get_job_stats(self, job_id: str) -> Dict[str, Any]:
        """Get job statistics"""
        if job_id not in self.jobs:
            return {}
        
        job = self.jobs[job_id]
        logs = self.get_execution_logs(job_id, 10)
        
        return {
            "job": asdict(job),
            "recent_executions": [asdict(log) for log in logs],
            "success_rate": job.success_count / (job.success_count + job.failure_count) if (job.success_count + job.failure_count) > 0 else 0
        }