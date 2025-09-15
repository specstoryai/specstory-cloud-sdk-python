#!/usr/bin/env python3
"""
SpecStory Chat Extractor - Extract and analyze conversations from SpecStory sessions

This module provides functions to:
- List all projects and sessions
- Extract conversations from session markdown content
- Export structured data for further analysis
"""

import os
import json
import re
from typing import List, Dict, Optional, Any
from datetime import datetime
from dotenv import load_dotenv
from specstory import Client

load_dotenv()


# Set SPECSTORY_API_KEY in env var or pass your api key
api_key = os.getenv('SPECSTORY_API_KEY', 'your-api-key-here')
specstory_client = Client(api_key=api_key)

conversation_file = 'all_conversations.json'


def list_all_projects():
    """
    Get all projects for the authenticated user
    Returns:
        List of project dictionaries with id, name, and other metadata
    """
    try:
        projects = specstory_client.projects.list()
        return projects
    except Exception as e:
        print(f"Error fetching projects: {e}")
        return []


def list_project_sessions(project_id: str) -> List[Dict[str, Any]]:
    """
    Get all sessions for a specific project
    Args:
        project_id: Project ID to fetch sessions for
    Returns:
        List of session dictionaries with id, name, and metadata
    """
    try:
        sessions = specstory_client.sessions.list(project_id)
        return sessions
    except Exception as e:
        print(f"Error fetching sessions for project {project_id}: {e}")
        return []


def get_session_content(project_id: str, session_id: str) -> Optional[Dict[str, Any]]:
    """
    Get full content details for a specific session
    Args:
        project_id: Project ID
        session_id: Session ID
    Returns:
        Session details including markdown content, or None if error
    """
    try:
        details = specstory_client.sessions.read(project_id, session_id)
        return details
    except Exception as e:
        print(f"Error reading session {session_id}: {e}")
        return None


def parse_conversation_turns(markdown_content: str) -> List[Dict[str, Any]]:
    """
    Extract conversation turns from SpecStory markdown format
    Args:
        markdown_content: Raw markdown content from session
    Returns:
        List of conversation turns with user prompts and agent responses
    """
    if not markdown_content:
        return []

    conversations = []

    # Pattern to match user and agent sections
    # Looking for _**User**_ and _**Agent...**_ markers
    user_pattern = r'_\*\*User\*\*_\s*\n(.*?)(?=_\*\*(?:User|Agent)|---|$)'
    agent_pattern = r'_\*\*Agent.*?\*\*_\s*\n(.*?)(?=_\*\*(?:User|Agent)|---|$)'

    # Find all user prompts and agent responses
    user_matches = re.findall(user_pattern, markdown_content, re.DOTALL)
    agent_matches = re.findall(agent_pattern, markdown_content, re.DOTALL)

    # Pair up conversations
    for i, user_prompt in enumerate(user_matches):
        conversation_turn = {
            'turn_number': i + 1,
            'user_prompt': user_prompt.strip(),
            'agent_response': agent_matches[i].strip() if i < len(agent_matches) else None
        }
        conversations.append(conversation_turn)

    return conversations


def extract_project_conversations(project_id: str, project_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Extract all conversations from a project
    Args:
        project_id: Project ID to extract from
        project_name: Optional project name for metadata
    Returns:
        Dictionary containing project metadata and all session conversations
    """
    sessions = list_project_sessions(project_id)

    project_data = {
        'project_id': project_id,
        'project_name': project_name or 'Unknown Project',
        'total_sessions': len(sessions),
        'sessions': []
    }

    for session in sessions:
        session_id = session.get('session_id') or session.get('id')
        session_name = session.get('name', 'Unnamed Session')

        # Get session content
        content = get_session_content(project_id, session_id)

        if content:
            markdown_content = content.get('markdownContent', '')
            conversations = parse_conversation_turns(markdown_content)

            session_data = {
                'session_id': session_id,
                'session_name': session_name,
                'created_at': str(content.get('createdAt', '')),
                'updated_at': str(content.get('updatedAt', '')),
                'markdown_size': content.get('markdownSize', 0),
                'total_turns': len(conversations),
                'conversations': conversations
            }

            project_data['sessions'].append(session_data)

    # Calculate project totals
    project_data['total_conversations'] = sum(s['total_turns'] for s in project_data['sessions'])

    return project_data


def extract_all_conversations() -> List[Dict[str, Any]]:
    """
    Extract all conversations from all projects
    Returns:
        List of project dictionaries, each containing sessions and conversations
    """

    projects = list_all_projects()
    all_data = []

    for project in projects:
        project_id = project['id']
        project_name = project.get('name', 'Unnamed Project')

        print(f"Extracting from project: {project_name}")
        project_data = extract_project_conversations(project_id, project_name)
        all_data.append(project_data)

    return all_data


def save_conversations_to_file(data: List[Dict[str, Any]], filename: str = conversation_file) -> str:
    """
    Save extracted conversations to a JSON file

    Args:
        data: List of project data with conversations
        filename: Output filename (default: extracted_conversations.json)

    Returns:
        Path to the saved file
    """
    # Add metadata about extraction
    output = {
        'extraction_timestamp': datetime.now().isoformat(),
        'total_projects': len(data),
        'total_sessions': sum(p['total_sessions'] for p in data),
        'total_conversations': sum(p['total_conversations'] for p in data),
        'projects': data
    }

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    return os.path.abspath(filename)


def get_conversation_summary(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate summary statistics from extracted conversation data
    Args:
        data: List of project data with conversations
    Returns:
        Dictionary with summary statistics
    """
    total_projects = len(data)
    total_sessions = sum(p['total_sessions'] for p in data)
    total_conversations = sum(p['total_conversations'] for p in data)

    # Find most active sessions
    all_sessions = []
    for project in data:
        for session in project['sessions']:
            all_sessions.append({
                'project_name': project['project_name'],
                'session_name': session['session_name'],
                'total_turns': session['total_turns'],
                'updated_at': session['updated_at']
            })

    # Sort by activity
    most_active = sorted(all_sessions, key=lambda x: x['total_turns'], reverse=True)[:5]

    return {
        'total_projects': total_projects,
        'total_sessions': total_sessions,
        'total_conversations': total_conversations,
        'average_turns_per_session': total_conversations / total_sessions if total_sessions > 0 else 0,
        'most_active_sessions': most_active
    }


def main():

    # Extract all conversations
    print('\nExtracting conversations from all projects...\n')
    all_data = extract_all_conversations()

    # Generate and display summary
    summary = get_conversation_summary(all_data)

    print('\n' + '=' * 80)
    print('EXTRACTION SUMMARY')
    print('=' * 80)
    print(f"\nTotal Projects: {summary['total_projects']}")
    print(f"Total Sessions: {summary['total_sessions']}")
    print(f"Total Conversation Turns: {summary['total_conversations']}")
    print(f"Average Turns per Session: {summary['average_turns_per_session']:.2f}")

    if summary['most_active_sessions']:
        print('\n' + '-' * 50)
        print('Top 5 Most Active Sessions:')
        print('-' * 50)
        for i, session in enumerate(summary['most_active_sessions'], 1):
            print(f"{i}. {session['session_name'][:40]}")
            print(f"   Project: {session['project_name']}")
            print(f"   Turns: {session['total_turns']}")
            print(f"   Last Updated: {session['updated_at']}")

    # Save to file (you can use those conversations for other use)
    print('\n' + '-' * 50)
    output_file = save_conversations_to_file(all_data)
    print(f'Full conversation data saved to: {output_file}')


if __name__ == '__main__':
    main()