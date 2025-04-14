import pytest
from typing import Dict, Any
from unittest.mock import MagicMock

from src.universal_agent.core.agent import UniversalAgent
from src.universal_agent.interfaces.i_router import IRouter
from src.universal_agent.utils.nlp_parser import NlpParser

# --- Mocks ---

class MockRouter(IRouter):
    """Mock implementation of IRouter for testing UniversalAgent."""
    
    def __init__(self, route_request_return_value: Dict[str, Any] = None):
        self.registered_tools = {}
        self.last_request = None
        self.route_request_called_with = None
        self.route_request_return_value = route_request_return_value or {"success": True, "data": "Mock result"}
    
    def register_tool(self, tool):
        self.registered_tools[tool.id] = tool
    
    def deregister_tool(self, tool_id: str):
        if tool_id in self.registered_tools:
            del self.registered_tools[tool_id]
        else:
            raise KeyError(f"Tool with ID '{tool_id}' not found.")
    
    async def route_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        self.route_request_called_with = request
        self.last_request = request
        return self.route_request_return_value

class MockNlpParser:
    """Mock NlpParser that returns a predefined AgentRequest without depending on the actual NlpParser."""
    def __init__(self, model_name=None):
        """Initialize without loading actual models."""
        pass
        
    async def parse(self, command: str) -> Dict[str, Any]:
        """Mock parse method that returns predefined responses."""
        if "read file" in command.lower():
            return {"tool_id": "file_reader", "params": {"path": command.split("'")[1] if "'" in command else "unknown"}}
        else:
            return {"tool_id": "mock_tool", "params": {}}

# --- Test Cases ---

@pytest.fixture
def success_router():
    """Router that returns a successful tool execution result."""
    return MockRouter(route_request_return_value={"success": True, "data": "Mock successful result"})

@pytest.fixture
def error_router():
    """Router that returns an error result."""
    return MockRouter(route_request_return_value={"success": False, "error": "Mock error message"})

@pytest.fixture
def tool_not_found_router():
    """Router that returns a 'tool not found' error."""
    return MockRouter(route_request_return_value={
        "success": False, 
        "error": "Tool with ID 'unknown_tool' not found."
    })

def test_agent_instantiation():
    """Test that UniversalAgent can be properly instantiated with a valid router."""
    router = MockRouter()
    nlp_parser = MockNlpParser()
    agent = UniversalAgent(router=router, nlp_parser=nlp_parser)
    assert agent._router is router

def test_agent_instantiation_with_invalid_router():
    """Test that UniversalAgent raises TypeError when instantiated with an invalid router."""
    not_a_router = MagicMock()
    nlp_parser = MockNlpParser()
    with pytest.raises(TypeError, match="Router must implement the IRouter interface"):
        UniversalAgent(router=not_a_router, nlp_parser=nlp_parser)

@pytest.mark.asyncio
async def test_agent_execute_success(success_router):
    """Test the execute method's success path."""
    nlp_parser = MockNlpParser()
    agent = UniversalAgent(router=success_router, nlp_parser=nlp_parser)
    result = await agent.execute("test command")
    
    # Check the result structure
    assert result["status"] == "success"
    assert result["result"] == "Mock successful result"
    assert result["message"] == "Command executed successfully."
    
    # Verify router was called
    assert success_router.route_request_called_with is not None
    assert success_router.route_request_called_with["tool_id"] == "mock_tool"

@pytest.mark.asyncio
async def test_agent_execute_error(error_router):
    """Test the execute method's error path."""
    nlp_parser = MockNlpParser()
    agent = UniversalAgent(router=error_router, nlp_parser=nlp_parser)
    result = await agent.execute("test command")
    
    # Check the result structure for error
    assert result["status"] == "error"
    assert result["result"] is None
    assert "Tool execution failed" in result["message"]
    assert "Mock error message" in result["message"]
    
    # Verify router was called
    assert error_router.route_request_called_with is not None
    assert error_router.route_request_called_with["tool_id"] == "mock_tool"

@pytest.mark.asyncio
async def test_agent_execute_tool_not_found(tool_not_found_router):
    """Test the execute method when a tool is not found."""
    nlp_parser = MockNlpParser()
    agent = UniversalAgent(router=tool_not_found_router, nlp_parser=nlp_parser)
    result = await agent.execute("test command")
    
    # Check the result structure for tool not found
    assert result["status"] == "tool_not_found"
    assert result["result"] is None
    assert "Tool with ID" in result["message"]
    assert "not found" in result["message"]
    
    # Verify router was called
    assert tool_not_found_router.route_request_called_with is not None
    assert tool_not_found_router.route_request_called_with["tool_id"] == "mock_tool"

@pytest.mark.asyncio
async def test_agent_execute_exception_handling():
    """Test that exceptions in execute are caught and formatted properly."""
    # Create a router that raises an exception when route_request is called
    router = MockRouter()
    router.route_request = MagicMock(side_effect=Exception("Test exception"))
    
    nlp_parser = MockNlpParser()
    agent = UniversalAgent(router=router, nlp_parser=nlp_parser)
    result = await agent.execute("test command")
    
    # Check error handling
    assert result["status"] == "error"
    assert result["result"] is None
    assert "An unexpected error occurred" in result["message"]
    assert "Test exception" in result["message"]

@pytest.mark.asyncio
async def test_agent_execute_read_file_command():
    """Test the execute method with a 'read file' command."""
    nlp_parser = MockNlpParser()
    router = MockRouter()
    agent = UniversalAgent(router=router, nlp_parser=nlp_parser)
    
    # Test a 'read file' command with a file path
    result = await agent.execute("read file 'test.txt'")
    
    # Verify route_request was called with file_reader tool and correct path
    assert router.route_request_called_with["tool_id"] == "file_reader"
    assert router.route_request_called_with["params"]["path"] == "test.txt"
