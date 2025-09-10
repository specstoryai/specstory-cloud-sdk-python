# SpecStory Python SDK

[![PyPI version](https://badge.fury.io/py/specstory.svg)](https://badge.fury.io/py/specstory)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![codecov](https://codecov.io/gh/specstoryai/specstory-cloud-sdk-python/branch/main/graph/badge.svg)](https://codecov.io/gh/specstoryai/specstory-cloud-sdk-python)
[![Python Versions](https://img.shields.io/pypi/pyversions/specstory.svg)](https://pypi.org/project/specstory/)

The official Python SDK for the SpecStory API, providing intuitive access to all SpecStory features.

## Prerequisites

Before using this SDK, you'll need:

1. **SpecStory Extension**: Install one or more SpecStory extensions in your development environment
   - Learn more: [SpecStory Introduction](https://docs.specstory.com/specstory/introduction)
   
2. **SpecStory Cloud Account**: Create an account to obtain your API key
   - Quick start guide: [SpecStory Cloud Quickstart](https://docs.specstory.com/cloud/quickstart)
   - Sign up at: [cloud.specstory.com](https://cloud.specstory.com)

3. **Python**: Version 3.9 or higher

## Installation

### From PyPI (coming soon)

```bash
pip install specstory
```

### From GitHub (for early access)

Until the package is published to PyPI, you can install directly from GitHub:

```bash
# Install directly from GitHub
pip install git+https://github.com/specstoryai/specstory-cloud-sdk-python.git

# Or clone and install locally for development
git clone https://github.com/specstoryai/specstory-cloud-sdk-python.git
cd specstory-cloud-sdk-python
pip install -e .
```

## Quick Start

First, create a `.env` file in your project root:
```bash
# .env
SPECSTORY_API_KEY=your-api-key-here
```

**Important**: Add `.env` to your `.gitignore` file to keep your API key secure.

Then use the SDK:

```python
import os
from specstory import Client

# Load environment variables from .env file
# You may need to: pip install python-dotenv
from dotenv import load_dotenv
load_dotenv()

# Initialize the client with your API key
# Get your API key from: https://cloud.specstory.com/api-keys
client = Client(
    api_key=os.environ["SPECSTORY_API_KEY"],  # Required
    # Optional: Override base URL for self-hosted instances
    # base_url="https://cloud.specstory.com"  # Default, override for self-hosted
)

# Search across sessions
results = client.graphql.search("error 500")
print(f"Found {results['total']} results")
```

## Features

- 🐍 **Pythonic**: Designed with Python best practices and idioms
- 🔒 **Type-safe**: Full type hints for better IDE support
- 🚀 **Async support**: Both sync and async clients available
- 🔄 **Auto-retry**: Built-in retry logic with exponential backoff
- 📦 **Zero dependencies**: Only requires standard library (httpx for async)
- 🧪 **Well-tested**: Comprehensive test coverage

## API Reference

### Client Configuration

```python
from specstory import Client

client = Client(
    api_key: str,                              # Your API key (required)
    base_url: str = "https://cloud.specstory.com",  # API base URL (default)
    timeout_s: float = 30.0,                   # Request timeout in seconds
    cache: dict | bool = None,                # Cache configuration or False to disable
)
```

### Async Client

```python
from specstory import AsyncClient
import asyncio

async def main():
    client = AsyncClient(api_key="your-api-key")
    
    # All methods are async
    projects = await client.projects.list()
    
    # Don't forget to close the client
    await client.close()

asyncio.run(main())
```

### Projects

```python
# List projects
projects = client.projects.list(page=1, limit=10)

# Get a project
project = client.projects.get(project_id)

# Create a project
project = client.projects.create(
    name="Project Name",
    description="Project description"
)

# Update a project
project = client.projects.update(
    project_id,
    name="New Name"
)

# Delete a project
client.projects.delete(project_id)
```

### Sessions

```python
# List sessions for a project
sessions = client.sessions.list(project_id)

# Read a specific session
session = client.sessions.read(project_id, session_id)
if session:
    print(f"Session name: {session['name']}")
    print(f"Markdown size: {session['markdownSize']} bytes")

# Get recent sessions across all projects
recent_sessions = client.sessions.recent(10)

# Delete a session
client.sessions.delete(project_id, session_id)

# Get session metadata without content
metadata = client.sessions.head(project_id, session_id)
if metadata and metadata['exists']:
    print(f"Last modified: {metadata['lastModified']}")
```

### GraphQL Search

```python
# Search across all sessions
results = client.graphql.search("error 500", 
    limit=20,
    filters={
        "projectId": "specific-project-id",
        "tags": ["production"]
    }
)

print(f"Found {results['total']} matches")
for result in results['results']:
    print(f"{result['name']} (rank: {result['rank']})")

```

### Error Handling

The SDK provides typed exceptions for better error handling:

```python
from specstory import Client, SpecStoryError, ValidationError

try:
    session = client.sessions.read(project_id, session_id)
except ValidationError as e:
    # Handle validation errors
    print(f"Validation failed: {e.errors}")
except SpecStoryError as e:
    # Handle other API errors
    print(f"API error: {e.message}")
except Exception as e:
    # Handle unexpected errors
    print(f"Unexpected error: {e}")
```

## Advanced Usage

### Context Manager

```python
from specstory import Client

# Client automatically closes connections
with Client(api_key="your-api-key") as client:
    projects = client.projects.list()
```

### Custom Headers

```python
client = Client(
    api_key="your-api-key",
    headers={
        "X-Custom-Header": "value"
    }
)
```

### Timeout Configuration

```python
client = Client(
    api_key="your-api-key",
    timeout=60.0  # 60 seconds
)
```

### Pagination

```python
# Use the paginated iterator for sessions
for session in client.sessions.list_paginated(project_id):
    print(f"Session: {session['name']}")
    # Process each session without loading all into memory
```

### Convenience Methods

```python
# Get project by name
project = client.projects.get_by_name("My Project")
if project:
    print(f"Found project: {project['id']}")
```

## Async Usage

```python
import asyncio
from specstory import AsyncClient

async def main():
    async with AsyncClient(api_key="your-api-key") as client:
        # All methods are async versions of sync client
        projects = await client.projects.list()
        
        # Search asynchronously
        results = await client.graphql.search("error")
        print(f"Found {results['total']} results")
        
        # Concurrent requests
        sessions, recent = await asyncio.gather(
            client.sessions.list(projects[0]['id']),
            client.sessions.recent(5)
        )

asyncio.run(main())
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/specstoryai/specstory-cloud-sdk-python.git
cd specstory-cloud-sdk-python

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check specstory tests
black --check specstory tests
```

## Requirements

- Python 3.9 or higher
- No runtime dependencies for sync client
- httpx for async client (installed automatically with `pip install specstory[async]`)

## Advanced Usage

### Caching

```python
# Enable caching (default)
client = Client(
    api_key="your-api-key",
    cache={
        "max_size": 200,      # Cache up to 200 items
        "default_ttl": 600.0  # 10 minutes
    }
)

# Disable caching
no_cache = Client(
    api_key="your-api-key",
    cache=False
)
```

### Conditional Requests with ETags

```python
# First read
session = client.sessions.read(project_id, session_id)
etag = session.get('etag') if session else None

# Later, check if changed
updated = client.sessions.read(project_id, session_id, if_none_match=etag)
if updated is None:
    print("Session has not changed")
```

### Request Timeouts

```python
# Set default timeout
client = Client(
    api_key="your-api-key",
    timeout_s=60.0  # 60 seconds
)

# Override for specific request
client.sessions.write(
    project_id,
    name="Large Session",
    markdown="# Big content...",
    raw_data=large_json_data,
    timeout_s=120.0  # 2 minutes for large uploads
)
```

## License

This SDK is distributed under the Apache License 2.0. See [LICENSE](LICENSE) for more information.

## Support

- 📧 Email: support@specstory.com
- 💬 Community: [Join our Slack](https://specstory.slack.com/join/shared_invite/zt-2vq0274ck-MYS39rgOpDSmgfE1IeK9gg#/shared-invite/email)
- 📖 Documentation: [docs.specstory.com](https://docs.specstory.com)
- 🐛 Issues: [GitHub Issues](https://github.com/specstoryai/specstory-cloud-sdk-python/issues)

## Links

- [PyPI Package](https://pypi.org/project/specstory/)
- [GitHub Repository](https://github.com/specstoryai/specstory-cloud-sdk-python)
- [API Documentation](https://docs.specstory.com/api)
- [Examples](https://github.com/specstoryai/specstory-cloud-sdk-python/tree/main/examples)