"""SpecStory Cloud SDK for Python"""

__version__ = "0.1.0"

from .client import Client
from ._errors import SDKError

# For async support
try:
    from .client import AsyncClient
except ImportError:
    # AsyncClient requires Python 3.8+ with asyncio
    AsyncClient = None  # type: ignore

__all__ = ["Client", "AsyncClient", "SDKError"]