# SpecStory SDK for Python

Tiny & delightful SDK for SpecStory Cloud API.

## Install

```bash
pip install specstory
```

## Quick Start

```python
from specstory import Client

client = Client(api_key="your-api-key")

# Upload a session
session = client.sessions.write(
    project_id="project-id",
    name="My Session",
    markdown="# Session Content",
    raw_data='{"data": "here"}'
)

# Search across sessions
results = client.graphql.search("error handling")
print(f"Found {results['total']} results")
```

## Async Support

```python
import asyncio
from specstory import AsyncClient

async def main():
    async with AsyncClient(api_key="your-api-key") as client:
        results = await client.graphql.search("query")
        print(results)

asyncio.run(main())
```

## Development Status

⚠️ **Beta SDK** - This SDK is under active development. APIs may change.

## License

MIT