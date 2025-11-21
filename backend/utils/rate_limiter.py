"""
Rate Limiting Utilities for API Request Management
Implements token bucket algorithm to stay within Gemini's 10 RPM free tier limit
"""

import asyncio
import time
from typing import List, Callable, Any
import logging

logger = logging.getLogger(__name__)


class TokenBucketRateLimiter:
    """
    Token bucket algorithm for precise rate limiting
    
    How it works:
    - You have a bucket with N tokens (N = RPM limit)
    - Each API request consumes 1 token
    - Tokens refill at a constant rate (RPM limit per minute)
    - If bucket is empty, you must wait for refill
    
    Example for Gemini Free Tier (10 RPM):
    - Bucket starts with 10 tokens
    - You can make 10 requests instantly (burst)
    - After 6 seconds, you get 1 new token (10 tokens/60 seconds)
    - This enforces the 10 RPM average
    """
    
    def __init__(self, rpm_limit: int = 10):
        """
        Args:
            rpm_limit: Requests per minute allowed (default: 10 for Gemini free tier)
        """
        self.rpm_limit = rpm_limit
        self.tokens = float(rpm_limit)  # Start with full bucket
        self.last_refill = time.time()
        self.lock = asyncio.Lock()
        
        logger.info(f"⏱️ Rate limiter initialized: {rpm_limit} RPM limit")
    
    async def acquire(self, tokens_needed: int = 1):
        """
        Wait until enough tokens are available
        
        Args:
            tokens_needed: Number of tokens needed (= number of parallel agents)
        """
        async with self.lock:
            while True:
                # Refill tokens based on time passed
                now = time.time()
                time_passed = now - self.last_refill
                
                # Refill rate: rpm_limit tokens per 60 seconds
                tokens_to_add = (time_passed / 60.0) * self.rpm_limit
                self.tokens = min(self.rpm_limit, self.tokens + tokens_to_add)
                self.last_refill = now
                
                # Check if we have enough tokens
                if self.tokens >= tokens_needed:
                    self.tokens -= tokens_needed
                    logger.debug(f"✅ Acquired {tokens_needed} tokens. Remaining: {self.tokens:.2f}")
                    return
                
                # Not enough tokens, calculate wait time
                tokens_needed_to_wait = tokens_needed - self.tokens
                wait_time = (tokens_needed_to_wait / self.rpm_limit) * 60.0
                
                logger.info(f"⏳ Rate limit: waiting {wait_time:.1f}s for {tokens_needed} tokens")
                await asyncio.sleep(wait_time)


class RateLimitedExecutor:
    """
    Execute tasks in parallel but respect API rate limits
    Uses semaphore to limit concurrent execution
    
    Example:
        executor = RateLimitedExecutor(max_concurrent=2)
        tasks = [task1, task2, task3, task4, task5]
        results = await executor.execute_batch(tasks)
        
    Execution flow:
        [task1, task2] → parallel (batch 1)
        [task3, task4] → parallel (batch 2)
        [task5] → single (batch 3)
    """
    
    def __init__(self, max_concurrent: int = 2):
        """
        Args:
            max_concurrent: Maximum parallel requests allowed
                           For Gemini free tier: 2 is safe (10 RPM / 5 agents avg = 2)
        """
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.max_concurrent = max_concurrent
        
        logger.info(f"🔀 Executor initialized: max {max_concurrent} concurrent tasks")
    
    async def execute_with_limit(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute a single function with rate limiting
        
        The semaphore ensures only max_concurrent tasks run at once
        """
        async with self.semaphore:
            logger.debug(f"▶️ Executing task: {func.__name__ if hasattr(func, '__name__') else 'async_task'}")
            result = await func(*args, **kwargs)
            # Small delay to avoid burst
            await asyncio.sleep(0.1)
            return result
    
    async def execute_batch(self, tasks: List[Callable]) -> List[Any]:
        """
        Execute multiple tasks respecting rate limits
        
        Args:
            tasks: List of async functions to execute
        
        Returns:
            List of results (or exceptions if return_exceptions=True)
        """
        logger.info(f"📦 Executing batch of {len(tasks)} tasks (max {self.max_concurrent} concurrent)")
        
        # Wrap each task with rate limiting
        limited_tasks = [
            self.execute_with_limit(task) 
            for task in tasks
        ]
        
        # asyncio.gather will automatically batch them
        # based on semaphore availability
        results = await asyncio.gather(*limited_tasks, return_exceptions=True)
        
        # Count successes vs failures
        successes = sum(1 for r in results if not isinstance(r, Exception))
        failures = len(results) - successes
        
        logger.info(f"✅ Batch complete: {successes} succeeded, {failures} failed")
        
        return results


class SmartRateLimitedOrchestrator:
    """
    Combines token bucket rate limiting with concurrent execution limiting
    
    Two-layer protection:
    1. Token bucket: Ensures we don't exceed RPM limit over time
    2. Semaphore: Ensures we don't exceed concurrent limit at any moment
    
    Example for Gemini Free Tier:
    - Token bucket: 10 tokens/minute
    - Semaphore: 2 concurrent max
    - Result: Run 2 agents at a time, never exceed 10 RPM overall
    """
    
    def __init__(self, rpm_limit: int = 10, max_concurrent: int = 2):
        """
        Args:
            rpm_limit: Requests per minute limit (10 for Gemini free tier)
            max_concurrent: Max parallel requests (2 for safe free tier usage)
        """
        self.rate_limiter = TokenBucketRateLimiter(rpm_limit)
        self.executor = RateLimitedExecutor(max_concurrent)
        self.rpm_limit = rpm_limit
        self.max_concurrent = max_concurrent
        
        logger.info(f"🎯 Smart orchestrator ready: {rpm_limit} RPM, {max_concurrent} concurrent")
    
    async def execute_with_rate_limit(self, tasks: List[Callable]) -> List[Any]:
        """
        Execute tasks with both RPM and concurrent limits
        
        Flow:
        1. Acquire tokens from bucket (for RPM limit)
        2. Execute tasks with semaphore (for concurrent limit)
        
        Args:
            tasks: List of async callable tasks
        
        Returns:
            List of results from all tasks
        """
        num_tasks = len(tasks)
        
        logger.info(f"🚀 Starting rate-limited execution of {num_tasks} tasks")
        
        # Step 1: Acquire tokens from rate limiter
        # This ensures we don't exceed RPM limit
        await self.rate_limiter.acquire(tokens_needed=num_tasks)
        
        # Step 2: Execute tasks with concurrent limit
        # This ensures we don't exceed parallel execution capacity
        results = await self.executor.execute_batch(tasks)
        
        logger.info(f"✅ Rate-limited execution complete")
        
        return results
