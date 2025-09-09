"""SpecStory Cloud SDK for Python"""

__version__ = "0.1.0"

from .client import Client
from ._errors import (
    SDKError,
    NetworkError,
    TimeoutError,
    ValidationError,
    AuthenticationError,
    PermissionError,
    NotFoundError,
    RateLimitError,
    ServerError,
    GraphQLError,
    UnknownError,
    SpecStoryError,
)

# For async support
try:
    from .client import AsyncClient
except ImportError:
    # AsyncClient requires Python 3.8+ with asyncio
    AsyncClient = None  # type: ignore

from ._cache import LRUCache, CacheEntry

__all__ = [
    "Client",
    "AsyncClient",
    "SDKError",
    "NetworkError",
    "TimeoutError", 
    "ValidationError",
    "AuthenticationError",
    "PermissionError",
    "NotFoundError",
    "RateLimitError",
    "ServerError",
    "GraphQLError",
    "UnknownError",
    "SpecStoryError",
    "LRUCache",
    "CacheEntry",
]