#!/usr/bin/env python3
import os
import json
import re
from dotenv import load_dotenv
from specstory import Client

load_dotenv()

def count_prompts_in_content(content):
    """
    Count prompts in session content
    Looks for SpecStory markdown format: _**User**_ markers
    """
    if not content:
        return 0
    
    prompt_count = 0
    
    # First try to parse as JSON if it looks like JSON
    if isinstance(content, str) and content.strip().startswith('{'):
        try:
            data = json.loads(content)
            # Check for common chat structures in JSON
            if isinstance(data, dict):
                if 'messages' in data:
                    messages = data['messages']
                    if isinstance(messages, list):
                        prompt_count = sum(1 for msg in messages 
                                         if isinstance(msg, dict) and 
                                         msg.get('role') in ['user', 'human', 'prompt'])
                elif 'prompts' in data:
                    if isinstance(data['prompts'], list):
                        prompt_count = len(data['prompts'])
                elif 'conversation' in data:
                    conv = data['conversation']
                    if isinstance(conv, list):
                        prompt_count = sum(1 for item in conv 
                                         if isinstance(item, dict) and 
                                         item.get('type') in ['user', 'prompt', 'question'])
                if prompt_count > 0:
                    return prompt_count
        except (json.JSONDecodeError, TypeError):
            pass
    
    # Parse SpecStory markdown format
    # Looking for patterns like: _**User**_ or **User** or ### User
    if isinstance(content, str):
        # Count occurrences of user prompt markers in SpecStory format
        # Pattern 1: _**User**_ (SpecStory format)
        user_pattern1 = content.count('_**User**_')
        
        # Pattern 2: Alternative formats that might be used
        user_pattern2 = len(re.findall(r'(?:^|\n)\*\*User\*\*', content, re.MULTILINE))
        user_pattern3 = len(re.findall(r'(?:^|\n)### User', content, re.MULTILINE))
        user_pattern4 = len(re.findall(r'(?:^|\n)User:', content, re.MULTILINE))
        
        # Take the maximum count from all patterns
        prompt_count = max(user_pattern1, user_pattern2, user_pattern3, user_pattern4)
    
    return prompt_count

def main():
    # Initialize the client with your API key
    api_key = os.getenv('SPECSTORY_API_KEY', 'your-api-key-here')
    
    try:
        client = Client(api_key=api_key)
        
        print('=' * 60)
        print('SpecStory Chat Analytics')
        print('=' * 60)
        
        # Get all projects
        print('\nFetching all projects...')
        projects = client.projects.list()
        print(f'Found {len(projects)} projects\n')
        
        total_sessions = 0
        total_prompts = 0
        project_stats = []
        
        # Iterate through each project
        for project in projects:
            project_name = project.get('name', 'Unnamed')
            project_id = project['id']
            print(f'Processing project: {project_name} ({project_id})')
            
            # Get all sessions for this project
            sessions = client.sessions.list(project_id)
            project_session_count = len(sessions)
            project_prompt_count = 0
            
            print(f'  Found {project_session_count} sessions')
            
            # Process each session
            for i, session in enumerate(sessions):
                session_id = session.get('session_id') or session.get('id')
                session_name = session.get('name', 'Unnamed Session')
                
                # Debug: Show session structure
                if i == 0:  # Show first session details
                    print(f'    Debug - Session keys: {session.keys()}')
                    print(f'    Debug - Session ID: {session_id}')
                
                try:
                    # Read session details to get content
                    details = client.sessions.read(project_id, session_id)
                    
                    if details:
                        # Debug: Show what's returned
                        if i == 0:
                            print(f'    Debug - Details keys: {details.keys()}')
                            print(f'    Debug - Details: {str(details)[:500]}...')
                        
                        # Count prompts in markdown content
                        # Note: API returns 'markdownContent' not 'markdown'
                        markdown = details.get('markdownContent', '')
                        raw_data = details.get('rawData', '')
                        
                        # Debug: Show content preview
                        if i == 0 and (markdown or raw_data):
                            if markdown:
                                print(f'    Debug - Markdown preview: {markdown[:200]}...')
                            if raw_data:
                                print(f'    Debug - Raw data preview: {raw_data[:200]}...')
                        
                        markdown_prompts = count_prompts_in_content(markdown)
                        raw_prompts = count_prompts_in_content(raw_data)
                        
                        session_prompts = max(markdown_prompts, raw_prompts)
                        project_prompt_count += session_prompts
                        
                        print(f'    Session "{session_name}": {session_prompts} prompts detected')
                
                except Exception as e:
                    print(f'    Error reading session {session_id}: {e}')
            
            # Store project statistics
            project_stats.append({
                'name': project_name,
                'sessions': project_session_count,
                'prompts': project_prompt_count
            })
            
            total_sessions += project_session_count
            total_prompts += project_prompt_count
            
            print(f'  Project total: {project_prompt_count} prompts\n')
        
        # Display summary
        print('=' * 60)
        print('SUMMARY')
        print('=' * 60)
        print(f'\nTotal Projects: {len(projects)}')
        print(f'Total Sessions: {total_sessions}')
        print(f'Total Prompts: {total_prompts}')
        
        if total_sessions > 0:
            avg_prompts = total_prompts / total_sessions
            print(f'Average Prompts per Session: {avg_prompts:.2f}')
        
        # Display per-project breakdown
        if project_stats:
            print('\n' + '-' * 40)
            print('Per-Project Breakdown:')
            print('-' * 40)
            for stat in project_stats:
                print(f'{stat["name"]:30} | Sessions: {stat["sessions"]:5} | Prompts: {stat["prompts"]:5}')
        
        # Search for sessions with high activity
        print('\n' + '-' * 40)
        print('Searching for active sessions...')
        print('-' * 40)
        
        # Search for common keywords that might indicate active chats
        search_keywords = ['conversation', 'chat', 'message', 'prompt']
        active_sessions = set()
        
        for keyword in search_keywords:
            try:
                results = client.graphql.search(keyword, limit=100)
                if results and 'sessions' in results:
                    for session in results['sessions']:
                        session_key = f"{session.get('projectId')}:{session.get('id')}"
                        active_sessions.add(session_key)
            except:
                pass
        
        if active_sessions:
            print(f'Found {len(active_sessions)} potentially active sessions based on content search')
        
    except Exception as e:
        print(f'\nError: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()