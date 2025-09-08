#!/usr/bin/env python3
import os
import json
import asyncio
from specstory import AsyncClient

async def main():
    # Initialize the async client with your API key
    api_key = os.getenv('SPECSTORY_API_KEY', '')
    
    async with AsyncClient(api_key=api_key) as client:
        # List all projects
        print('Fetching projects...')
        projects = await client.projects.list()
        print(f'Found {len(projects)} projects')
        
        if projects:
            project = projects[0]
            print(f'\nUsing project: {project["name"]} ({project["id"]})')
            
            # Create multiple sessions concurrently
            print('\nCreating multiple sessions concurrently...')
            session_tasks = []
            for i in range(3):
                task = client.sessions.write(
                    project['id'],
                    name=f'Async Session {i}',
                    markdown=f'# Async Session {i}\n\nCreated with async client.',
                    raw_data=json.dumps({'index': i, 'async': True}),
                    metadata={
                        'clientName': 'async-example',
                        'tags': ['async', 'demo'],
                    },
                    idempotency_key=f'async-session-{i}'
                )
                session_tasks.append(task)
            
            sessions = await asyncio.gather(*session_tasks)
            print(f'Created {len(sessions)} sessions')
            
            # List sessions using pagination (async generator)
            print('\nListing sessions with async pagination...')
            count = 0
            async for session in client.sessions.list_paginated(project['id']):
                count += 1
                print(f'  - {session["name"]} (ID: {session["id"]})')
                if count >= 5:  # Limit output
                    break
            
            # Read multiple sessions concurrently
            print('\nReading sessions concurrently...')
            read_tasks = []
            for session in sessions[:2]:
                task = client.sessions.read(project['id'], session['session_id'])
                read_tasks.append(task)
            
            details_list = await asyncio.gather(*read_tasks)
            for details in details_list:
                if details:
                    print(f'  - {details["name"]}: {details["markdownSize"]} bytes')
            
            # Delete all created sessions
            print('\nDeleting sessions...')
            delete_tasks = []
            for session in sessions:
                task = client.sessions.delete(project['id'], session['session_id'])
                delete_tasks.append(task)
            
            results = await asyncio.gather(*delete_tasks)
            print(f'Deleted {sum(results)} sessions')
            
            # Execute a custom GraphQL query
            print('\nExecuting custom GraphQL query...')
            custom_query = """
                query GetProjectSessions($projectId: String!, $limit: Int) {
                    project(id: $projectId) {
                        id
                        name
                        sessions(limit: $limit) {
                            total
                            items {
                                id
                                name
                                createdAt
                            }
                        }
                    }
                }
            """
            result = await client.graphql.query(
                custom_query,
                variables={'projectId': project['id'], 'limit': 5}
            )
            print('Query result:', json.dumps(result, indent=2))

if __name__ == '__main__':
    asyncio.run(main())