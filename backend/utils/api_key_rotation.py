"""
API Key Rotation Manager for Multi-Agent Parallel Execution
Implements round-robin API key rotation to distribute load across multiple
Google Gemini API keys and avoid rate limit throttling.
"""

import asyncio
import os
import random
import logging
from typing import List, Callable, Any
from functools import wraps
from dotenv import load_dotenv
import threading

# Ensure env vars are loaded
load_dotenv()

logger = logging.getLogger(__name__)

class RateLimitError(Exception):
    """Raised when API rate limit is exceeded"""
    pass


class APIKeyRotator:
    """
    Manages multiple API keys with round-robin rotation
    
    Benefits:
    - Distributes load across multiple API keys
    - Prevents rate limit errors in parallel execution
    - 5 free keys = 50 RPM instead of 10 RPM
    
    Usage:
        rotator = APIKeyRotator.from_env()
        key = rotator.get_next_key()
    """
    
    def __init__(self, api_keys: List[str]):
        if not api_keys:
            raise ValueError("At least one API key must be provided")
        
        self.api_keys = api_keys
        self.current_index = 0
        # Use threading.Lock for thread safety across event loops
        self.lock = threading.Lock()
        
        logger.info(f"Initialized APIKeyRotator with {len(api_keys)} keys")
        logger.info(f"Total rate limit: {len(api_keys) * 10} RPM (Free Tier)")
    
    @classmethod
    def from_env(cls, env_var: str = "GEMINI_API_KEY") -> "APIKeyRotator":
        """
        Create rotator from environment variables.
        Auto-detects provider if specific env_var not found.
        """
        # Prefixes to check if default is not found
        prefixes = [env_var.replace("_API_KEY", ""), "GEMINI", "GROQ", "OPENAI", "ANTHROPIC"]
        
        api_keys = []
        found_prefix = ""
        
        for prefix in prefixes:
            base_var = f"{prefix}_API_KEY"
            
            # 1. Check base key
            if os.getenv(base_var):
                api_keys.append(os.getenv(base_var))
            
            # 2. Check indexed keys (PREFIX_API_KEY1, PREFIX_API_KEY_1, etc.)
            i = 1
            while True:
                key = os.getenv(f"{base_var}{i}") or os.getenv(f"{base_var}_{i}")
                if not key:
                    break
                api_keys.append(key)
                i += 1
                
            # 3. Check comma-separated list
            keys_str = os.getenv(f"{base_var}S", "")
            if keys_str:
                api_keys.extend([k.strip() for k in keys_str.split(",") if k.strip()])
                
            if api_keys:
                found_prefix = prefix
                logger.info(f"Found {len(api_keys)} API keys for provider: {prefix}")
                break
        
        if not api_keys:
            # Fallback for when no specific keys are found - prevent crash but warn
            logger.warning("No API keys found in environment variables!")
            # We don't raise here to allow manual instantiation, but typical usage might fail later
            
        # Remove duplicates while preserving order
        unique_keys = []
        seen = set()
        for key in api_keys:
            if key and key not in seen:
                unique_keys.append(key)
                seen.add(key)
                
        if not unique_keys:
             raise ValueError("No valid API keys found. Please check your .env file.")

        return cls(unique_keys)
    
    def get_next_key(self) -> str:
        """
        Get next API key in round-robin fashion
        Thread-safe with threading lock
        
        Returns:
            API key string
        """
        with self.lock:
            key = self.api_keys[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.api_keys)
            
            # Don't log full key for security
            key_preview = f"{key[:10]}...{key[-4:]}"
            logger.debug(f"Selected key {self.current_index}/{len(self.api_keys)}: {key_preview}")
            
            return key
    
    def get_current_key_sync(self) -> str:
        """
        Synchronous version of get_next_key (alias)
        """
        return self.get_next_key()
    
    async def execute_with_retry(
        self,
        func: Callable,
        max_retries: int = 3,
        base_delay: float = 1.0
    ) -> Any:
        """
        Execute function with exponential backoff on rate limit errors
        
        Args:
            func: Async function to execute
            max_retries: Maximum retry attempts
            base_delay: Base delay in seconds (exponentially increased)
            
        Returns:
            Result from func()
            
        Raises:
            Original exception if max retries exceeded
        """
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                # Try with current key
                result = await func()
                
                # Success - reset to avoid unnecessary delays
                if attempt > 0:
                    logger.info(f"Retry succeeded on attempt {attempt + 1}")
                
                return result
                
            except Exception as e:
                last_exception = e
                error_msg = str(e).lower()
                
                # Check if it's a rate limit error
                is_rate_limit = any(
                    phrase in error_msg
                    for phrase in ["rate limit", "quota", "429", "too many requests"]
                )
                
                if not is_rate_limit or attempt == max_retries - 1:
                    # Not a rate limit error, or final attempt - re-raise
                    raise
                
                # Exponential backoff with jitter
                wait_time = (base_delay * (2 ** attempt)) + random.uniform(0, 0.5)
                logger.warning(
                    f"Rate limit hit (attempt {attempt + 1}/{max_retries}). "
                    f"Retrying in {wait_time:.2f}s with next API key..."
                )
                
                await asyncio.sleep(wait_time)
        
        # Should never reach here, but just in case
        raise last_exception


# Singleton instance
_global_rotator = None


def get_rotator() -> APIKeyRotator:
    """
    Get global APIKeyRotator singleton
    
    Returns:
        APIKeyRotator instance
    """
    global _global_rotator
    
    if _global_rotator is None:
        _global_rotator = APIKeyRotator.from_env()
    
    return _global_rotator


def with_api_key_rotation(func):
    """
    Decorator to automatically rotate API keys for async functions
    
    Usage:
        @with_api_key_rotation
        async def call_api():
            key = get_rotator().get_current_key_sync()
            # Use key for API call
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        rotator = get_rotator()
        return await rotator.execute_with_retry(lambda: func(*args, **kwargs))
    
    return wrapper


# Example usage
if __name__ == "__main__":
    async def test_rotation():
        """Test API key rotation"""
        # Load from environment
        rotator = APIKeyRotator.from_env()
        
        print(f"Loaded {len(rotator.api_keys)} API keys")
        print(f"Total RPM capacity: {len(rotator.api_keys) * 10} (Free Tier)\n")
        
        # Simulate 10 parallel agent requests
        print("Simulating 10 parallel agent requests:")
        for i in range(10):
            key = rotator.get_next_key()
            key_preview = f"{key[:10]}...{key[-4:]}"
            print(f"  Agent {i+1}: Using key {key_preview}")
        
        print("\n✅ API keys rotated successfully!")
    
    # Run test
    asyncio.run(test_rotation())
