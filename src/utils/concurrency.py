"""
Concurrency Utilities.

This module provides tools for managing asynchronous execution and rate limiting
to prevent API abuse and handle high-scale agent simulations.
"""

import asyncio
import time
from typing import Optional

class AsyncRateLimiter:
    """
    A simple asynchronous rate limiter using a sliding window.
    
    Ensures that requests do not exceed a certain number per time window.
    """
    def __init__(self, max_requests: int, window_seconds: float = 60.0):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = []
        self._lock = asyncio.Lock()

    async def wait(self):
        """
        Wait until a request can be made without exceeding the rate limit.
        """
        async with self._lock:
            while True:
                now = time.time()
                # Remove timestamps outside the window
                self.requests = [t for t in self.requests if now - t < self.window_seconds]
                
                if len(self.requests) < self.max_requests:
                    self.requests.append(now)
                    return
                
                # Wait for the oldest request to expire
                sleep_time = self.window_seconds - (now - self.requests[0])
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)

class GlobalRateLimiter:
    """
    Singleton-style rate limiter to be shared across all agents.
    """
    _instance: Optional[AsyncRateLimiter] = None
    
    @classmethod
    def get_instance(cls, max_rpm: int = 30) -> AsyncRateLimiter:
        if cls._instance is None:
            cls._instance = AsyncRateLimiter(max_requests=max_rpm, window_seconds=60.0)
        return cls._instance
