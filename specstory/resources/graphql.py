"""GraphQL resource implementation"""

from typing import Any, Dict, List, Optional

from ._base import BaseResource, AsyncBaseResource


class GraphQL(BaseResource):
    """Synchronous GraphQL resource"""
    
    def search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 200
    ) -> Dict[str, Any]:
        """Search sessions using GraphQL"""
        # TODO: Add proper types after generation
        graphql_query = """
            query SearchSessions($query: String!, $filters: SessionFilters, $limit: Int) {
                searchSessions(query: $query, filters: $filters, limit: $limit) {
                    total
                    results {
                        id
                        name
                        projectId
                        rank
                        metadata {
                            clientName
                            tags
                        }
                    }
                }
            }
        """
        
        variables = {"query": query, "limit": limit}
        if filters:
            variables["filters"] = filters
        
        response = self._request(
            method="POST",
            path="/api/v1/graphql",
            body={
                "query": graphql_query,
                "variables": variables
            }
        )
        
        return response.get("data", {}).get("searchSessions", {})
    
    def query(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a raw GraphQL query"""
        return self._request(
            method="POST",
            path="/api/v1/graphql",
            body={
                "query": query,
                "variables": variables or {}
            }
        )


class AsyncGraphQL(AsyncBaseResource):
    """Asynchronous GraphQL resource"""
    
    async def search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 200
    ) -> Dict[str, Any]:
        """Search sessions using GraphQL"""
        # TODO: Add proper types after generation
        graphql_query = """
            query SearchSessions($query: String!, $filters: SessionFilters, $limit: Int) {
                searchSessions(query: $query, filters: $filters, limit: $limit) {
                    total
                    results {
                        id
                        name
                        projectId
                        rank
                        metadata {
                            clientName
                            tags
                        }
                    }
                }
            }
        """
        
        variables = {"query": query, "limit": limit}
        if filters:
            variables["filters"] = filters
        
        response = await self._request(
            method="POST",
            path="/api/v1/graphql",
            body={
                "query": graphql_query,
                "variables": variables
            }
        )
        
        return response.get("data", {}).get("searchSessions", {})
    
    async def query(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a raw GraphQL query"""
        return await self._request(
            method="POST",
            path="/api/v1/graphql",
            body={
                "query": query,
                "variables": variables or {}
            }
        )