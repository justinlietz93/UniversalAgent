# Universal Agent

A comprehensive framework offering two powerful approaches:

1. **Universal Agent Protocol** - A natural language interface to tools using transformer-based NLP
2. **Provider Integration** - A universal wrapper for LLM providers (OpenAI, Gemini, etc.)

## Key Features

### Universal Agent Protocol (Direct NL Interface)
- **Transformer-Based NLP**: Natural language parsing using Hugging Face Transformers (T5 model)
- **Dynamic Request Routing**: Routes natural language commands to appropriate tools
- **Multiple Fallback Mechanisms**: Ensures robust parsing even if the model fails
- **Unified Tool Interface**: Standard interface for all tools (`ITool`)

### Provider-Based Features
- **Universal Provider Support**: Works with any LLM provider through dynamic capability analysis
- **Automatic Adapter Selection**: Chooses the right adapter based on provider documentation
- **Native & Prompted Tool Support**: Works with both native function calling and prompt engineering
- **Streaming Support**: Handles streaming responses with tool call detection

### Shared Features
- **Security**: Comprehensive security features for safe command execution
- **Tool Ecosystem**: Rich set of built-in tools with consistent interfaces

## Quick Start

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
result = await agent.execute("read file 'config.json'")
print(result)

# Execute another command - the NLP parser will detect intent and parameters
result = await agent.execute("write 'Hello World' to the file example.txt")
print(result)
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
