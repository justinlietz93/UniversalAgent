# Custom Tools Development Guide

This guide explains how to create and use custom tools with the Universal Agent.

## Tool Basics

Tools in Universal Agent are Python classes that extend the `BaseTool` class and implement the `run` method. They define:

1. A name and description
2. An input schema (what parameters the tool accepts) 
3. An output schema (what the tool returns)
4. The execution logic

## Creating a Basic Tool

Here's a simple example of a calculator tool:

```python
from universal_agent.tools.base_tool import BaseTool

class CalculatorTool(BaseTool):
    def __init__(self):
        super().__init__()
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
        
        self._output_schema = {
            "type": "object",
            "properties": {
                "result": {
                    "type": "number",
                    "description": "The result of the calculation"
                }
            },
            "required": ["result"]
        }
    
    async def run(self, **kwargs):
        """Execute the calculator tool."""
        expression = kwargs.get("expression")
        
        # IMPORTANT: In production code, you would use a safer evaluation method
        # This is just for demonstration
        try:
            # Replace potentially dangerous functions with safer ones
            safe_globals = {"__builtins__": {}}
            safe_locals = {"abs": abs, "round": round, "min": min, "max": max, 
                          "sum": sum, "len": len}
            
            # Evaluate the expression in the safe context
            result = eval(expression, safe_globals, safe_locals)
            return {"result": result}
        except Exception as e:
            return {"error": f"Error evaluating expression: {str(e)}"}
```

## Input and Output Schemas

Input and output schemas are defined using JSON Schema format:

### Input Schema

The input schema defines the parameters your tool accepts:

```python
self._input_schema = {
    "type": "object",
    "properties": {
        "param1": {
            "type": "string",
            "description": "Description of parameter 1"
        },
        "param2": {
            "type": "number",
            "description": "Description of parameter 2"
        },
        "param3": {
            "type": "boolean",
            "description": "Description of parameter 3",
            "default": False
        }
    },
    "required": ["param1", "param2"]
}
```

### Output Schema

The output schema defines what your tool returns:

```python
self._output_schema = {
    "type": "object",
    "properties": {
        "result": {
            "type": "string",
            "description": "The output of the tool"
        },
        "status": {
            "type": "string",
            "enum": ["success", "error"],
            "description": "The status of the operation"
        }
    },
    "required": ["result", "status"]
}
```

## Advanced Tool Examples

### File Reading Tool

```python
import os
from universal_agent.tools.base_tool import BaseTool

class FileReaderTool(BaseTool):
    def __init__(self):
        super().__init__()
        self._name = "file_reader"
        self._description = "Read the contents of a file"
        
        self._input_schema = {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "The path to the file to read"
                },
                "max_lines": {
                    "type": "integer",
                    "description": "Maximum number of lines to read",
                    "default": 100
                }
            },
            "required": ["file_path"]
        }
        
        self._output_schema = {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "The content of the file"
                },
                "truncated": {
                    "type": "boolean",
                    "description": "Whether the content was truncated"
                }
            },
            "required": ["content", "truncated"]
        }
    
    async def run(self, **kwargs):
        """Read a file and return its contents."""
        file_path = kwargs.get("file_path")
        max_lines = kwargs.get("max_lines", 100)
        
        try:
            if not os.path.exists(file_path):
                return {"error": f"File not found: {file_path}"}
                
            with open(file_path, 'r') as file:
                lines = file.readlines()
                
            truncated = len(lines) > max_lines
            content = ''.join(lines[:max_lines])
            
            if truncated:
                content += f"\n[...File truncated after {max_lines} lines...]"
            
            return {
                "content": content,
                "truncated": truncated
            }
            
        except Exception as e:
            return {"error": f"Error reading file: {str(e)}"}
```

### Web Search Tool

```python
import aiohttp
from universal_agent.tools.base_tool import BaseTool

class WebSearchTool(BaseTool):
    def __init__(self, api_key):
        super().__init__()
        self._name = "web_search"
        self._description = "Search the web for information"
        self.api_key = api_key
        
        self._input_schema = {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query"
                },
                "num_results": {
                    "type": "integer",
                    "description": "Number of results to return",
                    "default": 3,
                    "minimum": 1,
                    "maximum": 10
                }
            },
            "required": ["query"]
        }
        
        self._output_schema = {
            "type": "object",
            "properties": {
                "results": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Result title"
                            },
                            "link": {
                                "type": "string",
                                "description": "Result URL"
                            },
                            "snippet": {
                                "type": "string",
                                "description": "Result snippet"
                            }
                        }
                    },
                    "description": "Search results"
                }
            },
            "required": ["results"]
        }
    
    async def run(self, **kwargs):
        """Search the web for information."""
        query = kwargs.get("query")
        num_results = kwargs.get("num_results", 3)
        
        try:
            # This is a placeholder for an actual web search API call
            # In a real implementation, you would use a search API like Google Custom Search or Bing
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.search.example.com/search",
                    params={
                        "q": query,
                        "num": num_results,
                        "key": self.api_key
                    }
                ) as response:
                    if response.status != 200:
                        return {"error": f"Search API error: {response.status}"}
                    
                    data = await response.json()
                    
            # Extract and format results
            results = []
            for item in data.get("items", [])[:num_results]:
                results.append({
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "snippet": item.get("snippet", "")
                })
                
            return {"results": results}
            
        except Exception as e:
            return {"error": f"Error performing search: {str(e)}"}
```

## Registering Tools with Universal Agent

Once you've created your tools, you can register them with the Universal Agent:

### Method 1: Direct Registration

```python
from universal_agent import UniversalAgent
from my_tools import CalculatorTool, FileReaderTool

agent = UniversalAgent(
    provider="openai",
    credentials={"api_key": "your-api-key"}
)

# Register tools
calculator = CalculatorTool()
file_reader = FileReaderTool()

agent.register_tool("calculator", calculator)
agent.register_tool("file_reader", file_reader)
```

### Method 2: Using a Decorator

```python
from universal_agent import UniversalAgent
from universal_agent.tools.base_tool import BaseTool

agent = UniversalAgent(
    provider="openai",
    credentials={"api_key": "your-api-key"}
)

@agent.register_tool
class CalculatorTool(BaseTool):
    def __init__(self):
        super().__init__()
        self._name = "calculator"
        self._description = "Perform mathematical calculations"
        # ... rest of implementation
```

## Best Practices

1. **Input Validation**: Always validate inputs before processing
2. **Error Handling**: Catch and handle exceptions gracefully
3. **Security**: Be cautious with tools that execute code or access the filesystem
4. **Clear Descriptions**: Provide clear descriptions for your tool and its parameters
5. **Proper Schemas**: Define input and output schemas carefully to help the LLM understand the tool
6. **Performance**: For long-running operations, consider implementing a way to indicate progress
7. **Logging**: Log tool usage and results for debugging and monitoring

## Advanced Topics

### Streaming Tools

For tools that produce streaming output, you can implement the `stream_run` method:

```python
class StreamingTool(BaseTool):
    # ... initialize as usual ...
    
    async def stream_run(self, **kwargs):
        """Execute the tool with streaming output."""
        for i in range(10):
            yield f"Processing step {i+1}/10..."
            # Simulate some work
            await asyncio.sleep(0.5)
            
        # Final result can be a dictionary
        yield {"final_result": "Completed", "details": "All steps processed"}
```

### Tool Chaining

Tools can be chained together to create more complex workflows:

```python
# First, get information from a file
file_result = await agent.execute_tool("file_reader", file_path="data.txt")

# Use that information to perform a web search
search_result = await agent.execute_tool("web_search", query=file_result["content"])

# Perform calculations based on search results
calculation = await agent.execute_tool("calculator", 
                                      expression=f"len({search_result['results']})")

# Generate a response using all the gathered information
response = await agent.generate_response(
    f"The file contains: {file_result['content']}\n"
    f"The search returned {calculation['result']} results."
)
```

### Tool Groups

You can organize tools into logical groups for better management:

```python
class ToolGroup:
    def __init__(self, name):
        self.name = name
        self.tools = {}
        
    def add_tool(self, tool):
        self.tools[tool.name] = tool
        
    def get_tool(self, name):
        return self.tools.get(name)
        
    def list_tools(self):
        return list(self.tools.keys())

# Example usage
file_tools = ToolGroup("file_operations")
file_tools.add_tool(FileReaderTool())
file_tools.add_tool(FileWriterTool())

# Register all tools in a group
for name, tool in file_tools.tools.items():
    agent.register_tool(name, tool)
