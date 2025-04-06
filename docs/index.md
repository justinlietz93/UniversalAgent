# Universal Agent Documentation

This is the comprehensive documentation for the Universal Agent project, which provides a universal wrapper for interacting with various LLM providers with dynamic capability discovery and unified tool handling.

## Documentation Structure

The documentation is organized into the following sections:

### API Reference

- [API Reference](./api/reference.md) - Comprehensive reference for all Universal Agent API classes and methods
- [Custom Tools Guide](./api/custom_tools.md) - Guide to creating and using custom tools
- [API Overview](./api/api.md) - High-level overview of the Universal Agent API

### Integration Guides

- [General Integration](./integration/integration.md) - Guide to integrating Universal Agent with existing systems
- [Provider Integration](./integration/provider_integration.md) - Guide to integrating with different LLM providers

### Use Cases

- [Use Case Examples](./use_cases/use_cases.md) - Detailed examples of implementing Universal Agent for specific use cases
- [UI Components](./use_cases/components/USE_CASES_REACT_COMPONENT.md) - React component examples for use with Universal Agent

### Implementation

- [Status](../STATUS.md) - Current status of the Universal Agent implementation
- [Implementation Plan](../IMPLEMENTATION_PLAN.md) - Detailed plan for completing the Universal Agent implementation

## Quick Start

For a quick introduction to Universal Agent, see the [README](../README.md).

```python
from universal_agent import UniversalAgent

# Initialize the agent
agent = UniversalAgent(
    provider="openai",
    credentials={"api_key": "your-api-key"}
)

# Register tools
@agent.register_tool
class CalculatorTool:
    def __init__(self):
        self._name = "calculator"
        self._description = "Perform mathematical calculations"
        self._input_schema = {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The mathematical expression to evaluate"
                }
            },
            "required": ["expression"]
        }
    
    async def run(self, **kwargs):
        expression = kwargs.get("expression")
        result = eval(expression)  # Note: This is simplified; use a safer approach in production
        return {"result": result}

# Get response with potential tool use
response = await agent.generate_response(
    "What's 235 * 89?"
)

print(response)
```

## Configuration

Universal Agent uses a centralized configuration system that supports:

- Provider-specific settings
- Authentication configuration
- Tool capability limits
- Regex patterns for tool call detection
- Security settings

For more information, see the [Configuration](./guides/configuration.md) guide.
