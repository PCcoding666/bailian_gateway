import logging
import os
from datetime import datetime
from typing import Optional
import json

class Logger:
    def __init__(self, name: str = "bailian_api"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Create file handler
        file_handler = logging.FileHandler(os.path.join(log_dir, "api.log"))
        file_handler.setLevel(logging.INFO)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers to logger
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def info(self, message: str, extra: Optional[dict] = None):
        """Log info message"""
        self.logger.info(message, extra=extra)
    
    def error(self, message: str, extra: Optional[dict] = None):
        """Log error message"""
        self.logger.error(message, extra=extra)
    
    def warning(self, message: str, extra: Optional[dict] = None):
        """Log warning message"""
        self.logger.warning(message, extra=extra)
    
    def log_api_call(self, user_id: int, endpoint: str, method: str, 
                    status_code: int, duration: float, client_ip: str = None,
                    user_agent: str = None, request_data: dict = None):
        """Log API call"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "api_call",
            "user_id": user_id,
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "duration_ms": duration,
            "client_ip": client_ip,
            "user_agent": user_agent,
            "request_data": request_data
        }
        
        self.info(f"API Call: {endpoint}", extra={"api_call": log_data})
    
    def log_security_event(self, event_type: str, user_id: Optional[int] = None,
                          details: dict = None, severity: str = "info"):
        """Log security event"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "security_event",
            "event_type": event_type,
            "user_id": user_id,
            "severity": severity,
            "details": details
        }
        
        if severity == "error":
            self.error(f"Security Event: {event_type}", extra={"security_event": log_data})
        elif severity == "warning":
            self.warning(f"Security Event: {event_type}", extra={"security_event": log_data})
        else:
            self.info(f"Security Event: {event_type}", extra={"security_event": log_data})

# Global logger instance
logger = Logger()