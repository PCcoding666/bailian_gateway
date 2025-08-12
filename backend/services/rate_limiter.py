import redis
import time
from typing import Optional
import os

class RateLimiter:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=int(os.getenv("REDIS_DB", 0)),
            decode_responses=True
        )
    
    def is_allowed(self, key: str, max_requests: int, window: int) -> bool:
        """
        Check if a request is allowed based on rate limiting rules
        
        Args:
            key: Unique identifier for the rate limit (e.g., user_id:endpoint)
            max_requests: Maximum number of requests allowed in the window
            window: Time window in seconds
            
        Returns:
            bool: True if request is allowed, False if rate limited
        """
        # Use Redis pipeline for atomic operations
        pipe = self.redis_client.pipeline()
        
        # Get current timestamp
        now = time.time()
        # Remove expired entries
        pipe.zremrangebyscore(key, 0, now - window)
        # Get current count
        pipe.zcard(key)
        # Add current request
        pipe.zadd(key, {str(now): now})
        # Set expiration for the key
        pipe.expire(key, window)
        
        results = pipe.execute()
        current_count = results[1]
        
        return current_count < max_requests
    
    def get_rate_limit_headers(self, key: str, max_requests: int, window: int) -> dict:
        """
        Get rate limit headers for response
        
        Returns:
            dict: Headers with rate limit information
        """
        # Get current count
        now = time.time()
        current_count = self.redis_client.zcard(key)
        
        # Get reset time (earliest request in window)
        earliest = self.redis_client.zrange(key, 0, 0, withscores=True)
        reset_time = int(earliest[0][1]) + window if earliest else int(now) + window
        
        return {
            "X-RateLimit-Limit": str(max_requests),
            "X-RateLimit-Remaining": str(max(max_requests - current_count, 0)),
            "X-RateLimit-Reset": str(reset_time)
        }