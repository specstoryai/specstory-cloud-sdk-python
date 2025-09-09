#!/usr/bin/env python3
"""Demonstrate developer experience features in SpecStory SDK"""

import os
import asyncio
from specstory import Client, AsyncClient, SDKError


def demonstrate_developer_experience():
    """Show developer experience features"""
    print('SpecStory SDK Developer Experience Features\n')
    
    # 1. Environment variable support
    print('1. Environment Variable Support:')
    
    # SDK automatically reads from SPECSTORY_API_KEY
    # Just don't pass api_key and it will use env var
    try:
        client_from_env = Client()  # Uses SPECSTORY_API_KEY env var
        print('   ✅ Client created using environment variables\n')
    except ValueError as e:
        print(f'   Set SPECSTORY_API_KEY: {e}\n')
    
    # 2. Flexible initialization
    print('2. Flexible Initialization:')
    
    api_key = os.getenv('SPECSTORY_API_KEY', 'your-api-key-here')
    
    # Various ways to create a client
    client = Client(api_key=api_key)
    client_with_timeout = Client(api_key=api_key, timeout_s=60.0)
    client_with_cache = Client(
        api_key=api_key,
        cache={'max_size': 200, 'default_ttl': 300.0}
    )
    print('   ✅ Multiple initialization options supported\n')
    
    # 3. Convenience methods
    print('3. Convenience Methods:')
    
    # Get project by name
    project = client.projects.get_by_name('Test Session')
    if project:
        print(f"   Found project by name: {project['id']}")
        
        # Write and read in one operation
        session = client.sessions.write_and_read(
            project['id'],
            {
                'markdown': '# Test Session',
                'raw_data': 'Test data',
                'name': 'DX Example Session',
                'metadata': {
                    'clientName': 'dx-example',
                    'tags': ['example', 'developer-experience']
                }
            }
        )
        print(f"   ✅ Created and read session: {session['id']}\n")
    
    # 4. Type hints and IDE support
    print('4. Python Type Hints:')
    print('   - Full type hints for better IDE support')
    print('   - Autocomplete for methods and parameters')
    print('   - Clear docstrings with examples')
    print('   - Compatible with mypy for type checking\n')
    
    # 5. Error handling with helpful messages
    print('5. Developer-Friendly Errors:')
    
    try:
        bad_client = Client(api_key='invalid-key')
        bad_client.projects.list()
    except SDKError as e:
        print(f'   ✅ Clear error: {e}')
        print(f'   - Status: {e.status}')
        print(f'   - Code: {e.code}')
        print(f'   - Suggestion: {e.suggestion}\n')
    
    # 6. Async support
    print('6. Async/Await Support:')
    print('   Using AsyncClient for concurrent operations...')
    
    async def async_example():
        async with AsyncClient(api_key=api_key) as async_client:
            # Concurrent requests
            projects = await async_client.projects.list()
            if projects:
                sessions = await async_client.sessions.list(projects[0]['id'])
                return len(sessions)
        return 0
    
    try:
        session_count = asyncio.run(async_example())
        print(f'   ✅ Found {session_count} sessions using async client\n')
    except:
        # Python 3.6 compatibility
        loop = asyncio.get_event_loop()
        session_count = loop.run_until_complete(async_example())
        print(f'   ✅ Found {session_count} sessions using async client\n')
    
    # 7. Pagination support
    print('7. Easy Pagination:')
    
    if project:
        print('   Iterating through sessions:')
        count = 0
        for session in client.sessions.list_paginated(project['id'], page_size=10):
            count += 1
            if count > 3:  # Just show first 3
                break
            print(f"   - {session['name']}")
        print()
    
    # 8. Single dependency
    print('8. Minimal Dependencies:')
    print('   - Only depends on httpx')
    print('   - Optional h2 for HTTP/2 support')
    print('   - Small installation footprint')
    print('   - Well-maintained dependencies\n')
    
    # 9. Flexible configuration
    print('9. Flexible Configuration:')
    
    configured_client = Client(
        api_key=api_key,
        base_url='https://cloud.specstory.com',
        timeout_s=60.0,  # 1 minute timeout
        cache={
            'max_size': 200,     # Cache up to 200 items
            'default_ttl': 300.0  # 5 minute TTL
        }
    )
    
    print('   ✅ Client configured with all options\n')
    
    # 10. Cache management
    print('10. Cache Management:')
    
    # Clear specific patterns
    configured_client.invalidate_cache(r'^session:')
    print('   ✅ Invalidated session cache')
    
    # Clear all cache
    configured_client.clear_cache()
    print('   ✅ Cleared entire cache\n')
    
    # Summary
    print('Developer Experience Summary:')
    print('- Environment variable support (SPECSTORY_API_KEY)')
    print('- Flexible initialization options')
    print('- Convenience methods (get_by_name, write_and_read)')
    print('- Full type hints for IDE support')
    print('- Clear, actionable error messages')
    print('- Async/await support with context managers')
    print('- Built-in pagination')
    print('- Single dependency (httpx)')
    print('- Configurable caching')
    print('- Python 3.7+ support')


if __name__ == '__main__':
    demonstrate_developer_experience()