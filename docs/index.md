# Universal Agent Documentation

This is the comprehensive documentation for the Universal Agent project, which offers two complementary approaches:

1. **Universal Agent Protocol** - A natural language interface to tools using transformer-based NLP (documented in [api.md](api.md))
2. **Provider Integration** - A universal wrapper for LLM providers like OpenAI, Gemini, etc. (documented in [api/api.md](api/api.md))

## Documentation Structure

The documentation is organized according to the [Table of Contents](table_of_contents.md) which provides a complete overview of all documentation resources.

### Core Documentation

- [Architecture Overview](architecture.md) - The system architecture and data flow of the Universal Agent Protocol
- [API Specification](api.md) - Core interfaces, data structures, and API endpoints
- [Tool Adaptation Plan](tool_adaptation_plan.md) - Strategy for adapting existing tools to the framework

### API Reference

- [API Reference](./api/reference.md) - Comprehensive reference for all Universal Agent API classes and methods
- [Custom Tools Guide](./api/custom_tools.md) - Guide to creating and using custom tools

### Integration Guides

- [General Integration](./integration/integration.md) - Guide to integrating Universal Agent with existing systems
- [Provider Integration](./integration/provider_integration.md) - Guide to integrating with different LLM providers

### Use Cases

- [Use Case Examples](./use_cases/use_cases.md) - Detailed examples of implementing Universal Agent for specific use cases
- [UI Components](./use_cases/components/USE_CASES_REACT_COMPONENT.md) - React component examples for use with Universal Agent

### Testing & Analysis

- [Test Result Analysis](Test_Result_Analysis.md) - Results from test execution and performance analysis

## Quick Start

For a quick introduction to Universal Agent, see the [README](../README.md).

### Provider-Based Usage

```python
from universal_agent import UniversalAgent

# Initialize the agent with a provider
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

### Natural Language Interface

```python
from src.universal_agent.core.agent import UniversalAgent
from src.universal_agent.router.router import Router
from src.universal_agent.utils.nlp_parser import NlpParser
from src.universal_agent.tools.file_tool import FileReaderTool, FileWriterTool

# Initialize core components
router = Router()
nlp_parser = NlpParser()  # Uses Hugging Face Transformers (T5 model)

# Create agent with NLP capabilities
agent = UniversalAgent(router=router, nlp_parser=nlp_parser)

# Register tools with the router
router.register_tool(FileReaderTool())
router.register_tool(FileWriterTool())

# Execute natural language commands directly
result = await agent.execute("read the file 'config.json'")
print(f"Status: {result['status']}")
print(f"Content: {result['result']}")

# The NLP parser automatically extracts intent and parameters
result = await agent.execute("save 'Hello World' to a file called example.txt")
print(f"Status: {result['status']}")
print(f"Message: {result['message']}")
```

## Configuration

Universal Agent uses a centralized configuration system that supports:

- Provider-specific settings
- Authentication configuration
- Tool capability limits
- Regex patterns for tool call detection
- Security settings

For more information, see the [Configuration](./guides/configuration.md) guide.
