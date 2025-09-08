"""Sessions resource implementation"""

from typing import Any, Dict, List, Optional

from ._base import BaseResource, AsyncBaseResource


class Sessions(BaseResource):
    """Synchronous sessions resource"""
    
    def write(
        self,
        project_id: str,
        name: str,
        markdown: str,
        raw_data: str,
        metadata: Optional[Dict[str, Any]] = None,
        project_name: Optional[str] = None,
        idempotency_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """Write a new session"""
        # TODO: Add proper types after generation
        body = {
            "name": name,
            "markdown": markdown,
            "rawData": raw_data,
        }
        
        if metadata:
            body["metadata"] = metadata
        
        if project_name:
            body["projectName"] = project_name
        
        return self._request(
            method="PUT",
            path=f"/api/v1/projects/{project_id}/sessions",
            body=body,
            idempotency_key=idempotency_key
        )
    
    def list(self, project_id: str) -> List[Dict[str, Any]]:
        """List sessions for a project"""
        # TODO: Add proper types after generation
        response = self._request(
            method="GET",
            path=f"/api/v1/projects/{project_id}/sessions"
        )
        return response.get("data", {}).get("sessions", [])
    
    def read(
        self,
        project_id: str,
        session_id: str,
        if_none_match: Optional[str] = None
    ) -> Dict[str, Any]:
        """Read a session"""
        # TODO: Add proper types after generation
        headers = {}
        if if_none_match:
            headers["If-None-Match"] = if_none_match
        
        return self._request(
            method="GET",
            path=f"/api/v1/projects/{project_id}/sessions/{session_id}",
            headers=headers if headers else None
        )


class AsyncSessions(AsyncBaseResource):
    """Asynchronous sessions resource"""
    
    async def write(
        self,
        project_id: str,
        name: str,
        markdown: str,
        raw_data: str,
        metadata: Optional[Dict[str, Any]] = None,
        project_name: Optional[str] = None,
        idempotency_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """Write a new session"""
        # TODO: Add proper types after generation
        body = {
            "name": name,
            "markdown": markdown,
            "rawData": raw_data,
        }
        
        if metadata:
            body["metadata"] = metadata
        
        if project_name:
            body["projectName"] = project_name
        
        return await self._request(
            method="PUT",
            path=f"/api/v1/projects/{project_id}/sessions",
            body=body,
            idempotency_key=idempotency_key
        )
    
    async def list(self, project_id: str) -> List[Dict[str, Any]]:
        """List sessions for a project"""
        # TODO: Add proper types after generation
        response = await self._request(
            method="GET",
            path=f"/api/v1/projects/{project_id}/sessions"
        )
        return response.get("data", {}).get("sessions", [])
    
    async def read(
        self,
        project_id: str,
        session_id: str,
        if_none_match: Optional[str] = None
    ) -> Dict[str, Any]:
        """Read a session"""
        # TODO: Add proper types after generation
        headers = {}
        if if_none_match:
            headers["If-None-Match"] = if_none_match
        
        return await self._request(
            method="GET",
            path=f"/api/v1/projects/{project_id}/sessions/{session_id}",
            headers=headers if headers else None
        )