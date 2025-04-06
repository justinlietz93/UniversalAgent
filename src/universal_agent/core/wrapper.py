"""
Universal Agent wrapper module.

This module provides the main UniversalAgent class, which serves as a universal wrapper
for interacting with various LLM providers with dynamic capability discovery and unified tool handling.
"""
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union, AsyncGenerator

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
# Use absolute import from src
from src.config import get_provider_config, get_adapter_class_name
from ..adapters.adapter_factory import get_adapter_class
from ..tools.base_tool import BaseTool
from ..utils.streaming import StreamingManager

logger = logging.getLogger(__name__)

class UniversalAgent:
    """
    Universal wrapper for interacting with LLM providers.
    
    This class provides a unified interface for working with different LLM providers,
    handling tool registration, execution, and response generation.
    """
    
    def __init__(
        self,
        provider: str,
        credentials: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the UniversalAgent.
        
        Args:
            provider: The LLM provider name (e.g., 'openai', 'gemini')
            credentials: Authentication credentials for the LLM provider
            config: Optional configuration parameters
        """
        self.provider = provider.lower()
        self.credentials = credentials
        self.config = config or {}
        
        # Get adapter-specific configuration
        self.provider_config = get_provider_config(self.provider, "tool_capabilities")
        
        # Initialize tools registry
        self.tools: Dict[str, BaseTool] = {}
        
        # Initialize adapter
        self._initialize_adapter()
        
        # Initialize streaming manager
        self.streaming_manager = StreamingManager()
        
        logger.info(f"Initialized UniversalAgent with provider: {self.provider}")
    
    def _initialize_adapter(self) -> None:
        """
        Initialize the adapter for the specified LLM provider.
        """
        adapter_class_name = get_adapter_class_name(self.provider)
        adapter_class = get_adapter_class(adapter_class_name)
        
        if not adapter_class:
            raise ValueError(f"No adapter found for provider: {self.provider}")
        
        self.adapter = adapter_class(
            provider=self.provider,
            credentials=self.credentials,
            config=self.config,
            tool_capabilities=self.provider_config
        )
        
        logger.info(f"Initialized adapter: {adapter_class_name}")
    
    def register_tool(self, name: str, tool: BaseTool) -> None:
        """
        Register a tool with the agent.
        
        Args:
            name: The name to register the tool under
            tool: The tool to register
        """
        if name in self.tools:
            logger.warning(f"Tool '{name}' already registered, overwriting")
        
        self.tools[name] = tool
        logger.info(f"Registered tool: {name}")
    
    def unregister_tool(self, name: str) -> None:
        """
        Unregister a tool from the agent.
        
        Args:
            name: The name of the tool to unregister
        """
        if name in self.tools:
            del self.tools[name]
            logger.info(f"Unregistered tool: {name}")
        else:
            logger.warning(f"Tool '{name}' not found, cannot unregister")
    
    def get_tool_descriptions(self) -> List[Dict[str, Any]]:
        """
        Get descriptions of all registered tools.
        
        Returns:
            List of tool descriptions
        """
        tool_descriptions = []
        
        for name, tool in self.tools.items():
            tool_description = {
                "name": tool._name if hasattr(tool, "_name") else name,
                "description": tool._description if hasattr(tool, "_description") else "",
                "input_schema": tool._input_schema if hasattr(tool, "_input_schema") else {}
            }
            
            tool_descriptions.append(tool_description)
        
        return tool_descriptions
    
    async def execute_tool(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool based on a tool call.
        
        Args:
            tool_call: The tool call information
            
        Returns:
            The result of the tool execution
        """
        tool_name = tool_call.get("tool")
        tool_args = tool_call.get("arguments", {})
        
        if not tool_name:
            logger.error("Tool call missing tool name")
            return {"error": "Tool call missing tool name"}
        
        if tool_name not in self.tools:
            logger.error(f"Tool '{tool_name}' not found")
            return {"error": f"Tool '{tool_name}' not found"}
        
        tool = self.tools[tool_name]
        
        try:
            logger.info(f"Executing tool: {tool_name}")
            result = await tool.run(**tool_args)
            
            # Check if the result is a dict
            if not isinstance(result, dict):
                result = {"result": result}
            
            return result
        
        except Exception as e:
            logger.error(f"Error executing tool '{tool_name}': {str(e)}")
            return {"error": f"Error executing tool '{tool_name}': {str(e)}"}
    
    async def generate_response(self, prompt: str) -> str:
        """
        Generate a response from the LLM, potentially using tools.
        
        Args:
            prompt: The input prompt for the LLM
            
        Returns:
            The response from the LLM
        """
        # Get tool descriptions
        tool_descriptions = self.get_tool_descriptions()
        
        # Generate initial response
        response = await self.adapter.generate_response(prompt, tool_descriptions)
        
        # Check if the response contains a tool call
        tool_call = self.adapter.extract_tool_call(response)
        
        # If no tool call, return the response
        if not tool_call:
            return response
        
        # Execute the tool
        tool_result = await self.execute_tool(tool_call)
        
        # Process the tool result
        final_response = await self.adapter.process_tool_result(
            prompt, response, tool_call, tool_result
        )
        
        return final_response
    
    async def generate_streaming_response(self, prompt: str) -> AsyncGenerator[str, None]:
        """
        Generate a streaming response from the LLM, potentially using tools.
        
        Args:
            prompt: The input prompt for the LLM
            
        Yields:
            Chunks of the response from the LLM
        """
        # Get tool descriptions
        tool_descriptions = self.get_tool_descriptions()
        
        # Generate streaming response
        stream = self.adapter.generate_streaming_response(prompt, tool_descriptions)
        
        # Process the stream
        detected_tool_call = None
        
        async def on_tool_call(tool_call):
            nonlocal detected_tool_call
            detected_tool_call = tool_call
        
        async for chunk in self.streaming_manager.process_streaming_response(
            stream, on_tool_call
        ):
            yield chunk
        
        # If a tool call was detected, execute it
        if detected_tool_call:
            # Execute the tool
            tool_result = await self.execute_tool(detected_tool_call)
            
            # Process the tool result
            final_response = await self.adapter.process_tool_result(
                prompt, "", detected_tool_call, tool_result
            )
            
            # Yield the final response
            yield f"\n\n{final_response}"
