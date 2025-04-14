# Creating Tools for Universal Agent

This guide provides a comprehensive, step-by-step tutorial for creating new tools for the Universal Agent framework. Tools are the building blocks that give the agent its capabilities, and creating custom tools allows you to extend the agent with domain-specific functionality.

## Overview

The Universal Agent framework uses a standardized tool interface (`ITool`) to ensure consistent behavior across all tools. By implementing this interface, your custom tools can be seamlessly integrated into the agent and used via natural language commands.

## Step 1: Set Up the Tool Class

First, create a new Python file for your tool. The filename should reflect the tool's purpose (e.g., `weather_tool.py`):

```python
from typing import Dict, Any, Optional
from src.universal_agent.interfaces.i_tool import ITool
from src.universal_agent.interfaces.types import ToolParams, ToolResult

class WeatherTool(ITool):
    """A tool for retrieving weather information."""
    
    def __init__(self, api_key: str = None):
        """
        Initialize the weather tool.
        
        Args:
            api_key (str, optional): API key for the weather service.
        """
        self._id = "weather_tool"
        self._name = "Weather Information Tool"
        self._description = "Gets current weather information for a specified location."
        self._api_key = api_key
```

## Step 2: Implement Required ITool Properties

The `ITool` interface requires you to implement three properties:

```python
@property
def id(self) -> str:
    """
    Get the unique identifier for this tool.
    
    Returns:
        str: The tool ID.
    """
    return self._id

@property
def name(self) -> str:
    """
    Get the human-readable name for this tool.
    
    Returns:
        str: The tool name.
    """
    return self._name

@property
def description(self) -> str:
    """
    Get the description of this tool.
    
    Returns:
        str: The tool description.
    """
    return self._description
```

## Step 3: Implement the Execute Method

The core of your tool is the `execute` method, which implements the actual functionality:

```python
async def execute(self, params: ToolParams) -> ToolResult:
    """
    Get weather information for a location.
    
    Args:
        params (ToolParams): A dictionary with at least a 'location' key.
    
    Returns:
        ToolResult: The result of the tool execution.
    """
    try:
        # Extract required parameters
        location = params.get("location")
        if not location:
            return ToolResult(
                success=False,
                error="Location parameter is required."
            )
        
        # Use external API or service to get weather data
        # Here we're simulating API call for demonstration
        weather_data = await self._get_weather_data(location)
        
        # Return successful result with data
        return ToolResult(
            success=True,
            data={
                "location": location,
                "temperature": weather_data["temperature"],
                "conditions": weather_data["conditions"],
                "forecast": weather_data["forecast"]
            }
        )
    except Exception as e:
        # Handle any errors and return appropriate error message
        return ToolResult(
            success=False,
            error=f"Error retrieving weather data: {str(e)}"
        )
```

## Step 4: Implement Helper Methods

For more complex tools, add helper methods to keep your code organized:

```python
async def _get_weather_data(self, location: str) -> Dict[str, Any]:
    """
    Get weather data from an external service.
    
    Args:
        location (str): The location to get weather for.
    
    Returns:
        Dict[str, Any]: Weather data.
    """
    # In a real implementation, you would call an actual weather API
    # For demonstration, we return mock data
    import asyncio
    
    # Simulate API latency
    await asyncio.sleep(0.5)
    
    return {
        "temperature": 72,
        "conditions": "Partly Cloudy",
        "forecast": ["Sunny", "Rainy", "Cloudy"]
    }
```

## Step 5: Implement the Optional Parameter Schema (Recommended)

Adding a parameter schema improves usability and documentation:

```python
def get_parameter_schema(self) -> Dict[str, Any]:
    """
    Get the schema for the parameters expected by this tool.
    
    Returns:
        Dict[str, Any]: JSON Schema for parameters.
    """
    return {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "The city or location to get weather for (e.g., 'New York', 'London')."
            },
            "units": {
                "type": "string",
                "enum": ["imperial", "metric"],
                "description": "Temperature units: 'imperial' for Fahrenheit, 'metric' for Celsius.",
                "default": "metric"
            }
        },
        "required": ["location"]
    }
```

## Complete Tool Implementation

Here's the complete implementation of our example `WeatherTool`:

```python
from typing import Dict, Any, Optional
import asyncio
from src.universal_agent.interfaces.i_tool import ITool
from src.universal_agent.interfaces.types import ToolParams, ToolResult

class WeatherTool(ITool):
    """A tool for retrieving weather information."""
    
    def __init__(self, api_key: str = None):
        """
        Initialize the weather tool.
        
        Args:
            api_key (str, optional): API key for the weather service.
        """
        self._id = "weather_tool"
        self._name = "Weather Information Tool"
        self._description = "Gets current weather information for a specified location."
        self._api_key = api_key
    
    @property
    def id(self) -> str:
        """
        Get the unique identifier for this tool.
        
        Returns:
            str: The tool ID.
        """
        return self._id
    
    @property
    def name(self) -> str:
        """
        Get the human-readable name for this tool.
        
        Returns:
            str: The tool name.
        """
        return self._name
    
    @property
    def description(self) -> str:
        """
        Get the description of this tool.
        
        Returns:
            str: The tool description.
        """
        return self._description
    
    def get_parameter_schema(self) -> Dict[str, Any]:
        """
        Get the schema for the parameters expected by this tool.
        
        Returns:
            Dict[str, Any]: JSON Schema for parameters.
        """
        return {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city or location to get weather for (e.g., 'New York', 'London')."
                },
                "units": {
                    "type": "string",
                    "enum": ["imperial", "metric"],
                    "description": "Temperature units: 'imperial' for Fahrenheit, 'metric' for Celsius.",
                    "default": "metric"
                }
            },
            "required": ["location"]
        }
    
    async def execute(self, params: ToolParams) -> ToolResult:
        """
        Get weather information for a location.
        
        Args:
            params (ToolParams): A dictionary with at least a 'location' key.
        
        Returns:
            ToolResult: The result of the tool execution.
        """
        try:
            # Extract required parameters
            location = params.get("location")
            if not location:
                return ToolResult(
                    success=False,
                    error="Location parameter is required."
                )
            
            # Extract optional parameters
            units = params.get("units", "metric")
            
            # Use external API or service to get weather data
            weather_data = await self._get_weather_data(location, units)
            
            # Return successful result with data
            return ToolResult(
                success=True,
                data={
                    "location": location,
                    "temperature": weather_data["temperature"],
                    "units": units,
                    "conditions": weather_data["conditions"],
                    "forecast": weather_data["forecast"]
                }
            )
        except Exception as e:
            # Handle any errors and return appropriate error message
            return ToolResult(
                success=False,
                error=f"Error retrieving weather data: {str(e)}"
            )
    
    async def _get_weather_data(self, location: str, units: str = "metric") -> Dict[str, Any]:
        """
        Get weather data from an external service.
        
        Args:
            location (str): The location to get weather for.
            units (str): The units to use ('metric' or 'imperial').
        
        Returns:
            Dict[str, Any]: Weather data.
        """
        # In a real implementation, you would call an actual weather API
        # For demonstration, we return mock data
        
        # Simulate API latency
        await asyncio.sleep(0.5)
        
        # Mock temperature based on units
        temp = 22 if units == "metric" else 72
        
        return {
            "temperature": temp,
            "conditions": "Partly Cloudy",
            "forecast": ["Sunny", "Rainy", "Cloudy"]
        }
```

## Step 6: Register Your Tool with the Router

To use your tool with the Universal Agent, you need to register it with a Router:

```python
from src.universal_agent.core.agent import UniversalAgent
from src.universal_agent.router.router import Router
from src.universal_agent.utils.nlp_parser import NlpParser
from your_module.weather_tool import WeatherTool

# Initialize core components
router = Router()
nlp_parser = NlpParser()

# Create and register your tool
weather_tool = WeatherTool(api_key="your-api-key")
router.register_tool(weather_tool)

# Create agent with registered tools
agent = UniversalAgent(router=router, nlp_parser=nlp_parser)

# Now you can use the tool via natural language
result = await agent.execute("what's the weather in New York?")
print(result)
```

## Testing Your Tool

It's important to test your tool before integrating it with the agent:

```python
# Simple test script for WeatherTool
import asyncio
from your_module.weather_tool import WeatherTool

async def test_weather_tool():
    # Create tool instance
    tool = WeatherTool()
    
    # Test with valid parameters
    result = await tool.execute({"location": "London"})
    print("Valid params result:", result)
    
    # Test with missing required parameter
    result = await tool.execute({})
    print("Missing params result:", result)
    
    # Test with all parameters
    result = await tool.execute({"location": "Tokyo", "units": "imperial"})
    print("All params result:", result)

# Run the test
asyncio.run(test_weather_tool())
```

## Best Practices for Tool Creation

1. **Clear Descriptions**: Make your tool's description clear and informative to help NLP parsing.
2. **Parameter Validation**: Always validate input parameters and provide clear error messages.
3. **Comprehensive Error Handling**: Catch all exceptions and return proper `ToolResult` objects.
4. **Provide Parameter Schema**: Use `get_parameter_schema()` to define expected parameters.
5. **Descriptive IDs**: Use descriptive, unique IDs for your tools (e.g., `weather_get` not `tool1`).
6. **Stateless Design**: Design tools to be stateless when possible, storing any needed state outside the tool.
7. **Asynchronous Support**: Implement proper async patterns to ensure non-blocking execution.
8. **Documentation**: Include docstrings and comments to make your code maintainable.

## Using the BaseTool Helper (Optional)

For convenience, we provide a `BaseTool` helper class that handles some of the boilerplate code:

```python
from src.universal_agent.tools.base_tool import BaseTool

class WeatherTool(BaseTool):
    """A tool for retrieving weather information."""
    
    def __init__(self, api_key: str = None):
        """Initialize the weather tool."""
        super().__init__(
            id="weather_tool",
            name="Weather Information Tool",
            description="Gets current weather information for a specified location."
        )
        self._api_key = api_key
        
    def get_parameter_schema(self) -> Dict[str, Any]:
        # Schema as defined above
        pass
        
    async def execute(self, params: ToolParams) -> ToolResult:
        # Implementation as defined above
        pass
```

The `BaseTool` class handles the basic properties and provides additional helper methods for common tasks.

## Conclusion

Creating tools for the Universal Agent is straightforward if you follow the `ITool` interface. With proper implementation, your tools will seamlessly integrate with the natural language processing capabilities of the Universal Agent, extending its functionality to meet your specific needs.

Remember to follow the best practices and use the provided helpers when appropriate. Happy tool creation!
