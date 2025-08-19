"""
Security Middleware for Bailian Demo
Integrates with Alibaba Cloud Security Services
"""

import os
import time
import json
import hashlib
import ipaddress
from typing import Dict, List, Optional, Tuple, Any
from fastapi import Request, Response, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
import redis
import logging
from datetime import datetime, timedelta

from utils.cloud_logger import get_logger
from utils.metrics import record_security_event

logger = get_logger(__name__)

class SecurityConfig:
    """Security configuration settings"""
    
    # Rate limiting settings
    RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "3600"))  # 1 hour
    
    # Security headers
    SECURITY_HEADERS = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
    }
    
    # Blocked IP ranges (example - customize based on requirements)
    BLOCKED_IP_RANGES = [
        "10.0.0.0/8",    # Private networks (if not internal)
        "172.16.0.0/12", # Private networks
        "192.168.0.0/16" # Private networks
    ]
    
    # Allowed IP ranges for admin operations
    ADMIN_IP_RANGES = [
        "10.0.0.0/8",    # Internal network
    ]
    
    # Suspicious patterns
    SUSPICIOUS_PATTERNS = [
        "eval(",
        "exec(",
        "<script",
        "javascript:",
        "vbscript:",
        "onload=",
        "onerror=",
        "../",
        "..\\",
        "union select",
        "drop table",
        "insert into"
    ]

class SecurityMetrics:
    """Security metrics collector"""
    
    def __init__(self):
        self.redis_client = None
        try:
            redis_host = os.getenv("REDIS_HOST", "localhost")
            redis_port = int(os.getenv("REDIS_PORT", "6379"))
            self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        except Exception as e:
            logger.warning(f"Redis connection failed for security metrics: {e}")
    
    def record_attack_attempt(self, attack_type: str, client_ip: str, details: Dict):
        """Record security attack attempt"""
        try:
            record_security_event(attack_type, "blocked", details)
            
            if self.redis_client:
                key = f"security:attacks:{attack_type}:{datetime.now().strftime('%Y-%m-%d')}"
                self.redis_client.hincrby(key, client_ip, 1)
                self.redis_client.expire(key, 86400 * 7)  # Keep for 7 days
                
        except Exception as e:
            logger.error(f"Failed to record attack attempt: {e}")
    
    def record_rate_limit_violation(self, client_ip: str, endpoint: str):
        """Record rate limit violation"""
        try:
            record_security_event("rate_limit", "blocked", {
                "client_ip": client_ip,
                "endpoint": endpoint
            })
            
            if self.redis_client:
                key = f"security:rate_limit:{datetime.now().strftime('%Y-%m-%d')}"
                self.redis_client.hincrby(key, client_ip, 1)
                self.redis_client.expire(key, 86400)
                
        except Exception as e:
            logger.error(f"Failed to record rate limit violation: {e}")

class IPSecurityChecker:
    """IP-based security checks"""
    
    def __init__(self):
        self.blocked_ranges = [ipaddress.ip_network(cidr) for cidr in SecurityConfig.BLOCKED_IP_RANGES]
        self.admin_ranges = [ipaddress.ip_network(cidr) for cidr in SecurityConfig.ADMIN_IP_RANGES]
    
    def is_ip_blocked(self, ip: str) -> bool:
        """Check if IP is in blocked ranges"""
        try:
            ip_addr = ipaddress.ip_address(ip)
            return any(ip_addr in network for network in self.blocked_ranges)
        except ValueError:
            return True  # Block invalid IPs
    
    def is_admin_ip(self, ip: str) -> bool:
        """Check if IP is allowed for admin operations"""
        try:
            ip_addr = ipaddress.ip_address(ip)
            return any(ip_addr in network for network in self.admin_ranges)
        except ValueError:
            return False

class ContentSecurityChecker:
    """Content-based security checks"""
    
    @staticmethod
    def check_suspicious_content(content: str) -> List[str]:
        """Check for suspicious patterns in content"""
        if not content:
            return []
        
        content_lower = content.lower()
        found_patterns = []
        
        for pattern in SecurityConfig.SUSPICIOUS_PATTERNS:
            if pattern in content_lower:
                found_patterns.append(pattern)
        
        return found_patterns
    
    @staticmethod
    def check_sql_injection(content: str) -> bool:
        """Check for SQL injection patterns"""
        if not content:
            return False
        
        sql_patterns = [
            "union select",
            "drop table",
            "delete from",
            "insert into",
            "update set",
            "exec(",
            "execute(",
            "sp_executesql"
        ]
        
        content_lower = content.lower()
        return any(pattern in content_lower for pattern in sql_patterns)
    
    @staticmethod
    def check_xss_attempt(content: str) -> bool:
        """Check for XSS patterns"""
        if not content:
            return False
        
        xss_patterns = [
            "<script",
            "javascript:",
            "vbscript:",
            "onload=",
            "onerror=",
            "onclick=",
            "onmouseover="
        ]
        
        content_lower = content.lower()
        return any(pattern in content_lower for pattern in xss_patterns)

class RateLimiter:
    """Rate limiting implementation"""
    
    def __init__(self):
        self.redis_client = None
        try:
            redis_host = os.getenv("REDIS_HOST", "localhost")
            redis_port = int(os.getenv("REDIS_PORT", "6379"))
            self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        except Exception as e:
            logger.warning(f"Redis connection failed for rate limiting: {e}")
    
    def is_rate_limited(self, client_ip: str, endpoint: str = "default") -> Tuple[bool, int]:
        """Check if client is rate limited"""
        if not self.redis_client:
            return False, 0
        
        try:
            key = f"rate_limit:{client_ip}:{endpoint}"
            current_time = int(time.time())
            window_start = current_time - SecurityConfig.RATE_LIMIT_WINDOW
            
            # Remove old entries
            self.redis_client.zremrangebyscore(key, 0, window_start)
            
            # Count current requests
            current_count = self.redis_client.zcard(key)
            
            if current_count >= SecurityConfig.RATE_LIMIT_REQUESTS:
                # Get time until reset
                oldest_request = self.redis_client.zrange(key, 0, 0, withscores=True)
                if oldest_request:
                    reset_time = int(oldest_request[0][1]) + SecurityConfig.RATE_LIMIT_WINDOW
                    return True, reset_time - current_time
                return True, SecurityConfig.RATE_LIMIT_WINDOW
            
            # Add current request
            self.redis_client.zadd(key, {str(current_time): current_time})
            self.redis_client.expire(key, SecurityConfig.RATE_LIMIT_WINDOW)
            
            return False, 0
            
        except Exception as e:
            logger.error(f"Rate limiting check failed: {e}")
            return False, 0

class SecurityMiddleware(BaseHTTPMiddleware):
    """Comprehensive security middleware"""
    
    def __init__(self, app):
        super().__init__(app)
        self.metrics = SecurityMetrics()
        self.ip_checker = IPSecurityChecker()
        self.content_checker = ContentSecurityChecker()
        self.rate_limiter = RateLimiter()
    
    async def dispatch(self, request: Request, call_next):
        """Main security processing"""
        client_ip = self.get_client_ip(request)
        endpoint = str(request.url.path)
        
        # Security checks
        security_result = await self.perform_security_checks(request, client_ip, endpoint)
        
        if security_result["blocked"]:
            return self.create_blocked_response(security_result)
        
        # Process request
        response = await call_next(request)
        
        # Add security headers
        self.add_security_headers(response)
        
        # Log successful request
        logger.info("Request processed successfully", extra={
            "client_ip": client_ip,
            "endpoint": endpoint,
            "method": request.method,
            "user_agent": request.headers.get("user-agent", "")
        })
        
        return response
    
    def get_client_ip(self, request: Request) -> str:
        """Extract client IP address"""
        # Check for forwarded headers (from load balancer)
        forwarded_ips = request.headers.get("x-forwarded-for")
        if forwarded_ips:
            return forwarded_ips.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fallback to direct connection
        if request.client:
            return request.client.host
        
        return "unknown"
    
    async def perform_security_checks(self, request: Request, client_ip: str, endpoint: str) -> Dict:
        """Perform comprehensive security checks"""
        
        # IP-based checks
        if self.ip_checker.is_ip_blocked(client_ip):
            self.metrics.record_attack_attempt("blocked_ip", client_ip, {
                "endpoint": endpoint,
                "reason": "IP in blocked range"
            })
            return {
                "blocked": True,
                "reason": "IP blocked",
                "status_code": status.HTTP_403_FORBIDDEN
            }
        
        # Rate limiting
        is_limited, reset_time = self.rate_limiter.is_rate_limited(client_ip, endpoint)
        if is_limited:
            self.metrics.record_rate_limit_violation(client_ip, endpoint)
            return {
                "blocked": True,
                "reason": "Rate limit exceeded",
                "status_code": status.HTTP_429_TOO_MANY_REQUESTS,
                "reset_time": reset_time
            }
        
        # Content security checks
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    content = body.decode("utf-8")
                    
                    # Check for SQL injection
                    if self.content_checker.check_sql_injection(content):
                        self.metrics.record_attack_attempt("sql_injection", client_ip, {
                            "endpoint": endpoint,
                            "content_preview": content[:100]
                        })
                        return {
                            "blocked": True,
                            "reason": "SQL injection attempt detected",
                            "status_code": status.HTTP_400_BAD_REQUEST
                        }
                    
                    # Check for XSS
                    if self.content_checker.check_xss_attempt(content):
                        self.metrics.record_attack_attempt("xss_attempt", client_ip, {
                            "endpoint": endpoint,
                            "content_preview": content[:100]
                        })
                        return {
                            "blocked": True,
                            "reason": "XSS attempt detected", 
                            "status_code": status.HTTP_400_BAD_REQUEST
                        }
                    
                    # Check for other suspicious patterns
                    suspicious_patterns = self.content_checker.check_suspicious_content(content)
                    if suspicious_patterns:
                        self.metrics.record_attack_attempt("suspicious_content", client_ip, {
                            "endpoint": endpoint,
                            "patterns": suspicious_patterns,
                            "content_preview": content[:100]
                        })
                        return {
                            "blocked": True,
                            "reason": f"Suspicious content detected: {', '.join(suspicious_patterns)}",
                            "status_code": status.HTTP_400_BAD_REQUEST
                        }
            
            except Exception as e:
                logger.warning(f"Content security check failed: {e}")
        
        # Admin endpoint protection
        if "/admin" in endpoint or "/api/admin" in endpoint:
            if not self.ip_checker.is_admin_ip(client_ip):
                self.metrics.record_attack_attempt("unauthorized_admin", client_ip, {
                    "endpoint": endpoint
                })
                return {
                    "blocked": True,
                    "reason": "Admin access not allowed from this IP",
                    "status_code": status.HTTP_403_FORBIDDEN
                }
        
        return {"blocked": False}
    
    def create_blocked_response(self, security_result: Dict) -> Response:
        """Create response for blocked requests"""
        
        status_code = security_result.get("status_code", status.HTTP_403_FORBIDDEN)
        reason = security_result.get("reason", "Request blocked")
        
        response_data = {
            "error": "Security policy violation",
            "message": reason,
            "timestamp": datetime.utcnow().isoformat(),
            "support_reference": f"SEC-{int(time.time())}"
        }
        
        # Add rate limit headers if applicable
        if status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            reset_time = security_result.get("reset_time", 3600)
            response_data["retry_after"] = reset_time
        
        response = Response(
            content=json.dumps(response_data),
            status_code=status_code,
            media_type="application/json"
        )
        
        # Add security headers
        self.add_security_headers(response)
        
        return response
    
    def add_security_headers(self, response: Response):
        """Add security headers to response"""
        for header, value in SecurityConfig.SECURITY_HEADERS.items():
            response.headers[header] = value
        
        # Add custom headers
        response.headers["X-Security-Policy"] = "enabled"
        response.headers["X-Request-ID"] = str(int(time.time() * 1000))

class SecurityHealthCheck:
    """Security health check utilities"""
    
    def __init__(self):
        self.metrics = SecurityMetrics()
    
    def check_security_status(self) -> Dict[str, Any]:
        """Check overall security status"""
        try:
            status = {
                "security_middleware": "active",
                "rate_limiting": "enabled",
                "content_filtering": "enabled",
                "ip_filtering": "enabled",
                "security_headers": "enabled",
                "redis_connection": "unknown",
                "last_check": datetime.utcnow().isoformat()
            }
            
            # Test Redis connection
            if self.metrics.redis_client:
                try:
                    self.metrics.redis_client.ping()
                    status["redis_connection"] = "connected"
                except:
                    status["redis_connection"] = "failed"
            else:
                status["redis_connection"] = "not_configured"
            
            return status
            
        except Exception as e:
            logger.error(f"Security health check failed: {e}")
            return {
                "error": str(e),
                "status": "unhealthy",
                "last_check": datetime.utcnow().isoformat()
            }
    
    def get_security_metrics(self) -> Dict[str, Any]:
        """Get security metrics summary"""
        try:
            metrics = {
                "blocked_requests_today": 0,
                "rate_limited_requests_today": 0,
                "attack_attempts_today": 0,
                "top_blocked_ips": [],
                "last_updated": datetime.utcnow().isoformat()
            }
            
            if self.metrics.redis_client:
                today = datetime.now().strftime('%Y-%m-%d')
                
                # Get blocked requests
                for attack_type in ["blocked_ip", "sql_injection", "xss_attempt", "suspicious_content"]:
                    key = f"security:attacks:{attack_type}:{today}"
                    count = sum(int(v) for v in self.metrics.redis_client.hvals(key) or [])
                    metrics["attack_attempts_today"] += count
                
                # Get rate limited requests
                rate_limit_key = f"security:rate_limit:{today}"
                rate_limited = sum(int(v) for v in self.metrics.redis_client.hvals(rate_limit_key) or [])
                metrics["rate_limited_requests_today"] = rate_limited
                
                metrics["blocked_requests_today"] = metrics["attack_attempts_today"] + rate_limited
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get security metrics: {e}")
            return {"error": str(e)}

# Export main components
__all__ = [
    "SecurityMiddleware",
    "SecurityConfig", 
    "SecurityHealthCheck",
    "SecurityMetrics"
]