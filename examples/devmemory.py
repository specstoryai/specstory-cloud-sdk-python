#!/usr/bin/env python3
"""
DevMemory - Your Development Memory Assistant
Intelligently searches and answers questions about your past development work

This example demonstrates how to use the SpecStory SDK with OpenAI Agents
to create an intelligent Q&A system over your development conversation history.

Requirements:
    pip install openai-agents specstory python-dotenv

Environment variables:
    SPECSTORY_API_KEY - Your SpecStory API key
    OPENAI_API_KEY - Your OpenAI API key
"""

import os
import asyncio
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check for required dependencies
try:
    from agents import Agent, function_tool, Runner
    from specstory import Client
except ImportError as e:
    print(f"Error: Missing required dependencies. {e}")
    print("Please install: pip install openai-agents specstory python-dotenv")
    exit(1)

# Initialize SpecStory client
try:
    specstory_client = Client(api_key=os.getenv('SPECSTORY_API_KEY'))
except Exception as e:
    print(f"Error initializing SpecStory client: {e}")
    print("Please set SPECSTORY_API_KEY in your .env file")
    exit(1)


# Tool Functions for the Agent
@function_tool
def search_dev_history(query: str, limit: int = 10) -> List[Dict]:
    """
    Search through development history using natural language.
    Searches across all projects and sessions for relevant conversations.

    Args:
        query: Natural language search query
        limit: Maximum number of results to return

    Returns:
        List of simplified session results with excerpts
    """
    try:
        # Use GraphQL search to find relevant sessions
        results = specstory_client.graphql.search(query, limit=limit)

        # Get all projects to build a lookup map for finding correct project IDs
        all_projects = specstory_client.projects.list()
        project_by_name = {p['name']: p['id'] for p in all_projects}

        simplified = []
        for result in results.get('results', []):
            session_id = result['id']
            session_name = result.get('name', 'Unnamed Session')

            # Try to find the session in any project (search might return wrong project ID)
            content = None
            actual_project_id = None

            # First try the project ID from search results
            try:
                content = specstory_client.sessions.read(result['projectId'], session_id)
                actual_project_id = result['projectId']
            except:
                # If that fails, try to find it in other projects
                for project in all_projects:
                    try:
                        content = specstory_client.sessions.read(project['id'], session_id)
                        actual_project_id = project['id']
                        break
                    except:
                        continue

            if content:
                # Extract markdown content and create excerpt
                markdown = content.get('markdownContent', '')
                excerpt = markdown[:1500] if markdown else 'No content available'

                # Clean up the excerpt (remove excessive whitespace)
                excerpt = ' '.join(excerpt.split())

                simplified.append({
                    'session_id': session_id,
                    'session_name': session_name,
                    'project_id': actual_project_id,
                    'excerpt': excerpt,
                    'rank': result.get('rank', 0)
                })
            else:
                # Session not found in any project
                print(f"Warning: Session {session_id} not found in any project")

        return simplified
    except Exception as e:
        print(f"Search error: {e}")
        return []


@function_tool
def get_full_session(session_id: str, project_id: str) -> str:
    """
    Get the complete content of a development session.
    Use this when you need more context than the excerpt provides.
    Args:
        session_id: The ID of the session to retrieve
        project_id: The ID of the project containing the session
    Returns:
        Full markdown content of the session
    """
    try:
        content = specstory_client.sessions.read(project_id, session_id)
        markdown = content.get('markdownContent', 'Session content not found')

        # Return first 10000 chars to avoid token limits
        if len(markdown) > 10000:
            return markdown[:10000] + "\n\n[Content truncated due to length...]"
        return markdown
    except Exception as e:
        return f"Error retrieving session: {e}"


# @function_tool
# def find_code_implementations(topic: str) -> List[Dict]:
#     """
#     Search specifically for code implementations related to a topic.
#     Returns sessions containing code blocks relevant to the query.
#
#     Args:
#         topic: The topic or technology to search for code examples
#
#     Returns:
#         List of sessions with code snippets
#     """
#     import re
#
#     # Search for the topic
#     results = search_dev_history(topic, limit=10)
#     code_results = []
#
#     for result in results:
#         try:
#             # Get full session content
#             content = get_full_session(result['session_id'], result['project_id'])
#
#             # Find code blocks (markdown code blocks)
#             code_blocks = re.findall(r'```[\w]*\n(.*?)\n```', content, re.DOTALL)
#
#             if code_blocks:
#                 # Get first meaningful code block
#                 first_code = None
#                 for block in code_blocks:
#                     if len(block.strip()) > 50:  # Skip tiny blocks
#                         first_code = block[:500]
#                         break
#
#                 if first_code:
#                     code_results.append({
#                         'session_name': result['session_name'],
#                         'session_id': result['session_id'],
#                         'project_id': result['project_id'],
#                         'code_count': len(code_blocks),
#                         'sample_code': first_code
#                     })
#         except Exception as e:
#             print(f"Warning: Error processing session {result['session_id']}: {e}")
#             continue
#
#     return code_results


# Create the DevMemory Agent
devmemory_agent = Agent(
    name="DevMemory Assistant",
    instructions="""You are DevMemory, an intelligent assistant that helps developers recall information from their past coding sessions and conversations.

You have access to a searchable history of development conversations including:
- Infrastructure and DevOps (Snowflake, Railway, Git, CI/CD)
- Application development (Next.js, React, Supabase)
- Debugging sessions and problem-solving
- Architecture decisions and design discussions
- UI/UX implementations
- Data engineering and ETL processes

When answering questions:
1. Start by searching for relevant sessions using search_dev_history
2. Review the excerpts to identify the most relevant sessions
3. If you need more detail, use get_full_session to read complete conversations
4. Always cite the specific session names when referencing information
5. If multiple sessions contain relevant info, synthesize the knowledge
6. Be clear when you don't find relevant information

Format your responses clearly:
- Start with a direct answer to the question
- Cite sources with session names in [brackets]
- Include relevant code snippets when applicable
- Suggest related topics if found

Remember: You're helping developers recall their own past work, so be specific and reference actual sessions.""",
    model="gpt-4o",
    tools=[search_dev_history, get_full_session]
)


# Main Application
async def ask_devmemory(query: str) -> Dict:
    """
    Main function to query DevMemory
    Args:
        query: Natural language question about past development work
    Returns:
        Dictionary with answer and success status
    """
    try:
        # Run the agent with the query using Runner
        result = await Runner.run(devmemory_agent, query)

        return {
            'answer': result.final_output,
            'success': True
        }
    except Exception as e:
        return {
            'answer': f"Sorry, I encountered an error: {str(e)}",
            'success': False
        }


async def batch_mode(queries: List[str]):
    """
    Process multiple queries in batch mode
    Args:
        queries: List of questions to process
    """
    for i, query in enumerate(queries, 1):
        print(f"Query {i}: {query}")
        result = await ask_devmemory(query)
        print(result['answer'])
        print("\n" + "-" * 30 + "\n")


async def main():
    """Main entry point for the application"""

    # Check if batch mode (queries passed as arguments)
    # await batch_mode(queries)

    # Example queries based on actual conversation topics in the data
    EXAMPLE_QUERIES = [
        "How did we set up Snowflake ETL for PostHog data?",
        "What was the JWT token invalid error and how did we fix it?",
        "Show me how we implemented URL shortening with custom slugs",
        "What issues did we have with Railway deployment?",
        "How did we implement the Slack decision capture app?",
        "What's our approach to code modularization and refactoring?",
        "How did we fix React component width issues?",
        "What Git repository issues did we resolve?",
        "How to handle Supabase transcript processing?",
        "What was our monorepo setup with Turbo?",
        "Show the VS Code extension implementation",
        "How did we implement persistent backup state?"
    ]
    query = EXAMPLE_QUERIES[2]
    response = await ask_devmemory(query)
    return response['answer']


if __name__ == "__main__":
    print(asyncio.run(main()))
