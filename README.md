# SpecStory Python SDK - Internal Development Guide

This is the internal development guide for the SpecStory Python SDK. For public documentation, see `templates/python-sdk/README.md`.

## Prerequisites

- Python 3.9+ (recommended: use `pyenv`)
- pip or poetry
- Understanding of sync/async Python

## Project Structure

```
python/
├── specstory/        # Source code
│   ├── client.py     # Main client implementations (sync/async)
│   ├── resources/    # API resource implementations
│   ├── _errors.py    # Error classes
│   └── _types.py     # Type definitions
├── tests/            # Test files
├── examples/         # Example usage scripts
├── build/            # Build artifacts (git-ignored)
└── htmlcov/          # Coverage reports (git-ignored)
```

## Getting Started

### 1. Set Up Virtual Environment

```bash
cd python

# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip
```

### 2. Install Dependencies

```bash
# Install in development mode with all extras
pip install -e ".[dev,test,async]"
```

### 3. Set Up Environment

Create a `.env` file (copy from `.env.example`):
```bash
cp .env.example .env
# Edit .env and add your API key
SPECSTORY_API_KEY=your-actual-api-key-here
```

### 4. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=specstory --cov-report=html

# Run only unit tests
pytest tests/unit/

# Run only integration tests (requires API key)
pytest tests/integration/

# Run specific test file
pytest tests/unit/test_client.py

# Run with verbose output
pytest -v

# Run tests matching a pattern
pytest -k "test_error"
```

### 5. Linting and Formatting

```bash
# Run all linting
ruff check specstory tests

# Fix linting issues
ruff check --fix specstory tests

# Format code with black
black specstory tests

# Type check with mypy
mypy specstory

# Run all checks at once
make lint  # if Makefile exists
```

## Development Workflow

### Running Examples

```bash
# Run any example directly
python examples/basic_usage.py

# With environment variable
SPECSTORY_API_KEY=your-key python examples/error_handling.py

# Run async examples
python examples/async_usage.py
```

### Testing Your Changes

1. **Unit Testing**: Write tests in `tests/unit/`
   ```python
   # tests/unit/test_my_feature.py
   import pytest
   from specstory import my_feature
   
   def test_my_feature_works():
       result = my_feature()
       assert result == expected_value
   
   @pytest.mark.asyncio
   async def test_async_feature():
       result = await async_feature()
       assert result == expected_value
   ```

2. **Integration Testing**: Write tests in `tests/integration/`
   - Requires valid API key
   - Tests against real API
   - Use fixtures for setup/teardown

### Local Development

To use the SDK locally in another project:

```bash
# Install in editable mode
pip install -e /path/to/specstory-cloud-sdk/python

# Or using pip link equivalent
pip install -e ../specstory-cloud-sdk/python
```

### Debugging

1. **Enable Debug Logging**:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   
   from specstory import Client
   client = Client(api_key="your-key", debug=True)
   ```

2. **IPython/Jupyter**:
   ```python
   %load_ext autoreload
   %autoreload 2
   
   from specstory import Client
   client = Client(api_key="your-key")
   ```

3. **VS Code Launch Config** (`.vscode/launch.json`):
   ```json
   {
     "version": "0.2.0",
     "configurations": [
       {
         "name": "Python: Current File",
         "type": "python",
         "request": "launch",
         "program": "${file}",
         "console": "integratedTerminal",
         "env": {
           "SPECSTORY_API_KEY": "your-key-here"
         }
       }
     ]
   }
   ```

## Build and Distribution

### Building the Package

```bash
# Install build tools
pip install build twine

# Build distribution packages
python -m build

# Check the build
twine check dist/*
```

### Package Structure

The build creates:
- `dist/*.whl` - Wheel distribution
- `dist/*.tar.gz` - Source distribution
- `build/` - Intermediate build files

## API Key Management

**Never commit API keys!**

- Use environment variables
- Use `.env` files (git-ignored)
- For CI/CD, use GitHub secrets
- Consider using `python-dotenv`:
  ```python
  from dotenv import load_dotenv
  load_dotenv()
  ```

## Common Issues

### Import Errors

```bash
# Reinstall in development mode
pip install -e ".[dev]"
```

### Async Errors

```bash
# Make sure httpx is installed
pip install -e ".[async]"
```

### Type Checking Issues

```bash
# Regenerate type stubs
stubgen -p specstory -o stubs/
```

## Publishing (Internal)

**Do NOT publish directly to PyPI!** Use the release workflow:

1. Update version in `pyproject.toml`
2. Push to main branch
3. The sync workflow handles publishing

## Performance Testing

```python
# Run performance benchmarks
python -m pytest tests/performance/ --benchmark-only

# Profile a specific operation
python -m cProfile -o profile.stats examples/performance.py
```

## Async vs Sync

The SDK provides both sync and async clients:

```python
# Sync (default)
from specstory import Client
client = Client(api_key="key")
projects = client.projects.list()

# Async
from specstory import AsyncClient
async with AsyncClient(api_key="key") as client:
    projects = await client.projects.list()
```

Choose based on your application:
- Sync: Simple scripts, Flask, Django
- Async: FastAPI, aiohttp, async applications

## Contributing

1. Create feature branch from `main`
2. Add tests for new functionality
3. Ensure all tests pass
4. Run linting and formatting
5. Submit PR with description

## Commands Reference

| Command | Description |
|---------|-------------|
| `pytest` | Run all tests |
| `pytest --cov=specstory` | Run with coverage |
| `black specstory tests` | Format code |
| `ruff check specstory` | Lint code |
| `mypy specstory` | Type check |
| `python -m build` | Build package |
| `pip install -e ".[dev]"` | Install for development |

## Architecture Notes

- **Client Design**: Separate sync/async implementations
- **Resources**: Shared resource classes with sync/async methods
- **Error Handling**: Rich exception hierarchy with context
- **Type Safety**: Full typing with Python 3.9+ features
- **Zero Dependencies**: Core has no deps, async needs httpx

## Testing Strategy

- **Mocking**: Use `pytest-httpx` for async tests
- **Fixtures**: Shared fixtures in `conftest.py`
- **Markers**: `@pytest.mark.integration` for real API tests
- **Coverage**: Aim for >90% coverage

## Questions?

- Check `docs/` for design decisions
- Review examples in `examples/`
- Ask in #sdk-development Slack channel