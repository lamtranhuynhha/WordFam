from functools import wraps
from typing import Any, Callable
import hashlib
import json

_cache = {}

def get_cache_key(*args, **kwargs) -> str:
    """Generate a cache key from function arguments."""
    key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
    return hashlib.md5(key_data.encode()).hexdigest()

def cached(func: Callable) -> Callable:
    """Decorator to cache function results."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        cache_key = f"{func.__name__}:{get_cache_key(*args, **kwargs)}"
        
        if cache_key in _cache:
            return _cache[cache_key]
        
        result = func(*args, **kwargs)
        _cache[cache_key] = result
        return result
    
    return wrapper

def clear_cache():
    """Clear all cached data."""
    global _cache
    _cache = {}
