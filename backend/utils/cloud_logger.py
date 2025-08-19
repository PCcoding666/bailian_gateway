"""
Enhanced Cloud Logging Utility for Alibaba Cloud Log Service Integration
Provides structured JSON logging with correlation IDs and cloud-native features
"""

import json
import logging
import sys
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from contextvars import ContextVar
from functools import wraps

# Context variable for correlation ID
correlation_id: ContextVar[str] = ContextVar('correlation_id', default='')

class CloudJSONFormatter(logging.Formatter):
    """Custom JSON formatter for cloud-native logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON"""
        
        # Get correlation ID from context
        corr_id = correlation_id.get('')
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": "bailian-backend",
            "version": "0.1.0",
            "correlation_id": corr_id,
            "thread": record.thread,
            "thread_name": record.threadName,
            "process": record.process,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "pathname": record.pathname
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info)
            }
        
        # Add extra fields if present
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        return json.dumps(log_entry, ensure_ascii=False)

class CloudLogger:
    """Enhanced logger for cloud environments"""
    
    def __init__(self, name: str = "bailian-backend"):
        self.logger = logging.getLogger(name)
        self._setup_logger()
    
    def _setup_logger(self):
        """Configure logger with JSON formatter"""
        if not self.logger.handlers:
            # Create console handler
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(CloudJSONFormatter())
            
            # Set log level from environment or default to INFO
            import os
            log_level = os.getenv("LOG_LEVEL", "INFO").upper()
            self.logger.setLevel(getattr(logging, log_level, logging.INFO))
            
            self.logger.addHandler(handler)
            self.logger.propagate = False
    
    def _log_with_context(self, level: int, message: str, extra_fields: Optional[Dict[str, Any]] = None):
        """Log message with additional context"""
        if extra_fields:
            self.logger.log(level, message, extra={'extra_fields': extra_fields})
        else:
            self.logger.log(level, message)
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self._log_with_context(logging.DEBUG, message, kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self._log_with_context(logging.INFO, message, kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self._log_with_context(logging.WARNING, message, kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message"""
        self._log_with_context(logging.ERROR, message, kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message"""
        self._log_with_context(logging.CRITICAL, message, kwargs)
    
    def api_call(self, method: str, endpoint: str, status_code: int, 
                duration_ms: float, user_id: Optional[int] = None, **kwargs):
        """Log API call with structured data"""
        extra_fields = {
            "event_type": "api_call",
            "http_method": method,
            "endpoint": endpoint,
            "status_code": status_code,
            "duration_ms": duration_ms,
            "user_id": user_id,
            **kwargs
        }
        self.info(f"{method} {endpoint} - {status_code} ({duration_ms:.2f}ms)", **extra_fields)
    
    def business_event(self, event_name: str, **kwargs):
        """Log business event with context"""
        extra_fields = {
            "event_type": "business_event",
            "event_name": event_name,
            **kwargs
        }
        self.info(f"Business event: {event_name}", **extra_fields)
    
    def security_event(self, event_type: str, severity: str, **kwargs):
        """Log security-related events"""
        extra_fields = {
            "event_type": "security_event",
            "security_event_type": event_type,
            "severity": severity,
            **kwargs
        }
        if severity.upper() in ['HIGH', 'CRITICAL']:
            self.error(f"Security event: {event_type}", **extra_fields)
        else:
            self.warning(f"Security event: {event_type}", **extra_fields)

def generate_correlation_id() -> str:
    """Generate a new correlation ID"""
    return str(uuid.uuid4())

def set_correlation_id(corr_id: str):
    """Set correlation ID in context"""
    correlation_id.set(corr_id)

def get_correlation_id() -> str:
    """Get current correlation ID"""
    return correlation_id.get('')

def log_execution_time(logger: CloudLogger):
    """Decorator to log function execution time"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = datetime.utcnow()
            try:
                result = func(*args, **kwargs)
                duration = (datetime.utcnow() - start_time).total_seconds() * 1000
                logger.debug(
                    f"Function {func.__name__} executed successfully",
                    function=func.__name__,
                    duration_ms=duration,
                    status="success"
                )
                return result
            except Exception as e:
                duration = (datetime.utcnow() - start_time).total_seconds() * 1000
                logger.error(
                    f"Function {func.__name__} failed with error: {str(e)}",
                    function=func.__name__,
                    duration_ms=duration,
                    status="error",
                    error_type=type(e).__name__,
                    error_message=str(e)
                )
                raise
        return wrapper
    return decorator

# Global logger instance
cloud_logger = CloudLogger()

def get_logger(name: str = "bailian-backend") -> CloudLogger:
    """Get a logger instance with the specified name"""
    return CloudLogger(name)