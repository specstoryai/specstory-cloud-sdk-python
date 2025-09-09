"""Pytest configuration and shared fixtures."""
import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from unittest.mock import Mock

import pytest
from httpx import Request, Response


# Test data factories are now fixtures below


class RequestTracker:
    """Track HTTP requests for test assertions."""
    
    def __init__(self):
        self.requests: List[Request] = []
    
    def add_request(self, request: Request):
        """Add a request to the tracker."""
        self.requests.append(request)
    
    def clear(self):
        """Clear all tracked requests."""
        self.requests.clear()
    
    def get_last(self) -> Optional[Request]:
        """Get the last request."""
        return self.requests[-1] if self.requests else None
    
    def get_by_url(self, url: str) -> Optional[Request]:
        """Get the first request matching the URL."""
        for req in self.requests:
            if url in str(req.url):
                return req
        return None
    
    def count(self) -> int:
        """Get the number of tracked requests."""
        return len(self.requests)


@pytest.fixture
def request_tracker():
    """Fixture to track HTTP requests."""
    return RequestTracker()


@pytest.fixture
def mock_httpx(httpx_mock):
    """Just return the httpx_mock fixture directly."""
    return httpx_mock


# Common response builders
class ResponseBuilder:
    """Helper to build common API responses."""
    
    @staticmethod
    def success(data: Any, headers: Optional[Dict[str, str]] = None) -> Response:
        """Build a successful API response."""
        response_headers = {"content-type": "application/json"}
        if headers:
            response_headers.update(headers)
        
        return Response(
            status_code=200,
            json={"success": True, "data": data},
            headers=response_headers,
        )
    
    @staticmethod
    def error(
        status_code: int, 
        code: str, 
        message: str,
        fields: Optional[Dict[str, List[str]]] = None
    ) -> Response:
        """Build an error API response."""
        error_data = {"code": code, "message": message}
        if fields:
            error_data["fields"] = fields
            
        return Response(
            status_code=status_code,
            json={"success": False, "error": error_data},
            headers={"content-type": "application/json"},
        )
    
    @staticmethod
    def graphql(
        data: Optional[Dict[str, Any]] = None,
        errors: Optional[List[Dict[str, Any]]] = None
    ) -> Response:
        """Build a GraphQL response."""
        response = {}
        if data is not None:
            response["data"] = data
        if errors:
            response["errors"] = errors
            
        return Response(
            status_code=200,
            json=response,
            headers={"content-type": "application/json"},
        )


@pytest.fixture
def response_builder():
    """Fixture for response builder."""
    return ResponseBuilder()


# API client fixture
@pytest.fixture
def api_key():
    """Test API key."""
    return "test-api-key"


@pytest.fixture
def base_url():
    """Test base URL."""
    return "https://cloud.specstory.com"


@pytest.fixture
def client(api_key):
    """Test client."""
    from specstory import Client
    return Client(api_key=api_key)


# Async test helpers
@pytest.fixture
def async_capture_error():
    """Helper to capture errors in async tests."""
    async def _capture(coro):
        try:
            await coro
            raise AssertionError("Expected coroutine to raise an exception")
        except Exception as e:
            return e
    return _capture


@pytest.fixture
def capture_error():
    """Helper to capture errors in sync tests."""
    def _capture(func, *args, **kwargs):
        try:
            func(*args, **kwargs)
            raise AssertionError("Expected function to raise an exception")
        except Exception as e:
            return e
    return _capture


@pytest.fixture
def create_project():
    """Fixture for test project factory."""
    def factory(overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a test project with optional overrides."""
        project = {
            "id": "test-project-id",
            "name": "Test Project",
            "ownerId": "test-owner-id",
            "icon": None,
            "color": None,
            "createdAt": "2025-01-09T12:00:00Z",
            "updatedAt": "2025-01-09T12:00:00Z",
        }
        if overrides:
            project.update(overrides)
        return project
    return factory


@pytest.fixture
def create_session_summary():
    """Fixture for test session summary factory."""
    def factory(overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a test session summary with optional overrides."""
        session = {
            "id": "test-session-id",
            "projectId": "test-project-id",
            "name": "Test Session",
            "createdAt": "2025-01-09T12:00:00Z",
            "updatedAt": "2025-01-09T12:00:00Z",
            "eventCount": 5,
        }
        if overrides:
            session.update(overrides)
        return session
    return factory


@pytest.fixture
def create_session_detail():
    """Fixture for test session detail factory."""
    def factory(overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a test session detail with optional overrides."""
        session = {
            "id": "test-session-id",
            "projectId": "test-project-id",
            "projectName": "Test Project",
            "name": "Test Session",
            "markdown": "# Test Session",
            "rawData": '{"test": true}',
            "createdAt": "2025-01-09T12:00:00Z",
            "updatedAt": "2025-01-09T12:00:00Z",
            "events": [
                {
                    "timestamp": "2025-01-09T12:00:00Z",
                    "type": "test",
                    "data": {"message": "Test event"},
                }
            ],
            "metadata": {
                "clientName": "test-client",
                "clientVersion": "1.0.0",
            },
        }
        if overrides:
            session.update(overrides)
        return session
    return factory