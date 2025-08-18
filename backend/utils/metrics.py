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
APP_INFO.info({\n    'name': 'bailian-backend',\n    'version': '0.1.0',\n    'description': 'Alibaba Cloud Bailian API Integration Platform'\n})

# HTTP metrics
HTTP_REQUESTS_TOTAL = Counter(\n    'http_requests_total',\n    'Total number of HTTP requests',\n    ['method', 'endpoint', 'status_code'],\n    registry=REGISTRY\n)

HTTP_REQUEST_DURATION = Histogram(\n    'http_request_duration_seconds',\n    'HTTP request duration in seconds',\n    ['method', 'endpoint'],\n    registry=REGISTRY\n)

HTTP_REQUESTS_IN_PROGRESS = Gauge(\n    'http_requests_in_progress',\n    'Number of HTTP requests currently being processed',\n    registry=REGISTRY\n)

# Database metrics
DATABASE_CONNECTIONS = Gauge(\n    'database_connections_active',\n    'Number of active database connections',\n    registry=REGISTRY\n)

DATABASE_QUERIES_TOTAL = Counter(\n    'database_queries_total',\n    'Total number of database queries',\n    ['operation'],\n    registry=REGISTRY\n)

DATABASE_QUERY_DURATION = Histogram(\n    'database_query_duration_seconds',\n    'Database query duration in seconds',\n    ['operation'],\n    registry=REGISTRY\n)

# Redis metrics\nREDIS_CONNECTIONS = Gauge(\n    'redis_connections_active',\n    'Number of active Redis connections',\n    registry=REGISTRY\n)

REDIS_OPERATIONS_TOTAL = Counter(\n    'redis_operations_total',\n    'Total number of Redis operations',\n    ['operation'],\n    registry=REGISTRY\n)

REDIS_OPERATION_DURATION = Histogram(\n    'redis_operation_duration_seconds',\n    'Redis operation duration in seconds',\n    ['operation'],\n    registry=REGISTRY\n)

# AI Service metrics\nAI_REQUESTS_TOTAL = Counter(\n    'ai_requests_total',\n    'Total number of AI service requests',\n    ['model', 'status'],\n    registry=REGISTRY\n)

AI_REQUEST_DURATION = Histogram(\n    'ai_request_duration_seconds',\n    'AI service request duration in seconds',\n    ['model'],\n    registry=REGISTRY\n)

AI_TOKEN_USAGE = Counter(\n    'ai_token_usage_total',\n    'Total number of tokens used',\n    ['model', 'type'],  # type: input, output\n    registry=REGISTRY\n)

# Authentication metrics\nAUTH_REQUESTS_TOTAL = Counter(\n    'auth_requests_total',\n    'Total number of authentication requests',\n    ['operation', 'status'],  # operation: login, register, refresh\n    registry=REGISTRY\n)

AUTH_ACTIVE_SESSIONS = Gauge(\n    'auth_active_sessions',\n    'Number of active user sessions',\n    registry=REGISTRY\n)

# Rate limiting metrics\nRATE_LIMIT_HITS = Counter(\n    'rate_limit_hits_total',\n    'Total number of rate limit hits',\n    ['user_type', 'endpoint'],\n    registry=REGISTRY\n)

RATE_LIMIT_CURRENT = Gauge(\n    'rate_limit_current_requests',\n    'Current number of requests in rate limit window',\n    ['user_id', 'endpoint'],\n    registry=REGISTRY\n)

# System health metrics\nHEALTH_CHECK_STATUS = Gauge(\n    'health_check_status',\n    'Health check status (1 = healthy, 0 = unhealthy)',\n    ['check_type'],  # database, redis, external_api\n    registry=REGISTRY\n)

class MetricsCollector:\n    \"\"\"Centralized metrics collection utility\"\"\"\n    \n    @staticmethod\n    def record_http_request(method: str, endpoint: str, status_code: int, duration: float):\n        \"\"\"Record HTTP request metrics\"\"\"\n        HTTP_REQUESTS_TOTAL.labels(\n            method=method,\n            endpoint=endpoint,\n            status_code=str(status_code)\n        ).inc()\n        \n        HTTP_REQUEST_DURATION.labels(\n            method=method,\n            endpoint=endpoint\n        ).observe(duration)\n    \n    @staticmethod\n    def start_http_request():\n        \"\"\"Increment in-progress HTTP requests\"\"\"\n        HTTP_REQUESTS_IN_PROGRESS.inc()\n    \n    @staticmethod\n    def end_http_request():\n        \"\"\"Decrement in-progress HTTP requests\"\"\"\n        HTTP_REQUESTS_IN_PROGRESS.dec()\n    \n    @staticmethod\n    def record_database_query(operation: str, duration: float):\n        \"\"\"Record database query metrics\"\"\"\n        DATABASE_QUERIES_TOTAL.labels(operation=operation).inc()\n        DATABASE_QUERY_DURATION.labels(operation=operation).observe(duration)\n    \n    @staticmethod\n    def set_database_connections(count: int):\n        \"\"\"Set current database connection count\"\"\"\n        DATABASE_CONNECTIONS.set(count)\n    \n    @staticmethod\n    def record_redis_operation(operation: str, duration: float):\n        \"\"\"Record Redis operation metrics\"\"\"\n        REDIS_OPERATIONS_TOTAL.labels(operation=operation).inc()\n        REDIS_OPERATION_DURATION.labels(operation=operation).observe(duration)\n    \n    @staticmethod\n    def set_redis_connections(count: int):\n        \"\"\"Set current Redis connection count\"\"\"\n        REDIS_CONNECTIONS.set(count)\n    \n    @staticmethod\n    def record_ai_request(model: str, status: str, duration: float, \n                         input_tokens: int = 0, output_tokens: int = 0):\n        \"\"\"Record AI service request metrics\"\"\"\n        AI_REQUESTS_TOTAL.labels(model=model, status=status).inc()\n        AI_REQUEST_DURATION.labels(model=model).observe(duration)\n        \n        if input_tokens > 0:\n            AI_TOKEN_USAGE.labels(model=model, type='input').inc(input_tokens)\n        if output_tokens > 0:\n            AI_TOKEN_USAGE.labels(model=model, type='output').inc(output_tokens)\n    \n    @staticmethod\n    def record_auth_request(operation: str, status: str):\n        \"\"\"Record authentication request metrics\"\"\"\n        AUTH_REQUESTS_TOTAL.labels(operation=operation, status=status).inc()\n    \n    @staticmethod\n    def set_active_sessions(count: int):\n        \"\"\"Set current active session count\"\"\"\n        AUTH_ACTIVE_SESSIONS.set(count)\n    \n    @staticmethod\n    def record_rate_limit_hit(user_type: str, endpoint: str):\n        \"\"\"Record rate limit hit\"\"\"\n        RATE_LIMIT_HITS.labels(user_type=user_type, endpoint=endpoint).inc()\n    \n    @staticmethod\n    def set_rate_limit_current(user_id: str, endpoint: str, count: int):\n        \"\"\"Set current rate limit count\"\"\"\n        RATE_LIMIT_CURRENT.labels(user_id=user_id, endpoint=endpoint).set(count)\n    \n    @staticmethod\n    def set_health_status(check_type: str, is_healthy: bool):\n        \"\"\"Set health check status\"\"\"\n        HEALTH_CHECK_STATUS.labels(check_type=check_type).set(1 if is_healthy else 0)\n\ndef get_metrics() -> Response:\n    \"\"\"Get Prometheus metrics endpoint response\"\"\"\n    data = generate_latest(REGISTRY)\n    return Response(content=data, media_type=CONTENT_TYPE_LATEST)\n\n# Global metrics collector instance\nmetrics = MetricsCollector()