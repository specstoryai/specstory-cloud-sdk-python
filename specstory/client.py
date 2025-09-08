"""SpecStory Client for API interaction"""

import os
from typing import Optional, Any

from ._http import HTTPClient, AsyncHTTPClient
from .resources.projects import Projects, AsyncProjects
from .resources.sessions import Sessions, AsyncSessions
from .resources.graphql import GraphQL, AsyncGraphQL


class Client:
    """Synchronous client for SpecStory Cloud API"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout_s: Optional[float] = None
    ) -> None:
        api_key = api_key or os.environ.get("SPECSTORY_API_KEY")
        
        if not api_key:
            raise ValueError(
                "API key is required. Pass it as api_key parameter or "
                "set SPECSTORY_API_KEY environment variable."
            )
        
        self._http = HTTPClient(
            api_key=api_key,
            base_url=base_url or "https://cloud.specstory.com",
            timeout_s=timeout_s or 30.0
        )
        
        self.projects = Projects(self._http)
        self.sessions = Sessions(self._http)
        self.graphql = GraphQL(self._http)


class AsyncClient:
    """Asynchronous client for SpecStory Cloud API"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout_s: Optional[float] = None
    ) -> None:
        api_key = api_key or os.environ.get("SPECSTORY_API_KEY")
        
        if not api_key:
            raise ValueError(
                "API key is required. Pass it as api_key parameter or "
                "set SPECSTORY_API_KEY environment variable."
            )
        
        self._http = AsyncHTTPClient(
            api_key=api_key,
            base_url=base_url or "https://cloud.specstory.com",
            timeout_s=timeout_s or 30.0
        )
        
        self.projects = AsyncProjects(self._http)
        self.sessions = AsyncSessions(self._http)
        self.graphql = AsyncGraphQL(self._http)
    
    async def __aenter__(self) -> "AsyncClient":
        await self._http.__aenter__()
        return self
    
    async def __aexit__(self, *args: Any) -> None:
        await self._http.__aexit__(*args)