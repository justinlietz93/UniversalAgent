"""
Base tool module for the Universal LLM Tool Wrapper Interface.

This module defines the base tool class that all tools must extend.
"""
import logging
import json
import abc
from typing import Dict, Any, Optional

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
# Use absolute import from src
from src.config import SECURITY

logger = logging.getLogger(__name__)

class BaseTool(abc.ABC):
    """
    Abstract base class for tools.
    
    This class defines the interface that all tools must implement.
    """
    
    def __init__(self):
        """
        Initialize the base tool.
        """
        self._name = None
        self._description = None
        self._input_schema = None
        self._output_schema = None
        # Get sensitive keys from configuration
        self._sensitive_keys = SECURITY["sensitive_keys"]
    
    @property
    def name(self) -> str:
        """
        Get the tool name.
        
        Returns:
            The tool name
        """
        if not self._name:
            raise ValueError("Tool name is not set")
        return self._name
    
    @property
    def description(self) -> str:
        """
        Get the tool description.
        
        Returns:
            The tool description
        """
        if not self._description:
            raise ValueError("Tool description is not set")
        return self._description
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        """
        Get the tool input schema.
        
        Returns:
            The input schema as a JSON Schema object
        """
        if not self._input_schema:
            raise ValueError("Tool input schema is not set")
        return self._input_schema
    
    @property
    def output_schema(self) -> Dict[str, Any]:
        """
        Get the tool output schema.
        
        Returns:
            The output schema as a JSON Schema object
        """
        if not self._output_schema:
            raise ValueError("Tool output schema is not set")
        return self._output_schema
    
    @abc.abstractmethod
    async def run(self, **kwargs) -> Dict[str, Any]:
        """
        Run the tool.
        
        Args:
            **kwargs: Tool input parameters
            
        Returns:
            Tool output
        """
        pass
    
    def _log_execution(self, kwargs: Dict[str, Any]) -> None:
        """
        Log the tool execution.
        
        Args:
            kwargs: Tool input parameters
        """
        # Sanitize sensitive values in the log
        sanitized_kwargs = self._sanitize_sensitive_values(kwargs)
        logger.info(f"Executing tool {self.name} with parameters: {sanitized_kwargs}")
    
    def _log_result(self, result: Dict[str, Any]) -> None:
        """
        Log the tool result.
        
        Args:
            result: Tool output
        """
        # Sanitize sensitive values in the log
        sanitized_result = self._sanitize_sensitive_values(result)
        logger.info(f"Tool {self.name} executed with result: {sanitized_result}")
    
    def _sanitize_sensitive_values(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize sensitive values in the data.
        
        Args:
            data: Data to sanitize
            
        Returns:
            Sanitized data
        """
        if not isinstance(data, dict):
            return data
        
        sanitized = {}
        
        for key, value in data.items():
            if any(sensitive_key in key.lower() for sensitive_key in self._sensitive_keys):
                sanitized[key] = "********"
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_sensitive_values(value)
            else:
                sanitized[key] = value
        
        return sanitized
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the tool to a dictionary.
        
        Returns:
            Dictionary representation of the tool
        """
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema
        }

    @staticmethod
    def safe_eval(expression: str) -> Any:
        """
        Safely evaluate a mathematical expression.
        
        Args:
            expression: The expression to evaluate
            
        Returns:
            The result of the evaluation
            
        Raises:
            ValueError: If the expression contains unsafe constructs
        """
        # Get safe evaluation settings from config
        safe_globals = SECURITY["safe_eval_globals"].copy()
        safe_locals = SECURITY["safe_eval_locals"].copy()
        
        # Check for unsafe constructs
        unsafe_patterns = [
            "import", "exec", "eval", "compile", "open", "file", 
            "__", "os.", "sys.", "subprocess", "shutil"
        ]
        if any(pattern in expression for pattern in unsafe_patterns):
            raise ValueError(f"Expression contains unsafe constructs: {expression}")
        
        # Evaluate the expression in a safe context
        try:
            result = eval(expression, safe_globals, safe_locals)
            return result
        except Exception as e:
            raise ValueError(f"Error evaluating expression: {str(e)}")
