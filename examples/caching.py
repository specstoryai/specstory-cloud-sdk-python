#!/usr/bin/env python3
"""Demonstrate caching capabilities in SpecStory SDK"""

import os
import time
import asyncio
from specstory import Client, AsyncClient


def demonstrate_sync_caching():
    """Show caching features with sync client"""
    api_key = os.getenv('SPECSTORY_API_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyXzJ0WFdLR2o3cWc3TTRGRHNUZnJZUVJJb3VmSiIsInR5cGUiOiJhcGkiLCJzY29wZSI6WyJyZWFkIiwid3JpdGUiXSwiaWF0IjoxNzU3MzY5MTYyfQ.yGyAXUWfsMysZC9O1FIXDGGzdy0FuzuMP5gv0pu34k8')
    
    # Create client with custom cache settings
    client = Client(
        api_key=api_key,
        cache={
            "max_size": 50,       # Store up to 50 items
            "default_ttl": 60.0   # 1 minute default TTL
        }
    )
    
    print('SpecStory SDK Python Caching Examples\n')
    
    # Get a project to work with
    projects = client.projects.list()
    if not projects:
        print('No projects found. Create a project first.')
        return
    
    project_id = projects[0]['id']
    
    # Get sessions to work with
    sessions = client.sessions.list(project_id, page_size=1)
    if not sessions:
        print('No sessions found. Create a session first.')
        return
    
    session_id = sessions[0]['id']
    
    print(f"Using project: {projects[0]['name']} ({project_id})")
    print(f"Using session: {sessions[0]['name']} ({session_id})\n")
    
    # Example 1: Automatic ETag handling
    print('1. Automatic ETag caching:')
    print('   First request fetches from server...')
    start_time = time.time()
    session1 = client.sessions.read(project_id, session_id)
    duration = (time.time() - start_time) * 1000
    print(f"   ✅ Fetched in {duration:.0f}ms, ETag: {session1.get('etag') if session1 else 'None'}")
    
    print('   Second request uses cached ETag...')
    start_time = time.time()
    session2 = client.sessions.read(project_id, session_id)
    duration = (time.time() - start_time) * 1000
    print(f"   ✅ Response in {duration:.0f}ms (304 Not Modified if unchanged)")
    print(f"   Same data: {session1 and session2 and session1['id'] == session2['id']}\n")
    
    # Example 2: Manual ETag usage
    print('2. Manual ETag handling:')
    etag = session1.get('etag') if session1 else None
    if etag:
        print(f"   Checking with ETag: {etag}")
        session3 = client.sessions.read(project_id, session_id, if_none_match=etag)
        if session3 is None:
            print('   ✅ Session not modified (304 response)')
        else:
            print('   ✅ Session was modified, new data received')
    
    # Example 3: Cache invalidation
    print('\n3. Cache management:')
    
    # Clear specific pattern
    print('   Invalidating session cache...')
    client.invalidate_cache(r'^session:')
    print('   ✅ Session cache cleared')
    
    # Clear all cache
    print('   Clearing entire cache...')
    client.clear_cache()
    print('   ✅ All cache cleared\n')
    
    # Example 4: Efficient polling with ETags
    print('4. Efficient polling example:')
    print('   Polling for changes (5 times, 1 second intervals)...')
    
    last_etag = None
    unchanged_count = 0
    
    for i in range(5):
        time.sleep(1)
        
        result = client.sessions.read(project_id, session_id, if_none_match=last_etag)
        
        if result is None:
            unchanged_count += 1
            print(f'   Poll {i + 1}: No changes (using cached data)')
        else:
            print(f'   Poll {i + 1}: Data updated!')
            last_etag = result.get('etag')
            unchanged_count = 0
    
    print(f'\n   ✅ Polling complete: {unchanged_count} unchanged responses saved bandwidth\n')
    
    # Example 5: Disable caching
    print('5. Disable caching:')
    no_cache_client = Client(
        api_key=api_key,
        cache=False  # Disable caching entirely
    )
    
    print('   Client created with caching disabled')
    uncached_session = no_cache_client.sessions.read(project_id, session_id)
    print('   ✅ Always fetches fresh data\n')


async def demonstrate_async_caching():
    """Show caching features with async client"""
    api_key = os.getenv('SPECSTORY_API_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyXzJ0WFdLR2o3cWc3TTRGRHNUZnJZUVJJb3VmSiIsInR5cGUiOiJhcGkiLCJzY29wZSI6WyJyZWFkIiwid3JpdGUiXSwiaWF0IjoxNzU3MzY5MTYyfQ.yGyAXUWfsMysZC9O1FIXDGGzdy0FuzuMP5gv0pu34k8')
    
    async with AsyncClient(api_key=api_key) as client:
        print('6. Async concurrent caching:')
        
        projects = await client.projects.list()
        if not projects:
            return
            
        project_id = projects[0]['id']
        sessions = await client.sessions.list(project_id, page_size=1)
        if not sessions:
            return
            
        session_id = sessions[0]['id']
        
        # Multiple concurrent requests benefit from caching
        print('   Making 5 concurrent requests...')
        start_time = time.time()
        
        results = await asyncio.gather(*[
            client.sessions.read(project_id, session_id)
            for _ in range(5)
        ])
        
        duration = (time.time() - start_time) * 1000
        print(f'   ✅ Completed in {duration:.0f}ms')
        print('   All requests benefit from shared cache')


def main():
    """Run all caching demonstrations"""
    demonstrate_sync_caching()
    
    # Run async example
    try:
        asyncio.run(demonstrate_async_caching())
    except:
        # Python 3.6 compatibility
        loop = asyncio.get_event_loop()
        loop.run_until_complete(demonstrate_async_caching())
    
    # Summary
    print('\nCaching benefits:')
    print('- Reduces API calls with automatic ETag handling')
    print('- Improves response times for unchanged data')
    print('- Enables efficient polling patterns')
    print('- Configurable cache size and TTL')
    print('- Works with both sync and async clients')
    print('- Can be disabled when fresh data is critical')


if __name__ == '__main__':
    main()