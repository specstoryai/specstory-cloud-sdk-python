"""Projects resource implementation"""

from typing import Any, Dict, List, Optional

from ._base import BaseResource, AsyncBaseResource
from ..types_generated import (
    Project,
    ListProjectsResponse,
    UpdateProjectRequest,
    UpdateProjectResponse,
    DeleteProjectResponse,
)


class Projects(BaseResource):
    """Synchronous projects resource"""
    
    def list(self) -> List[Dict[str, Any]]:
        """List all projects accessible to the authenticated user
        
        Returns:
            List of project dictionaries
        """
        response = self._request(
            method="GET",
            path="/api/v1/projects"
        )
        
        # Parse response with Pydantic model
        parsed = ListProjectsResponse.model_validate(response)
        # Convert to dictionaries for easier use
        return [project.model_dump() for project in parsed.data.projects]
    
    def update(
        self,
        project_id: str,
        *,
        name: Optional[str] = None,
        icon: Optional[str] = None,
        color: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update a project's properties
        
        Args:
            project_id: The project ID
            name: New project name (optional)
            icon: New project icon (optional)
            color: New project color (optional)
            
        Returns:
            Dictionary with updated properties
        """
        # Build update request
        update_data = UpdateProjectRequest(
            name=name,
            icon=icon,
            color=color
        ).model_dump(exclude_none=True)
        
        response = self._request(
            method="PATCH",
            path=f"/api/v1/projects/{project_id}",
            body=update_data
        )
        
        # Parse and return data
        parsed = UpdateProjectResponse.model_validate(response)
        return parsed.data.model_dump(exclude_none=True)
    
    def delete(self, project_id: str) -> Dict[str, Any]:
        """Delete a project and all its sessions
        
        Args:
            project_id: The project ID to delete
            
        Returns:
            Dictionary with deletion details
        """
        response = self._request(
            method="DELETE",
            path=f"/api/v1/projects/{project_id}"
        )
        
        # Parse and return deletion info
        parsed = DeleteProjectResponse.model_validate(response)
        return {
            "deleted_project": parsed.data.deletedProject.model_dump(),
            "deleted_at": parsed.data.deletedAt.isoformat()
        }
    
    def get_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a project by name (convenience method)
        
        Args:
            name: The project name to search for
            
        Returns:
            The first project with matching name, or None if not found
            
        Example:
            project = client.projects.get_by_name('My Project')
            if project:
                print(f"Found project: {project['id']}")
        """
        projects = self.list()
        for project in projects:
            if project.get('name') == name:
                return project
        return None


class AsyncProjects(AsyncBaseResource):
    """Asynchronous projects resource"""
    
    async def list(self) -> List[Dict[str, Any]]:
        """List all projects accessible to the authenticated user
        
        Returns:
            List of project dictionaries
        """
        response = await self._request(
            method="GET",
            path="/api/v1/projects"
        )
        
        # Parse response with Pydantic model
        parsed = ListProjectsResponse.model_validate(response)
        # Convert to dictionaries for easier use
        return [project.model_dump() for project in parsed.data.projects]
    
    async def update(
        self,
        project_id: str,
        *,
        name: Optional[str] = None,
        icon: Optional[str] = None,
        color: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update a project's properties
        
        Args:
            project_id: The project ID
            name: New project name (optional)
            icon: New project icon (optional)
            color: New project color (optional)
            
        Returns:
            Dictionary with updated properties
        """
        # Build update request
        update_data = UpdateProjectRequest(
            name=name,
            icon=icon,
            color=color
        ).model_dump(exclude_none=True)
        
        response = await self._request(
            method="PATCH",
            path=f"/api/v1/projects/{project_id}",
            body=update_data
        )
        
        # Parse and return data
        parsed = UpdateProjectResponse.model_validate(response)
        return parsed.data.model_dump(exclude_none=True)
    
    async def delete(self, project_id: str) -> Dict[str, Any]:
        """Delete a project and all its sessions
        
        Args:
            project_id: The project ID to delete
            
        Returns:
            Dictionary with deletion details
        """
        response = await self._request(
            method="DELETE",
            path=f"/api/v1/projects/{project_id}"
        )
        
        # Parse and return deletion info
        parsed = DeleteProjectResponse.model_validate(response)
        return {
            "deleted_project": parsed.data.deletedProject.model_dump(),
            "deleted_at": parsed.data.deletedAt.isoformat()
        }