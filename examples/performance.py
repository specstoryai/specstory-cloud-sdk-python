#!/usr/bin/env python3
"""Demonstrate performance optimizations in SpecStory SDK"""

import os
import time
import asyncio
from specstory import Client, AsyncClient


def demonstrate_sync_performance():
    """Show performance features with sync client"""
    api_key = os.getenv('SPECSTORY_API_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyXzJ0WFdLR2o3cWc3TTRGRHNUZnJZUVJJb3VmSiIsInR5cGUiOiJhcGkiLCJzY29wZSI6WyJyZWFkIiwid3JpdGUiXSwiaWF0IjoxNzU3MzY5MTYyfQ.yGyAXUWfsMysZC9O1FIXDGGzdy0FuzuMP5gv0pu34k8')
    client = Client(api_key=api_key)
    
    print('Testing connection reuse with sequential requests...\n')
    
    start_time = time.time()
    projects = None
    for i in range(5):
        projects = client.projects.list()
    duration = (time.time() - start_time) * 1000
    
    print(f'✅ Made 5 sequential requests in {duration:.0f}ms')
    print(f'   Found {len(projects)} projects')
    print('   Connection pooling enabled faster subsequent requests\n')
    
    print('Testing request caching (1 second cache)...\n')
    
    # First request
    start_time = time.time()
    result1 = client.projects.list()
    duration1 = (time.time() - start_time) * 1000
    
    # Second request (should be cached)
    start_time = time.time()
    result2 = client.projects.list()
    duration2 = (time.time() - start_time) * 1000
    
    print(f'✅ First request: {duration1:.0f}ms')
    print(f'✅ Cached request: {duration2:.0f}ms')
    print(f'   Cache reduced response time by {(duration1 - duration2) / duration1 * 100:.0f}%\n')


async def demonstrate_async_performance():
    """Show performance features with async client"""
    api_key = os.getenv('SPECSTORY_API_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyXzJ0WFdLR2o3cWc3TTRGRHNUZnJZUVJJb3VmSiIsInR5cGUiOiJhcGkiLCJzY29wZSI6WyJyZWFkIiwid3JpdGUiXSwiaWF0IjoxNzU3MzY5MTYyfQ.yGyAXUWfsMysZC9O1FIXDGGzdy0FuzuMP5gv0pu34k8')
    
    async with AsyncClient(api_key=api_key) as client:
        print('Testing parallel async requests...\n')
        
        start_time = time.time()
        results = await asyncio.gather(
            client.projects.list(),
            client.projects.list(),
            client.projects.list(),
            client.projects.list(),
            client.projects.list(),
        )
        duration = (time.time() - start_time) * 1000
        
        print(f'✅ Made 5 parallel requests in {duration:.0f}ms')
        print(f'   All returned {len(results[0])} projects')
        print('   Async concurrency maximizes throughput\n')
        
        print('Testing different endpoints in parallel...\n')
        
        start_time = time.time()
        projects, sessions, recent = await asyncio.gather(
            client.projects.list(),
            client.sessions.list(results[0][0]['id']),
            client.sessions.recent(5),
        )
        duration = (time.time() - start_time) * 1000
        
        print(f'✅ Made 3 different requests in parallel: {duration:.0f}ms')
        print(f'   Projects: {len(projects)}')
        print(f'   Sessions: {len(sessions)}')
        print(f'   Recent sessions: {len(recent)}')


def main():
    """Run all performance demonstrations"""
    print('SpecStory SDK Performance Optimizations\n')
    print('=' * 50 + '\n')
    
    demonstrate_sync_performance()
    
    print('=' * 50 + '\n')
    
    asyncio.run(demonstrate_async_performance())
    
    print('\n' + '=' * 50 + '\n')
    print('Performance optimizations summary:')
    print('- HTTP/2 support for improved throughput')
    print('- Connection pooling with keep-alive (30s)')
    print('- Request caching for GET requests (1s TTL)')
    print('- Configurable connection limits')
    print('- Built-in retry logic with exponential backoff')
    print('- Async support for maximum concurrency')
    print('- Single dependency (httpx) keeps installation fast')


if __name__ == '__main__':
    main()