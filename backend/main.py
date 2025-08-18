from fastapi import FastAPI, Depends, HTTPException
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from redis.exceptions import RedisError
from starlette.exceptions import HTTPException as StarletteHTTPException
from config.database import engine, Base, get_db
from api import auth, conversations, bailian
from models import User, Conversation, Message, APICall
from middleware.logging_middleware import LoggingMiddleware
from middleware.metrics_middleware import MetricsMiddleware
from utils.cloud_logger import cloud_logger
from utils.metrics import get_metrics
from utils.error_handler import (
    ApplicationError,
    application_error_handler,
    http_exception_handler,
    starlette_http_exception_handler,
    validation_error_handler,
    sqlalchemy_error_handler,
    redis_error_handler,
    generic_exception_handler
)
from utils.security_middleware import SecurityMiddleware, SecurityHealthCheck
import os
import redis
from datetime import datetime
from typing import Dict, Any

# Create tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Alibaba Cloud Bailian API Integration Platform",
    description="A unified API interface for Alibaba Cloud Bailian platform services",
    version="0.1.0"
)

# Add middlewares (order matters - security first, then metrics, then logging)
app.add_middleware(SecurityMiddleware)
app.add_middleware(MetricsMiddleware)
app.add_middleware(LoggingMiddleware)

# Add exception handlers
app.add_exception_handler(ApplicationError, application_error_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(StarletteHTTPException, starlette_http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_error_handler)
app.add_exception_handler(RedisError, redis_error_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Include routers
app.include_router(auth.router)
app.include_router(conversations.router)
app.include_router(bailian.router)

# Metrics endpoint
@app.get("/metrics")
def metrics_endpoint():
    """Prometheus metrics endpoint"""
    return get_metrics()

@app.get("/health")
def health_check():
    """Basic health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/health/live")
def liveness_check():
    """Kubernetes liveness probe - checks if application is alive"""
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "bailian-backend",
        "version": "0.1.0"
    }

@app.get("/health/ready")
def readiness_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Kubernetes readiness probe - checks if application is ready to serve traffic"""
    health_status = {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }
    
    # Check database connectivity
    try:
        db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = "connected"
    except Exception as e:
        health_status["checks"]["database"] = f"error: {str(e)}"
        health_status["status"] = "not_ready"
    
    # Check Redis connectivity
    try:
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", "6379"))
        redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        redis_client.ping()
        health_status["checks"]["redis"] = "connected"
    except Exception as e:
        health_status["checks"]["redis"] = f"error: {str(e)}"
        health_status["status"] = "not_ready"
    
    # Check external API connectivity (DashScope)
    dashscope_api_key = os.getenv("QWEN_API_KEY")
    if dashscope_api_key:
        health_status["checks"]["dashscope_api"] = "configured"
    else:
        health_status["checks"]["dashscope_api"] = "not_configured"
        health_status["status"] = "not_ready"
    
    # Check security middleware status
    try:
        security_checker = SecurityHealthCheck()
        security_status = security_checker.check_security_status()
        health_status["checks"]["security_middleware"] = security_status.get("security_middleware", "unknown")
        health_status["checks"]["rate_limiting"] = security_status.get("rate_limiting", "unknown")
    except Exception as e:
        health_status["checks"]["security_middleware"] = f"error: {str(e)}"
    
    if health_status["status"] == "not_ready":
        raise HTTPException(status_code=503, detail=health_status)
    
    return health_status

@app.get("/health/security")
def security_health_check():
    """Security-specific health check endpoint"""
    security_checker = SecurityHealthCheck()
    return security_checker.check_security_status()

@app.get("/health/security/metrics")
def security_metrics():
    """Security metrics endpoint"""
    security_checker = SecurityHealthCheck()
    return security_checker.get_security_metrics()

@app.get("/")
def read_root():
    """Root endpoint with service information"""
    return {
        "message": "Welcome to the Alibaba Cloud Bailian API Integration Platform",
        "service": "bailian-backend",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
        "ready": "/health/ready",
        "alive": "/health/live"
    }

# Create initial admin user if it doesn't exist
@app.on_event("startup")
def create_initial_admin():
    """Create initial admin user on startup"""
    cloud_logger.info("Application startup - Creating initial admin user")
    db = next(get_db())
    admin_user = db.query(User).filter(User.username == "admin").first()
    if not admin_user:
        admin_user = User(
            username="admin",
            email="admin@example.com",
            nickname="Administrator"
        )
        admin_user.set_password("AdminPass123!")
        db.add(admin_user)
        db.commit()
        cloud_logger.info("Initial admin user created successfully")
    else:
        cloud_logger.info("Initial admin user already exists")