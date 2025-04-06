# Universal Agent Configuration Guide

This guide explains the centralized configuration system used by Universal Agent and how to customize it for your specific needs.

## Configuration Overview

Universal Agent uses a central configuration file (`config.py`) that contains all settings for:

- Provider documentation sources
- Authentication methods for each provider
- Tool calling capabilities and formats
- Regex patterns for tool call detection
- Security settings and sensitive key protection

## Using Environment Variables

You can override configuration values using environment variables:

```python
# Example .env file
OPENAI_API_KEY=your_api_key_here
GEMINI_API_KEY=your_api_key_here
ANTHROPIC_API_KEY=your_api_key_here
MISTRAL_API_KEY=your_api_key_here
UNIVERSAL_AGENT_CACHE_DIR=/path/to/cache
```

When the Universal Agent starts, it will check for these environment variables and use them to override the default configuration.

## Configuration Options

### Provider-Specific Settings

Each provider has specific settings that control its behavior:

```python
# Example configuration for a provider
PROVIDER_CONFIGS = {
    "openai": {
        "model": "gpt-4",
        "temperature": 0.7,
        "max_tokens": 4096,
        "top_p": 1.0,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0
    },
    "gemini": {
        "model": "gemini-pro",
        "temperature": 0.7,
        "max_output_tokens": 2048,
        "top_p": 0.8,
        "top_k": 40
    },
    # Other providers...
}
```

### Authentication Configuration

Authentication settings for each provider:

```python
AUTH_CONFIG = {
    "openai": {
        "method": "api_key",
        "header": "Authorization",
        "prefix": "Bearer ",
        "env_var": "OPENAI_API_KEY"
    },
    "gemini": {
        "method": "api_key",
        "header": "x-goog-api-key",
        "env_var": "GEMINI_API_KEY"
    },
    # Other providers...
}
```

### Tool Capability Settings

Settings that control tool execution and limits:

```python
TOOL_CAPABILITIES = {
    "openai": {
        "schema_format": "openai_functions",
        "maximum_tools": 128,
        "supports_multiple_calls": True,
        "streaming_tool_calls": True
    },
    "gemini": {
        "schema_format": "google_functions",
        "maximum_tools": 64,
        "supports_multiple_calls": True,
        "streaming_tool_calls": False
    },
    # Other providers...
}
```

### Regex Patterns

Patterns used for detecting and extracting tool calls in responses:

```python
REGEX_PATTERNS = {
    "tool_call": {
        "start": r'(```json|\{\"tool\"|\"function_call\"|\"tool_calls\"|<tool>)',
        "end": r'(```|\}\"|\}\]\}|\}\}|</tool>)'
    },
    "json_extraction": {
        "json_block": r'```json\s*(.*?)\s*```',
        "openai_function": r'\"function_call\"\s*:\s*\{(.*?)\}',
        "gemini_tool_calls": r'\"tool_calls\"\s*:\s*\[(.*?)\]',
        "xml_tool": r'<tool>(.*?)</tool>'
    },
    # Other pattern groups...
}
```

### Security Settings

Settings for securing sensitive information and safe execution:

```python
SECURITY = {
    "sensitive_keys": [
        "api_key", "apikey", "key", "secret", "password", "token", "auth",
        "credential", "credentials", "access", "private"
    ],
    "safe_eval_globals": {
        "abs": abs, "round": round, "min": min, "max": max,
        "sum": sum, "len": len
    },
    "safe_eval_locals": {},
    "blocked_commands": [
        "rm", "del", "remove", "system", "exec", "eval", "subprocess"
    ]
}
```

## Customizing Configuration

### Providing Custom Configuration at Runtime

You can provide custom configuration when initializing the agent:

```python
agent = UniversalAgent(
    provider="openai",
    credentials={"api_key": "your-api-key"},
    config={
        "model": "gpt-4",
        "temperature": 0.5,
        "max_tokens": 2048,
        "tool_capabilities": {
            "maximum_tools": 5
        },
        "security": {
            "additional_sensitive_keys": ["customer_id", "account_number"]
        }
    }
)
```

### Adding a New Provider

To add support for a new LLM provider:

1. Update the provider documentation sources:

```python
PROVIDER_DOCS["new_provider"] = {
    "api_docs": "https://api.newprovider.com/docs",
    "function_calling_docs": "https://api.newprovider.com/docs/functions",
    "github_repo": "https://github.com/newprovider/api"
}
```

2. Add authentication configuration:

```python
AUTH_CONFIG["new_provider"] = {
    "method": "api_key",
    "header": "Authorization",
    "prefix": "Bearer ",
    "env_var": "NEW_PROVIDER_API_KEY"
}
```

3. Add tool capabilities:

```python
TOOL_CAPABILITIES["new_provider"] = {
    "schema_format": "openai_compatible",
    "maximum_tools": 50,
    "supports_multiple_calls": True,
    "streaming_tool_calls": False
}
```

4. Register the adapter in the factory:

```python
ADAPTER_REGISTRATIONS.append(("new_provider", "NewProviderAdapter"))
```

### Customizing Tool Execution

You can configure how tools are executed:

```python
agent = UniversalAgent(
    provider="openai",
    credentials={"api_key": "your-api-key"},
    config={
        "tool_execution": {
            "timeout": 10.0,  # Timeout in seconds
            "max_consecutive_calls": 5,  # Max number of consecutive tool calls
            "allow_concurrent": True,  # Allow concurrent tool execution
        }
    }
)
```

## Loading Configuration from Files

You can load configuration from a JSON or YAML file:

```python
import json
from universal_agent import UniversalAgent

# Load configuration from file
with open("agent_config.json", "r") as f:
    config = json.load(f)

# Initialize with loaded config
agent = UniversalAgent(
    provider=config["provider"],
    credentials=config["credentials"],
    config=config["settings"]
)
```

Example configuration file:

```json
{
  "provider": "openai",
  "credentials": {
    "api_key": "your-api-key"
  },
  "settings": {
    "model": "gpt-4",
    "temperature": 0.7,
    "system_prompt": "You are a helpful assistant with access to tools."
  }
}
```

## Best Practices

1. **Use environment variables for sensitive information** - Never hardcode API keys or other sensitive information in your code.

2. **Set appropriate tool limits** - Configure reasonable limits for tool usage to prevent excessive API calls or potential abuse.

3. **Customize security settings** - Add domain-specific sensitive keys to the security settings to prevent accidental exposure.

4. **Use different configurations for different environments** - Create separate configurations for development, testing, and production.

5. **Monitor tool usage** - Configure logging and monitoring to track tool usage and detect potential issues.
