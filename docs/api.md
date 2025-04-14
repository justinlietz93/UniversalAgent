# Universal Agent API Specification

This document outlines the core interfaces, data structures, and the primary network API endpoint for the Universal Agent framework.

## Core Interfaces

These abstract base classes define the contracts for the main components of the framework. Implementations must adhere to these interfaces.

### `IUniversalAgent` (`src/universal_agent/interfaces/i_universal_agent.py`)

The primary entry point for interacting with the framework.

*   **`async execute(command: str) -> AgentResult`**:
    *   Processes a natural language `command`.
    *   Orchestrates NLP parsing, routing via `IRouter`, `ITool` execution, and result formatting.
    *   Returns an `AgentResult` dictionary.

### `IRouter` (`src/universal_agent/interfaces/i_router.py`)

Responsible for managing and routing requests to tools.

*   **`register_tool(tool: ITool) -> None`**: Registers a tool instance. Raises `ValueError` if ID conflicts.
*   **`deregister_tool(tool_id: str) -> None`**: Deregisters a tool by its ID. Raises `KeyError` if not found.
*   **`async route_request(request: AgentRequest) -> ToolResult`**: Routes an `AgentRequest` to the correct `ITool` and executes it. Returns a `ToolResult`. Handles tool not found and execution errors.

### `ITool` (`src/universal_agent/interfaces/i_tool.py`)

The interface that all tools must implement.

*   **`id: str` (Property)**: A unique identifier for the tool.
*   **`name: str` (Property)**: A human-readable name.
*   **`description: str` (Property)**: A brief description.
*   **`async execute(params: ToolParams) -> ToolResult`**: Executes the tool's logic with given `params`. Returns a `ToolResult`.

## Core Data Structures (`src/universal_agent/interfaces/types.py`)

Pydantic models are used for data validation and structure definition.

*   **`ToolParams`**: `Dict[str, Any]` - Parameters passed to a tool's `execute` method.
*   **`ToolResult`**: `BaseModel`
    *   `success: bool` (Required): Indicates if the tool execution succeeded.
    *   `data: Optional[Any]`: Result data on success.
    *   `error: Optional[str]`: Error message on failure.
*   **`AgentRequest`**: `BaseModel`
    *   `tool_id: str` (Required): The ID of the target tool, determined by the NLP parser.
    *   `params: ToolParams`: Parameters for the tool, extracted by the NLP parser.
*   **`AgentResult`**: `BaseModel`
    *   `status: str` (Required): Overall status (e.g., 'success', 'error', 'tool_not_found').
    *   `result: Optional[Any]`: Result data if status is 'success'.
    *   `message: Optional[str]`: Informational or error message.

## Network API Endpoint (Conceptual - To be implemented in Phase 6)

The framework will expose its functionality via a network API.

*   **Endpoint:** `POST /execute`
*   **Request Body (JSON):**
    ```json
    {
      "command": "The natural language command string"
    }
    ```
*   **Response Body (JSON - Success):**
    ```json
    {
      "status": "success",
      "result": <ToolResult.data>, // Data returned by the successful tool execution
      "message": "Optional success message"
    }
    ```
*   **Response Body (JSON - Error):**
    ```json
    {
      "status": "error | tool_not_found | nlp_error | etc.",
      "result": null,
      "message": "Detailed error message"
    }
    ```

## Tool Adaptation Strategy (Reference - To be detailed in `docs/tool_adaptation_plan.md`)

Existing Python tools will be adapted by:
1.  Modifying or wrapping them in classes that implement the `ITool` interface.
2.  Ensuring the `execute` method handles parameter mapping (`ToolParams` -> tool input) and result formatting (tool output -> `ToolResult`).
3.  Registering these adapted tools with the `Router`.
