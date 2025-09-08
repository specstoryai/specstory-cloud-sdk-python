"""Base resource class"""

from typing import Any, Dict, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from .._http import HTTPClient, AsyncHTTPClient


class BaseResource:
    """Base class for synchronous resources"""
    
    def __init__(self, http: "HTTPClient") -> None:
        self._http = http
    
    def _request(self, **kwargs: Any) -> Any:
        return self._http.request(**kwargs)
    
    def _request_with_headers(self, **kwargs: Any) -> Tuple[Any, Dict[str, str]]:
        return self._http.request_with_headers(**kwargs)


class AsyncBaseResource:
    """Base class for asynchronous resources"""
    
    def __init__(self, http: "AsyncHTTPClient") -> None:
        self._http = http
    
    async def _request(self, **kwargs: Any) -> Any:
        return await self._http.request(**kwargs)
    
    async def _request_with_headers(self, **kwargs: Any) -> Tuple[Any, Dict[str, str]]:
        return await self._http.request_with_headers(**kwargs)