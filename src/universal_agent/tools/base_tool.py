"""Base tool implementation providing utility functions for tool development."""

from typing import Dict, Any, Optional
from src.universal_agent.interfaces.i_tool import ITool
from src.universal_agent.interfaces.types import ToolParams, ToolResult


class BaseTool(ITool):
    """
    Base implementation of ITool providing common functionality.
    
    This class implements the basic properties and provides helper methods
    for parameter validation, error handling, and other common tasks.
    Tool developers can inherit from this class instead of implementing
    ITool directly for convenience.
    """
    
    def __init__(self, id: str, name: str, description: str):
        """
        Initialize a BaseTool with core properties.
        
        Args:
            id (str): Unique identifier for the tool.
            name (str): Human-readable name for the tool.
            description (str): Description of the tool's functionality.
        """
        self._id = id
        self._name = name
        self._description = description
    
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
    
    def get_parameter_schema(self) -> Optional[Dict[str, Any]]:
        """
        Get the schema for the parameters expected by this tool.
        
        Returns:
            Optional[Dict[str, Any]]: JSON Schema for parameters, or None if not defined.
        """
        # Base implementation returns None
        # Subclasses should override this method if they want to provide a schema
        return None
    
    async def execute(self, params: ToolParams) -> ToolResult:
        """
        Execute the tool's logic with the given parameters.
        
        This method must be implemented by subclasses.
        
        Args:
            params (ToolParams): Parameters for the tool execution.
        
        Returns:
            ToolResult: The result of the tool execution.
        """
        raise NotImplementedError("Subclasses must implement the execute method")
    
    def validate_parameters(self, params: ToolParams) -> Optional[str]:
        """
        Validate parameters against the schema (if provided).
        
        Args:
            params (ToolParams): Parameters to validate.
        
        Returns:
            Optional[str]: Error message if validation fails, None if parameters are valid.
        """
        schema = self.get_parameter_schema()
        if not schema:
            return None  # No schema to validate against
        
        try:
            # Basic validation of required fields
            if "required" in schema:
                for field in schema["required"]:
                    if field not in params:
                        return f"Missing required parameter: {field}"
            
            # More advanced validation could be implemented here
            # using a proper JSON Schema validator
            
            return None  # Validation passed
        except Exception as e:
            return f"Parameter validation error: {str(e)}"
    
    def create_error_result(self, message: str) -> ToolResult:
        """
        Create a ToolResult representing an error.
        
        Args:
            message (str): Error message.
        
        Returns:
            ToolResult: Error result.
        """
        return ToolResult(success=False, error=message)
    
    def create_success_result(self, data: Any) -> ToolResult:
        """
        Create a ToolResult representing success.
        
        Args:
            data (Any): Result data.
        
        Returns:
            ToolResult: Success result.
        """
        return ToolResult(success=True, data=data)
