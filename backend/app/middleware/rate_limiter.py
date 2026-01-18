from fastapi import Request, HTTPException
from collections import defaultdict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed for this client"""
        now = datetime.now()
        window_start = now - timedelta(seconds=self.window_seconds)
        
        # Remove old requests
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if req_time > window_start
        ]
        
        # Check if under limit
        if len(self.requests[client_id]) >= self.max_requests:
            logger.warning(f"Rate limit exceeded for client: {client_id}")
            return False
        
        # Add current request
        self.requests[client_id].append(now)
        return True


# Global rate limiter instance
chat_rate_limiter = RateLimiter(max_requests=30, window_seconds=60)  # 30 requests per minute
ticket_rate_limiter = RateLimiter(max_requests=10, window_seconds=60)  # 10 tickets per minute