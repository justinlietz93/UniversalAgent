# Contributing to Universal Agent

Thank you for your interest in contributing to the Universal Agent project! This document provides guidelines and instructions for contributing.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** to your local machine
3. **Install development dependencies** with `pip install -e ".[dev]"`
4. **Create a new branch** for your feature or bugfix

## Development Process

### Setting Up Your Environment

```bash
# Clone your fork
git clone https://github.com/your-username/UniversalAgent.git
cd UniversalAgent

# Install development dependencies
pip install -e ".[dev]"

# Install required libraries for transformer-based NLP
pip install transformers torch sentencepiece
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test modules
python -m pytest tests/unit/test_agent.py tests/unit/test_nlp_parser.py

# Run tests with coverage
python -m pytest --cov=src
```

## Code Style and Standards

We follow these coding standards:

- Use **PEP 8** styling for Python code
- Document all classes and methods with docstrings
- Maintain test coverage for all new code
- Follow the established project architecture and patterns

## Pull Request Process

1. Ensure your code passes all tests and linting checks
2. Update documentation as necessary for your changes
3. Add appropriate test coverage for your changes
4. Submit a pull request with a clear description of the changes and their purpose
5. Link any related issues in your pull request

## Core Components

When contributing to core components, be mindful of:

### Transformer NLP Parser

The NLP parser is a crucial component of the Universal Agent framework:

- Uses Hugging Face Transformers (T5 model) for natural language parsing
- Includes multi-level fallback mechanisms for robustness
- Structured to provide consistent output regardless of model availability

### Router

The Router component handles dynamic tool routing:

- Maintains a registry of available tools
- Routes requests to the appropriate tool based on the NLP parser output
- Provides standardized error handling

### Universal Agent

The main agent class orchestrates the flow:

- Connects the NLP parser with the router
- Provides a simple `execute(command)` interface
- Formats responses consistently

## Reporting Issues

When reporting issues, please include:

- A clear description of the problem
- Steps to reproduce the issue
- Expected vs. actual behavior
- Any relevant logs or error messages
- Environment information (Python version, OS, etc.)

## License

By contributing to the Universal Agent project, you agree that your contributions will be licensed under the project's MIT license.
