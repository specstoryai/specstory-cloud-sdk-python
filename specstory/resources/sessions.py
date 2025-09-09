"""Sessions resource implementation"""

from typing import Any, Dict, List, Optional, AsyncGenerator
from uuid import UUID

from ._base import BaseResource, AsyncBaseResource
from ..types_generated import (
    SessionSummary,
    SessionDetail,
    ListSessionsResponse,
    WriteSessionRequest,
    WriteSessionResponse,
    SessionDetailResponse,
    DeleteSessionResponse,
    SessionMetadata,
)


class Sessions(BaseResource):
    """Synchronous sessions resource"""
    
    def write(
        self,
        project_id: str,
        *,
        markdown: str,
        raw_data: str,
        name: str,
        project_name: Optional[str] = None,
        metadata: Optional[SessionMetadata] = None,
        idempotency_key: Optional[str] = None,
        timeout_ms: Optional[int] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Write (create or update) a session
        
        Args:
            project_id: The project ID
            markdown: Session markdown content
            raw_data: Raw session data
            name: Session name
            project_name: Project name (defaults to session name)
            metadata: Optional session metadata
            idempotency_key: Optional idempotency key for request
            timeout_ms: Optional timeout override
            session_id: Optional session ID (auto-generated if not provided)
            
        Returns:
            Dictionary with session ID, project ID, created_at, and optional ETag
        """
        # Build request body
        body = WriteSessionRequest(
            projectName=project_name or name,
            markdown=markdown,
            rawData=raw_data,
            name=name,
            metadata=metadata
        ).model_dump(exclude_none=True)
        
        # Generate session ID if not provided
        import uuid
        sid = session_id or str(uuid.uuid4())
        
        response, headers = self._request_with_headers(
            method="PUT",
            path=f"/api/v1/projects/{project_id}/sessions/{sid}",
            body=body,
            idempotency_key=idempotency_key,
            timeout_s=timeout_ms / 1000 if timeout_ms else None
        )
        
        # Parse response
        parsed = WriteSessionResponse.model_validate(response)
        result = {
            "session_id": parsed.data.sessionId,
            "project_id": parsed.data.projectId,
            "created_at": parsed.data.createdAt.isoformat()
        }
        
        # Add ETag if available
        if "etag" in headers:
            result["etag"] = headers["etag"]
            
        return result
    
    def list(
        self,
        project_id: str,
        *,
        page_size: Optional[int] = None,
        page_token: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List sessions for a project
        
        Args:
            project_id: The project ID
            page_size: Optional page size (not implemented yet)
            page_token: Optional page token (not implemented yet)
            
        Returns:
            List of session summaries with ETags
        """
        response = self._request(
            method="GET",
            path=f"/api/v1/projects/{project_id}/sessions"
        )
        
        # Parse response
        parsed = ListSessionsResponse.model_validate(response)
        return [session.model_dump() for session in parsed.data.sessions]
    
    def list_paginated(
        self,
        project_id: str,
        *,
        page_size: Optional[int] = None
    ) -> Any:
        """List sessions with pagination (generator)
        
        Args:
            project_id: The project ID
            page_size: Optional page size (not implemented yet)
            
        Yields:
            Session summaries one by one
        """
        # For now, yield all sessions at once
        # TODO: Implement proper cursor-based pagination when API supports it
        sessions = self.list(project_id, page_size=page_size)
        for session in sessions:
            yield session
    
    def read(
        self,
        project_id: str,
        session_id: str,
        *,
        if_none_match: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Read a specific session
        
        Args:
            project_id: The project ID
            session_id: The session ID
            if_none_match: Optional ETag for conditional request
            
        Returns:
            Session details with optional ETag, or None if not modified
        """
        headers = {"Accept": "application/json"}
        if if_none_match:
            headers["If-None-Match"] = if_none_match
        
        try:
            response, response_headers = self._request_with_headers(
                method="GET",
                path=f"/api/v1/projects/{project_id}/sessions/{session_id}",
                headers=headers
            )
            
            # Parse response
            parsed = SessionDetailResponse.model_validate(response)
            result = parsed.data.session.model_dump()
            
            # Add ETag if available
            if "etag" in response_headers:
                result["etag"] = response_headers["etag"]
                
            return result
            
        except Exception as e:
            # Return None for 304 Not Modified
            if hasattr(e, "status_code") and e.status_code == 304:
                return None
            raise
    
    def delete(self, project_id: str, session_id: str) -> bool:
        """Delete a session
        
        Args:
            project_id: The project ID
            session_id: The session ID
            
        Returns:
            True if successful
        """
        response = self._request(
            method="DELETE",
            path=f"/api/v1/projects/{project_id}/sessions/{session_id}"
        )
        
        # Parse response
        parsed = DeleteSessionResponse.model_validate(response)
        return parsed.success
    
    def head(
        self,
        project_id: str,
        session_id: str,
        *,
        if_none_match: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get session metadata without content
        
        Args:
            project_id: The project ID
            session_id: The session ID
            if_none_match: Optional ETag for conditional request
            
        Returns:
            Dictionary with metadata or None if not modified
        """
        headers = {}
        if if_none_match:
            headers["If-None-Match"] = if_none_match
        
        try:
            response, response_headers = self._request_with_headers(
                method="HEAD",
                path=f"/api/v1/projects/{project_id}/sessions/{session_id}",
                headers=headers
            )
            
            return {
                "exists": True,
                "etag": response_headers.get("etag"),
                "content_length": int(response_headers["content-length"])
                if "content-length" in response_headers else None,
                "last_modified": response_headers.get("last-modified"),
                "markdown_size": int(response_headers["x-markdown-size"])
                if "x-markdown-size" in response_headers else None,
                "raw_data_size": int(response_headers["x-raw-data-size"])
                if "x-raw-data-size" in response_headers else None,
            }
            
        except Exception as e:
            # Return None for 304 Not Modified
            if hasattr(e, "status_code") and e.status_code == 304:
                return None
            # Return exists: False for 404
            if hasattr(e, "status_code") and e.status_code == 404:
                return {"exists": False}
            raise
    
    def recent(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get recent sessions across all projects
        
        Args:
            limit: Number of sessions to return (1-100, default 5)
            
        Returns:
            List of recent session summaries
        """
        params = {}
        if limit is not None:
            params["limit"] = str(limit)
        
        response = self._request(
            method="GET",
            path="/api/v1/sessions/recent",
            params=params
        )
        
        # Parse response
        parsed = ListSessionsResponse.model_validate(response)
        return [session.model_dump() for session in parsed.data.sessions]


class AsyncSessions(AsyncBaseResource):
    """Asynchronous sessions resource"""
    
    async def write(
        self,
        project_id: str,
        *,
        markdown: str,
        raw_data: str,
        name: str,
        project_name: Optional[str] = None,
        metadata: Optional[SessionMetadata] = None,
        idempotency_key: Optional[str] = None,
        timeout_ms: Optional[int] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Write (create or update) a session
        
        Args:
            project_id: The project ID
            markdown: Session markdown content
            raw_data: Raw session data
            name: Session name
            project_name: Project name (defaults to session name)
            metadata: Optional session metadata
            idempotency_key: Optional idempotency key for request
            timeout_ms: Optional timeout override
            session_id: Optional session ID (auto-generated if not provided)
            
        Returns:
            Dictionary with session ID, project ID, created_at, and optional ETag
        """
        # Build request body
        body = WriteSessionRequest(
            projectName=project_name or name,
            markdown=markdown,
            rawData=raw_data,
            name=name,
            metadata=metadata
        ).model_dump(exclude_none=True)
        
        # Generate session ID if not provided
        import uuid
        sid = session_id or str(uuid.uuid4())
        
        response, headers = await self._request_with_headers(
            method="PUT",
            path=f"/api/v1/projects/{project_id}/sessions/{sid}",
            body=body,
            idempotency_key=idempotency_key,
            timeout_s=timeout_ms / 1000 if timeout_ms else None
        )
        
        # Parse response
        parsed = WriteSessionResponse.model_validate(response)
        result = {
            "session_id": parsed.data.sessionId,
            "project_id": parsed.data.projectId,
            "created_at": parsed.data.createdAt.isoformat()
        }
        
        # Add ETag if available
        if "etag" in headers:
            result["etag"] = headers["etag"]
            
        return result
    
    async def list(
        self,
        project_id: str,
        *,
        page_size: Optional[int] = None,
        page_token: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List sessions for a project
        
        Args:
            project_id: The project ID
            page_size: Optional page size (not implemented yet)
            page_token: Optional page token (not implemented yet)
            
        Returns:
            List of session summaries with ETags
        """
        response = await self._request(
            method="GET",
            path=f"/api/v1/projects/{project_id}/sessions"
        )
        
        # Parse response
        parsed = ListSessionsResponse.model_validate(response)
        return [session.model_dump() for session in parsed.data.sessions]
    
    async def list_paginated(
        self,
        project_id: str,
        *,
        page_size: Optional[int] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """List sessions with pagination (async generator)
        
        Args:
            project_id: The project ID
            page_size: Optional page size (not implemented yet)
            
        Yields:
            Session summaries one by one
        """
        # For now, yield all sessions at once
        # TODO: Implement proper cursor-based pagination when API supports it
        sessions = await self.list(project_id, page_size=page_size)
        for session in sessions:
            yield session
    
    async def read(
        self,
        project_id: str,
        session_id: str,
        *,
        if_none_match: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Read a specific session
        
        Args:
            project_id: The project ID
            session_id: The session ID
            if_none_match: Optional ETag for conditional request
            
        Returns:
            Session details with optional ETag, or None if not modified
        """
        headers = {"Accept": "application/json"}
        if if_none_match:
            headers["If-None-Match"] = if_none_match
        
        try:
            response, response_headers = await self._request_with_headers(
                method="GET",
                path=f"/api/v1/projects/{project_id}/sessions/{session_id}",
                headers=headers
            )
            
            # Parse response
            parsed = SessionDetailResponse.model_validate(response)
            result = parsed.data.session.model_dump()
            
            # Add ETag if available
            if "etag" in response_headers:
                result["etag"] = response_headers["etag"]
                
            return result
            
        except Exception as e:
            # Return None for 304 Not Modified
            if hasattr(e, "status_code") and e.status_code == 304:
                return None
            raise
    
    async def delete(self, project_id: str, session_id: str) -> bool:
        """Delete a session
        
        Args:
            project_id: The project ID
            session_id: The session ID
            
        Returns:
            True if successful
        """
        response = await self._request(
            method="DELETE",
            path=f"/api/v1/projects/{project_id}/sessions/{session_id}"
        )
        
        # Parse response
        parsed = DeleteSessionResponse.model_validate(response)
        return parsed.success
    
    async def head(
        self,
        project_id: str,
        session_id: str,
        *,
        if_none_match: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get session metadata without content
        
        Args:
            project_id: The project ID
            session_id: The session ID
            if_none_match: Optional ETag for conditional request
            
        Returns:
            Dictionary with metadata or None if not modified
        """
        headers = {}
        if if_none_match:
            headers["If-None-Match"] = if_none_match
        
        try:
            response, response_headers = await self._request_with_headers(
                method="HEAD",
                path=f"/api/v1/projects/{project_id}/sessions/{session_id}",
                headers=headers
            )
            
            return {
                "exists": True,
                "etag": response_headers.get("etag"),
                "content_length": int(response_headers["content-length"])
                if "content-length" in response_headers else None,
                "last_modified": response_headers.get("last-modified"),
                "markdown_size": int(response_headers["x-markdown-size"])
                if "x-markdown-size" in response_headers else None,
                "raw_data_size": int(response_headers["x-raw-data-size"])
                if "x-raw-data-size" in response_headers else None,
            }
            
        except Exception as e:
            # Return None for 304 Not Modified
            if hasattr(e, "status_code") and e.status_code == 304:
                return None
            # Return exists: False for 404
            if hasattr(e, "status_code") and e.status_code == 404:
                return {"exists": False}
            raise
    
    async def recent(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get recent sessions across all projects
        
        Args:
            limit: Number of sessions to return (1-100, default 5)
            
        Returns:
            List of recent session summaries
        """
        params = {}
        if limit is not None:
            params["limit"] = str(limit)
        
        response = await self._request(
            method="GET",
            path="/api/v1/sessions/recent",
            params=params
        )
        
        # Parse response
        parsed = ListSessionsResponse.model_validate(response)
        return [session.model_dump() for session in parsed.data.sessions]
