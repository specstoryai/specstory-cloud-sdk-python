"""SDK Error classes"""

from typing import Optional, Dict, Any, List
from datetime import datetime
import json


class ErrorContext:
    """Context information for errors"""
    def __init__(
        self,
        method: Optional[str] = None,
        url: Optional[str] = None,
        request_id: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        duration_ms: Optional[int] = None,
        retry_count: Optional[int] = None
    ):
        self.method = method
        self.url = url
        self.request_id = request_id
        self.timestamp = timestamp or datetime.now()
        self.duration_ms = duration_ms
        self.retry_count = retry_count
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "method": self.method,
            "url": self.url,
            "request_id": self.request_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "duration_ms": self.duration_ms,
            "retry_count": self.retry_count
        }


class ErrorDetails:
    """Additional error details"""
    def __init__(
        self,
        code: Optional[str] = None,
        details: Optional[Any] = None,
        suggestion: Optional[str] = None
    ):
        self.code = code
        self.details = details
        self.suggestion = suggestion
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "code": self.code,
            "details": self.details,
            "suggestion": self.suggestion
        }


class SDKError(Exception):
    """Base error class for SDK exceptions"""
    
    def __init__(
        self,
        message: str,
        status: Optional[int] = None,
        details: Optional[ErrorDetails] = None,
        context: Optional[ErrorContext] = None
    ) -> None:
        super().__init__(message)
        self.status = status
        self.details = details or ErrorDetails()
        self.context = context or ErrorContext()
    
    @property
    def request_id(self) -> Optional[str]:
        """Get request ID from context"""
        return self.context.request_id
    
    @property
    def code(self) -> Optional[str]:
        """Get error code from details"""
        return self.details.code
    
    @property
    def suggestion(self) -> Optional[str]:
        """Get suggestion from details"""
        return self.details.suggestion
    
    def get_curl_command(self) -> Optional[str]:
        """Get a curl command to reproduce the request"""
        if not self.context.method or not self.context.url:
            return None
        
        parts = ["curl"]
        parts.extend(["-X", self.context.method])
        parts.append(f"'{self.context.url}'")
        
        if self.context.request_id:
            parts.extend(["-H", f"'x-request-id: {self.context.request_id}'"])
        
        return " ".join(parts)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for JSON serialization"""
        return {
            "type": self.__class__.__name__,
            "message": str(self),
            "status": self.status,
            "details": self.details.to_dict(),
            "context": self.context.to_dict()
        }
    
    def __repr__(self) -> str:
        parts = [f"{self.__class__.__name__}({self.args[0]!r}"]
        if self.status:
            parts.append(f"status={self.status}")
        if self.code:
            parts.append(f"code={self.code!r}")
        if self.request_id:
            parts.append(f"request_id={self.request_id!r}")
        return ", ".join(parts) + ")"
    
    @classmethod
    def from_response(
        cls, 
        status: int, 
        request_id: Optional[str] = None,
        context: Optional[ErrorContext] = None,
        retry_after: Optional[str] = None
    ) -> "SDKError":
        """Create error from HTTP response status"""
        if context:
            context.request_id = request_id or context.request_id
        else:
            context = ErrorContext(request_id=request_id)
        
        # Map status codes to specific error types
        if status == 400:
            return ValidationError("The request was invalid", context)
        elif status == 401:
            return AuthenticationError(
                "Invalid API key",
                ErrorDetails(
                    code="authentication_error",
                    suggestion="Get a new API key at https://cloud.specstory.com/api-keys"
                ),
                context
            )
        elif status == 403:
            return PermissionError(
                "You do not have permission to access this resource",
                context
            )
        elif status == 404:
            return NotFoundError(
                "The requested resource does not exist",
                context
            )
        elif status == 429:
            retry_seconds = None
            if retry_after:
                try:
                    retry_seconds = int(retry_after)
                except ValueError:
                    pass
            return RateLimitError(
                "Rate limit exceeded",
                retry_seconds,
                context
            )
        elif status in (500, 502, 503, 504):
            return ServerError(f"Server error: {status}", status, context)
        else:
            return UnknownError(f"Unexpected error: {status}", status, context)


class NetworkError(SDKError):
    """Network-related errors (connection failures, timeouts)"""
    def __init__(self, message: str, cause: Optional[Exception] = None, context: Optional[ErrorContext] = None):
        super().__init__(
            message,
            None,
            ErrorDetails(
                code="network_error",
                suggestion="Check your internet connection and try again",
                details={"cause": str(cause)} if cause else None
            ),
            context
        )
        self.cause = cause


class ValidationError(SDKError):
    """Validation errors for bad requests"""
    def __init__(self, message: str, context: Optional[ErrorContext] = None, fields: Optional[Dict[str, List[str]]] = None):
        super().__init__(
            message,
            400,
            ErrorDetails(
                code="validation_error",
                details=fields,
                suggestion="Check the request parameters and try again"
            ),
            context
        )
        self.fields = fields


class AuthenticationError(SDKError):
    """Authentication errors"""
    def __init__(self, message: str, details: Optional[ErrorDetails] = None, context: Optional[ErrorContext] = None):
        super().__init__(
            message,
            401,
            details or ErrorDetails(code="authentication_error"),
            context
        )


class PermissionError(SDKError):
    """Permission/authorization errors"""
    def __init__(self, message: str, context: Optional[ErrorContext] = None):
        super().__init__(
            message,
            403,
            ErrorDetails(
                code="permission_error",
                suggestion="Ensure you have the necessary permissions for this resource"
            ),
            context
        )


class NotFoundError(SDKError):
    """Resource not found errors"""
    def __init__(self, message: str, context: Optional[ErrorContext] = None):
        super().__init__(
            message,
            404,
            ErrorDetails(
                code="not_found",
                suggestion="Verify the resource ID and try again"
            ),
            context
        )


class RateLimitError(SDKError):
    """Rate limiting errors with retry information"""
    def __init__(self, message: str, retry_after_seconds: Optional[int] = None, context: Optional[ErrorContext] = None):
        self.retry_after = datetime.fromtimestamp(
            datetime.now().timestamp() + retry_after_seconds
        ) if retry_after_seconds else None
        
        super().__init__(
            message,
            429,
            ErrorDetails(
                code="rate_limit",
                details={"retry_after_seconds": retry_after_seconds},
                suggestion=f"Retry after {self.retry_after.isoformat()}" if self.retry_after else "Reduce request frequency and try again"
            ),
            context
        )


class ServerError(SDKError):
    """Server errors (5xx)"""
    def __init__(self, message: str, status: int, context: Optional[ErrorContext] = None):
        super().__init__(
            message,
            status,
            ErrorDetails(
                code="server_error",
                suggestion="The server encountered an error. Please try again later"
            ),
            context
        )


class GraphQLError(SDKError):
    """GraphQL-specific errors"""
    def __init__(
        self, 
        message: str,
        errors: List[Dict[str, Any]],
        query: Optional[str] = None,
        variables: Optional[Dict[str, Any]] = None,
        context: Optional[ErrorContext] = None
    ):
        super().__init__(
            message,
            200,  # GraphQL errors typically return 200
            ErrorDetails(
                code="graphql_error",
                details={"errors": errors, "query": query, "variables": variables},
                suggestion="Check the GraphQL query syntax and variables"
            ),
            context
        )
        self.errors = errors
        self.query = query
        self.variables = variables


class UnknownError(SDKError):
    """Unknown/unexpected errors"""
    def __init__(self, message: str, status: Optional[int] = None, context: Optional[ErrorContext] = None):
        super().__init__(
            message,
            status,
            ErrorDetails(
                code="unknown_error",
                suggestion="An unexpected error occurred. Please report this issue"
            ),
            context
        )


class TimeoutError(SDKError):
    """Timeout errors"""
    def __init__(self, message: str, timeout_ms: int, context: Optional[ErrorContext] = None):
        super().__init__(
            message,
            None,
            ErrorDetails(
                code="timeout",
                details={"timeout_ms": timeout_ms},
                suggestion=f"Request timed out after {timeout_ms}ms. Try increasing the timeout"
            ),
            context
        )
        self.timeout_ms = timeout_ms


# Re-export for backwards compatibility
SpecStoryError = SDKError

__all__ = [
    "SDKError",
    "NetworkError",
    "TimeoutError",
    "ValidationError", 
    "AuthenticationError",
    "PermissionError",
    "NotFoundError",
    "RateLimitError",
    "ServerError",
    "GraphQLError",
    "UnknownError",
    "SpecStoryError",
    "ErrorContext",
    "ErrorDetails",
]