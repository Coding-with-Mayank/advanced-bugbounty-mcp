# Contributing to Advanced Bug Bounty MCP Server

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/advanced-bugbounty-mcp.git`
3. Create a branch: `git checkout -b feature/amazing-feature`
4. Make your changes
5. Test your changes
6. Commit: `git commit -m 'Add amazing feature'`
7. Push: `git push origin feature/amazing-feature`
8. Open a Pull Request

## Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt
pip install pytest pytest-asyncio black flake8 mypy

# Run tests
pytest tests/

# Format code
black mcp_server/

# Lint
flake8 mcp_server/
```

## Code Style

- Follow PEP 8 guidelines
- Use type hints
- Write docstrings for all functions
- Keep functions focused and small
- Add tests for new features

## Pull Request Process

1. Update README.md with details of changes
2. Update documentation if needed
3. Add tests for new functionality
4. Ensure all tests pass
5. Update CHANGELOG.md

## Bug Reports

When filing a bug report, include:

- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- System information
- Logs if applicable

## Feature Requests

For feature requests, please:

- Clearly describe the feature
- Explain why it's needed
- Provide examples if possible
- Consider implementation details

## Questions?

Open a discussion on GitHub Discussions or file an issue.

Thank you for contributing! 🚀