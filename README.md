# Universal Agent

A universal wrapper for interacting with various LLM providers (OpenAI, Gemini, Anthropic, Mistral, etc.) with dynamic capability discovery and unified tool handling.

## Key Features

- **Universal Provider Support**: Works with any LLM provider through dynamic capability analysis
- **Automatic Adapter Selection**: Chooses the right adapter based on provider documentation
- **Unified Tool Interface**: Consistent tool execution across all providers
- **Native & Prompted Tool Support**: Works with both native function calling and prompt engineering
- **Streaming Support**: Handles streaming responses with tool call detection
- **Security**: Comprehensive security features for safe command execution

## Quick Start

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

## Installation

```bash
pip install universal-agent
```

## Documentation

For complete documentation, see the [docs directory](./docs/README.md).

## Supported Providers

- **OpenAI**: GPT-3.5, GPT-4
- **Google**: Gemini 1.0, Gemini 1.5, Gemini Pro
- **Anthropic**: Claude 1, Claude 2, Claude Instant
- **Mistral AI**: Mistral models
- **Generic Providers**: Through configuration-based adapters

## Project Structure

```
src/
├── universal_agent/            # Main package
│   ├── core/                   # Core functionality
│   ├── adapters/               # LLM provider adapters
│   ├── tools/                  # Tool implementations
│   ├── utils/                  # Utility functions
│   └── security/               # Security components
├── documentation/              # Documentation analyzer
```

## License

MIT
