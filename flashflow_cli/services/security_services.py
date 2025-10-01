"""
FlashFlow Security Services
========================

Comprehensive security services for FlashFlow applications.
Provides API rate limiting, authentication, authorization, and security monitoring.
"""

import os
import json
import time
import logging
import hashlib
import secrets
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict, deque
import sqlite3
import re
import jwt
from functools import wraps

logger = logging.getLogger(__name__)

@dataclass
class SecurityEvent:
    """Represents a security event"""
    id: str
    event_type: str  # login_attempt, failed_login, rate_limit_exceeded, suspicious_activity
    user_id: Optional[str]
    ip_address: str
    user_agent: Optional[str]
    details: Dict[str, Any]
    timestamp: datetime
    severity: str = "info"  # info, warning, critical

@dataclass
class RateLimitRule:
    """Represents a rate limiting rule"""
    id: str
    name: str
    endpoint_pattern: str
    method: str  # GET, POST, PUT, DELETE, ALL
    limit: int  # Number of requests
    window_seconds: int  # Time window in seconds
    scope: str  # ip, user, global
    enabled: bool = True
    description: str = ""

@dataclass
class RateLimitEntry:
    """Represents a rate limit entry for tracking"""
    key: str
    count: int
    reset_time: datetime

@dataclass
class SecurityConfig:
    """Security configuration"""
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    rate_limit_enabled: bool = True
    max_login_attempts: int = 5
    login_lockout_minutes: int = 30
    password_min_length: int = 8
    password_require_uppercase: bool = True
    password_require_lowercase: bool = True
    password_require_numbers: bool = True
    password_require_special: bool = True
    enable_cors: bool = True
    cors_origins: List[str] = None
    enable_csrf_protection: bool = True
    enable_hsts: bool = True
    hsts_max_age: int = 31536000  # 1 year
    enable_xss_protection: bool = True
    enable_content_type_sniffing_protection: bool = True
    
    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = ["*"]

class SecurityManager:
    """Main security manager for FlashFlow applications"""
    
    def __init__(self, db_path: str = "security.db", config: Optional[SecurityConfig] = None):
        self.db_path = db_path
        self.config = config or SecurityConfig(jwt_secret=secrets.token_urlsafe(32))
        self.setup_database()
        self.rate_limit_cache = {}  # key -> RateLimitEntry
        self.failed_login_attempts = defaultdict(int)  # ip/user -> count
        self.lockout_until = {}  # ip/user -> datetime
        self.security_events = deque(maxlen=1000)
    
    def setup_database(self):
        """Initialize security database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Security events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS security_events (
                    id TEXT PRIMARY KEY,
                    event_type TEXT,
                    user_id TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    details TEXT,
                    timestamp TIMESTAMP,
                    severity TEXT
                )
            ''')
            
            # Rate limit rules table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS rate_limit_rules (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    endpoint_pattern TEXT,
                    method TEXT,
                    limit INTEGER,
                    window_seconds INTEGER,
                    scope TEXT,
                    enabled BOOLEAN,
                    description TEXT
                )
            ''')
            
            # User security data table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_security (
                    user_id TEXT PRIMARY KEY,
                    password_hash TEXT,
                    salt TEXT,
                    failed_login_attempts INTEGER DEFAULT 0,
                    last_failed_login TIMESTAMP,
                    locked_until TIMESTAMP,
                    mfa_enabled BOOLEAN DEFAULT FALSE,
                    mfa_secret TEXT,
                    last_password_change TIMESTAMP,
                    password_history TEXT
                )
            ''')
            
            # API keys table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS api_keys (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    key_hash TEXT,
                    name TEXT,
                    permissions TEXT,
                    created_at TIMESTAMP,
                    expires_at TIMESTAMP,
                    last_used TIMESTAMP,
                    revoked BOOLEAN DEFAULT FALSE
                )
            ''')
            
            # Default rate limit rules
            default_rules = [
                RateLimitRule(
                    id="default_api",
                    name="Default API Rate Limit",
                    endpoint_pattern="*",
                    method="ALL",
                    limit=1000,
                    window_seconds=3600,  # 1 hour
                    scope="ip",
                    description="Default rate limit for all API endpoints"
                ),
                RateLimitRule(
                    name="Login Rate Limit",
                    endpoint_pattern="/api/auth/login",
                    method="POST",
                    limit=5,
                    window_seconds=300,  # 5 minutes
                    scope="ip",
                    description="Rate limit for login attempts"
                )
            ]
            
            conn.commit()
            conn.close()
            logger.info("Security database initialized")
            
        except Exception as e:
            logger.error(f"Failed to setup security database: {e}")
            raise
    
    def check_rate_limit(self, endpoint: str, method: str, ip_address: str, user_id: Optional[str] = None) -> bool:
        """Check if request is within rate limits"""
        if not self.config.rate_limit_enabled:
            return True
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get applicable rate limit rules
            cursor.execute('''
                SELECT id, name, endpoint_pattern, method, limit, window_seconds, scope
                FROM rate_limit_rules 
                WHERE enabled = 1
            ''')
            rules = cursor.fetchall()
            
            conn.close()
            
            # Check each rule
            for rule in rules:
                rule_id, name, pattern, rule_method, limit, window_seconds, scope = rule
                
                # Check if rule applies to this request
                if rule_method != "ALL" and rule_method != method:
                    continue
                
                # Check endpoint pattern match
                if not self._matches_pattern(endpoint, pattern):
                    continue
                
                # Determine rate limit key based on scope
                if scope == "ip":
                    key = f"{rule_id}:{ip_address}"
                elif scope == "user" and user_id:
                    key = f"{rule_id}:{user_id}"
                elif scope == "global":
                    key = f"{rule_id}:global"
                else:
                    continue
                
                # Check rate limit
                if not self._check_rate_limit_key(key, limit, window_seconds):
                    # Log rate limit exceeded event
                    self.log_security_event(
                        event_type="rate_limit_exceeded",
                        ip_address=ip_address,
                        user_id=user_id,
                        details={
                            "rule_name": name,
                            "endpoint": endpoint,
                            "method": method,
                            "limit": limit,
                            "window_seconds": window_seconds
                        },
                        severity="warning"
                    )
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            return True  # Allow request on error
    
    def _matches_pattern(self, endpoint: str, pattern: str) -> bool:
        """Check if endpoint matches pattern"""
        if pattern == "*":
            return True
        
        # Simple pattern matching (could be enhanced with regex)
        if pattern.endswith("*"):
            return endpoint.startswith(pattern[:-1])
        return endpoint == pattern
    
    def _check_rate_limit_key(self, key: str, limit: int, window_seconds: int) -> bool:
        """Check rate limit for a specific key"""
        now = datetime.now()
        
        # Check cache first
        if key in self.rate_limit_cache:
            entry = self.rate_limit_cache[key]
            if entry.reset_time > now:
                if entry.count >= limit:
                    return False
                else:
                    entry.count += 1
                    return True
            else:
                # Reset expired entry
                del self.rate_limit_cache[key]
        
        # Check database
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT count, reset_time FROM rate_limit_entries 
                WHERE key = ? AND reset_time > ?
            ''', (key, now))
            result = cursor.fetchone()
            
            if result:
                count, reset_time_str = result
                reset_time = datetime.fromisoformat(reset_time_str)
                
                if count >= limit:
                    conn.close()
                    return False
                else:
                    # Update count
                    cursor.execute('''
                        UPDATE rate_limit_entries 
                        SET count = count + 1 
                        WHERE key = ?
                    ''', (key,))
                    conn.commit()
                    conn.close()
                    return True
            else:
                # Create new entry
                reset_time = now + timedelta(seconds=window_seconds)
                cursor.execute('''
                    INSERT OR REPLACE INTO rate_limit_entries 
                    (key, count, reset_time) 
                    VALUES (?, 1, ?)
                ''', (key, reset_time.isoformat()))
                conn.commit()
                conn.close()
                
                # Cache the entry
                self.rate_limit_cache[key] = RateLimitEntry(
                    key=key,
                    count=1,
                    reset_time=reset_time
                )
                return True
                
        except Exception as e:
            logger.error(f"Error checking rate limit key: {e}")
            return True
    
    def check_login_attempts(self, identifier: str) -> bool:
        """Check if login attempts are within limits"""
        now = datetime.now()
        
        # Check if account is locked
        if identifier in self.lockout_until:
            if self.lockout_until[identifier] > now:
                return False
            else:
                # Unlock account
                del self.lockout_until[identifier]
                self.failed_login_attempts[identifier] = 0
        
        # Check failed attempts
        if self.failed_login_attempts[identifier] >= self.config.max_login_attempts:
            # Lock account
            self.lockout_until[identifier] = now + timedelta(minutes=self.config.login_lockout_minutes)
            return False
        
        return True
    
    def record_failed_login(self, identifier: str):
        """Record a failed login attempt"""
        self.failed_login_attempts[identifier] += 1
        
        # Lock account if attempts exceeded
        if self.failed_login_attempts[identifier] >= self.config.max_login_attempts:
            self.lockout_until[identifier] = datetime.now() + timedelta(minutes=self.config.login_lockout_minutes)
    
    def reset_login_attempts(self, identifier: str):
        """Reset login attempts after successful login"""
        self.failed_login_attempts[identifier] = 0
        if identifier in self.lockout_until:
            del self.lockout_until[identifier]
    
    def hash_password(self, password: str) -> tuple[str, str]:
        """Hash a password with salt"""
        salt = secrets.token_urlsafe(32)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return password_hash.hex(), salt
    
    def verify_password(self, password: str, password_hash: str, salt: str) -> bool:
        """Verify a password against its hash"""
        hash_to_check = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return hash_to_check.hex() == password_hash
    
    def create_user_security(self, user_id: str, password: str) -> bool:
        """Create security record for a user"""
        try:
            password_hash, salt = self.hash_password(password)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO user_security 
                (user_id, password_hash, salt, failed_login_attempts, last_password_change)
                VALUES (?, ?, ?, 0, ?)
            ''', (user_id, password_hash, salt, datetime.now()))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error creating user security: {e}")
            return False
    
    def verify_user_password(self, user_id: str, password: str) -> bool:
        """Verify user password"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT password_hash, salt FROM user_security WHERE user_id = ?
            ''', (user_id,))
            result = cursor.fetchone()
            
            conn.close()
            
            if not result:
                return False
            
            password_hash, salt = result
            return self.verify_password(password, password_hash, salt)
        except Exception as e:
            logger.error(f"Error verifying user password: {e}")
            return False
    
    def generate_jwt_token(self, user_id: str, additional_claims: Dict[str, Any] = None) -> str:
        """Generate JWT token for user"""
        try:
            payload = {
                'user_id': user_id,
                'exp': datetime.now() + timedelta(hours=self.config.jwt_expiration_hours),
                'iat': datetime.now()
            }
            
            if additional_claims:
                payload.update(additional_claims)
            
            token = jwt.encode(payload, self.config.jwt_secret, algorithm=self.config.jwt_algorithm)
            return token
        except Exception as e:
            logger.error(f"Error generating JWT token: {e}")
            raise
    
    def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.config.jwt_secret, algorithms=[self.config.jwt_algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid JWT token: {e}")
            return None
    
    def log_security_event(self, event_type: str, ip_address: str, user_id: Optional[str] = None, 
                          user_agent: Optional[str] = None, details: Dict[str, Any] = None, 
                          severity: str = "info"):
        """Log a security event"""
        try:
            event = SecurityEvent(
                id=secrets.token_urlsafe(16),
                event_type=event_type,
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                details=details or {},
                timestamp=datetime.now(),
                severity=severity
            )
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO security_events 
                (id, event_type, user_id, ip_address, user_agent, details, timestamp, severity)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event.id,
                event.event_type,
                event.user_id,
                event.ip_address,
                event.user_agent,
                json.dumps(event.details),
                event.timestamp,
                event.severity
            ))
            
            conn.commit()
            conn.close()
            
            # Add to cache
            self.security_events.append(event)
            
            logger.info(f"Security event logged: {event_type} from {ip_address}")
        except Exception as e:
            logger.error(f"Error logging security event: {e}")
    
    def get_security_events(self, limit: int = 100) -> List[SecurityEvent]:
        """Get recent security events"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, event_type, user_id, ip_address, user_agent, details, timestamp, severity
                FROM security_events 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            rows = cursor.fetchall()
            
            conn.close()
            
            events = []
            for row in rows:
                event = SecurityEvent(
                    id=row[0],
                    event_type=row[1],
                    user_id=row[2],
                    ip_address=row[3],
                    user_agent=row[4],
                    details=json.loads(row[5]) if row[5] else {},
                    timestamp=datetime.fromisoformat(row[6]),
                    severity=row[7]
                )
                events.append(event)
            
            return events
        except Exception as e:
            logger.error(f"Error retrieving security events: {e}")
            return []
    
    def add_rate_limit_rule(self, rule: RateLimitRule) -> bool:
        """Add a new rate limit rule"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO rate_limit_rules 
                (id, name, endpoint_pattern, method, limit, window_seconds, scope, enabled, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                rule.id,
                rule.name,
                rule.endpoint_pattern,
                rule.method,
                rule.limit,
                rule.window_seconds,
                rule.scope,
                rule.enabled,
                rule.description
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error adding rate limit rule: {e}")
            return False
    
    def get_rate_limit_rules(self) -> List[RateLimitRule]:
        """Get all rate limit rules"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, name, endpoint_pattern, method, limit, window_seconds, scope, enabled, description
                FROM rate_limit_rules
            ''')
            rows = cursor.fetchall()
            
            conn.close()
            
            rules = []
            for row in rows:
                rule = RateLimitRule(
                    id=row[0],
                    name=row[1],
                    endpoint_pattern=row[2],
                    method=row[3],
                    limit=row[4],
                    window_seconds=row[5],
                    scope=row[6],
                    enabled=row[7],
                    description=row[8]
                )
                rules.append(rule)
            
            return rules
        except Exception as e:
            logger.error(f"Error retrieving rate limit rules: {e}")
            return []
    
    def validate_password_strength(self, password: str) -> tuple[bool, List[str]]:
        """Validate password strength according to security config"""
        errors = []
        
        if len(password) < self.config.password_min_length:
            errors.append(f"Password must be at least {self.config.password_min_length} characters long")
        
        if self.config.password_require_uppercase and not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if self.config.password_require_lowercase and not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if self.config.password_require_numbers and not re.search(r'[0-9]', password):
            errors.append("Password must contain at least one number")
        
        if self.config.password_require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")
        
        return len(errors) == 0, errors
    
    def is_account_locked(self, identifier: str) -> bool:
        """Check if account is locked"""
        if identifier in self.lockout_until:
            if self.lockout_until[identifier] > datetime.now():
                return True
            else:
                # Unlock expired lockout
                del self.lockout_until[identifier]
                self.failed_login_attempts[identifier] = 0
                return False
        return False