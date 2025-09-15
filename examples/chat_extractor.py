#!/usr/bin/env python3
import os
import json
import re
from dotenv import load_dotenv
from specstory import Client

load_dotenv()

def extract_conversations(markdown_content):
    """
    Extract user prompts and agent responses from SpecStory markdown format
    Returns a list of conversation turns
    """
    if not markdown_content:
        return []
    
    conversations = []
    
    # Split by user markers to get individual conversations
    # Pattern looks for _**User**_ followed by content until next marker or end
    user_pattern = r'_\*\*User\*\*_\s*\n(.*?)(?=_\*\*(?:User|Agent)|$)'
    agent_pattern = r'_\*\*Agent.*?\*\*_\s*\n(.*?)(?=_\*\*(?:User|Agent)|---|$)'
    
    # Find all user prompts
    user_matches = re.findall(user_pattern, markdown_content, re.DOTALL)
    
    # Find all agent responses  
    agent_matches = re.findall(agent_pattern, markdown_content, re.DOTALL)
    
    # Combine into conversation format
    for i, user_prompt in enumerate(user_matches):
        conv = {
            'turn': i + 1,
            'user': user_prompt.strip(),
            'agent': agent_matches[i].strip() if i < len(agent_matches) else None
        }
        conversations.append(conv)
    
    return conversations

def main():
    # Initialize the client with your API key
    api_key = os.getenv('SPECSTORY_API_KEY', 'your-api-key-here')
    
    try:
        client = Client(api_key=api_key)
        
        # Get all projects
        print('\nFetching all projects...')
        projects = client.projects.list()
        print(f'Found {len(projects)} projects\n')
        
        all_chats = []
        
        # Iterate through each project
        for project in projects:
            project_name = project.get('name', 'Unnamed')
            project_id = project['id']
            
            print(f'\n{"="*60}')
            print(f'PROJECT: {project_name}')
            print(f'ID: {project_id}')
            print('='*60)
            
            # Get all sessions for this project
            sessions = client.sessions.list(project_id)
            print(f'Found {len(sessions)} sessions\n')
            
            # Process each session
            for session in sessions:
                session_id = session.get('session_id') or session.get('id')
                session_name = session.get('name', 'Unnamed Session')
                
                try:
                    # Read session details to get content
                    details = client.sessions.read(project_id, session_id)
                    
                    if details:
                        markdown_content = details.get('markdownContent', '')
                        
                        if markdown_content:
                            print(f'\n{"-"*50}')
                            print(f'SESSION: {session_name}')
                            print(f'Session ID: {session_id}')
                            print(f'Created: {details.get("createdAt", "N/A")}')
                            print(f'Updated: {details.get("updatedAt", "N/A")}')
                            print(f'Size: {details.get("markdownSize", 0)} bytes')
                            print('-'*50)
                            
                            # Extract conversations
                            conversations = extract_conversations(markdown_content)
                            
                            if conversations:
                                print(f'\nFound {len(conversations)} conversation turns:')
                                
                                for conv in conversations:
                                    print(f'\n[Turn {conv["turn"]}]')
                                    print(f'USER: {conv["user"][:200]}{"..." if len(conv["user"]) > 200 else ""}')
                                    
                                    if conv["agent"]:
                                        print(f'AGENT: {conv["agent"][:200]}{"..." if len(conv["agent"]) > 200 else ""}')
                                
                                # Store chat data
                                all_chats.append({
                                    'project': project_name,
                                    'project_id': project_id,
                                    'session': session_name,
                                    'session_id': session_id,
                                    'conversations': conversations,
                                    'prompt_count': len(conversations),
                                    'created_at': details.get('createdAt'),
                                    'updated_at': details.get('updatedAt')
                                })
                            else:
                                print('\nNo conversations found in this session.')
                        else:
                            print(f'\nSession "{session_name}" has no content.')
                
                except Exception as e:
                    print(f'\nError reading session {session_id}: {e}')
        
        # Summary statistics
        print('\n' + '='*80)
        print('SUMMARY')
        print('='*80)
        
        total_conversations = sum(chat['prompt_count'] for chat in all_chats)
        print(f'\nTotal Projects: {len(projects)}')
        print(f'Total Sessions with Content: {len(all_chats)}')
        print(f'Total Conversation Turns: {total_conversations}')
        
        if all_chats:
            avg_prompts = total_conversations / len(all_chats)
            print(f'Average Prompts per Session: {avg_prompts:.2f}')
            
            # Show top sessions by activity
            print('\n' + '-'*50)
            print('Top 5 Most Active Sessions:')
            print('-'*50)
            
            sorted_chats = sorted(all_chats, key=lambda x: x['prompt_count'], reverse=True)
            for i, chat in enumerate(sorted_chats[:5], 1):
                print(f'{i}. {chat["session"][:40]}')
                print(f'   Project: {chat["project"]}')
                print(f'   Prompts: {chat["prompt_count"]}')
                print(f'   Last Updated: {chat["updated_at"]}')
        
        # Export option
        print('\n' + '-'*50)
        output_file = 'extracted_chats.json'
        with open(output_file, 'w') as f:
            json.dump(all_chats, f, indent=2, default=str)
        print(f'Full chat data exported to: {output_file}')
        
    except Exception as e:
        print(f'\nError: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()