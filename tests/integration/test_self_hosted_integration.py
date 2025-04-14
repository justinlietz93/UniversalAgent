"""Integration tests for the self-hosted model adapter."""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any, Optional

from src.universal_agent.adapters.openai_compatible_adapter import OpenAICompatibleAdapter
from src.universal_agent.core.agent import UniversalAgent
from src.universal_agent.router.router import Router
from src.universal_agent.tools.base_tool import BaseTool
from src.universal_agent.interfaces.types import ToolParams, ToolResult


# Test tool for integration testing
class CalculatorTool(BaseTool):
    """A simple calculator tool for testing."""
    
    def __init__(self):
        """Initialize calculator tool."""
        super().__init__(
            id="calculator",
            name="Calculator Tool",
            description="Perform mathematical calculations."
        )
    
    def get_parameter_schema(self) -> Dict[str, Any]:
        """Return parameter schema for calculator."""
        return {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The mathematical expression to evaluate."
                }
            },
            "required": ["expression"]
        }
    
    async def execute(self, params: ToolParams) -> ToolResult:
        """Execute calculator function."""
        try:
            expression = params.get("expression")
            if not expression:
                return self.create_error_result("Expression parameter is required")
            
            # Simple safe eval for demonstration (real implementation would use a safer approach)
            result = eval(expression, {"__builtins__": {}}, {"abs": abs, "round": round, "min": min, "max": max})
            
            return self.create_success_result({
                "result": result
            })
        except Exception as e:
            return self.create_error_result(f"Error calculating result: {str(e)}")


@pytest.mark.asyncio
async def test_agent_with_self_hosted_adapter():
    """Test the UniversalAgent with self-hosted adapter."""
    # Mock configuration
    config = {
        "base_url": "http://localhost:11434/v1",
        "model": "llama3",
        "temperature": 0.7,
        "max_tokens": 1024
    }
    
    # Mock credentials (empty for self-hosted)
    credentials = {}
    
    # Create router
    router = Router()
    
    # Create and register calculator tool
    calculator_tool = CalculatorTool()
    router.register_tool(calculator_tool)
    
    # Mock adapter response for the test
    with patch("src.universal_agent.adapters.openai_compatible_adapter.OpenAICompatibleAdapter") as MockAdapter:
        # Setup mock adapter behavior
        mock_adapter_instance = AsyncMock()
        mock_adapter_instance.generate_response.return_value = "To calculate 25 + 15, I'll use the calculator tool."
        mock_adapter_instance.extract_tool_call.return_value = {
            "tool_name": "calculator",
            "arguments": {"expression": "25+15"}
        }
        mock_adapter_instance.process_tool_result.return_value = "The result of 25 + 15 is 40."
        MockAdapter.return_value = mock_adapter_instance
        
        # Create agent with mock adapter
        agent = UniversalAgent(
            provider="openai_compatible",
            credentials=credentials,
            config=config,
            router=router
        )
        
        # Test agent with a command that should trigger the calculator tool
        result = await agent.execute("What's 25 + 15?")
        
        # Validate results
        assert result.status == "success"
        assert "40" in result.message
        
        # Verify the adapter methods were called correctly
        mock_adapter_instance.generate_response.assert_called()
        mock_adapter_instance.extract_tool_call.assert_called()
        mock_adapter_instance.process_tool_result.assert_called()


@pytest.mark.asyncio
async def test_agent_basic_response_without_tool():
    """Test the UniversalAgent with self-hosted adapter for basic response."""
    # Mock configuration
    config = {
        "base_url": "http://localhost:11434/v1",
        "model": "llama3",
        "temperature": 0.7,
        "max_tokens": 1024
    }
    
    # Create router
    router = Router()
    
    # Mock adapter response for the test
    with patch("src.universal_agent.adapters.openai_compatible_adapter.OpenAICompatibleAdapter") as MockAdapter:
        # Setup mock adapter behavior
        mock_adapter_instance = AsyncMock()
        mock_adapter_instance.generate_response.return_value = "Hello! I'm a self-hosted model assistant. How can I help you today?"
        mock_adapter_instance.extract_tool_call.return_value = None  # No tool call
        MockAdapter.return_value = mock_adapter_instance
        
        # Create agent with mock adapter
        agent = UniversalAgent(
            provider="openai_compatible",
            credentials={},  # Empty credentials
            config=config,
            router=router
        )
        
        # Test agent with a basic command
        result = await agent.execute("Hello, how are you?")
        
        # Validate results
        assert result.status == "success"
        assert "Hello" in result.message
        
        # Verify the adapter methods were called correctly
        mock_adapter_instance.generate_response.assert_called()
        mock_adapter_instance.extract_tool_call.assert_called()
        # process_tool_result should not be called for basic responses
        mock_adapter_instance.process_tool_result.assert_not_called()
