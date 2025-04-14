"""Tests for the BaseTool class."""

import pytest
import asyncio
from typing import Dict, Any, Optional

from src.universal_agent.tools.base_tool import BaseTool
from src.universal_agent.interfaces.types import ToolParams, ToolResult


class MockTool(BaseTool):
    """Mock tool implementation for testing BaseTool functionality."""
    
    def __init__(self):
        """Initialize the mock tool."""
        super().__init__(
            id="mock_tool",
            name="Mock Tool",
            description="A mock tool for testing."
        )
    
    def get_parameter_schema(self) -> Dict[str, Any]:
        """Return a parameter schema for testing."""
        return {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "A test message."
                }
            },
            "required": ["message"]
        }
    
    async def execute(self, params: ToolParams) -> ToolResult:
        """Return a mock result."""
        validation_error = self.validate_parameters(params)
        if validation_error:
            return self.create_error_result(validation_error)
        
        message = params.get("message", "")
        return self.create_success_result({
            "message": message,
            "processed": True
        })


class InvalidMockTool(BaseTool):
    """Invalid mock tool that doesn't implement execute."""
    
    def __init__(self):
        """Initialize the invalid mock tool."""
        super().__init__(
            id="invalid_tool",
            name="Invalid Tool",
            description="A tool that doesn't implement execute."
        )


@pytest.mark.asyncio
async def test_base_tool_properties():
    """Test that BaseTool properties work correctly."""
    tool = MockTool()
    
    assert tool.id == "mock_tool"
    assert tool.name == "Mock Tool"
    assert tool.description == "A mock tool for testing."
    
    # Test that get_parameter_schema works
    schema = tool.get_parameter_schema()
    assert schema is not None
    assert schema["type"] == "object"
    assert "message" in schema["properties"]
    assert schema["required"] == ["message"]


@pytest.mark.asyncio
async def test_parameter_validation():
    """Test parameter validation functionality."""
    tool = MockTool()
    
    # Valid parameters
    assert tool.validate_parameters({"message": "Hello"}) is None
    
    # Missing required parameter
    error = tool.validate_parameters({})
    assert error is not None
    assert "Missing required parameter: message" in error


@pytest.mark.asyncio
async def test_execute_with_valid_params():
    """Test execute with valid parameters."""
    tool = MockTool()
    
    result = await tool.execute({"message": "Hello"})
    
    assert result.success is True
    assert result.data["message"] == "Hello"
    assert result.data["processed"] is True
    assert result.error is None


@pytest.mark.asyncio
async def test_execute_with_invalid_params():
    """Test execute with invalid parameters."""
    tool = MockTool()
    
    result = await tool.execute({})
    
    assert result.success is False
    assert result.error is not None
    assert "Missing required parameter: message" in result.error
    assert result.data is None


@pytest.mark.asyncio
async def test_helper_methods():
    """Test helper methods for creating results."""
    tool = MockTool()
    
    # Test create_error_result
    error_result = tool.create_error_result("Test error")
    assert error_result.success is False
    assert error_result.error == "Test error"
    assert error_result.data is None
    
    # Test create_success_result
    success_result = tool.create_success_result({"test": "data"})
    assert success_result.success is True
    assert success_result.data == {"test": "data"}
    assert success_result.error is None


@pytest.mark.asyncio
async def test_not_implemented_execute():
    """Test that NotImplementedError is raised when execute is not implemented."""
    tool = InvalidMockTool()
    
    with pytest.raises(NotImplementedError):
        await tool.execute({})
