"""Test Client class"""

import os
import pytest
from specstory import Client, AsyncClient, SDKError


class TestClient:
    """Test synchronous client"""
    
    def test_client_requires_api_key(self):
        """Client should raise error when no API key provided"""
        # Remove env var
        original = os.environ.pop("SPECSTORY_API_KEY", None)
        
        try:
            with pytest.raises(ValueError, match="API key is required"):
                Client()
        finally:
            # Restore env var
            if original:
                os.environ["SPECSTORY_API_KEY"] = original
    
    def test_client_with_api_key(self):
        """Client should initialize with API key"""
        client = Client(api_key="test-key")
        assert client.projects is not None
        assert client.sessions is not None
        assert client.graphql is not None
    
    def test_client_with_env_var(self):
        """Client should use environment variable"""
        os.environ["SPECSTORY_API_KEY"] = "env-test-key"
        client = Client()
        assert client is not None
    
    def test_client_with_custom_base_url(self):
        """Client should accept custom base URL"""
        client = Client(
            api_key="test-key",
            base_url="https://custom.example.com"
        )
        assert client._http.base_url == "https://custom.example.com"
    
    def test_client_with_custom_timeout(self):
        """Client should accept custom timeout"""
        client = Client(
            api_key="test-key",
            timeout_s=60.0
        )
        assert client._http.timeout_s == 60.0


class TestAsyncClient:
    """Test asynchronous client"""
    
    def test_async_client_requires_api_key(self):
        """AsyncClient should raise error when no API key provided"""
        original = os.environ.pop("SPECSTORY_API_KEY", None)
        
        try:
            with pytest.raises(ValueError, match="API key is required"):
                AsyncClient()
        finally:
            if original:
                os.environ["SPECSTORY_API_KEY"] = original
    
    def test_async_client_with_api_key(self):
        """AsyncClient should initialize with API key"""
        client = AsyncClient(api_key="test-key")
        assert client.projects is not None
        assert client.sessions is not None
        assert client.graphql is not None
    
    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        """AsyncClient should work as context manager"""
        async with AsyncClient(api_key="test-key") as client:
            assert client is not None