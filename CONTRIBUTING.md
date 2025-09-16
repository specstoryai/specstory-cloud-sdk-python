# Contributing to SpecStory Python SDK

Thank you for your interest in contributing to the SpecStory Python SDK! We welcome contributions from the community.

## Important Note

This repository is automatically synchronized from our development monorepo. While we encourage discussions and contributions here, the actual implementation happens in our main repository.

## How to Contribute

### Reporting Issues

1. **Search existing issues** to avoid duplicates
2. **Create a new issue** with a clear title and description
3. **Include reproduction steps** if reporting a bug
4. **Provide environment details** (Python version, OS, etc.)

### Suggesting Features

1. **Open a feature request issue**
2. **Describe the problem** you're trying to solve
3. **Propose your solution** with example usage
4. **Discuss alternatives** you've considered

### Pull Requests

While this repository is read-only for code changes, we still accept PRs for:
- Documentation improvements
- Example code additions
- Test case suggestions

**Process:**
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a PR with a clear description

## Development Workflow

If you want to test changes locally:

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/specstory-cloud-sdk-python.git
cd specstory-cloud-sdk-python

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check specstory tests
black --check specstory tests
mypy specstory
```

## Code Style

- Follow PEP 8 guidelines
- Use type hints for all public APIs
- Format code with Black
- Lint with Ruff
- Add tests for new functionality

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=specstory --cov-report=html

# Run specific test file
pytest tests/test_client.py

# Run tests with verbose output
pytest -v
```

## Type Checking

```bash
# Run mypy type checker
mypy specstory

# Check specific file
mypy specstory/client.py
```

## Documentation

- Update README.md for user-facing changes
- Add docstrings to all public functions/classes
- Follow Google style docstrings
- Include code examples where helpful

## Community Guidelines

- Be respectful and inclusive
- Follow our [Code of Conduct](CODE_OF_CONDUCT.md)
- Help others in discussions
- Share your use cases and feedback

## Questions?

- 💬 Join our [Discord community](https://discord.gg/specstory)
- 📧 Email us at support@specstory.com
- 📖 Check our [documentation](https://docs.specstory.com)

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.