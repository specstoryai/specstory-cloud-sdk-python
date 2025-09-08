"""SDK Error classes"""

from typing import Optional, Dict, Any


class SDKError(Exception):
    """Base error class for SDK exceptions"""
    
    def __init__(
        self,
        message: str,
        status: Optional[int] = None,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None
    ) -> None:
        super().__init__(message)
        self.status = status
        self.code = code
        self.details = details or {}
        self.request_id = request_id
    
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
    def from_response(cls, status: int, request_id: Optional[str] = None) -> "SDKError":
        """Create error from HTTP response status"""
        status_messages = {
            400: "Bad Request - The request was invalid",
            401: "Unauthorized - Invalid API key. Get a new key at https://cloud.specstory.com/api-keys",
            403: "Forbidden - You do not have permission to access this resource",
            404: "Not Found - The requested resource does not exist",
            429: "Too Many Requests - Rate limit exceeded. Please retry after some time",
            500: "Internal Server Error - Something went wrong on our end",
            502: "Bad Gateway - The server received an invalid response",
            503: "Service Unavailable - The service is temporarily unavailable",
            504: "Gateway Timeout - The server did not respond in time",
        }
        
        message = status_messages.get(status, f"HTTP Error {status}")
        return cls(message, status=status, request_id=request_id)