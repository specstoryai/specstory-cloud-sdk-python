"""HTTP client implementation with retry logic"""

import asyncio
import json
import random
import time
from typing import Optional, Dict, Any, Union, TypeVar, Literal, Tuple

import httpx

from ._errors import (
    SDKError, 
    NetworkError, 
    TimeoutError, 
    ErrorContext
)
from datetime import datetime
from ._constants import (
    SDK_VERSION,
    SDK_LANGUAGE,
    DEFAULT_TIMEOUT_S,
    DEFAULT_MAX_RETRIES,
    DEFAULT_BASE_DELAY_MS,
    IDEMPOTENT_METHODS,
    RETRY_STATUS_CODES,
)

T = TypeVar("T")
Method = Literal["GET", "POST", "PUT", "DELETE", "HEAD", "PATCH"]


class HTTPClient:
    """Synchronous HTTP client with retry logic"""
    
    def __init__(self, api_key: str, base_url: str, timeout_s: float, 
                 max_connections: int = 100, max_keepalive_connections: int = 20) -> None:
        self.api_key = api_key
        self.base_url = base_url
        self.timeout_s = timeout_s
        self._request_cache: Dict[str, Any] = {}
        
        # Configure connection pooling
        limits = httpx.Limits(
            max_connections=max_connections,
            max_keepalive_connections=max_keepalive_connections,
            keepalive_expiry=30.0
        )
        # Try to enable HTTP/2 if available
        try:
            self.client = httpx.Client(
                timeout=timeout_s,
                limits=limits,
                http2=True
            )
        except ImportError:
            # Fallback to HTTP/1.1 if h2 package is not installed
            self.client = httpx.Client(
                timeout=timeout_s,
                limits=limits
            )
    
    def request(
        self,
        method: Method,
        path: str,
        body: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout_s: Optional[float] = None,
        idempotency_key: Optional[str] = None,
        retries: Optional[int] = None,
        params: Optional[Dict[str, str]] = None,
    ) -> Any:
        """Make HTTP request with retry logic"""
        url = f"{self.base_url}{path}"
        timeout = timeout_s or self.timeout_s
        max_retries = retries if retries is not None else DEFAULT_MAX_RETRIES
        start_time = time.time()
        
        # Request deduplication for GET requests
        if method == "GET":
            cache_key = f"{method}:{url}"
            if cache_key in self._request_cache:
                # Return cached response if available
                cached = self._request_cache[cache_key]
                if time.time() - cached["timestamp"] < 1.0:  # 1 second cache
                    return cached["data"]
        
        request_headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": f"specstory-sdk-{SDK_LANGUAGE}/{SDK_VERSION}",
            "X-SDK-Version": SDK_VERSION,
            "X-SDK-Language": SDK_LANGUAGE,
        }
        
        if headers:
            request_headers.update(headers)
        
        if idempotency_key:
            request_headers["Idempotency-Key"] = idempotency_key
        
        last_error: Optional[Exception] = None
        
        for attempt in range(max_retries + 1):
            try:
                response = self.client.request(
                    method=method,
                    url=url,
                    json=body if body is not None else None,
                    headers=request_headers,
                    timeout=timeout,
                    params=params,
                )
                
                request_id = response.headers.get("x-request-id")
                
                if response.status_code >= 400:
                    context = ErrorContext(
                        method=method,
                        url=url,
                        timestamp=datetime.now(),
                        duration_ms=int((time.time() - start_time) * 1000),
                        retry_count=attempt
                    )
                    retry_after = response.headers.get("retry-after")
                    error = SDKError.from_response(
                        response.status_code, 
                        request_id, 
                        context,
                        retry_after
                    )
                    
                    # Retry logic
                    if (
                        attempt < max_retries
                        and (
                            response.status_code in RETRY_STATUS_CODES
                            or (method == "POST" and idempotency_key and response.status_code >= 500)
                        )
                    ):
                        self._sleep_with_backoff(attempt)
                        continue
                    
                    raise error
                
                # Handle 204 No Content
                if response.status_code == 204:
                    return None
                
                # Handle HEAD requests
                if method == "HEAD":
                    return {
                        "headers": dict(response.headers),
                        "status": response.status_code,
                    }
                
                result = response.json()
                
                # Cache successful GET responses
                if method == "GET" and response.status_code == 200:
                    cache_key = f"{method}:{url}"
                    self._request_cache[cache_key] = {
                        "data": result,
                        "timestamp": time.time()
                    }
                
                return result
                
            except httpx.RequestError as e:
                last_error = e
                
                if attempt < max_retries and self._should_retry(method):
                    self._sleep_with_backoff(attempt)
                    continue
                
                context = ErrorContext(
                    method=method,
                    url=url,
                    timestamp=datetime.now(),
                    duration_ms=int((time.time() - start_time) * 1000),
                    retry_count=attempt
                )
                
                # Check if it's a timeout error
                if isinstance(e, httpx.TimeoutException):
                    raise TimeoutError(
                        f"Request timed out after {timeout}s",
                        int(timeout * 1000),
                        context
                    )
                
                raise NetworkError(
                    f"Request failed: {str(e)}",
                    e,
                    context
                )
        
        raise NetworkError(
            f"Request failed after {max_retries + 1} attempts",
            last_error,
            ErrorContext(
                method=method,
                url=url,
                timestamp=datetime.now(),
                duration_ms=int((time.time() - start_time) * 1000),
                retry_count=max_retries + 1
            )
        )
    
    def request_with_headers(
        self,
        method: Method,
        path: str,
        body: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout_s: Optional[float] = None,
        idempotency_key: Optional[str] = None,
        retries: Optional[int] = None,
        params: Optional[Dict[str, str]] = None,
    ) -> Tuple[Any, Dict[str, str]]:
        """Make HTTP request with retry logic and return response with headers"""
        url = f"{self.base_url}{path}"
        timeout = timeout_s or self.timeout_s
        max_retries = retries if retries is not None else DEFAULT_MAX_RETRIES
        start_time = time.time()
        
        request_headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": f"specstory-sdk-{SDK_LANGUAGE}/{SDK_VERSION}",
            "X-SDK-Version": SDK_VERSION,
            "X-SDK-Language": SDK_LANGUAGE,
        }
        
        if headers:
            request_headers.update(headers)
        
        if idempotency_key:
            request_headers["Idempotency-Key"] = idempotency_key
        
        last_error: Optional[Exception] = None
        
        for attempt in range(max_retries + 1):
            try:
                response = self.client.request(
                    method=method,
                    url=url,
                    json=body if body is not None else None,
                    headers=request_headers,
                    timeout=timeout,
                    params=params,
                )
                
                request_id = response.headers.get("x-request-id")
                
                if response.status_code >= 400:
                    context = ErrorContext(
                        method=method,
                        url=url,
                        timestamp=datetime.now(),
                        duration_ms=int((time.time() - start_time) * 1000),
                        retry_count=attempt
                    )
                    retry_after = response.headers.get("retry-after")
                    error = SDKError.from_response(
                        response.status_code, 
                        request_id, 
                        context,
                        retry_after
                    )
                    
                    # Retry logic
                    if (
                        attempt < max_retries
                        and (
                            response.status_code in RETRY_STATUS_CODES
                            or (method == "POST" and idempotency_key and response.status_code >= 500)
                        )
                    ):
                        self._sleep_with_backoff(attempt)
                        continue
                    
                    raise error
                
                response_headers = dict(response.headers)
                
                # Handle 204 No Content
                if response.status_code == 204:
                    return None, response_headers
                
                # Handle HEAD requests
                if method == "HEAD":
                    return {
                        "headers": response_headers,
                        "status": response.status_code,
                    }, response_headers
                
                return response.json(), response_headers
                
            except httpx.RequestError as e:
                last_error = e
                
                if attempt < max_retries and self._should_retry(method):
                    self._sleep_with_backoff(attempt)
                    continue
                
                context = ErrorContext(
                    method=method,
                    url=url,
                    timestamp=datetime.now(),
                    duration_ms=int((time.time() - start_time) * 1000),
                    retry_count=attempt
                )
                
                # Check if it's a timeout error
                if isinstance(e, httpx.TimeoutException):
                    raise TimeoutError(
                        f"Request timed out after {timeout}s",
                        int(timeout * 1000),
                        context
                    )
                
                raise NetworkError(
                    f"Request failed: {str(e)}",
                    e,
                    context
                )
        
        raise NetworkError(
            f"Request failed after {max_retries + 1} attempts",
            last_error,
            ErrorContext(
                method=method,
                url=url,
                timestamp=datetime.now(),
                duration_ms=int((time.time() - start_time) * 1000),
                retry_count=max_retries + 1
            )
        )
    
    def _should_retry(self, method: str) -> bool:
        return method in IDEMPOTENT_METHODS
    
    def _sleep_with_backoff(self, attempt: int) -> None:
        jitter = random.random() * 0.1  # 0-100ms jitter
        delay = (DEFAULT_BASE_DELAY_MS / 1000) * (2 ** attempt) + jitter
        time.sleep(delay)
    
    def __enter__(self) -> "HTTPClient":
        return self
    
    def __exit__(self, *args: Any) -> None:
        self.client.close()


class AsyncHTTPClient:
    """Asynchronous HTTP client with retry logic"""
    
    def __init__(self, api_key: str, base_url: str, timeout_s: float,
                 max_connections: int = 100, max_keepalive_connections: int = 20) -> None:
        self.api_key = api_key
        self.base_url = base_url
        self.timeout_s = timeout_s
        self._request_cache: Dict[str, Any] = {}
        self._max_connections = max_connections
        self._max_keepalive_connections = max_keepalive_connections
        self.client: Optional[httpx.AsyncClient] = None
    
    async def request(
        self,
        method: Method,
        path: str,
        body: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout_s: Optional[float] = None,
        idempotency_key: Optional[str] = None,
        retries: Optional[int] = None,
        params: Optional[Dict[str, str]] = None,
    ) -> Any:
        """Make async HTTP request with retry logic"""
        if not self.client:
            limits = httpx.Limits(
                max_connections=self._max_connections,
                max_keepalive_connections=self._max_keepalive_connections,
                keepalive_expiry=30.0
            )
            # Try to enable HTTP/2 if available
            try:
                self.client = httpx.AsyncClient(
                    timeout=self.timeout_s,
                    limits=limits,
                    http2=True
                )
            except ImportError:
                # Fallback to HTTP/1.1 if h2 package is not installed
                self.client = httpx.AsyncClient(
                    timeout=self.timeout_s,
                    limits=limits
                )
        
        url = f"{self.base_url}{path}"
        timeout = timeout_s or self.timeout_s
        max_retries = retries if retries is not None else DEFAULT_MAX_RETRIES
        start_time = time.time()
        
        request_headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": f"specstory-sdk-{SDK_LANGUAGE}/{SDK_VERSION}",
            "X-SDK-Version": SDK_VERSION,
            "X-SDK-Language": SDK_LANGUAGE,
        }
        
        if headers:
            request_headers.update(headers)
        
        if idempotency_key:
            request_headers["Idempotency-Key"] = idempotency_key
        
        last_error: Optional[Exception] = None
        
        for attempt in range(max_retries + 1):
            try:
                response = await self.client.request(
                    method=method,
                    url=url,
                    json=body if body is not None else None,
                    headers=request_headers,
                    timeout=timeout,
                    params=params,
                )
                
                request_id = response.headers.get("x-request-id")
                
                if response.status_code >= 400:
                    context = ErrorContext(
                        method=method,
                        url=url,
                        timestamp=datetime.now(),
                        duration_ms=int((time.time() - start_time) * 1000),
                        retry_count=attempt
                    )
                    retry_after = response.headers.get("retry-after")
                    error = SDKError.from_response(
                        response.status_code, 
                        request_id, 
                        context,
                        retry_after
                    )
                    
                    # Retry logic
                    if (
                        attempt < max_retries
                        and (
                            response.status_code in RETRY_STATUS_CODES
                            or (method == "POST" and idempotency_key and response.status_code >= 500)
                        )
                    ):
                        await self._sleep_with_backoff(attempt)
                        continue
                    
                    raise error
                
                # Handle 204 No Content
                if response.status_code == 204:
                    return None
                
                # Handle HEAD requests
                if method == "HEAD":
                    return {
                        "headers": dict(response.headers),
                        "status": response.status_code,
                    }
                
                result = response.json()
                
                # Cache successful GET responses
                if method == "GET" and response.status_code == 200:
                    cache_key = f"{method}:{url}"
                    self._request_cache[cache_key] = {
                        "data": result,
                        "timestamp": time.time()
                    }
                
                return result
                
            except httpx.RequestError as e:
                last_error = e
                
                if attempt < max_retries and self._should_retry(method):
                    await self._sleep_with_backoff(attempt)
                    continue
                
                raise SDKError(
                    f"Request failed: {str(e)}",
                    code="network_error",
                    details={"original_error": str(e)},
                )
        
        raise NetworkError(
            f"Request failed after {max_retries + 1} attempts",
            last_error,
            ErrorContext(
                method=method,
                url=url,
                timestamp=datetime.now(),
                duration_ms=int((time.time() - start_time) * 1000),
                retry_count=max_retries + 1
            )
        )
    
    async def request_with_headers(
        self,
        method: Method,
        path: str,
        body: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout_s: Optional[float] = None,
        idempotency_key: Optional[str] = None,
        retries: Optional[int] = None,
        params: Optional[Dict[str, str]] = None,
    ) -> Tuple[Any, Dict[str, str]]:
        """Make async HTTP request with retry logic and return response with headers"""
        if not self.client:
            limits = httpx.Limits(
                max_connections=self._max_connections,
                max_keepalive_connections=self._max_keepalive_connections,
                keepalive_expiry=30.0
            )
            # Try to enable HTTP/2 if available
            try:
                self.client = httpx.AsyncClient(
                    timeout=self.timeout_s,
                    limits=limits,
                    http2=True
                )
            except ImportError:
                # Fallback to HTTP/1.1 if h2 package is not installed
                self.client = httpx.AsyncClient(
                    timeout=self.timeout_s,
                    limits=limits
                )
        
        url = f"{self.base_url}{path}"
        timeout = timeout_s or self.timeout_s
        max_retries = retries if retries is not None else DEFAULT_MAX_RETRIES
        
        request_headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": f"specstory-sdk-{SDK_LANGUAGE}/{SDK_VERSION}",
            "X-SDK-Version": SDK_VERSION,
            "X-SDK-Language": SDK_LANGUAGE,
        }
        
        if headers:
            request_headers.update(headers)
        
        if idempotency_key:
            request_headers["Idempotency-Key"] = idempotency_key
        
        last_error: Optional[Exception] = None
        
        for attempt in range(max_retries + 1):
            try:
                response = await self.client.request(
                    method=method,
                    url=url,
                    json=body if body is not None else None,
                    headers=request_headers,
                    timeout=timeout,
                    params=params,
                )
                
                request_id = response.headers.get("x-request-id")
                
                if response.status_code >= 400:
                    context = ErrorContext(
                        method=method,
                        url=url,
                        timestamp=datetime.now(),
                        duration_ms=int((time.time() - start_time) * 1000),
                        retry_count=attempt
                    )
                    retry_after = response.headers.get("retry-after")
                    error = SDKError.from_response(
                        response.status_code, 
                        request_id, 
                        context,
                        retry_after
                    )
                    
                    # Retry logic
                    if (
                        attempt < max_retries
                        and (
                            response.status_code in RETRY_STATUS_CODES
                            or (method == "POST" and idempotency_key and response.status_code >= 500)
                        )
                    ):
                        await self._sleep_with_backoff(attempt)
                        continue
                    
                    raise error
                
                response_headers = dict(response.headers)
                
                # Handle 204 No Content
                if response.status_code == 204:
                    return None, response_headers
                
                # Handle HEAD requests
                if method == "HEAD":
                    return {
                        "headers": response_headers,
                        "status": response.status_code,
                    }, response_headers
                
                return response.json(), response_headers
                
            except httpx.RequestError as e:
                last_error = e
                
                if attempt < max_retries and self._should_retry(method):
                    await self._sleep_with_backoff(attempt)
                    continue
                
                raise SDKError(
                    f"Request failed: {str(e)}",
                    code="network_error",
                    details={"original_error": str(e)},
                )
        
        raise NetworkError(
            f"Request failed after {max_retries + 1} attempts",
            last_error,
            ErrorContext(
                method=method,
                url=url,
                timestamp=datetime.now(),
                duration_ms=int((time.time() - start_time) * 1000),
                retry_count=max_retries + 1
            )
        )
    
    def _should_retry(self, method: str) -> bool:
        return method in IDEMPOTENT_METHODS
    
    async def _sleep_with_backoff(self, attempt: int) -> None:
        jitter = random.random() * 0.1  # 0-100ms jitter
        delay = (DEFAULT_BASE_DELAY_MS / 1000) * (2 ** attempt) + jitter
        await asyncio.sleep(delay)
    
    async def __aenter__(self) -> "AsyncHTTPClient":
        self.client = httpx.AsyncClient(timeout=self.timeout_s)
        return self
    
    async def __aexit__(self, *args: Any) -> None:
        if self.client:
            await self.client.aclose()