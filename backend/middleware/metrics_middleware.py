"""
Metrics Middleware for automatic Prometheus metrics collection
"""

import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from utils.metrics import metrics

class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware for automatic metrics collection"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with metrics collection"""
        
        # Start tracking request
        metrics.start_http_request()
        start_time = time.time()
        
        # Get request details
        method = request.method
        path = request.url.path
        
        # Normalize path for metrics (remove IDs and dynamic parts)
        normalized_path = self._normalize_path(path)
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Record metrics
            metrics.record_http_request(
                method=method,
                endpoint=normalized_path,
                status_code=response.status_code,
                duration=duration
            )
            
            return response
            
        except Exception as e:
            # Calculate duration for failed request
            duration = time.time() - start_time
            
            # Record metrics with 500 status code for exceptions
            metrics.record_http_request(
                method=method,
                endpoint=normalized_path,
                status_code=500,
                duration=duration
            )
            
            # Re-raise the exception
            raise
            
        finally:
            # Always decrement in-progress counter
            metrics.end_http_request()
    
    def _normalize_path(self, path: str) -> str:
        """Normalize path for metrics by removing dynamic parts"""
        # Remove common ID patterns
        import re
        
        # Replace UUIDs
        path = re.sub(r'/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '/{id}', path)
        
        # Replace numeric IDs
        path = re.sub(r'/\d+', '/{id}', path)
        
        # Replace other common patterns
        path = re.sub(r'/[0-9a-zA-Z]{20,}', '/{token}', path)
        
        return path