"""Projects resource implementation"""

from typing import Any, Dict, List

from ._base import BaseResource, AsyncBaseResource


class Projects(BaseResource):
    """Synchronous projects resource"""
    
    def list(self) -> List[Dict[str, Any]]:
        """List all projects"""
        # TODO: Add proper types after generation
        response = self._request(
            method="GET",
            path="/api/v1/projects"
        )
        return response.get("data", {}).get("projects", [])


class AsyncProjects(AsyncBaseResource):
    """Asynchronous projects resource"""
    
    async def list(self) -> List[Dict[str, Any]]:
        """List all projects"""
        # TODO: Add proper types after generation
        response = await self._request(
            method="GET",
            path="/api/v1/projects"
        )
        return response.get("data", {}).get("projects", [])