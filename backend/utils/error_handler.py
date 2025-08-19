"""
Centralized Error Handling for Cloud-Native Applications
Provides consistent error responses, logging, and monitoring integration
"""

import traceback
from typing import Dict, Any, Optional, Union
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from redis.exceptions import RedisError
from utils.cloud_logger import cloud_logger, get_correlation_id
from utils.metrics import metrics

class ApplicationError(Exception):
    """Base application error class"""
    
    def __init__(self, message: str, error_code: str = "APP_ERROR", 
                 status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)

class BusinessLogicError(ApplicationError):
    """Business logic validation error"""
    
    def __init__(self, message: str, error_code: str = "BUSINESS_ERROR", 
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code, 400, details)

class AuthenticationError(ApplicationError):
    """Authentication related error"""
    
    def __init__(self, message: str = "Authentication failed", 
                 error_code: str = "AUTH_ERROR", 
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code, 401, details)

class AuthorizationError(ApplicationError):
    """Authorization related error"""
    
    def __init__(self, message: str = "Access denied", 
                 error_code: str = "AUTHZ_ERROR", 
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code, 403, details)

class ResourceNotFoundError(ApplicationError):
    """Resource not found error"""
    
    def __init__(self, message: str = "Resource not found", 
                 resource_type: str = "resource", resource_id: str = "", 
                 error_code: str = "NOT_FOUND"):
        details = {"resource_type": resource_type, "resource_id": resource_id}
        super().__init__(message, error_code, 404, details)

class ExternalServiceError(ApplicationError):
    """External service integration error"""
    
    def __init__(self, message: str, service_name: str, 
                 error_code: str = "EXTERNAL_SERVICE_ERROR", 
                 status_code: int = 502, 
                 details: Optional[Dict[str, Any]] = None):
        details = details or {}
        details["service_name"] = service_name
        super().__init__(message, error_code, status_code, details)

class RateLimitError(ApplicationError):
    """Rate limit exceeded error"""
    
    def __init__(self, message: str = "Rate limit exceeded", 
                 retry_after: Optional[int] = None,
                 error_code: str = "RATE_LIMIT_EXCEEDED"):
        details = {"retry_after": retry_after} if retry_after else {}
        super().__init__(message, error_code, 429, details)

class ErrorHandler:
    """Centralized error handler"""
    
    @staticmethod
    def create_error_response(
        error: Exception,
        request: Request,
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
        message: str = "Internal server error",
        details: Optional[Dict[str, Any]] = None
    ) -> JSONResponse:
        """Create standardized error response"""
        
        correlation_id = get_correlation_id()
        
        # Create error response
        error_response = {
            "error": {
                "code": error_code,
                "message": message,
                "correlation_id": correlation_id,
                "timestamp": "2024-01-01T00:00:00Z"  # Simplified timestamp
            }
        }
        
        # Add details if provided
        if details:
            error_response["error"]["details"] = details
        
        # Log error with context
        error_context = {
            "error_type": type(error).__name__,
            "error_code": error_code,
            "status_code": status_code,
            "path": request.url.path,
            "method": request.method,
            "client_ip": getattr(request.client, 'host', 'unknown') if request.client else 'unknown',
            "user_agent": request.headers.get("user-agent", ""),
            "correlation_id": correlation_id
        }
        
        if details:
            error_context["details"] = details
        
        # Log at appropriate level
        if status_code >= 500:
            cloud_logger.error(f"Server error: {message}", **error_context)
        elif status_code >= 400:
            cloud_logger.warning(f"Client error: {message}", **error_context)
        else:
            cloud_logger.info(f"Error response: {message}", **error_context)
        
        # Record metrics
        metrics.record_http_request(
            method=request.method,
            endpoint=request.url.path,
            status_code=status_code,
            duration=0  # Will be updated by middleware
        )
        
        return JSONResponse(
            status_code=status_code,
            content=error_response,
            headers={"X-Correlation-ID": correlation_id}
        )

# Global error handler instance
error_handler = ErrorHandler()

# Exception handlers for FastAPI
async def application_error_handler(request: Request, exc: ApplicationError) -> JSONResponse:
    """Handle custom application errors"""
    return error_handler.create_error_response(
        error=exc,
        request=request,
        status_code=exc.status_code,
        error_code=exc.error_code,
        message=exc.message,
        details=exc.details
    )

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI HTTP exceptions"""
    return error_handler.create_error_response(
        error=exc,
        request=request,
        status_code=exc.status_code,
        error_code="HTTP_ERROR",
        message=exc.detail,
        details={"status_code": exc.status_code}
    )

async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle Starlette HTTP exceptions"""
    return error_handler.create_error_response(
        error=exc,
        request=request,
        status_code=exc.status_code,
        error_code="HTTP_ERROR",
        message=exc.detail,
        details={"status_code": exc.status_code}
    )

async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle request validation errors"""
    validation_details = {
        "validation_errors": exc.errors(),
        "body": exc.body
    }
    
    return error_handler.create_error_response(
        error=exc,
        request=request,
        status_code=422,
        error_code="VALIDATION_ERROR",
        message="Request validation failed",
        details=validation_details
    )

async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Handle SQLAlchemy database errors"""
    error_code = "DATABASE_ERROR"
    message = "Database operation failed"
    status_code = 500
    
    # Handle specific database errors
    if isinstance(exc, IntegrityError):
        error_code = "INTEGRITY_ERROR"
        message = "Database integrity constraint violation"
        status_code = 409
    
    return error_handler.create_error_response(
        error=exc,
        request=request,
        status_code=status_code,
        error_code=error_code,
        message=message,
        details={"database_error": str(exc)}
    )

async def redis_error_handler(request: Request, exc: RedisError) -> JSONResponse:
    """Handle Redis connection/operation errors"""
    return error_handler.create_error_response(
        error=exc,
        request=request,
        status_code=503,
        error_code="CACHE_ERROR",
        message="Cache service unavailable",
        details={"cache_error": str(exc)}
    )

async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions"""
    # Log the full traceback for debugging
    cloud_logger.error(
        f"Unhandled exception: {str(exc)}",
        error_type=type(exc).__name__,
        traceback=traceback.format_exc(),
        path=request.url.path,
        method=request.method
    )
    
    return error_handler.create_error_response(
        error=exc,
        request=request,
        status_code=500,
        error_code="INTERNAL_ERROR",
        message="An unexpected error occurred",
        details={"error_type": type(exc).__name__}
    )