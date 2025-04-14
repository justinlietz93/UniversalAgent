"""Template for creating new tools for the Universal Agent framework."""

from typing import Dict, Any, Optional
from src.universal_agent.tools.base_tool import BaseTool
from src.universal_agent.interfaces.types import ToolParams, ToolResult


class MyNewTool(BaseTool):
    """
    A custom tool for [describe the purpose].
    
    Customize this description to clearly explain what your tool does.
    This helps the NLP parser understand when to use this tool.
    """
    
    def __init__(self):
        """Initialize the tool with required properties."""
        super().__init__(
            id="my_new_tool",  # Unique ID for this tool
            name="My New Tool",  # Human-readable name
            description="Performs [specific function] with given parameters."  # Clear description
        )
        # Add any additional initialization here (API keys, configurations, etc.)
    
    def get_parameter_schema(self) -> Dict[str, Any]:
        """
        Define the expected parameters for this tool.
        
        Returns:
            Dict[str, Any]: JSON Schema for parameters.
        """
        return {
            "type": "object",
            "properties": {
                "param1": {
                    "type": "string",
                    "description": "Description of parameter 1."
                },
                "param2": {
                    "type": "integer",
                    "description": "Description of parameter 2."
                },
                "param3": {
                    "type": "boolean",
                    "description": "Description of parameter 3.",
                    "default": False
                }
            },
            "required": ["param1", "param2"]  # List required parameters
        }
    
    async def execute(self, params: ToolParams) -> ToolResult:
        """
        Execute the tool's functionality.
        
        Args:
            params (ToolParams): Parameters for the tool execution.
        
        Returns:
            ToolResult: The result of the tool execution.
        """
        try:
            # Validate parameters
            validation_error = self.validate_parameters(params)
            if validation_error:
                return self.create_error_result(validation_error)
            
            # Extract parameters
            param1 = params.get("param1")
            param2 = params.get("param2")
            param3 = params.get("param3", False)  # Default value for optional parameter
            
            # TODO: Implement your tool's core functionality here
            # ...
            
            # Example result data
            result_data = {
                "input_received": {
                    "param1": param1,
                    "param2": param2,
                    "param3": param3
                },
                "result": f"Processed {param1} with value {param2}",
                "success": True
            }
            
            # Return successful result
            return self.create_success_result(result_data)
            
        except Exception as e:
            # Handle unexpected errors
            return self.create_error_result(f"Error executing tool: {str(e)}")
