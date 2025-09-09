"""Unit tests for GraphQL resource."""
import json

import pytest
from httpx import Response

from specstory import Client
from specstory import GraphQLError


class TestGraphQL:
    """Test GraphQL resource operations."""
    
    @pytest.fixture
    def client(self, api_key):
        """Create a test client."""
        return Client(api_key=api_key)
    
    def test_search_sessions(self, client, mock_httpx):
        """Test searching sessions."""
        mock_results = {
            "searchSessions": {
                "total": 2,
                "pageInfo": {
                    "hasNextPage": False,
                    "hasPreviousPage": False,
                    "startCursor": "cursor1",
                    "endCursor": "cursor2",
                },
                "results": [
                    {
                        "id": "session-1",
                        "name": "Session 1",
                        "projectId": "project-1",
                        "projectName": "Project 1",
                        "rank": 0.95,
                        "highlights": {
                            "markdown": ["This is a <mark>test</mark> session"],
                        },
                    },
                    {
                        "id": "session-2",
                        "name": "Session 2", 
                        "projectId": "project-2",
                        "projectName": "Project 2",
                        "rank": 0.85,
                        "highlights": {
                            "markdown": ["Another <mark>test</mark> result"],
                        },
                    },
                ],
            }
        }
        
        mock_httpx.add_response(
            method="POST",
            url="https://cloud.specstory.com/api/v1/graphql",
            json={"data": mock_results},
            status_code=200,
        )
        
        results = client.graphql.search("test")
        
        assert results["total"] == 2
        assert len(results["results"]) == 2
        assert results["results"][0]["id"] == "session-1"
        assert results["results"][0]["rank"] == 0.95
        assert results["pageInfo"]["hasNextPage"] is False
        
        # Verify GraphQL query was sent
        request = mock_httpx.get_request()
        assert request.method == "POST"
        body = json.loads(request.content)
        assert "query SearchSessions" in body["query"]
        assert body["variables"]["query"] == "test"
    
    def test_search_with_filters(self, client, mock_httpx):
        """Test searching with filters."""
        mock_results = {
            "searchSessions": {
                "total": 1,
                "pageInfo": {
                    "hasNextPage": False,
                    "hasPreviousPage": False, 
                    "startCursor": None,
                    "endCursor": None,
                },
                "results": [],
            }
        }
        
        mock_httpx.add_response(
            method="POST",
            url="https://cloud.specstory.com/api/v1/graphql",
            json={"data": mock_results},
            status_code=200,
        )
        
        results = client.graphql.search(
            "error",
            filters={
                "projectIds": ["project-123", "project-456"],
                "startDate": "2025-01-01T00:00:00Z",
                "endDate": "2025-01-31T23:59:59Z",
            },
            limit=50,
        )
        
        assert results["total"] == 1
        assert len(results["results"]) == 0
        
        # Verify filters were included
        request = mock_httpx.get_request()
        body = json.loads(request.content)
        assert body["variables"]["filters"]["projectIds"] == ["project-123", "project-456"]
        assert body["variables"]["filters"]["startDate"] == "2025-01-01T00:00:00Z"
        assert body["variables"]["filters"]["endDate"] == "2025-01-31T23:59:59Z"
        assert body["variables"]["limit"] == 50
    
    def test_search_with_pagination(self, client, mock_httpx):
        """Test pagination with cursor."""
        mock_results = {
            "searchSessions": {
                "total": 100,
                "pageInfo": {
                    "hasNextPage": True,
                    "hasPreviousPage": True,
                    "startCursor": "start",
                    "endCursor": "end",
                },
                "results": [],
            }
        }
        
        mock_httpx.add_response(
            method="POST",
            url="https://cloud.specstory.com/api/v1/graphql",
            json={"data": mock_results},
            status_code=200,
        )
        
        client.graphql.search(
            "test",
            filters={"cursor": "previous-cursor"},
            limit=20,
        )
        
        request = mock_httpx.get_request()
        body = json.loads(request.content)
        assert body["variables"]["filters"]["cursor"] == "previous-cursor"
        assert body["variables"]["limit"] == 20
    
    def test_custom_query(self, client, mock_httpx):
        """Test executing custom GraphQL query."""
        custom_query = """
            query GetSessionDetails($id: ID!) {
                session(id: $id) {
                    id
                    name
                    createdAt
                    events {
                        timestamp
                        type
                    }
                }
            }
        """
        
        mock_response = {
            "session": {
                "id": "session-123",
                "name": "Custom Session",
                "createdAt": "2025-01-09T12:00:00Z",
                "events": [
                    {"timestamp": "2025-01-09T12:00:00Z", "type": "start"},
                    {"timestamp": "2025-01-09T12:00:01Z", "type": "log"},
                ],
            }
        }
        
        mock_httpx.add_response(
            method="POST",
            url="https://cloud.specstory.com/api/v1/graphql",
            json={"data": mock_response},
            status_code=200,
        )
        
        result = client.graphql.query(custom_query, {"id": "session-123"})
        
        assert result["session"]["id"] == "session-123"
        assert result["session"]["name"] == "Custom Session"
        assert len(result["session"]["events"]) == 2
        
        # Verify custom query was sent
        request = mock_httpx.get_request()
        body = json.loads(request.content)
        assert body["query"] == custom_query
        assert body["variables"]["id"] == "session-123"
    
    def test_mutation(self, client, mock_httpx):
        """Test executing mutations."""
        mutation = """
            mutation UpdateSession($id: ID!, $name: String!) {
                updateSession(id: $id, name: $name) {
                    id
                    name
                    updatedAt
                }
            }
        """
        
        mock_response = {
            "updateSession": {
                "id": "session-123",
                "name": "Updated Name",
                "updatedAt": "2025-01-09T13:00:00Z",
            }
        }
        
        mock_httpx.add_response(
            method="POST",
            url="https://cloud.specstory.com/api/v1/graphql",
            json={"data": mock_response},
            status_code=200,
        )
        
        result = client.graphql.query(
            mutation,
            {"id": "session-123", "name": "Updated Name"}
        )
        
        assert result["updateSession"]["name"] == "Updated Name"
    
    def test_graphql_errors(self, client, mock_httpx, capture_error):
        """Test handling GraphQL errors."""
        mock_httpx.add_response(
            method="POST",
            url="https://cloud.specstory.com/api/v1/graphql",
            json={
                "errors": [
                    {
                        "message": "Invalid search query",
                        "extensions": {
                            "code": "BAD_USER_INPUT",
                        },
                    }
                ]
            },
            status_code=200,
        )
        
        error = capture_error(client.graphql.search, "")
        
        assert isinstance(error, GraphQLError)
        assert "GraphQL query failed" in error.message
        assert len(error.errors) == 1
        assert error.errors[0]["extensions"]["code"] == "BAD_USER_INPUT"
    
    def test_network_error(self, client, mock_httpx, capture_error):
        """Test handling network errors."""
        # httpx_mock will raise a connection error if no response is added
        
        error = capture_error(client.graphql.search, "test")
        
        assert "Request failed" in str(error)
    
    def test_partial_data_with_errors(self, client, mock_httpx, capture_error):
        """Test handling both data and errors in response."""
        mock_httpx.add_response(
            method="POST",
            url="https://cloud.specstory.com/api/v1/graphql",
            json={
                "data": {
                    "searchSessions": {
                        "total": 1,
                        "pageInfo": {
                            "hasNextPage": False,
                            "hasPreviousPage": False,
                        },
                        "results": [
                            {"id": "partial-result", "name": "Partial"}
                        ],
                    }
                },
                "errors": [
                    {
                        "message": "Some sessions could not be accessed",
                        "path": ["searchSessions", "results", 1],
                    }
                ],
            },
            status_code=200,
        )
        
        # GraphQL can return partial data with errors
        error = capture_error(client.graphql.search, "test")
        
        assert isinstance(error, GraphQLError)
        assert len(error.errors) == 1
        assert "Some sessions could not be accessed" in error.errors[0]["message"]
    
    def test_search_no_results(self, client, mock_httpx):
        """Test search with no results."""
        mock_results = {
            "searchSessions": {
                "total": 0,
                "pageInfo": {
                    "hasNextPage": False,
                    "hasPreviousPage": False,
                    "startCursor": None,
                    "endCursor": None,
                },
                "results": [],
            }
        }
        
        mock_httpx.add_response(
            method="POST",
            url="https://cloud.specstory.com/api/v1/graphql",
            json={"data": mock_results},
            status_code=200,
        )
        
        results = client.graphql.search("nonexistent")
        
        assert results["total"] == 0
        assert len(results["results"]) == 0
        assert results["pageInfo"]["hasNextPage"] is False