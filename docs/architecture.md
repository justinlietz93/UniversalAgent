# Universal Agent Architecture

This document describes the high-level architecture and data flow of the Universal Agent framework, focusing on the implementation of the Universal Agent Protocol.

## Core Components Diagram

```mermaid
graph TD
    subgraph "Client Application"
        Client(Autonomous Coding App)
    end

    subgraph "Universal Agent Framework (Network API Layer - Phase 6)"
        API(POST /execute API)
    end

    subgraph "Universal Agent Core (Python)"
        UA[UniversalAgent<br>(IUniversalAgent)]
        NLP[NLP Parser<br>(Transformer - MANDATORY)]
        Router[Router<br>(IRouter)]
        ToolRegistry(Tool Registry<br>[ID -> ITool Instance])
        subgraph "Registered Tools"
            Tool1[Tool A<br>(ITool)]
            Tool2[Tool B<br>(ITool)]
            ToolN[...]
        end
    end

    Client -- "1. NL Command (string)" --> API
    API -- "2. NL Command (string)" --> UA
    UA -- "3. NL Command (string)" --> NLP
    NLP -- "4. AgentRequest<br>(tool_id, params)" --> UA
    UA -- "5. AgentRequest" --> Router
    Router -- "6. Lookup tool_id" --> ToolRegistry
    ToolRegistry -- "7. ITool Instance" --> Router
    Router -- "8. params" --> Tool1
    Tool1 -- "9. ToolResult<br>(success, data/error)" --> Router
    Router -- "10. ToolResult" --> UA
    UA -- "11. Formats AgentResult<br>(status, result/message)" --> API
    API -- "12. AgentResult (JSON)" --> Client

    style NLP fill:#f9d,stroke:#333,stroke-width:2px
    style UA fill:#ccf,stroke:#333,stroke-width:1px
    style Router fill:#ccf,stroke:#333,stroke-width:1px
    style ToolRegistry fill:#eee,stroke:#333,stroke-width:1px
```

## Data Flow and Protocol Components

The Universal Agent Protocol defines a specific interaction pattern centered around natural language command processing via a mandatory Transformer-based NLP component. The flow is as follows (referencing the diagram numbers):

1.  **Client Interaction (NL Interface):** The client application (e.g., Autonomous Coding App) initiates interaction by sending a natural language command string (e.g., "read the file 'main.py'") to the framework's primary entry point. In the final deployed version (Phase 6), this occurs via the `POST /execute` **Network API Layer**. Internally, this triggers the `UniversalAgent.execute` method.
2.  **Internal NLP Translation (MANDATORY: Transformer-based):** The `UniversalAgent` passes the raw command string to the **Internal NLP Translation** component (`src/utils/nlp_parser.py`). This component **MUST** use a powerful Transformer model (e.g., 't5-base' via the Hugging Face `transformers` library) to parse the command. Its function is to interpret the user's intent and extract relevant entities, translating the natural language into a structured `AgentRequest` object containing the target `tool_id` and necessary `params`. **Using non-Transformer methods (regex, simple patterns, hardcoding) for this core parsing logic is strictly forbidden by the protocol.**
3.  **Request Routing:** The `UniversalAgent` receives the `AgentRequest` from the NLP Parser and passes it to the **Dynamic Router** (`src/router/router.py`, implementing `IRouter`).
4.  **Tool Dispatch:** The `Router` uses the `tool_id` from the `AgentRequest` to look up the corresponding registered tool instance in its internal registry.
5.  **Tool Execution:** The `Router` invokes the `execute` method of the identified tool instance (which must conform to the **`ITool` Interface**), passing the `params` from the `AgentRequest`.
6.  **Result Handling:** The tool executes its logic and returns a `ToolResult` object (indicating `success` or `failure` and containing `data` or an `error` message) back to the `Router`.
7.  **Response Aggregation:** The `Router` forwards the `ToolResult` back to the `UniversalAgent`.
8.  **Final Response:** The `UniversalAgent` formats the final `AgentResult` based on the `ToolResult` and the overall process status (e.g., including potential errors from parsing or routing). This `AgentResult` is then returned to the initial caller (via the API layer in the deployed version).

**Goal:** The primary goal of this protocol is to **abstract tool complexity** behind a unified natural language interface. By mandating a **powerful Transformer-based NLP** component for command interpretation, the protocol enables flexible, robust, and context-aware interaction, minimizing the need for clients to know specific tool APIs or parameter formats. This creates a **demonstrably superior alternative** to protocols requiring pre-defined, rigid command structures or client-side mapping logic.

## Protocol Advantages vs. Alternatives (e.g., MCP)

The Universal Agent Protocol (UAP), with its mandatory Transformer NLP core, offers distinct advantages compared to protocols like the Model Context Protocol (MCP) or simpler function-calling mechanisms:

1.  **True Natural Language Interface:** Clients interact using free-form natural language commands (`execute(command: string)`). This contrasts with MCP, which typically requires the client (or an intermediary layer) to structure requests into specific tool calls with pre-defined parameters (`use_mcp_tool` with JSON arguments). UAP shifts the burden of understanding and structuring the request from the client to the framework's NLP component.
2.  **Reduced Client Complexity:** Clients using UAP do not need intrinsic knowledge of available tools, their specific IDs, or their parameter schemas. They only need to express their intent in natural language. The framework's NLP handles the mapping. MCP clients often need to know which tool to call and how to format its arguments.
3.  **Enhanced Flexibility & Robustness:** Transformer models can handle variations in phrasing, synonyms, and potentially infer implicit parameters from context (depending on the model and training/prompting strategy). This makes the interaction more flexible and robust to user input variations compared to rigid command structures or keyword matching.
4.  **Centralized Intelligence:** The core intelligence for request interpretation resides within the UA framework's NLP component. This allows for centralized updates and improvements to language understanding without requiring changes to potentially numerous client applications.
5.  **Abstraction:** UAP provides a higher level of abstraction over the underlying tools compared to protocols where the client directly invokes specific tool functions or endpoints.
