# Provider Integration Guide

The Universal Agent is designed to work with any LLM provider through its dynamic discovery system. This guide explains how to integrate with specific providers and how to add support for new providers.

## Supported Providers

The following providers are supported out of the box:

- **OpenAI**: GPT-3.5, GPT-4
- **Google Gemini**: Gemini 1.0, Gemini 1.5, Gemini Pro
- **Anthropic**: Claude 1, Claude 2, Claude Instant
- **Mistral AI**: Mistral models

## Using Built-in Providers

### OpenAI

```python
from universal_agent import UniversalAgent

agent = UniversalAgent(
    provider="openai",
    credentials={
        "api_key": "your-openai-api-key"
    },
    config={
        "model": "gpt-4",
        "temperature": 0.7,
        "max_tokens": 1024
    }
)
```

### Google Gemini

```python
from universal_agent import UniversalAgent

agent = UniversalAgent(
    provider="gemini",
    credentials={
        "api_key": "your-gemini-api-key"
    },
    config={
        "model": "gemini-pro",
        "temperature": 0.2
    }
)
```

### Anthropic

```python
from universal_agent import UniversalAgent

agent = UniversalAgent(
    provider="anthropic",
    credentials={
        "api_key": "your-anthropic-api-key"
    },
    config={
        "model": "claude-2",
        "temperature": 0.5
    }
)
```

### Mistral AI

```python
from universal_agent import UniversalAgent

agent = UniversalAgent(
    provider="mistral",
    credentials={
        "api_key": "your-mistral-api-key"
    },
    config={
        "model": "mistral-medium",
        "temperature": 0.7
    }
)
```

## Using the Generic Adapter

For providers that don't have a dedicated adapter, you can use the generic adapter with custom configuration:

```python
from universal_agent import UniversalAgent

agent = UniversalAgent(
    provider="custom",
    credentials={
        "api_key": "your-provider-api-key"
    },
    config={
        "api_url": "https://api.yourprovider.com/completions",
        "auth_method": "api_key",
        "auth_header": "Authorization",
        "auth_prefix": "Bearer ",
        "request_format": {
            "model": "{model}",
            "prompt": "{prompt}",
            "temperature": "{temperature}",
            "max_tokens": "{max_tokens}",
            "tools_key": "functions",
            "tools_format": {
                "name": "{name}",
                "description": "{description}",
                "parameters": "{parameters}"
            }
        },
        "response_format": {
            "content_path": "choices[0].message.content",
            "tool_call_path": "choices[0].message.function_call"
        }
    }
)
```

### Generic Adapter Configuration Options

The generic adapter supports the following configuration options:

- **api_url**: The API endpoint URL for completions
- **auth_method**: Authentication method (e.g., "api_key", "oauth")
- **auth_header**: HTTP header for authentication
- **auth_prefix**: Prefix for authentication value (e.g., "Bearer ")
- **request_format**: Template for formatting API requests
  - Use placeholders like `{model}`, `{prompt}`, etc.
- **response_format**: Template for parsing API responses
  - **content_path**: JSON path to extract the response content
  - **tool_call_path**: JSON path to extract tool calls

## Creating a Custom Adapter

For more advanced integration, you can create a custom adapter by extending the `BaseLLMAdapter` class:

```python
from universal_agent.adapters.base import BaseLLMAdapter

class MyProviderAdapter(BaseLLMAdapter):
    def __init__(
        self,
        provider: str,
        credentials: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None,
        capabilities: Optional[Dict[str, Any]] = None,
        tool_capabilities: Optional[Dict[str, Any]] = None
    ):
        super().__init__(provider, credentials, config, capabilities, tool_capabilities)
        # Initialize your provider-specific client
        self.api_key = credentials.get("api_key")
        self.model = config.get("model", "default-model")
        
    def _initialize_client(self) -> None:
        # Initialize your provider-specific client
        # This could be creating an API client or setting up SDK
        pass
        
    def _determine_tool_invocation_mode(self) -> str:
        # Determine if the provider supports native tool calling
        return "native" if self.capabilities.get("native_tool_calling", False) else "prompt_engineered"
        
    async def generate_response(
        self, 
        prompt: str,
        tool_descriptions: List[Dict[str, Any]] = None
    ) -> str:
        # Implement your provider-specific logic to generate a response
        # This should handle both with and without tools
        pass
        
    async def extract_tool_call(self, response: str) -> Optional[Dict[str, Any]]:
        # Implement your provider-specific logic to extract tool calls
        pass
        
    async def process_tool_result(
        self, 
        prompt: str,
        response: str,
        tool_call: Dict[str, Any],
        tool_result: Dict[str, Any]
    ) -> str:
        # Implement your provider-specific logic to process tool results
        pass
        
    async def generate_streaming_response(
        self, 
        prompt: str,
        tool_descriptions: List[Dict[str, Any]] = None
    ) -> AsyncGenerator[str, None]:
        # Implement your provider-specific logic for streaming
        pass
```

## Registering a Custom Adapter

Once you've created a custom adapter, you can register it with the adapter factory:

```python
from universal_agent import UniversalAgent
from universal_agent.adapters.adapter_factory import LLMAdapterFactory
from my_module import MyProviderAdapter

# Register your adapter
factory = LLMAdapterFactory()
factory._register_adapter("myprovider", MyProviderAdapter)

# Create an agent with your provider
agent = UniversalAgent(
    provider="myprovider",
    credentials={"api_key": "your-api-key"},
    config={"model": "your-model"}
)
```

## Advanced: Dynamic Capabilities Discovery

If you want to take advantage of the dynamic capabilities discovery feature:

1. Add your provider's documentation sources to the `DocumentationAnalyzer.doc_sources` dictionary:

```python
from universal_agent.documentation.documentation_analyzer import DocumentationAnalyzer

analyzer = DocumentationAnalyzer()
analyzer.doc_sources["myprovider"] = {
    "api_docs": "https://api.myprovider.com/docs",
    "function_calling_docs": "https://api.myprovider.com/docs/function-calling",
    "github_repo": "https://github.com/myprovider/sdk"
}
```

2. Add a provider-specific analyzer method:

```python
async def _analyze_myprovider_capabilities(self, documentation: str, capabilities: Dict[str, Any]) -> Dict[str, Any]:
    # Check for API key authentication
    if "API_KEY" in documentation:
        capabilities["authentication"]["method"] = "api_key"
        capabilities["authentication"]["header"] = "Authorization"
    
    # Check for native tool calling support
    if "function_calling" in documentation or "tools" in documentation:
        capabilities["native_tool_calling"] = True
        capabilities["tool_calling_format"] = "myprovider_function_calling"
    
    # Check for streaming support
    if "stream=true" in documentation.lower():
        capabilities["streaming_support"] = True
        capabilities["streaming_protocol"] = "server_sent_events"
    
    # Extract model information
    model_pattern = r"model-([\w-]+)"
    models = re.findall(model_pattern, documentation)
    capabilities["models"] = list(set(models))
    
    return capabilities
```

3. Add handling in the `analyze_capabilities` method:

```python
async def analyze_capabilities(self, provider: str, documentation: str) -> Dict[str, Any]:
    # ...existing code...
    
    if provider.lower() == "myprovider":
        capabilities = await self._analyze_myprovider_capabilities(documentation, capabilities)
    else:
        # ...existing code...
```

## Troubleshooting

If you encounter issues with a specific provider:

1. **Debug Mode**: Enable debug logging to see detailed information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

2. **Manual Capability Override**: If automatic capability detection doesn't work correctly:

```python
agent = UniversalAgent(
    provider="myprovider",
    credentials={"api_key": "your-api-key"},
    config={
        "capabilities": {
            "native_tool_calling": True,
            "tool_calling_format": "myprovider_format",
            "streaming_support": True
        }
    }
)
```

3. **Request/Response Inspection**: Use the debug logger to inspect raw requests and responses:

```python
import logging
logging.getLogger("universal_agent.adapters").setLevel(logging.DEBUG)
