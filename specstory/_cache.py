"""LRU Cache implementation for SpecStory SDK"""

from collections import OrderedDict
from dataclasses import dataclass
from typing import Any, Dict, Optional, Pattern
import time
import re


@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    data: Any
    etag: Optional[str] = None
    timestamp: float = 0.0
    ttl: float = 60.0  # seconds
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        return time.time() > self.timestamp + self.ttl


class LRUCache:
    """Simple LRU cache implementation"""
    
    def __init__(self, max_size: int = 100, default_ttl: float = 60.0):
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.max_size = max_size
        self.default_ttl = default_ttl
    
    def get(self, key: str) -> Optional[Any]:
        """Get an item from the cache"""
        entry = self._cache.get(key)
        if not entry:
            return None
        
        # Check if expired
        if entry.is_expired():
            del self._cache[key]
            return None
        
        # Move to end (most recently used)
        self._cache.move_to_end(key)
        return entry.data
    
    def get_entry(self, key: str) -> Optional[CacheEntry]:
        """Get entry with metadata"""
        entry = self._cache.get(key)
        if not entry:
            return None
        
        # Check if expired
        if entry.is_expired():
            del self._cache[key]
            return None
        
        # Move to end (most recently used)
        self._cache.move_to_end(key)
        return entry
    
    def set(self, key: str, data: Any, etag: Optional[str] = None, ttl: Optional[float] = None) -> None:
        """Set an item in the cache"""
        # Remove if exists to update position
        if key in self._cache:
            del self._cache[key]
        
        # Add to cache
        self._cache[key] = CacheEntry(
            data=data,
            etag=etag,
            timestamp=time.time(),
            ttl=ttl or self.default_ttl
        )
        
        # Evict if over size limit
        while len(self._cache) > self.max_size:
            # Remove least recently used (first item)
            self._cache.popitem(last=False)
    
    def has(self, key: str) -> bool:
        """Check if key exists and is not expired"""
        entry = self._cache.get(key)
        if not entry:
            return False
        
        # Check if expired
        if entry.is_expired():
            del self._cache[key]
            return False
        
        return True
    
    def delete(self, key: str) -> bool:
        """Delete an item from the cache"""
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    def clear(self) -> None:
        """Clear the entire cache"""
        self._cache.clear()
    
    @property
    def size(self) -> int:
        """Get cache size"""
        return len(self._cache)
    
    def invalidate_pattern(self, pattern: Pattern[str]) -> None:
        """Invalidate entries matching a pattern"""
        keys_to_delete = [
            key for key in self._cache.keys()
            if pattern.search(key)
        ]
        for key in keys_to_delete:
            del self._cache[key]