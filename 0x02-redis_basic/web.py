#!/usr/bin/env python3
'''A module with tools for request caching and tracking.
'''
from requests import get
from uuid import uuid4
import redis
from functools import wraps  # for decorator

# Cache class (same as previous exercise)
class Cache:
    def __init__(self):
        self._redis = redis.Redis()
        self._redis.flushdb()

    def store(self, data: str | bytes | int | float) -> str:
        key = str(uuid4())
        self._redis.set(key, data, ex=10)  # Store with 10 seconds expiration
        return key


cache = Cache()  # Create a global cache instance


def count_url_access(func):
    """Decorator to track URL access count in cache."""
    @wraps(func)
    def wrapper(url: str) -> str:
        count_key = f"count:{url}"
        # Increment count for accessed URL (initialize if not present)
        cache._redis.incr(count_key)
        return func(url)
    return wrapper


@count_url_access  # Apply the decorator to track access count
def get_page(url: str) -> str:
    """Fetches and caches the HTML content of a URL."""
    cache_key = f"page:{url}"  # Cache key format for page content
    cached_content = cache._redis.get(cache_key)

    if cached_content:
        print(f"Using cached content for {url}")
        return cached_content.decode("utf-8")  # Decode cached bytes

    # Fetch content if not cached
    response = get(url)
    response.raise_for_status()  # Raise error for non-2xx status codes

    # Store content in cache with 10 seconds expiration
    cache.store(response.content)

    return response.text
