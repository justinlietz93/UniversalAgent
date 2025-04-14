# Universal Agent Protocol API Specification

This document outlines the core interfaces, data structures, and the primary network API endpoint for the Universal Agent Protocol, which is focused on natural language command processing via transformer-based NLP.

> **Note:** This document describes the Universal Agent Protocol implementation, which provides a natural language interface using transformer-based NLP. For the provider-based API (OpenAI, Gemini, etc.), see the [API Reference](./api/reference.md).

## Core Interfaces

These abstract base classes define the contracts for the main components of the framework. Implementations must adhere to these interfaces.

### `NlpParser` (`src/universal_agent/utils/nlp_parser.py`)

The Transformer-based NLP parser responsible for interpreting natural language commands.

*   **`__init__(model_name: str = 't5-base') -> None`**:
    *   Initializes the parser with the specified Hugging Face Transformers model.
    *   Loads the model and tokenizer.
    *   Default model is 't5-base'.

*   **`async parse(command: str) -> Dict[str, Any]`**:
    *   Parses a natural language command into a structured `AgentRequest` dictionary.
    *   Uses the Transformer model to interpret the command.
    *   Extracts tool ID and parameters.
    *   Includes multiple fallback mechanisms for robustness.
    *   Returns a dictionary with `tool_id` and `params` keys.

### `IUniversalAgent` (`src/universal_agent/interfaces/i_universal_agent.py`)

The primary entry point for interacting with the framework.

*   **`__init__(router: IRouter, nlp_parser: NlpParser) -> None`**:
    *   Initializes the agent with an `IRouter` instance and a `NlpParser` instance.
    *   Validates that the router implements the `IRouter` interface.

*   **`async execute(command: str) -> AgentResult`**:
    *   Processes a natural language `command`.
    *   Uses the `NlpParser` to convert the command to a structured `AgentRequest`.
    *   Routes the request via `IRouter` to the appropriate tool.
    *   Handles execution errors and formats the final response.
    *   Supports special command `"list tools"` to return information about all registered tools.
    *   Returns an `AgentResult` dictionary.

### `IRouter` (`src/universal_agent/interfaces/i_router.py`)

Responsible for managing and routing requests to tools.

*   **`register_tool(tool: ITool) -> None`**: Registers a tool instance. Raises `ValueError` if ID conflicts.
*   **`deregister_tool(tool_id: str) -> None`**: Deregisters a tool by its ID. Raises `KeyError` if not found.
*   **`async route_request(request: AgentRequest) -> ToolResult`**: Routes an `AgentRequest` to the correct `ITool` and executes it. Returns a `ToolResult`. Handles tool not found and execution errors.

### `ITool` (`src/universal_agent/interfaces/i_tool.py`)

The interface that all tools must implement. Designed for clarity and ease of implementation by developers seeking to extend the agent.

*   **`id: str` (Property)**: A unique identifier for the tool (e.g., 'file_read', 'web_search'). MUST be unique within a router instance.
*   **`name: str` (Property)**: A human-readable name (e.g., 'File Reading Tool').
*   **`description: str` (Property)**: A brief description of the tool's function and capabilities, used for discoverability (e.g., via list_tools) and potentially aiding NLP model context. Should be clear and informative.
*   **`async execute(params: ToolParams) -> ToolResult`**: Executes the tool's logic with given `params`. MUST handle parameters defined implicitly by the description or explicitly via a schema. MUST return a `ToolResult`. Handles its own internal exceptions and reports them via `ToolResult`.
*   **`get_parameter_schema() -> Dict | None`** (Optional): Returns a schema (e.g., JSON Schema dict or a Pydantic model) defining the expected structure of `ToolParams` for validation and potentially introspection. Defaults to `None` if not implemented.

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
