import redis
import json
import os
import threading
from typing import Optional, Any, Union
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

class RedisCache:
    _instance: Optional['RedisCache'] = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.redis_url = os.getenv("REDIS_URL")
            self.default_ttl = int(os.getenv("REDIS_CACHE_TTL", 3600))
            self.client: Optional[redis.Redis] = None
            self._initialized = True
            self._connect()

    def _connect(self):
        """Initialize Redis connection"""
        try:
            if self.redis_url and self.redis_url != "redis://default:password@host:port":
                self.client = redis.Redis.from_url(
                    self.redis_url,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5
                )
                # Test connection
                self.client.ping()
                logger.info("Redis connection established successfully")
            else:
                logger.warning("Redis URL not configured or using default placeholder - caching disabled")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.client = None

    def is_connected(self) -> bool:
        """Check if Redis is connected and available"""
        try:
            if self.client:
                self.client.ping()
                return True
        except Exception as e:
            logger.error(f"Redis connection check failed: {e}")
        return False

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a value in cache with optional TTL"""
        if not self.client or not self.is_connected():
            return False

        try:
            serialized_value = json.dumps(value) if not isinstance(value, str) else value
            ttl = ttl or self.default_ttl

            result = self.client.setex(key, ttl, serialized_value)
            logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
            return result
        except Exception as e:
            logger.error(f"Failed to set cache key {key}: {e}")
            return False

    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache"""
        if not self.client or not self.is_connected():
            return None

        try:
            value = self.client.get(key)
            if value is None:
                logger.debug(f"Cache MISS: {key}")
                return None

            logger.debug(f"Cache HIT: {key}")

            # Try to deserialize JSON, fallback to string
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value

        except Exception as e:
            logger.error(f"Failed to get cache key {key}: {e}")
            return None

    def delete(self, key: str) -> bool:
        """Delete a key from cache"""
        if not self.client or not self.is_connected():
            return False

        try:
            result = self.client.delete(key) > 0
            logger.debug(f"Cache DELETE: {key}")
            return result
        except Exception as e:
            logger.error(f"Failed to delete cache key {key}: {e}")
            return False

    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching a pattern"""
        if not self.client or not self.is_connected():
            return 0

        try:
            keys = self.client.keys(pattern)
            if keys:
                count = self.client.delete(*keys)
                logger.debug(f"Cache DELETE_PATTERN: {pattern} ({count} keys)")
                return count
            return 0
        except Exception as e:
            logger.error(f"Failed to delete cache pattern {pattern}: {e}")
            return 0

    def exists(self, key: str) -> bool:
        """Check if a key exists in cache"""
        if not self.client or not self.is_connected():
            return False

        try:
            return bool(self.client.exists(key))
        except Exception as e:
            logger.error(f"Failed to check cache key existence {key}: {e}")
            return False

    def get_ttl(self, key: str) -> int:
        """Get TTL of a key (-1 if no TTL, -2 if key doesn't exist)"""
        if not self.client or not self.is_connected():
            return -2

        try:
            return self.client.ttl(key)
        except Exception as e:
            logger.error(f"Failed to get TTL for cache key {key}: {e}")
            return -2

    def extend_ttl(self, key: str, ttl: int) -> bool:
        """Extend TTL of an existing key"""
        if not self.client or not self.is_connected():
            return False

        try:
            result = self.client.expire(key, ttl)
            if result:
                logger.debug(f"Cache TTL extended: {key} ({ttl}s)")
            return result
        except Exception as e:
            logger.error(f"Failed to extend TTL for cache key {key}: {e}")
            return False

# Global cache instance
cache = RedisCache()

# Helper functions for easier usage
def cache_set(key: str, value: Any, ttl: Optional[int] = None) -> bool:
    """Set a value in cache"""
    return cache.set(key, value, ttl)

def cache_get(key: str) -> Optional[Any]:
    """Get a value from cache"""
    return cache.get(key)

def cache_delete(key: str) -> bool:
    """Delete a key from cache"""
    return cache.delete(key)

def cache_delete_pattern(pattern: str) -> int:
    """Delete all keys matching a pattern"""
    return cache.delete_pattern(pattern)

def cache_exists(key: str) -> bool:
    """Check if a key exists in cache"""
    return cache.exists(key)

def generate_cache_key(prefix: str, *args) -> str:
    """Generate a cache key from prefix and arguments"""
    return f"{prefix}:{':'.join(str(arg) for arg in args)}"

# Decorator for caching function results
def cached(key_prefix: str = "", ttl: Optional[int] = None):
    """Decorator to cache function results"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_prefix:
                cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            else:
                cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"

            # Try to get from cache
            cached_result = cache_get(cache_key)
            if cached_result is not None:
                return cached_result

            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_set(cache_key, result, ttl)
            return result

        return wrapper
    return decorator

if __name__ == "__main__":
    # Test connection
    if cache.is_connected():
        print("Redis connection successful!")
        print(f"Default TTL: {cache.default_ttl} seconds")
    else:
        print("Redis connection failed!")