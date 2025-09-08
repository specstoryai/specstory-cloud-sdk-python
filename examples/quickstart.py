#!/usr/bin/env python3
"""
Quick start example for SpecStory Python SDK
"""

import json
import os
from datetime import datetime

from specstory import Client, SDKError


def main():
    """Run the quickstart example"""
    # Initialize client with API key
    client = Client(api_key=os.environ.get("SPECSTORY_API_KEY"))
    
    try:
        # List all projects
        print("📁 Fetching projects...")
        projects = client.projects.list()
        print(f"Found {len(projects)} projects")
        
        if not projects:
            print("No projects found. Create one at https://cloud.specstory.com")
            return
        
        project = projects[0]
        print(f"\n📋 Using project: {project['name']}")
        
        # Upload a new session
        print("\n📤 Creating new session...")
        session = client.sessions.write(
            project_id=project["id"],
            name="SDK Test Session",
            markdown="# Test Session\n\nThis session was created using the SpecStory SDK.",
            raw_data=json.dumps({
                "timestamp": datetime.now().isoformat(),
                "source": "python-sdk-quickstart"
            }),
            metadata={
                "tags": ["test", "sdk-demo"],
                "client_name": "quickstart-example"
            }
        )
        
        print(f"✅ Session created with ID: {session['data']['sessionId']}")
        
        # Search for sessions
        print("\n🔍 Searching for sessions...")
        search_results = client.graphql.search("test")
        print(f"Found {search_results['total']} matching sessions")
        
    except SDKError as e:
        print(f"❌ SDK Error: {e}")
        if e.request_id:
            print(f"   Request ID: {e.request_id}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()