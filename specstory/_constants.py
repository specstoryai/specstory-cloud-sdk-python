"""Internal constants for the SDK"""

SDK_VERSION = "0.1.0"
SDK_LANGUAGE = "python"

DEFAULT_TIMEOUT_S = 30.0
DEFAULT_MAX_RETRIES = 3
DEFAULT_BASE_DELAY_MS = 200

IDEMPOTENT_METHODS = frozenset(["GET", "PUT", "DELETE", "HEAD"])

RETRY_STATUS_CODES = frozenset([
    408,  # Request Timeout
    429,  # Too Many Requests
    500,  # Internal Server Error
    502,  # Bad Gateway
    503,  # Service Unavailable
    504,  # Gateway Timeout
])