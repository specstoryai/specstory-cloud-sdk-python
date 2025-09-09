"""GraphQL resource implementation"""

from typing import Any, Dict, List, Optional, cast

from ._base import BaseResource, AsyncBaseResource
from .._errors import GraphQLError


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
        
        # Check for GraphQL errors
        if "errors" in response and response["errors"]:
            raise GraphQLError(
                "GraphQL query failed",
                response["errors"],
                graphql_query,
                variables
            )
        
        # Check if data is present
        if "data" not in response or response["data"] is None:
            raise GraphQLError(
                "No data returned from GraphQL query",
                [],
                graphql_query,
                variables
            )
        
        return cast(Dict[str, Any], response["data"]["searchSessions"])
    
    def query(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a raw GraphQL query"""
        result = self._request(
            method="POST",
            path="/api/v1/graphql",
            body={
                "query": query,
                "variables": variables or {}
            }
        )
        
        # Check for GraphQL errors
        if "errors" in result and result["errors"]:
            raise GraphQLError(
                "GraphQL query failed",
                result["errors"],
                query,
                variables
            )
        
        return cast(Dict[str, Any], result)


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
        
        # Check for GraphQL errors
        if "errors" in response and response["errors"]:
            raise GraphQLError(
                "GraphQL query failed",
                response["errors"],
                graphql_query,
                variables
            )
        
        # Check if data is present
        if "data" not in response or response["data"] is None:
            raise GraphQLError(
                "No data returned from GraphQL query",
                [],
                graphql_query,
                variables
            )
        
        return cast(Dict[str, Any], response["data"]["searchSessions"])
    
    async def query(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a raw GraphQL query"""
        result = await self._request(
            method="POST",
            path="/api/v1/graphql",
            body={
                "query": query,
                "variables": variables or {}
            }
        )
        
        # Check for GraphQL errors
        if "errors" in result and result["errors"]:
            raise GraphQLError(
                "GraphQL query failed",
                result["errors"],
                query,
                variables
            )
        
        return cast(Dict[str, Any], result)