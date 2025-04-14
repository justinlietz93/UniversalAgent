"""Tests for the OpenAI-compatible adapter."""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any, Optional

from src.universal_agent.adapters.openai_compatible_adapter import OpenAICompatibleAdapter


# Test fixture for OpenAICompatibleAdapter
@pytest.fixture
def mock_adapter():
    """Create a mock OpenAICompatibleAdapter instance for testing."""
    # Create mock credentials and config
    credentials = {"api_key": "test_key"}
    config = {"base_url": "http://localhost:11434/api", "model": "llama3"}
    
    # Create the adapter
    with patch('httpx.AsyncClient') as mock_client:
        adapter = OpenAICompatibleAdapter(
            provider="openai_compatible",
            credentials=credentials,
            config=config
        )
        # Replace the client with a mock
        adapter.client = AsyncMock()
        return adapter


@pytest.mark.asyncio
async def test_initialization():
    """Test initialization with valid configuration."""
    # Test with API key
    credentials = {"api_key": "test_key"}
    config = {"base_url": "http://localhost:11434/api"}
    
    with patch('httpx.AsyncClient'):
        adapter = OpenAICompatibleAdapter(
            provider="openai_compatible", 
            credentials=credentials,
            config=config
        )
        
        assert adapter.provider == "openai_compatible"
        assert adapter.base_url == "http://localhost:11434/api"
        
    # Test without API key (should also work)
    credentials = {}
    config = {"base_url": "http://localhost:11434/api"}
    
    with patch('httpx.AsyncClient'):
        adapter = OpenAICompatibleAdapter(
            provider="openai_compatible", 
            credentials=credentials,
            config=config
        )
        
        assert adapter.provider == "openai_compatible"
        assert adapter.base_url == "http://localhost:11434/api"


def test_initialization_fails_without_base_url():
    """Test initialization fails when base_url is missing."""
    credentials = {"api_key": "test_key"}
    config = {}  # Missing base_url
    
    with pytest.raises(ValueError) as excinfo:
        OpenAICompatibleAdapter(
            provider="openai_compatible", 
            credentials=credentials,
            config=config
        )
    
    assert "base_url" in str(excinfo.value)


def test_determine_tool_invocation_mode(mock_adapter):
    """Test the tool invocation mode determination."""
    # Default is prompt_engineered for safety
    assert mock_adapter._determine_tool_invocation_mode() == "prompt_engineered"
    
    # Test explicit setting in config
    mock_adapter.config["tool_invocation_mode"] = "native"
    assert mock_adapter._determine_tool_invocation_mode() == "native"
    
    mock_adapter.config["tool_invocation_mode"] = "prompt_engineered"
    assert mock_adapter._determine_tool_invocation_mode() == "prompt_engineered"
    
    # Test invalid value falls back to prompt_engineered
    mock_adapter.config["tool_invocation_mode"] = "invalid"
    assert mock_adapter._determine_tool_invocation_mode() == "prompt_engineered"


@pytest.mark.asyncio
async def test_generate_response_success(mock_adapter):
    """Test successful response generation."""
    # Setup mock response
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": "This is a test response"
                }
            }
        ]
    }
    mock_response.raise_for_status = MagicMock()
    
    # Setup mock client post
    mock_adapter.client.post = AsyncMock(return_value=mock_response)
    
    # Call generate_response
    response = await mock_adapter.generate_response("Test prompt", [])
    
    # Verify result
    assert response == "This is a test response"
    
    # Verify API call
    mock_adapter.client.post.assert_called_once()
    args, kwargs = mock_adapter.client.post.call_args
    assert args[0] == "/v1/chat/completions"
    assert "json" in kwargs
    
    # Check request payload
    payload = kwargs["json"]
    assert payload["messages"][0]["content"] == "Test prompt"
    assert payload["model"] == "llama3"  # From fixture config


@pytest.mark.asyncio
async def test_generate_response_with_system_prompt(mock_adapter):
    """Test response generation with system prompt."""
    # Add system prompt to config
    mock_adapter.config["system_prompt"] = "You are a helpful assistant."
    
    # Setup mock response
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": "This is a test response"
                }
            }
        ]
    }
    mock_response.raise_for_status = MagicMock()
    
    # Setup mock client post
    mock_adapter.client.post = AsyncMock(return_value=mock_response)
    
    # Call generate_response
    response = await mock_adapter.generate_response("Test prompt", [])
    
    # Verify result
    assert response == "This is a test response"
    
    # Verify API call
    mock_adapter.client.post.assert_called_once()
    args, kwargs = mock_adapter.client.post.call_args
    
    # Check request payload includes system message
    payload = kwargs["json"]
    assert len(payload["messages"]) == 2
    assert payload["messages"][0]["role"] == "system"
    assert payload["messages"][0]["content"] == "You are a helpful assistant."
    assert payload["messages"][1]["role"] == "user"
    assert payload["messages"][1]["content"] == "Test prompt"


@pytest.mark.asyncio
async def test_generate_response_http_error(mock_adapter):
    """Test response generation with HTTP error."""
    # Setup mock client post to raise an exception
    import httpx
    mock_adapter.client.post = AsyncMock(side_effect=httpx.HTTPStatusError("Error", request=MagicMock(), response=MagicMock()))
    
    # Call generate_response
    response = await mock_adapter.generate_response("Test prompt", [])
    
    # Verify result contains error message
    assert "Error: API request failed" in response


@pytest.mark.asyncio
async def test_extract_tool_call_json_block(mock_adapter):
    """Test extracting tool call from JSON block response."""
    # Test response with a JSON block
    response = """
    Here's what I can do for you:
    ```json
    {
        "name": "get_weather",
        "arguments": {
            "location": "New York",
            "units": "metric"
        }
    }
    ```
    """
    
    # Call extract_tool_call
    tool_call = await mock_adapter.extract_tool_call(response)
    
    # Verify result
    assert tool_call is not None
    assert tool_call["tool_name"] == "get_weather"
    assert tool_call["arguments"]["location"] == "New York"
    assert tool_call["arguments"]["units"] == "metric"


@pytest.mark.asyncio
async def test_extract_tool_call_inline_json(mock_adapter):
    """Test extracting tool call from inline JSON response."""
    # Test response with inline JSON
    response = """
    I'll help you with that. {"name": "search_web", "arguments": {"query": "latest news"}}
    """
    
    # Call extract_tool_call
    tool_call = await mock_adapter.extract_tool_call(response)
    
    # Verify result
    assert tool_call is not None
    assert tool_call["tool_name"] == "search_web"
    assert tool_call["arguments"]["query"] == "latest news"


@pytest.mark.asyncio
async def test_extract_tool_call_no_json(mock_adapter):
    """Test extracting tool call from response with no JSON."""
    # Test response with no JSON
    response = "I don't know how to do that."
    
    # Call extract_tool_call
    tool_call = await mock_adapter.extract_tool_call(response)
    
    # Verify result
    assert tool_call is None


@pytest.mark.asyncio
async def test_process_tool_result(mock_adapter):
    """Test processing tool result."""
    # Setup
    prompt = "What's the weather in New York?"
    response = "I'll check the weather for you."
    tool_call = {
        "tool_name": "get_weather",
        "arguments": {"location": "New York"}
    }
    tool_result = {
        "temperature": 22,
        "conditions": "Cloudy"
    }
    
    # Mock generate_response
    mock_adapter.generate_response = AsyncMock(return_value="The weather in New York is 22°C and cloudy.")
    
    # Call process_tool_result
    result = await mock_adapter.process_tool_result(prompt, response, tool_call, tool_result)
    
    # Verify result
    assert result == "The weather in New York is 22°C and cloudy."
    
    # Verify generate_response was called with correct arguments
    mock_adapter.generate_response.assert_called_once()
    args, kwargs = mock_adapter.generate_response.call_args
    assert prompt in args[0]  # Original prompt included
    assert "get_weather" in args[0]  # Tool name included
    assert "22" in args[0] or '"temperature": 22' in args[0]  # Tool result included


@pytest.mark.asyncio
async def test_format_tools_for_openai(mock_adapter):
    """Test formatting tools for OpenAI API format."""
    # Test tool descriptions
    tool_descriptions = [
        {
            "name": "get_weather",
            "description": "Get weather information for a location",
            "input_schema": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city or location"
                    },
                    "units": {
                        "type": "string",
                        "enum": ["metric", "imperial"],
                        "default": "metric"
                    }
                },
                "required": ["location"]
            }
        }
    ]
    
    # Call _format_tools_for_openai
    openai_tools = mock_adapter._format_tools_for_openai(tool_descriptions)
    
    # Verify result
    assert len(openai_tools) == 1
    assert openai_tools[0]["name"] == "get_weather"
    assert openai_tools[0]["description"] == "Get weather information for a location"
    assert "parameters" in openai_tools[0]
    assert openai_tools[0]["parameters"]["properties"]["location"]["type"] == "string"
