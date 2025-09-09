#!/usr/bin/env python3
import os
import json
from datetime import datetime
from specstory import Client

def main():
    output = []
    
    def log(message):
        """Log to both console and output list"""
        print(message)
        output.append(message)
    # Initialize the client with your API key
    api_key = os.getenv('SPECSTORY_API_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyXzJ0WFdLR2o3cWc3TTRGRHNUZnJZUVJJb3VmSiIsInR5cGUiOiJhcGkiLCJzY29wZSI6WyJyZWFkIiwid3JpdGUiXSwiaWF0IjoxNzU3MzY5MTYyfQ.yGyAXUWfsMysZC9O1FIXDGGzdy0FuzuMP5gv0pu34k8')
    
    try:
        client = Client(api_key=api_key)
        # List all projects
        log('Fetching projects...')
        projects = client.projects.list()
        log(f'Found {len(projects)} projects')
        
        if projects:
            project = projects[0]
            log(f'\nUsing project: {project["name"]} ({project["id"]})')
            
            # Create a new session
            log('\nCreating a new session...')
            session = client.sessions.write(
                project['id'],
                name='Test Session',
                markdown='# Test Session\n\nThis is a test session content.',
                raw_data=json.dumps({'test': True}),
                metadata={
                    'clientName': 'example-app',
                    'tags': ['test', 'demo'],
                },
                idempotency_key='test-session-001'
            )
            log(f'Created session: {session["session_id"]}')
            
            # List sessions for the project
            log('\nListing sessions...')
            sessions = client.sessions.list(project['id'])
            log(f'Found {len(sessions)} sessions')
            
            # Read the created session
            session_id = session['session_id']
            log('\nReading session details...')
            details = client.sessions.read(project['id'], session_id)
            if details:
                log(f'Session name: {details["name"]}')
                log(f'Markdown size: {details["markdownSize"]} bytes')
                log(f'ETag: {details.get("etag", "N/A")}')
            
            # Check session metadata with HEAD request
            log('\nChecking session metadata...')
            metadata = client.sessions.head(project['id'], session_id)
            if metadata and metadata.get('exists'):
                log(f'Session exists: {metadata["exists"]}')
                log(f'Last modified: {metadata.get("last_modified", "N/A")}')
            
            # Delete the session
            log('\nDeleting session...')
            deleted = client.sessions.delete(project['id'], session_id)
            log(f'Session deleted: {deleted}')
            
            # Search sessions using GraphQL
            log('\nSearching sessions...')
            search_results = client.graphql.search('test', limit=10)
            log(f'Search found {search_results.get("total", 0)} results')

    except Exception as e:
        print(f'Error: {e}')
        output.append(f'\nError: {e}')
    
    # Write output to file
    output_path = os.path.join(os.path.dirname(__file__), 'python-sdk-output.txt')
    with open(output_path, 'w') as f:
        f.write('\n'.join(output))
    print(f'\nOutput written to: {output_path}')

if __name__ == '__main__':
    main()