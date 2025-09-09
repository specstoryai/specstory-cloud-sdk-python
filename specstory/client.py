"""SpecStory Client for API interaction"""

import os
from typing import Optional, Any, Union, Dict
import re

from ._http import HTTPClient, AsyncHTTPClient
from .resources.projects import Projects, AsyncProjects
from .resources.sessions import Sessions, AsyncSessions
from .resources.graphql import GraphQL, AsyncGraphQL
from ._cache import LRUCache


class Client:
    """Synchronous client for SpecStory Cloud API"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout_s: Optional[float] = None,
        cache: Optional[Union[Dict[str, Any], bool]] = None
    ) -> None:
        api_key = api_key or os.environ.get("SPECSTORY_API_KEY")
        
        if not api_key:
            raise ValueError(
                "API key is required. Pass it as api_key parameter or "
                "set SPECSTORY_API_KEY environment variable."
            )
        
        # Initialize cache if not disabled
        if cache is False:
            self._cache = None
        else:
            cache_config = cache if isinstance(cache, dict) else {}
            self._cache = LRUCache(
                max_size=cache_config.get("max_size", 100),
                default_ttl=cache_config.get("default_ttl", 60.0)
            )
        
        self._http = HTTPClient(
            api_key=api_key,
            base_url=base_url or "https://cloud.specstory.com",
            timeout_s=timeout_s or 30.0
        )
        
        self.projects = Projects(self._http)
        self.sessions = Sessions(self._http, self._cache)
        self.graphql = GraphQL(self._http)
    
    def clear_cache(self) -> None:
        """Clear the response cache"""
        if self._cache:
            self._cache.clear()
    
    def invalidate_cache(self, pattern: str) -> None:
        """Invalidate cache entries matching a pattern"""
        if self._cache:
            self._cache.invalidate_pattern(re.compile(pattern))


class AsyncClient:
    """Asynchronous client for SpecStory Cloud API"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout_s: Optional[float] = None,
        cache: Optional[Union[Dict[str, Any], bool]] = None
    ) -> None:
        api_key = api_key or os.environ.get("SPECSTORY_API_KEY")
        
        if not api_key:
            raise ValueError(
                "API key is required. Pass it as api_key parameter or "
                "set SPECSTORY_API_KEY environment variable."
            )
        
        # Initialize cache if not disabled
        if cache is False:
            self._cache = None
        else:
            cache_config = cache if isinstance(cache, dict) else {}
            self._cache = LRUCache(
                max_size=cache_config.get("max_size", 100),
                default_ttl=cache_config.get("default_ttl", 60.0)
            )
            
        self._http = AsyncHTTPClient(
            api_key=api_key,
            base_url=base_url or "https://cloud.specstory.com",
            timeout_s=timeout_s or 30.0
        )
        
        self.projects = AsyncProjects(self._http)
        self.sessions = AsyncSessions(self._http, self._cache)
        self.graphql = AsyncGraphQL(self._http)
    
    async def __aenter__(self) -> "AsyncClient":
        await self._http.__aenter__()
        return self
    
    async def __aexit__(self, *args: Any) -> None:
        await self._http.__aexit__(*args)
    
    def clear_cache(self) -> None:
        """Clear the response cache"""
        if self._cache:
            self._cache.clear()
    
    def invalidate_cache(self, pattern: str) -> None:
        """Invalidate cache entries matching a pattern"""
        if self._cache:
            self._cache.invalidate_pattern(re.compile(pattern))