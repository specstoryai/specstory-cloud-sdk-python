#!/usr/bin/env python3
import os
import json
from datetime import datetime
from specstory import Client

def main():
    # Initialize the client with your API key
    api_key = os.getenv('SPECSTORY_API_KEY', '')
    
    with Client(api_key=api_key) as client:
        # List all projects
        print('Fetching projects...')
        projects = client.projects.list()
        print(f'Found {len(projects)} projects')
        
        if projects:
            project = projects[0]
            print(f'\nUsing project: {project["name"]} ({project["id"]})')
            
            # Create a new session
            print('\nCreating a new session...')
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
            print(f'Created session: {session["session_id"]}')
            
            # List sessions for the project
            print('\nListing sessions...')
            sessions = client.sessions.list(project['id'])
            print(f'Found {len(sessions)} sessions')
            
            # Read the created session
            session_id = session['session_id']
            print('\nReading session details...')
            details = client.sessions.read(project['id'], session_id)
            if details:
                print(f'Session name: {details["name"]}')
                print(f'Markdown size: {details["markdownSize"]} bytes')
                print(f'ETag: {details.get("etag", "N/A")}')
            
            # Check session metadata with HEAD request
            print('\nChecking session metadata...')
            metadata = client.sessions.head(project['id'], session_id)
            if metadata and metadata.get('exists'):
                print(f'Session exists: {metadata["exists"]}')
                print(f'Last modified: {metadata.get("last_modified", "N/A")}')
            
            # Delete the session
            print('\nDeleting session...')
            deleted = client.sessions.delete(project['id'], session_id)
            print(f'Session deleted: {deleted}')
            
            # Search sessions using GraphQL
            print('\nSearching sessions...')
            search_results = client.graphql.search('test', limit=10)
            print(f'Search found {search_results.get("total", 0)} results')

if __name__ == '__main__':
    main()