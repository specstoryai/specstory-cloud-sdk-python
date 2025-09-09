#!/usr/bin/env python3
"""Demonstrate enhanced error handling in SpecStory SDK"""

import os
import json
from specstory import (
    Client,
    SDKError,
    NetworkError,
    TimeoutError,
    ValidationError,
    AuthenticationError,
    PermissionError,
    NotFoundError,
    RateLimitError,
    ServerError,
    GraphQLError,
)

def demonstrate_error_handling():
    """Show various error handling scenarios"""
    
    # Test with invalid API key
    invalid_client = Client(
        api_key='invalid-key',
        timeout_s=5.0
    )
    
    print('Testing error handling with invalid API key...\n')
    
    try:
        invalid_client.projects.list()
    except AuthenticationError as e:
        print('✅ Caught AuthenticationError:')
        print(f'   Message: {e}')
        print(f'   Status: {e.status}')
        print(f'   Code: {e.code}')
        print(f'   Suggestion: {e.suggestion}')
        print(f'   Request ID: {e.request_id}')
        print(f'   Duration: {e.context.duration_ms}ms')
        print(f'   Curl command: {e.get_curl_command()}')
        print()
    
    # Test network error (bad base URL)
    network_error_client = Client(
        api_key='test-key',
        base_url='https://invalid-domain-that-does-not-exist.com',
        timeout_s=3.0
    )
    
    print('Testing network error handling...\n')
    
    try:
        network_error_client.projects.list()
    except NetworkError as e:
        print('✅ Caught NetworkError:')
        print(f'   Message: {e}')
        print(f'   Code: {e.code}')
        print(f'   Suggestion: {e.suggestion}')
        if e.cause:
            print(f'   Cause: {type(e.cause).__name__}')
        print()
    
    # Test timeout error
    timeout_client = Client(
        api_key='test-key',
        timeout_s=0.001  # 1ms timeout to force timeout
    )
    
    print('Testing timeout error handling...\n')
    
    try:
        timeout_client.projects.list()
    except TimeoutError as e:
        print('✅ Caught TimeoutError:')
        print(f'   Message: {e}')
        print(f'   Timeout: {e.timeout_ms}ms')
        print(f'   Suggestion: {e.suggestion}')
        print()
    except NetworkError as e:
        # Sometimes shows as network error on very short timeouts
        print('✅ Caught NetworkError (timeout):')
        print(f'   Message: {e}')
        print()
    
    # Test 404 error with valid client
    api_key = os.getenv('SPECSTORY_API_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyXzJ0WFdLR2o3cWc3TTRGRHNUZnJZUVJJb3VmSiIsInR5cGUiOiJhcGkiLCJzY29wZSI6WyJyZWFkIiwid3JpdGUiXSwiaWF0IjoxNzU3MzY5MTYyfQ.yGyAXUWfsMysZC9O1FIXDGGzdy0FuzuMP5gv0pu34k8')
    client = Client(api_key=api_key)
    
    print('Testing 404 error handling...\n')
    
    try:
        client.sessions.read('invalid-project-id', 'invalid-session-id')
    except NotFoundError as e:
        print('✅ Caught NotFoundError:')
        print(f'   Message: {e}')
        print(f'   Status: {e.status}')
        print(f'   Suggestion: {e.suggestion}')
        print()
    
    # Test GraphQL error
    print('Testing GraphQL error handling...\n')
    
    try:
        # Invalid GraphQL query
        client.graphql.query("""
            query InvalidQuery {
                thisFieldDoesNotExist
            }
        """)
    except GraphQLError as e:
        print('✅ Caught GraphQLError:')
        print(f'   Message: {e}')
        print(f'   Errors: {e.errors}')
        print(f'   Query: {e.query[:50] if e.query else "None"}...')
        print()
    except SDKError as e:
        print('✅ Caught SDKError (GraphQL):')
        print(f'   Message: {e}')
        print(f'   Status: {e.status}')
        print()
    
    # Test rate limit error simulation
    print('Testing rate limit error info...\n')
    
    # Create a mock rate limit error
    from specstory._errors import ErrorContext
    from datetime import datetime
    
    context = ErrorContext(
        method='GET',
        url='https://api.example.com/test',
        timestamp=datetime.now()
    )
    
    rate_limit_error = RateLimitError(
        'Rate limit exceeded',
        retry_after_seconds=60,
        context=context
    )
    
    print('✅ Created RateLimitError:')
    print(f'   Message: {rate_limit_error}')
    print(f'   Retry after: {rate_limit_error.retry_after}')
    print(f'   Suggestion: {rate_limit_error.suggestion}')
    print()
    
    # Test error serialization
    print('Testing error serialization...\n')
    
    try:
        invalid_client.projects.list()
    except SDKError as e:
        serialized = e.to_dict()
        print('✅ Error serialized to dict:')
        print(json.dumps(serialized, indent=2, default=str))

if __name__ == '__main__':
    demonstrate_error_handling()