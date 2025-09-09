"""Simple unit tests for Projects resource."""
import pytest

from specstory import Client
from specstory import NotFoundError, ValidationError, AuthenticationError


class TestProjects:
    """Test Projects resource operations."""
    
    def test_list_projects(self, httpx_mock):
        """Test listing all projects."""
        # Mock response
        httpx_mock.add_response(
            method="GET",
            url="https://cloud.specstory.com/api/v1/projects",
            json={
                "success": True,
                "data": {
                    "projects": [
                        {
                            "id": "project-1",
                            "name": "Project 1",
                            "ownerId": "owner-1",
                            "createdAt": "2025-01-09T12:00:00Z",
                            "updatedAt": "2025-01-09T12:00:00Z"
                        },
                        {
                            "id": "project-2",
                            "name": "Project 2",
                            "ownerId": "owner-2",
                            "createdAt": "2025-01-09T12:00:00Z",
                            "updatedAt": "2025-01-09T12:00:00Z"
                        },
                    ],
                    "total": 2
                }
            },
        )
        
        # Create client and call method
        client = Client(api_key="test-api-key")
        projects = client.projects.list()
        
        # Assertions
        assert len(projects) == 2
        assert projects[0]["id"] == "project-1"
        assert projects[1]["id"] == "project-2"
    
    def test_list_projects_error(self, httpx_mock, capture_error):
        """Test handling API errors."""
        httpx_mock.add_response(
            method="GET",
            url="https://cloud.specstory.com/api/v1/projects",
            json={
                "success": False,
                "error": {"code": "authentication_error", "message": "Invalid API key"}
            },
            status_code=401,
        )
        
        client = Client(api_key="bad-key")
        error = capture_error(client.projects.list)
        
        assert isinstance(error, AuthenticationError)
        assert error.status == 401
    
    def test_update_project(self, httpx_mock):
        """Test updating a project."""
        project_id = "project-123"
        
        httpx_mock.add_response(
            method="PATCH",
            url=f"https://cloud.specstory.com/api/v1/projects/{project_id}",
            json={"success": True, "data": {"name": "Updated Name"}},
        )
        
        client = Client(api_key="test-api-key")
        result = client.projects.update(project_id, name="Updated Name")
        
        assert result["name"] == "Updated Name"
    
    def test_delete_project(self, httpx_mock):
        """Test deleting a project."""
        project_id = "project-123"
        
        httpx_mock.add_response(
            method="DELETE",
            url=f"https://cloud.specstory.com/api/v1/projects/{project_id}",
            json={
                "success": True,
                "data": {
                    "deletedProject": {
                        "id": project_id,
                        "name": "Deleted Project",
                        "ownerId": "owner-123",
                        "createdAt": "2025-01-09T12:00:00Z",
                        "updatedAt": "2025-01-09T12:00:00Z"
                    },
                    "deletedAt": "2025-01-09T12:30:00Z"
                }
            },
        )
        
        client = Client(api_key="test-api-key")
        result = client.projects.delete(project_id)
        
        assert "deleted_project" in result
        assert result["deleted_project"]["id"] == project_id
        assert result["deleted_at"] == "2025-01-09T12:30:00+00:00"