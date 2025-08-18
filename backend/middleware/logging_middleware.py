"""
Logging Middleware for Request Correlation and Cloud Observability
"""

import time
from datetime import datetime
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from utils.cloud_logger import cloud_logger, generate_correlation_id, set_correlation_id

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request logging and correlation ID management"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with logging and correlation ID"""
        
        # Generate or extract correlation ID
        correlation_id = self._get_or_generate_correlation_id(request)
        set_correlation_id(correlation_id)
        
        # Record request start time
        start_time = time.time()
        
        # Get request details
        method = request.method
        url = str(request.url)
        path = request.url.path
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "")
        
        # Log incoming request
        cloud_logger.info(
            f"Incoming request: {method} {path}",
            event_type="request_start",
            http_method=method,
            url=url,
            path=path,
            client_ip=client_ip,
            user_agent=user_agent,
            correlation_id=correlation_id
        )
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Log successful response
            cloud_logger.api_call(
                method=method,
                endpoint=path,
                status_code=response.status_code,
                duration_ms=duration_ms,
                client_ip=client_ip,
                correlation_id=correlation_id
            )
            
            # Add correlation ID to response headers
            response.headers["X-Correlation-ID"] = correlation_id
            
            return response
            
        except Exception as e:
            # Calculate duration for failed request
            duration_ms = (time.time() - start_time) * 1000
            
            # Log error
            cloud_logger.error(
                f"Request failed: {method} {path} - {str(e)}",
                event_type="request_error",
                http_method=method,
                path=path,
                duration_ms=duration_ms,
                error_type=type(e).__name__,
                error_message=str(e),
                client_ip=client_ip,
                correlation_id=correlation_id
            )
            
            # Re-raise the exception
            raise
    
    def _get_or_generate_correlation_id(self, request: Request) -> str:
        """Get correlation ID from headers or generate new one"""
        # Try to get from headers (for distributed tracing)
        correlation_id = request.headers.get("X-Correlation-ID")
        if not correlation_id:
            correlation_id = request.headers.get("X-Request-ID")
        if not correlation_id:
            correlation_id = generate_correlation_id()
        
        return correlation_id
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address considering proxies"""
        # Check for forwarded headers (common in cloud environments)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct client IP
        if request.client:
            return request.client.host
        
        return "unknown"