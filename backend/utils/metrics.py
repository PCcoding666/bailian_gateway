"""
Prometheus Metrics Integration for Alibaba Cloud CloudMonitor
Provides comprehensive application metrics collection and exposure
"""

import time
from typing import Dict, Any
from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest, CONTENT_TYPE_LATEST
from prometheus_client.core import CollectorRegistry
from starlette.responses import Response
from fastapi import Request

# Create custom registry for better control
REGISTRY = CollectorRegistry()

# Application metrics
APP_INFO = Info('app_info', 'Application information', registry=REGISTRY)
APP_INFO.info({
    'name': 'bailian-backend',
    'version': '0.1.0',
    'description': 'Alibaba Cloud Bailian API Integration Platform'
})

# HTTP metrics
HTTP_REQUESTS_TOTAL = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status_code'],
    registry=REGISTRY
)

HTTP_REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    registry=REGISTRY
)

HTTP_REQUESTS_IN_PROGRESS = Gauge(
    'http_requests_in_progress',
    'Number of HTTP requests currently being processed',
    registry=REGISTRY
)

# Database metrics
DATABASE_CONNECTIONS = Gauge(
    'database_connections_active',
    'Number of active database connections',
    registry=REGISTRY
)

DATABASE_QUERIES_TOTAL = Counter(
    'database_queries_total',
    'Total number of database queries',
    ['operation'],
    registry=REGISTRY
)

DATABASE_QUERY_DURATION = Histogram(
    'database_query_duration_seconds',
    'Database query duration in seconds',
    ['operation'],
    registry=REGISTRY
)

# Redis metrics
REDIS_CONNECTIONS = Gauge(
    'redis_connections_active',
    'Number of active Redis connections',
    registry=REGISTRY
)

REDIS_OPERATIONS_TOTAL = Counter(
    'redis_operations_total',
    'Total number of Redis operations',
    ['operation'],
    registry=REGISTRY
)

REDIS_OPERATION_DURATION = Histogram(
    'redis_operation_duration_seconds',
    'Redis operation duration in seconds',
    ['operation'],
    registry=REGISTRY
)

# AI Service metrics
AI_REQUESTS_TOTAL = Counter(
    'ai_requests_total',
    'Total number of AI service requests',
    ['model', 'status'],
    registry=REGISTRY
)

AI_REQUEST_DURATION = Histogram(
    'ai_request_duration_seconds',
    'AI service request duration in seconds',
    ['model'],
    registry=REGISTRY
)

AI_TOKEN_USAGE = Counter(
    'ai_token_usage_total',
    'Total number of tokens used',
    ['model', 'type'],
    registry=REGISTRY
)

# Authentication metrics
AUTH_REQUESTS_TOTAL = Counter(
    'auth_requests_total',
    'Total number of authentication requests',
    ['operation', 'status'],
    registry=REGISTRY
)

AUTH_ACTIVE_SESSIONS = Gauge(
    'auth_active_sessions',
    'Number of active user sessions',
    registry=REGISTRY
)

# Rate limiting metrics
RATE_LIMIT_HITS = Counter(
    'rate_limit_hits_total',
    'Total number of rate limit hits',
    ['user_type', 'endpoint'],
    registry=REGISTRY
)

RATE_LIMIT_CURRENT = Gauge(
    'rate_limit_current_requests',
    'Current number of requests in rate limit window',
    ['user_id', 'endpoint'],
    registry=REGISTRY
)

# System health metrics
HEALTH_CHECK_STATUS = Gauge(
    'health_check_status',
    'Health check status (1 = healthy, 0 = unhealthy)',
    ['check_type'],
    registry=REGISTRY
)

class MetricsCollector:
    """Centralized metrics collection utility"""
    
    @staticmethod
    def record_http_request(method: str, endpoint: str, status_code: int, duration: float):
        """Record HTTP request metrics"""
        HTTP_REQUESTS_TOTAL.labels(
            method=method,
            endpoint=endpoint,
            status_code=str(status_code)
        ).inc()
        
        HTTP_REQUEST_DURATION.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
    
    @staticmethod
    def start_http_request():
        """Increment in-progress HTTP requests"""
        HTTP_REQUESTS_IN_PROGRESS.inc()
    
    @staticmethod
    def end_http_request():
        """Decrement in-progress HTTP requests"""
        HTTP_REQUESTS_IN_PROGRESS.dec()
    
    @staticmethod
    def record_database_query(operation: str, duration: float):
        """Record database query metrics"""
        DATABASE_QUERIES_TOTAL.labels(operation=operation).inc()
        DATABASE_QUERY_DURATION.labels(operation=operation).observe(duration)
    
    @staticmethod
    def set_database_connections(count: int):
        """Set current database connection count"""
        DATABASE_CONNECTIONS.set(count)
    
    @staticmethod
    def record_redis_operation(operation: str, duration: float):
        """Record Redis operation metrics"""
        REDIS_OPERATIONS_TOTAL.labels(operation=operation).inc()
        REDIS_OPERATION_DURATION.labels(operation=operation).observe(duration)
    
    @staticmethod
    def set_redis_connections(count: int):
        """Set current Redis connection count"""
        REDIS_CONNECTIONS.set(count)
    
    @staticmethod
    def record_ai_request(model: str, status: str, duration: float, 
                         input_tokens: int = 0, output_tokens: int = 0):
        """Record AI service request metrics"""
        AI_REQUESTS_TOTAL.labels(model=model, status=status).inc()
        AI_REQUEST_DURATION.labels(model=model).observe(duration)
        
        if input_tokens > 0:
            AI_TOKEN_USAGE.labels(model=model, type='input').inc(input_tokens)
        if output_tokens > 0:
            AI_TOKEN_USAGE.labels(model=model, type='output').inc(output_tokens)
    
    @staticmethod
    def record_auth_request(operation: str, status: str):
        """Record authentication request metrics"""
        AUTH_REQUESTS_TOTAL.labels(operation=operation, status=status).inc()
    
    @staticmethod
    def set_active_sessions(count: int):
        """Set current active session count"""
        AUTH_ACTIVE_SESSIONS.set(count)
    
    @staticmethod
    def record_rate_limit_hit(user_type: str, endpoint: str):
        """Record rate limit hit"""
        RATE_LIMIT_HITS.labels(user_type=user_type, endpoint=endpoint).inc()
    
    @staticmethod
    def set_rate_limit_current(user_id: str, endpoint: str, count: int):
        """Set current rate limit count"""
        RATE_LIMIT_CURRENT.labels(user_id=user_id, endpoint=endpoint).set(count)
    
    @staticmethod
    def set_health_status(check_type: str, is_healthy: bool):
        """Set health check status"""
        HEALTH_CHECK_STATUS.labels(check_type=check_type).set(1 if is_healthy else 0)

def record_ai_request(model: str, status: str, duration: float):
    """Record AI service request metrics"""
    AI_REQUESTS_TOTAL.labels(model=model, status=status).inc()
    AI_REQUEST_DURATION.labels(model=model).observe(duration / 1000.0)

def record_token_usage(model: str, token_type: str, count: int):
    """Record token usage metrics"""
    AI_TOKEN_USAGE.labels(model=model, type=token_type).inc(count)

def record_security_event(event_type: str, status: str, details: dict):
    """Record security event metrics"""
    # This is a placeholder function for security metrics
    # In a real implementation, you might want to use a separate security metrics registry
    pass

def get_metrics() -> Response:
    """Get Prometheus metrics endpoint response"""
    data = generate_latest(REGISTRY)
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)

# Global metrics collector instance
metrics = MetricsCollector()