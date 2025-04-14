# Using Universal Agent with Self-Hosted Models

The Universal Agent framework supports connecting to self-hosted, OpenAI-compatible API endpoints like Ollama, LM Studio, or custom LLM deployments. This guide explains how to configure and use the framework with these self-hosted models.

## Overview

The OpenAI-compatible adapter allows the Universal Agent to connect to any model server that implements the OpenAI API standard. This includes:

- [Ollama](https://ollama.ai/) (for running Llama, Mistral, and other open-source models locally)
- [LM Studio](https://lmstudio.ai/) (local inference server)
- [LocalAI](https://localai.io/) (self-hosted API compatible with OpenAI)
- Custom model deployments that implement the OpenAI API schema

## Configuration

To use a self-hosted model, you'll need to:

1. Run your model server locally or on a remote machine
2. Configure the Universal Agent to connect to your model server

### Sample Configuration

Here's a sample configuration for connecting to a self-hosted model:

```json
{
    "universal_agent": {
        "providers": {
            "openai_compatible": {
                "base_url": "http://localhost:11434/v1",
                "model": "llama3",
                "temperature": 0.7,
                "max_tokens": 2048,
                "system_prompt": "You are a helpful assistant. Answer as concisely as possible.",
                "tool_invocation_mode": "prompt_engineered"
            }
        },
        "default_provider": "openai_compatible"
    }
}
```

### Configuration Parameters

| Parameter | Description | Required | Default |
|-----------|-------------|----------|---------|
| `base_url` | The base URL of your model server's API endpoint | Yes | - |
| `model` | The model name to use on the server | Yes | - |
| `temperature` | Temperature for sampling (0.0-1.0) | No | 0.7 |
| `max_tokens` | Maximum tokens in the response | No | 1024 |
| `system_prompt` | System prompt to use for the model | No | - |
| `tool_invocation_mode` | Mode for tool invocation: "native" or "prompt_engineered" | No | "prompt_engineered" |

## Authentication

Many self-hosted model servers don't require authentication. However, if your server requires an API key, you can provide it in the credentials:

```json
{
    "credentials": {
        "openai_compatible": {
            "api_key": "your-api-key"
        }
    }
}
```

## Setting Up Common Model Servers

### Ollama

1. **Install Ollama**:
   - Follow the installation instructions at [ollama.ai](https://ollama.ai/)

2. **Pull a model**:
   ```bash
   ollama pull llama3
   ```

3. **Start the server**:
   ```bash
   ollama serve
   ```

4. **Configure Universal Agent**:
   - Set the `base_url` to `http://localhost:11434/v1`
   - Set the `model` to the name of the pulled model (e.g., `"llama3"`)

### LM Studio

1. **Install LM Studio**:
   - Download from [lmstudio.ai](https://lmstudio.ai/)

2. **Load a model in LM Studio**:
   - Open LM Studio and download a model

3. **Start the local inference server**:
   - Click on "Local Inference Server" in LM Studio
   - Start the server

4. **Configure Universal Agent**:
   - Set the `base_url` to `http://localhost:1234/v1` (or the port you configured)
   - Set the `model` to the name shown in LM Studio

## Tool Support

Not all self-hosted models support native function calling (OpenAI's functions format). The Universal Agent can work with any model regardless of function calling support, thanks to two different tool invocation modes.

### Tool Invocation Modes

The OpenAICompatibleAdapter supports two tool invocation modes:

1. **`prompt_engineered`** (Default): Works with ANY model, regardless of function calling support
   - Tools are described in natural language within the prompt
   - The model is instructed to generate JSON in its response when it wants to use a tool
   - More flexible but potentially less reliable

2. **`native`**: Only works with models that support OpenAI's function calling API
   - Tools are passed to the model via the API's dedicated function calling mechanism
   - More reliable and structured but requires models with specific capabilities
   - Recommended for models tagged with "tools" in the Ollama library

### Choosing the Right Mode

**For models with the "tools" tag in Ollama:**
```json
"tool_invocation_mode": "native"
```

**For all other models:**
```json
"tool_invocation_mode": "prompt_engineered"
```

### Configuration Example

Here's how to configure different tool invocation modes:

```json
{
    "universal_agent": {
        "providers": {
            "openai_compatible": {
                "base_url": "http://localhost:11434/v1",
                "model": "llama3.3",  // A model with "tools" support
                "tool_invocation_mode": "native"
            }
        }
    }
}
```

For a model without native function calling:

```json
{
    "universal_agent": {
        "providers": {
            "openai_compatible": {
                "base_url": "http://localhost:11434/v1",
                "model": "gemma",  // A model without "tools" support
                "tool_invocation_mode": "prompt_engineered"
            }
        }
    }
}
```

### Performance Considerations

- **Native mode** typically provides more reliable and consistent tool calling but requires compatible models
- **Prompt-engineered mode** works with any model but may be less reliable for complex tool interactions
- Larger models generally perform better with both modes
- When using prompt-engineered mode with smaller models, you may need to provide more explicit instructions

## Usage Example

Here's how to use the Universal Agent with a self-hosted model in your code:

```python
from src.universal_agent import UniversalAgent
import json

# Load the configuration
with open("config/self_hosted.json", "r") as f:
    config = json.load(f)

# Create the agent with the configuration
agent = UniversalAgent(
    provider="openai_compatible",
    credentials={},  # No API key needed for local models
    config=config["universal_agent"]["providers"]["openai_compatible"]
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
        # Simple evaluation for demo purposes
        result = eval(expression)
        return {"result": result}

# Use the agent
response = await agent.generate_response("What's 135 * 27?")
print(response)
```

## Troubleshooting

### Model Not Found

If you get an error like "Model not found", make sure:
- The model name matches exactly what's on your server
- For Ollama, make sure you've pulled the model first with `ollama pull <model>`

### Connection Errors

If you see connection errors:
- Verify your model server is running
- Check that the `base_url` is correct, including the `/v1` path
- Ensure there are no network restrictions blocking the connection

### Response Format Issues

If you see issues with the response format:
- Different models may have different response structures
- Check if your model fully implements the OpenAI API format
- Consider using a more recent model version that better supports the OpenAI API

## Supported Models

The adapter has been tested with the following models:

- Llama 3 (8B, 70B) via Ollama
- Mistral (7B) via Ollama
- Phi-2 via LM Studio
- Gemma (2B, 7B) via Ollama

However, it should work with any model server that implements the OpenAI API standard.

### Recommended Models with Tool/Function Calling Support

For the best experience with tool/function calling using the "native" tool invocation mode, we recommend these Ollama models tagged with "tools" support:

- **llama3.3** (70B) - Latest version with strong tool support
- **qwen2.5** (0.5B to 72B) - Multiple sizes with tool capabilities
- **mistral-small3.1** (24B) - Includes vision and tool support
- **phi4-mini** (3.8B) - Lightweight model with function calling
- **mistral-large** (123B) - Flagship model with extensive tool capabilities
- **granite3.1-dense** (2B, 8B) - Optimized for tool-based use cases
- **granite3.2** (2B, 8B) - Designed for advanced thinking capabilities

For a complete list of available models, see the [Ollama Models Library](https://ollama.com/library).

### Models for Specific Use Cases

Depending on your needs, consider these specialized models:

- **Code Generation**: codegemma, deepseek-coder-v2, codellama, qwen2.5-coder
- **Vision Capabilities**: llava, moondream, mistral-small3.1, llama3.2-vision 
- **Embedding Models**: nomic-embed-text, mxbai-embed-large, bge-large
- **Math & Reasoning**: deepseek-r1, openthinker, mathstral, qwen2-math
- **Lightweight Options**: phi4-mini (3.8B), gemma (2B), llama3.2 (3B), smollm2 (1.7B)
