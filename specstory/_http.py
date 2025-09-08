"""HTTP client implementation with retry logic"""

import asyncio
import json
import random
import time
from typing import Optional, Dict, Any, Union, TypeVar, Literal

import httpx

from ._errors import SDKError
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
    
    def __init__(self, api_key: str, base_url: str, timeout_s: float) -> None:
        self.api_key = api_key
        self.base_url = base_url
        self.timeout_s = timeout_s
        self.client = httpx.Client(timeout=timeout_s)
    
    def request(
        self,
        method: Method,
        path: str,
        body: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout_s: Optional[float] = None,
        idempotency_key: Optional[str] = None,
        retries: Optional[int] = None,
    ) -> Any:
        """Make HTTP request with retry logic"""
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
                response = self.client.request(
                    method=method,
                    url=url,
                    json=body,
                    headers=request_headers,
                    timeout=timeout,
                )
                
                request_id = response.headers.get("x-request-id")
                
                if response.status_code >= 400:
                    error = SDKError.from_response(response.status_code, request_id)
                    
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
                
                return response.json()
                
            except httpx.RequestError as e:
                last_error = e
                
                if attempt < max_retries and self._should_retry(method):
                    self._sleep_with_backoff(attempt)
                    continue
                
                raise SDKError(
                    f"Request failed: {str(e)}",
                    code="network_error",
                    details={"original_error": str(e)},
                )
        
        raise SDKError(
            f"Request failed after {max_retries + 1} attempts",
            code="max_retries_exceeded",
            details={"last_error": str(last_error) if last_error else None},
        )
    
    def _should_retry(self, method: str) -> bool:
        return method in IDEMPOTENT_METHODS
    
    def _sleep_with_backoff(self, attempt: int) -> None:
        jitter = random.random() * 0.1  # 0-100ms jitter
        delay = (DEFAULT_BASE_DELAY_MS / 1000) * (2 ** attempt) + jitter
        time.sleep(delay)
    
    def __enter__(self) -> "HTTPClient":
        return self
    
    def __exit__(self, *args) -> None:
        self.client.close()


class AsyncHTTPClient:
    """Asynchronous HTTP client with retry logic"""
    
    def __init__(self, api_key: str, base_url: str, timeout_s: float) -> None:
        self.api_key = api_key
        self.base_url = base_url
        self.timeout_s = timeout_s
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
    ) -> Any:
        """Make async HTTP request with retry logic"""
        if not self.client:
            self.client = httpx.AsyncClient(timeout=self.timeout_s)
        
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
                    json=body,
                    headers=request_headers,
                    timeout=timeout,
                )
                
                request_id = response.headers.get("x-request-id")
                
                if response.status_code >= 400:
                    error = SDKError.from_response(response.status_code, request_id)
                    
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
                
                return response.json()
                
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
        
        raise SDKError(
            f"Request failed after {max_retries + 1} attempts",
            code="max_retries_exceeded",
            details={"last_error": str(last_error) if last_error else None},
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
    
    async def __aexit__(self, *args) -> None:
        if self.client:
            await self.client.aclose()