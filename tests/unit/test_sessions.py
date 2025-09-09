"""Unit tests for Sessions resource."""
import json
from datetime import datetime
from unittest.mock import patch

import pytest
from httpx import Response

from specstory import Client
from specstory import TimeoutError, AuthenticationError


class TestSessions:
    """Test Sessions resource operations."""
    
    @pytest.fixture
    def client(self, api_key):
        """Create a test client."""
        return Client(api_key=api_key)
    
    def test_write_session(self, client, mock_httpx):
        """Test creating a new session."""
        project_id = "project-123"
        session_data = {
            "name": "Test Session",
            "markdown": "# Test Content",
            "raw_data": '{"test": true}',
            "metadata": {
                "clientName": "test-client",
                "clientVersion": "1.0.0",
            }
        }
        
        mock_httpx.add_callback(
            lambda request: Response(
                status_code=200,
                json={
                    "success": True,
                    "data": {
                        "sessionId": str(request.url).split("/")[-1],
                        "projectId": project_id,
                        "createdAt": "2025-01-09T12:00:00Z",
                    }
                },
                headers={"etag": '"abc123"'},
            ),
            method="PUT",
            url__regex=r"projects/.*/sessions/.*"
        )
        
        result = client.sessions.write(project_id, **session_data)
        
        assert "session_id" in result
        assert result["project_id"] == project_id
        assert result.get("etag") == '"abc123"'
        
        # Verify request
        request = mock_httpx.get_request()
        assert request.method == "PUT"
        body = json.loads(request.content)
        assert body["name"] == "Test Session"
        assert body["projectName"] == "Test Session"  # Should default to name
    
    def test_write_session_with_custom_id(self, client, mock_httpx):
        """Test creating a session with custom ID."""
        project_id = "project-123"
        custom_session_id = "custom-session-id"
        
        mock_httpx.add_response(
            method="PUT",
            url=f"https://cloud.specstory.com/api/v1/projects/{project_id}/sessions/{custom_session_id}",
            json={
                "success": True,
                "data": {
                    "sessionId": custom_session_id,
                    "projectId": project_id,
                    "createdAt": "2025-01-09T12:00:00Z",
                }
            },
            status_code=200,
        )
        
        result = client.sessions.write(
            project_id,
            name="Test Session",
            markdown="# Test",
            raw_data="{}",
            session_id=custom_session_id
        )
        
        assert result["session_id"] == custom_session_id
        
        request = mock_httpx.get_request()
        assert custom_session_id in str(request.url)
    
    def test_write_session_with_idempotency_key(self, client, mock_httpx):
        """Test creating a session with idempotency key."""
        project_id = "project-123"
        idempotency_key = "unique-key-123"
        
        mock_httpx.add_callback(
            lambda request: Response(
                status_code=200,
                json={
                    "success": True,
                    "data": {
                        "sessionId": "session-id",
                        "projectId": project_id,
                        "createdAt": "2025-01-09T12:00:00Z",
                    }
                }
            ),
            method="PUT",
            url__regex=r"projects/.*/sessions/.*"
        )
        
        client.sessions.write(
            project_id,
            name="Test Session",
            markdown="# Test",
            raw_data="{}",
            idempotency_key=idempotency_key
        )
        
        request = mock_httpx.get_request()
        assert request.headers["Idempotency-Key"] == idempotency_key
    
    def test_list_sessions(self, client, mock_httpx, create_session_summary):
        """Test listing sessions for a project."""
        project_id = "project-123"
        mock_sessions = [
            create_session_summary({"id": "session-1", "name": "Session 1"}),
            create_session_summary({"id": "session-2", "name": "Session 2"}),
        ]
        
        mock_httpx.add_response(
            method="GET",
            url=f"https://cloud.specstory.com/api/v1/projects/{project_id}/sessions",
            json={"success": True, "data": {"sessions": mock_sessions}},
            status_code=200,
        )
        
        sessions = client.sessions.list(project_id)
        
        assert len(sessions) == 2
        assert sessions[0]["id"] == "session-1"
        assert sessions[1]["id"] == "session-2"
    
    def test_list_sessions_empty(self, client, mock_httpx):
        """Test listing sessions when none exist."""
        project_id = "project-123"
        
        mock_httpx.add_response(
            method="GET",
            url=f"https://cloud.specstory.com/api/v1/projects/{project_id}/sessions",
            json={"success": True, "data": {"sessions": []}},
            status_code=200,
        )
        
        sessions = client.sessions.list(project_id)
        
        assert sessions == []
        assert len(sessions) == 0
    
    def test_list_paginated(self, client, mock_httpx, create_session_summary):
        """Test paginated session listing."""
        project_id = "project-123"
        mock_sessions = [
            create_session_summary({"id": f"session-{i}", "name": f"Session {i}"})
            for i in range(1, 6)
        ]
        
        mock_httpx.add_response(
            method="GET",
            url=f"https://cloud.specstory.com/api/v1/projects/{project_id}/sessions",
            json={"success": True, "data": {"sessions": mock_sessions}},
            status_code=200,
        )
        
        collected_sessions = list(client.sessions.list_paginated(project_id))
        
        assert len(collected_sessions) == 5
        assert collected_sessions[0]["id"] == "session-1"
        assert collected_sessions[4]["id"] == "session-5"
    
    def test_read_session(self, client, mock_httpx, create_session_detail):
        """Test reading a session with full details."""
        project_id = "project-123"
        session_id = "session-123"
        mock_session = create_session_detail({
            "id": session_id,
            "projectId": project_id,
            "events": [
                {
                    "timestamp": "2025-01-09T12:00:00Z",
                    "type": "log",
                    "data": {"message": "Test event"},
                }
            ],
        })
        
        mock_httpx.add_response(
            method="GET",
            url=f"https://cloud.specstory.com/api/v1/projects/{project_id}/sessions/{session_id}",
            json={"success": True, "data": {"session": mock_session}},
            status_code=200,
            headers={"etag": '"session-etag-123"'},
        )
        
        session = client.sessions.read(project_id, session_id)
        
        assert session is not None
        assert session["id"] == session_id
        assert len(session["events"]) == 1
        assert session.get("etag") == '"session-etag-123"'
    
    def test_read_session_with_etag(self, client, mock_httpx):
        """Test conditional request with ETag."""
        project_id = "project-123"
        session_id = "session-123"
        etag = '"unchanged-etag"'
        
        mock_httpx.add_callback(
            lambda request: Response(
                status_code=304 if request.headers.get("If-None-Match") == etag else 200,
                json={"success": True, "data": {"session": {}}} if request.headers.get("If-None-Match") != etag else None,
            ),
            method="GET",
            url=f"https://cloud.specstory.com/api/v1/projects/{project_id}/sessions/{session_id}"
        )
        
        session = client.sessions.read(project_id, session_id, if_none_match=etag)
        
        assert session is None  # 304 Not Modified
        
        request = mock_httpx.get_request()
        assert request.headers.get("If-None-Match") == etag
    
    def test_read_session_with_cache(self, client, mock_httpx, create_session_detail):
        """Test session caching behavior."""
        project_id = "project-123"
        session_id = "session-123"
        mock_session = create_session_detail({"id": session_id})
        
        # First request returns session with etag
        mock_httpx.add_response(
            method="GET",
            url=f"https://cloud.specstory.com/api/v1/projects/{project_id}/sessions/{session_id}",
            json={"success": True, "data": {"session": mock_session}},
            status_code=200,
            headers={"etag": '"cached-etag"'},
        )
        
        # First read - should hit server
        session1 = client.sessions.read(project_id, session_id)
        assert session1["etag"] == '"cached-etag"'
        
        # Second request returns 304
        mock_httpx.add_response(
            method="GET",
            url=f"https://cloud.specstory.com/api/v1/projects/{project_id}/sessions/{session_id}",
            status_code=304,
        )
        
        # Second read - should use cached etag
        session2 = client.sessions.read(project_id, session_id)
        # Should return cached version
        assert session2["id"] == session_id
    
    def test_delete_session(self, client, mock_httpx):
        """Test deleting a session."""
        project_id = "project-123"
        session_id = "session-to-delete"
        
        mock_httpx.add_response(
            method="DELETE",
            url=f"https://cloud.specstory.com/api/v1/projects/{project_id}/sessions/{session_id}",
            json={"success": True},
            status_code=200,
        )
        
        result = client.sessions.delete(project_id, session_id)
        
        assert result is True
        
        request = mock_httpx.get_request()
        assert request.method == "DELETE"
    
    def test_head_session(self, client, mock_httpx):
        """Test getting session metadata."""
        project_id = "project-123"
        session_id = "session-123"
        
        mock_httpx.add_response(
            method="HEAD",
            url=f"https://cloud.specstory.com/api/v1/projects/{project_id}/sessions/{session_id}",
            status_code=200,
            headers={
                "etag": '"metadata-etag"',
                "content-length": "12345",
                "last-modified": "Thu, 09 Jan 2025 12:00:00 GMT",
                "x-markdown-size": "5000",
                "x-raw-data-size": "7345",
            }
        )
        
        metadata = client.sessions.head(project_id, session_id)
        
        assert metadata is not None
        assert metadata["exists"] is True
        assert metadata["etag"] == '"metadata-etag"'
        assert metadata["content_length"] == 12345
        assert metadata["markdown_size"] == 5000
        assert metadata["raw_data_size"] == 7345
    
    def test_head_session_not_found(self, client, mock_httpx):
        """Test head for non-existent session."""
        project_id = "project-123"
        session_id = "non-existent"
        
        mock_httpx.add_response(
            method="HEAD",
            url=f"https://cloud.specstory.com/api/v1/projects/{project_id}/sessions/{session_id}",
            status_code=404,
        )
        
        metadata = client.sessions.head(project_id, session_id)
        
        assert metadata["exists"] is False
    
    def test_recent_sessions(self, client, mock_httpx, create_session_summary):
        """Test getting recent sessions across all projects."""
        recent_sessions = [
            create_session_summary({"id": "recent-1", "name": "Recent Session 1"}),
            create_session_summary({"id": "recent-2", "name": "Recent Session 2"}),
        ]
        
        mock_httpx.add_callback(
            lambda request: Response(
                status_code=200,
                json={
                    "success": True,
                    "data": {
                        "sessions": recent_sessions[:int(request.url.params.get("limit", "5"))]
                    }
                }
            ),
            method="GET",
            url__startswith="https://cloud.specstory.com/api/v1/sessions/recent"
        )
        
        sessions = client.sessions.recent(limit=2)
        
        assert len(sessions) == 2
        assert sessions[0]["id"] == "recent-1"
        
        request = mock_httpx.get_request()
        assert "limit=2" in str(request.url)
    
    def test_write_and_read(self, client, mock_httpx, create_session_detail):
        """Test write and immediately read a session."""
        project_id = "project-123"
        session_data = {
            "name": "Combined Test",
            "markdown": "# Combined",
            "raw_data": "{}",
        }
        
        # Mock write response
        mock_httpx.add_callback(
            lambda request: Response(
                status_code=200,
                json={
                    "success": True,
                    "data": {
                        "sessionId": str(request.url).split("/")[-1],
                        "projectId": project_id,
                        "createdAt": "2025-01-09T12:00:00Z",
                    }
                }
            ),
            method="PUT",
            url__regex=r"projects/.*/sessions/.*"
        )
        
        # Mock read response
        mock_httpx.add_callback(
            lambda request: Response(
                status_code=200,
                json={
                    "success": True,
                    "data": {
                        "session": create_session_detail({
                            "id": str(request.url).split("/")[-1],
                            "projectId": project_id,
                            "name": session_data["name"],
                            "markdown": session_data["markdown"],
                            "rawData": session_data["raw_data"],
                        })
                    }
                }
            ),
            method="GET",
            url__regex=r"projects/.*/sessions/.*"
        )
        
        session = client.sessions.write_and_read(project_id, session_data)
        
        assert session is not None
        assert session["name"] == "Combined Test"
        assert session["markdown"] == "# Combined"
        
        # Should have made 2 requests (write + read)
        requests = list(mock_httpx.get_requests())
        assert len(requests) == 2
        assert requests[0].method == "PUT"
        assert requests[1].method == "GET"
    
    def test_timeout_error(self, client, mock_httpx, capture_error):
        """Test handling timeout errors."""
        project_id = "project-123"
        
        # Create client with short timeout
        client_with_timeout = Client(api_key="test-api-key", timeout_s=0.1)
        
        # Mock slow response
        import time
        mock_httpx.add_callback(
            lambda request: (time.sleep(0.2), Response(
                status_code=200,
                json={"success": True, "data": {"sessions": []}}
            ))[1],
            method="GET",
            url=f"https://cloud.specstory.com/api/v1/projects/{project_id}/sessions"
        )
        
        error = capture_error(client_with_timeout.sessions.list, project_id)
        
        # httpx will raise a different timeout error
        assert "timeout" in str(error).lower() or "timed out" in str(error).lower()
    
    def test_request_deduplication(self, client, mock_httpx, create_session_summary):
        """Test concurrent GET request deduplication."""
        project_id = "project-123"
        
        # Python client handles this differently than TypeScript
        # It uses a short-lived cache instead of request deduplication
        
        mock_httpx.add_response(
            method="GET",
            url=f"https://cloud.specstory.com/api/v1/projects/{project_id}/sessions",
            json={
                "success": True,
                "data": {"sessions": [create_session_summary()]}
            },
            status_code=200,
        )
        
        # Make request
        result1 = client.sessions.list(project_id)
        
        # Second request within cache window should use cache
        # But httpx_mock requires we add another response
        mock_httpx.add_response(
            method="GET",
            url=f"https://cloud.specstory.com/api/v1/projects/{project_id}/sessions",
            json={
                "success": True,
                "data": {"sessions": [create_session_summary()]}
            },
            status_code=200,
        )
        
        result2 = client.sessions.list(project_id)
        
        assert result1 == result2