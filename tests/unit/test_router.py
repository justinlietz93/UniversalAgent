import pytest
from typing import Dict, Any
from src.universal_agent.interfaces.i_tool import ITool
from src.universal_agent.router.router import Router

# Mock ITool implementation for testing
class MockTool(ITool):
    def __init__(self, tool_id: str, name: str, description: str = "Mock tool description"):
        self._id = tool_id
        self._name = name
        self._description = description
        self.execute_called_with: Dict[str, Any] | None = None

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        self.execute_called_with = params
        # Return a basic success structure for now
        return {"success": True, "data": f"Executed {self.id} with {params}"}

# Test Fixture for Router instance
@pytest.fixture
def router_instance():
    """Provides a fresh Router instance for each test."""
    return Router()

# --- Test Cases for Registration ---

def test_register_tool_success(router_instance: Router):
    """Test successful registration of a valid tool."""
    tool = MockTool(tool_id="mock_tool_1", name="Mock Tool 1")
    router_instance.register_tool(tool)
    assert router_instance._get_tool("mock_tool_1") is tool
    assert len(router_instance._tools) == 1

def test_register_tool_duplicate_id(router_instance: Router):
    """Test registering a tool with an ID that already exists."""
    tool1 = MockTool(tool_id="duplicate_id", name="Tool 1")
    tool2 = MockTool(tool_id="duplicate_id", name="Tool 2")
    router_instance.register_tool(tool1)
    with pytest.raises(ValueError, match="Tool with ID 'duplicate_id' is already registered."):
        router_instance.register_tool(tool2)
    assert len(router_instance._tools) == 1 # Ensure only the first one remains

def test_register_tool_invalid_object(router_instance: Router):
    """Test registering an object that doesn't implement ITool."""
    invalid_tool = object()
    with pytest.raises(ValueError, match="Invalid tool object provided. Must implement ITool."):
        router_instance.register_tool(invalid_tool) # type: ignore
    assert len(router_instance._tools) == 0

def test_register_tool_invalid_id_none(router_instance: Router):
    """Test registering a tool with None as ID."""
    tool = MockTool(tool_id=None, name="Invalid ID Tool") # type: ignore
    with pytest.raises(ValueError, match="Tool ID must be a non-empty string."):
         router_instance.register_tool(tool)
    assert len(router_instance._tools) == 0

def test_register_tool_invalid_id_empty(router_instance: Router):
    """Test registering a tool with an empty string ID."""
    tool = MockTool(tool_id="", name="Empty ID Tool")
    with pytest.raises(ValueError, match="Tool ID must be a non-empty string."):
         router_instance.register_tool(tool)
    assert len(router_instance._tools) == 0

# --- Test Cases for Deregistration ---

def test_deregister_tool_success(router_instance: Router):
    """Test successful deregistration of an existing tool."""
    tool_id = "tool_to_deregister"
    tool = MockTool(tool_id=tool_id, name="Deregister Me")
    router_instance.register_tool(tool)
    assert tool_id in router_instance._tools

    router_instance.deregister_tool(tool_id)
    assert tool_id not in router_instance._tools
    assert router_instance._get_tool(tool_id) is None
    assert len(router_instance._tools) == 0

def test_deregister_tool_not_found(router_instance: Router):
    """Test deregistering a tool ID that doesn't exist."""
    non_existent_id = "non_existent_tool"
    with pytest.raises(KeyError, match=f"Tool with ID '{non_existent_id}' not found."):
        router_instance.deregister_tool(non_existent_id)
    assert len(router_instance._tools) == 0

# --- Test Cases for Internal Lookup (_get_tool) ---

def test_get_tool_found(router_instance: Router):
    """Test internal lookup for an existing tool."""
    tool = MockTool(tool_id="find_me", name="Findable Tool")
    router_instance.register_tool(tool)
    found_tool = router_instance._get_tool("find_me")
    assert found_tool is tool

def test_get_tool_not_found(router_instance: Router):
    """Test internal lookup for a non-existent tool."""
    found_tool = router_instance._get_tool("cant_find_me")
    assert found_tool is None

# --- Test Cases for Routing (route_request) ---

@pytest.mark.asyncio
async def test_route_request_success(router_instance: Router):
    """Test successful routing and execution of a tool."""
    tool_id = "success_tool"
    params = {"input": "data"}
    request = {"tool_id": tool_id, "params": params}
    tool = MockTool(tool_id=tool_id, name="Success Tool")
    router_instance.register_tool(tool)

    result = await router_instance.route_request(request)

    assert result["success"] is True
    assert result["data"] == f"Executed {tool_id} with {params}"
    assert result["error"] is None
    assert tool.execute_called_with == params # Verify tool's execute was called correctly

@pytest.mark.asyncio
async def test_route_request_tool_not_found(router_instance: Router):
    """Test routing a request for a tool ID that is not registered."""
    tool_id = "not_found_tool"
    request = {"tool_id": tool_id, "params": {}}

    result = await router_instance.route_request(request)

    assert result["success"] is False
    assert result["data"] is None
    assert result["error"] == f"Tool with ID '{tool_id}' not found."

@pytest.mark.asyncio
async def test_route_request_tool_execution_error(router_instance: Router):
    """Test routing when the tool's execute method raises an exception."""
    tool_id = "error_tool"
    error_message = "Something went wrong during execution"
    request = {"tool_id": tool_id, "params": {}}

    # Mock tool that raises an error
    class ErrorTool(MockTool):
        async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
            raise RuntimeError(error_message)

    tool = ErrorTool(tool_id=tool_id, name="Error Tool")
    router_instance.register_tool(tool)

    result = await router_instance.route_request(request)

    assert result["success"] is False
    assert result["data"] is None
    # The router wraps the exception
    assert f"An unexpected error occurred: {error_message}" in result["error"]

@pytest.mark.asyncio
async def test_route_request_invalid_request_structure_missing_id(router_instance: Router):
    """Test routing with an invalid request structure (missing tool_id)."""
    request = {"params": {}} # Missing tool_id

    result = await router_instance.route_request(request)

    assert result["success"] is False
    assert result["data"] is None
    assert "An unexpected error occurred" in result["error"]
    # Pydantic validation error details might be included depending on exact exception handling
    assert "Field required" in result["error"] or "validation error" in result["error"] # Check for validation error indication

@pytest.mark.asyncio
async def test_route_request_invalid_request_structure_bad_params_type(router_instance: Router):
    """Test routing with an invalid request structure (params not a dict)."""
    request = {"tool_id": "some_tool", "params": "not_a_dict"}

    result = await router_instance.route_request(request)

    assert result["success"] is False
    assert result["data"] is None
    assert "An unexpected error occurred" in result["error"]
    assert "validation error" in result["error"] # Check for validation error indication

@pytest.mark.asyncio
async def test_route_request_invalid_tool_result_structure(router_instance: Router):
    """Test routing when a tool returns an invalid result structure."""
    tool_id = "bad_result_tool"
    request = {"tool_id": tool_id, "params": {}}

    # Mock tool that returns a bad result
    class BadResultTool(MockTool):
        async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
            return {"unexpected_key": "some_value"} # Missing 'success'

    tool = BadResultTool(tool_id=tool_id, name="Bad Result Tool")
    router_instance.register_tool(tool)

    result = await router_instance.route_request(request)

    # The router's validation of the ToolResult should catch this
    assert result["success"] is False
    assert result["data"] is None
    assert "An unexpected error occurred" in result["error"]
    assert "validation error" in result["error"] # Check for validation error indication
