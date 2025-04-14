# Tool Adaptation Plan

This document outlines the strategy for adapting existing tools to the Universal Agent framework.

## Overview

The Universal Agent framework requires all tools to implement the `ITool` interface to ensure a consistent interaction pattern. To integrate existing tools (like `advanced_file_tool.py`, `code_runner_tool.py`, `shell_tool.py`, etc.), we need to create appropriate adapters or wrappers.

## Adaptation Strategy

### 1. Wrapper Implementation

For each tool, we will create a wrapper class that implements the `ITool` interface:

```python
from src.universal_agent.interfaces.i_tool import ITool
from src.universal_agent.interfaces.types import ToolParams, ToolResult

class ToolWrapper(ITool):
    def __init__(self):
        self._id = "tool_id"  # Unique identifier
        self._name = "Tool Name"  # Human-readable name
        self._description = "Description of the tool functionality"
        
    @property
    def id(self) -> str:
        return self._id
        
    @property
    def name(self) -> str:
        return self._name
        
    @property
    def description(self) -> str:
        return self._description
        
    async def execute(self, params: ToolParams) -> ToolResult:
        try:
            # Convert ToolParams to the format expected by the original tool
            # Call the original tool's functionality
            # Convert the original tool's response to a ToolResult
            return ToolResult(success=True, data=result)
        except Exception as e:
            return ToolResult(success=False, error=str(e))
```

### 2. Communication with Python Tools

For tools implemented in Python, there are two main approaches:

#### 2.1 Direct Integration

For Python tools within the same codebase, the wrapper directly imports and calls the tool:

```python
from src.universal_agent.tools.original_tool import OriginalTool

class OriginalToolWrapper(ITool):
    # ...
    
    async def execute(self, params: ToolParams) -> ToolResult:
        try:
            # Create an instance or use an existing one
            tool = OriginalTool()
            
            # Map parameters
            mapped_params = self._map_params(params)
            
            # Call the tool
            result = tool.run(**mapped_params)
            
            # Format result
            return ToolResult(success=True, data=result)
        except Exception as e:
            return ToolResult(success=False, error=str(e))
            
    def _map_params(self, params: ToolParams) -> dict:
        # Map from Universal Agent params to tool-specific params
        # ...
```

#### 2.2 Child Process Execution

For Python tools that need to be executed in separate processes:

```python
import asyncio
import json
import sys

class ExternalPythonToolWrapper(ITool):
    # ...
    
    async def execute(self, params: ToolParams) -> ToolResult:
        try:
            # Prepare command to execute the Python script
            cmd = [
                sys.executable,
                "/path/to/tool_script.py",
                json.dumps(params)  # Pass params as JSON
            ]
            
            # Execute as child process
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Get outputs
            stdout, stderr = await process.communicate()
            
            # Check result
            if process.returncode != 0:
                return ToolResult(success=False, error=stderr.decode())
                
            # Parse and return output
            result = json.loads(stdout.decode())
            return ToolResult(success=True, data=result)
        except Exception as e:
            return ToolResult(success=False, error=str(e))
```

### 3. Parameter Mapping

Each wrapper needs to map between the Universal Agent parameter format (`ToolParams`) and the original tool's expected parameters:

```python
def _map_params(self, params: ToolParams) -> dict:
    """Map Universal Agent params to tool-specific params."""
    tool_specific_params = {}
    
    # Example mappings
    if "path" in params:
        tool_specific_params["file_path"] = params["path"]
        
    if "content" in params:
        tool_specific_params["data"] = params["content"]
    
    # Default values for missing params
    tool_specific_params.setdefault("encoding", "utf-8")
    
    return tool_specific_params
```

### 4. Result Formatting

Similarly, each wrapper needs to format the tool's output as a `ToolResult`:

```python
def _format_result(self, tool_output) -> ToolResult:
    """Format tool output as a ToolResult."""
    # For success case
    if isinstance(tool_output, dict) and "error" not in tool_output:
        return ToolResult(success=True, data=tool_output)
        
    # For error case
    if isinstance(tool_output, dict) and "error" in tool_output:
        return ToolResult(success=False, error=tool_output["error"])
        
    # Default success case
    return ToolResult(success=True, data=tool_output)
```

## Specific Tool Adaptations

### File Reader/Writer Tool

```python
class FileReaderToolWrapper(ITool):
    def __init__(self):
        self._id = "file_reader"
        self._name = "File Reader"
        self._description = "Reads the content of a file"
        
    # ... (other methods)
    
    async def execute(self, params: ToolParams) -> ToolResult:
        try:
            # Extract path parameter
            path = params.get("path")
            if not path:
                return ToolResult(success=False, error="Path parameter is required")
                
            # Use original tool logic or adapted logic
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                
            return ToolResult(success=True, data={"content": content})
        except Exception as e:
            return ToolResult(success=False, error=f"Error reading file: {str(e)}")
```

### Shell Tool

```python
class ShellToolWrapper(ITool):
    def __init__(self):
        self._id = "shell_tool"
        self._name = "Shell Command Executor"
        self._description = "Executes shell commands safely"
        
    # ... (other methods)
    
    async def execute(self, params: ToolParams) -> ToolResult:
        try:
            # Extract command parameter
            command = params.get("command")
            if not command:
                return ToolResult(success=False, error="Command parameter is required")
                
            # Execute using asyncio for async support
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            # Format result
            result = {
                "exit_code": process.returncode,
                "stdout": stdout.decode(),
                "stderr": stderr.decode()
            }
            
            # Consider success based on exit code
            success = process.returncode == 0
            
            if success:
                return ToolResult(success=True, data=result)
            else:
                return ToolResult(success=False, error=f"Command failed with exit code {process.returncode}", data=result)
        except Exception as e:
            return ToolResult(success=False, error=f"Error executing command: {str(e)}")
```

## Registration with Router

Once the wrappers are implemented, they need to be registered with the Router:

```python
from src.universal_agent.router.router import Router
from src.universal_agent.tools.wrappers import (
    FileReaderToolWrapper,
    FileWriterToolWrapper,
    ShellToolWrapper,
    CodeRunnerToolWrapper
)

# Create Router instance
router = Router()

# Register tool wrappers
router.register_tool(FileReaderToolWrapper())
router.register_tool(FileWriterToolWrapper())
router.register_tool(ShellToolWrapper())
router.register_tool(CodeRunnerToolWrapper())
```

## Adaptation Priorities

We'll adapt tools in this priority order:

1. File operations (read/write)
2. Shell command execution
3. Code runner
4. Web search
5. Package manager

This sequence allows us to establish basic functionality first (file operations, shell commands) and then build more complex tools on top of that foundation.

## Testing Strategy

Each adapted tool will have:

1. Unit tests for the wrapper's parameter mapping and result formatting
2. Integration tests with the Router to verify registration and routing
3. End-to-end tests with the UniversalAgent to verify NLP parsing and complete execution flow

Tests will be located in:
- `tests/unit/` for unit tests
- `tests/integration/` for integration tests
- `tests/` for end-to-end tests
