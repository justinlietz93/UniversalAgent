"""
OpenAI-compatible adapter module for the Universal Agent framework.

This module defines an adapter for self-hosted, OpenAI-compatible API endpoints
(like Ollama, local LLM deployments) that follow the OpenAI API standard.
"""
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, AsyncGenerator

import httpx

from ..core.base import BaseLLMAdapter

logger = logging.getLogger(__name__)

class OpenAICompatibleAdapter(BaseLLMAdapter):
    """
    Adapter for self-hosted, OpenAI-compatible API endpoints.
    
    This adapter can connect to self-hosted models that implement the OpenAI API standard,
    such as Ollama, LM Studio, or local LLM deployments.
    """
    
    def __init__(
        self, 
        provider: str,
        credentials: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None,
        capabilities: Optional[Dict[str, Any]] = None,
        tool_capabilities: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the OpenAI-compatible adapter.
        
        Args:
            provider: The LLM provider name ('openai_compatible')
            credentials: Authentication credentials containing optional 'api_key'
            config: Configuration parameters including the mandatory 'base_url'
            capabilities: Optional provider capabilities
            tool_capabilities: Optional tool calling capabilities
        """
        # Ensure config contains base_url
        config = config or {}
        if 'base_url' not in config:
            raise ValueError("Configuration must include 'base_url' for OpenAI-compatible adapter")
        
        # Initialize the base adapter
        super().__init__(
            provider, 
            credentials, 
            config, 
            capabilities, 
            tool_capabilities
        )
    
    def _initialize_client(self) -> None:
        """
        Initialize the HTTP client for making API requests.
        
        The client is configured with the base URL from the config and
        authentication headers if an API key is provided.
        """
        # Configure headers with optional API key
        headers = {}
        api_key = self.credentials.get('api_key')
        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'
        
        # Create client with base URL
        self.base_url = self.config['base_url'].rstrip('/')
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=headers,
            timeout=30.0  # 30 second timeout
        )
        
        logger.info(f"Initialized OpenAI-compatible client with base URL: {self.base_url}")
    
    def _determine_tool_invocation_mode(self) -> str:
        """
        Determine if the endpoint supports native tool calling.
        
        Most self-hosted models don't support native function calling yet,
        so default to prompt engineering unless explicitly set in config.
        
        Returns:
            'native' if the model supports native tool calling, 'prompt_engineered' otherwise
        """
        # Check if tool mode is explicitly set in config
        if 'tool_invocation_mode' in self.config:
            mode = self.config['tool_invocation_mode']
            if mode in ['native', 'prompt_engineered']:
                return mode
        
        # Default to prompt engineering for safety
        return 'prompt_engineered'
    
    async def generate_response(
        self, 
        prompt: str,
        tool_descriptions: List[Dict[str, Any]]
    ) -> str:
        """
        Generate a response from the LLM endpoint.
        
        Args:
            prompt: The input prompt for the LLM
            tool_descriptions: List of tool descriptions
            
        Returns:
            The response from the LLM
        """
        try:
            # Prepare the request payload
            payload = {
                "model": self.config.get("model", "default"),
                "messages": [{"role": "user", "content": prompt}],
                "temperature": self.config.get("temperature", 0.7),
                "max_tokens": self.config.get("max_tokens", 1024)
            }
            
            # Add system message if specified
            system_prompt = self.config.get("system_prompt")
            if system_prompt:
                payload["messages"].insert(0, {
                    "role": "system", 
                    "content": system_prompt
                })
            
            # Add tools if using native tool invocation
            if self.tool_invocation_mode == 'native' and tool_descriptions:
                payload["functions"] = self._format_tools_for_openai(tool_descriptions)
            
            # Send the request
            response = await self.client.post(
                "/v1/chat/completions",
                json=payload
            )
            response.raise_for_status()
            
            # Parse the response
            data = response.json()
            
            # Extract the response content
            if 'choices' in data and len(data['choices']) > 0:
                if 'message' in data['choices'][0]:
                    return data['choices'][0]['message'].get('content', '')
            
            # Handle unexpected response format
            logger.warning(f"Unexpected response format: {data}")
            return f"Error: Unexpected response format from model API"
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error during response generation: {str(e)}")
            return f"Error: API request failed - {str(e)}"
        except httpx.RequestError as e:
            logger.error(f"Request error during response generation: {str(e)}")
            return f"Error: Failed to connect to the model API - {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error during response generation: {str(e)}")
            return f"Error: Failed to generate response - {str(e)}"
    
    async def extract_tool_call(self, response: str) -> Optional[Dict[str, Any]]:
        """
        Extract a tool call from the LLM response.
        
        In native mode, the API response will contain function_call object.
        In prompt engineered mode, attempt to extract JSON from the response.
        
        Args:
            response: The response from the LLM
            
        Returns:
            A dictionary containing the tool call information, or None if no tool call is found
        """
        if self.tool_invocation_mode == 'native':
            # This would be handled directly in the generate_response method
            # as it would come from the API response structure
            return None
        
        # In prompt-engineered mode, look for JSON in the response
        try:
            # Look for JSON blocks in the response
            json_match = None
            
            # Check for ```json format
            import re
            json_block_pattern = r'```json\s*(.*?)\s*```'
            json_matches = re.findall(json_block_pattern, response, re.DOTALL)
            
            if json_matches:
                json_match = json_matches[0]
            else:
                # Try to find any JSON object in the response
                json_pattern = r'\{(?:[^{}]|(?:\{(?:[^{}]|(?:\{[^{}]*\}))*\}))*\}'
                json_matches = re.findall(json_pattern, response)
                if json_matches:
                    json_match = json_matches[0]
            
            if json_match:
                tool_data = json.loads(json_match)
                
                # Check if this looks like a tool call
                if isinstance(tool_data, dict) and ("function" in tool_data or "name" in tool_data or "tool" in tool_data):
                    # Extract the tool name and arguments
                    tool_name = tool_data.get("function") or tool_data.get("name") or tool_data.get("tool")
                    arguments = tool_data.get("arguments") or tool_data.get("params") or {}
                    
                    # If arguments is a string, try to parse it as JSON
                    if isinstance(arguments, str):
                        try:
                            arguments = json.loads(arguments)
                        except:
                            pass
                    
                    return {
                        "tool_name": tool_name,
                        "arguments": arguments
                    }
                    
        except Exception as e:
            logger.warning(f"Error extracting tool call: {str(e)}")
        
        return None
    
    async def process_tool_result(
        self, 
        prompt: str,
        response: str,
        tool_call: Dict[str, Any],
        tool_result: Dict[str, Any]
    ) -> str:
        """
        Process the result of a tool execution with the LLM.
        
        Args:
            prompt: The original input prompt
            response: The original LLM response
            tool_call: The tool call information
            tool_result: The result of the tool execution
            
        Returns:
            The final response from the LLM
        """
        try:
            # Format the tool result as a message to the LLM
            tool_name = tool_call.get("tool_name", "unknown_tool")
            tool_result_str = json.dumps(tool_result)
            
            # Create a prompt that includes the original prompt, the tool call, and the result
            result_prompt = (
                f"{prompt}\n\n"
                f"You used tool '{tool_name}' which returned the following result:\n"
                f"{tool_result_str}\n\n"
                f"Please provide a final response based on this information."
            )
            
            # Generate a new response that incorporates the tool result
            return await self.generate_response(result_prompt, [])
            
        except Exception as e:
            logger.error(f"Error processing tool result: {str(e)}")
            return f"Error: Failed to process tool result - {str(e)}"
    
    async def generate_streaming_response(
        self, 
        prompt: str,
        tool_descriptions: List[Dict[str, Any]]
    ) -> AsyncGenerator[str, None]:
        """
        Generate a streaming response from the LLM.
        
        Args:
            prompt: The input prompt for the LLM
            tool_descriptions: List of tool descriptions
            
        Returns:
            An async generator yielding response chunks
        """
        try:
            # Prepare the request payload
            payload = {
                "model": self.config.get("model", "default"),
                "messages": [{"role": "user", "content": prompt}],
                "temperature": self.config.get("temperature", 0.7),
                "max_tokens": self.config.get("max_tokens", 1024),
                "stream": True  # Enable streaming
            }
            
            # Add system message if specified
            system_prompt = self.config.get("system_prompt")
            if system_prompt:
                payload["messages"].insert(0, {
                    "role": "system", 
                    "content": system_prompt
                })
            
            # Add tools if using native tool invocation
            if self.tool_invocation_mode == 'native' and tool_descriptions:
                payload["functions"] = self._format_tools_for_openai(tool_descriptions)
            
            # Send the streaming request
            async with self.client.stream(
                "POST",
                "/v1/chat/completions",
                json=payload,
                timeout=60.0  # Longer timeout for streaming
            ) as response:
                response.raise_for_status()
                
                # Yield chunks as they arrive
                async for chunk in response.aiter_bytes():
                    if not chunk:
                        continue
                    
                    # Try to decode and parse the chunk
                    try:
                        # Handle Server-Sent Events (SSE) format
                        chunk_text = chunk.decode('utf-8')
                        if chunk_text.startswith('data: '):
                            chunk_text = chunk_text[6:]  # Remove 'data: ' prefix
                        
                        if chunk_text.strip() in ["[DONE]", "data: [DONE]"]:
                            continue
                        
                        data = json.loads(chunk_text)
                        
                        # Extract delta content
                        if 'choices' in data and len(data['choices']) > 0:
                            choice = data['choices'][0]
                            if 'delta' in choice and 'content' in choice['delta']:
                                content = choice['delta']['content']
                                if content:
                                    yield content
                    except Exception as e:
                        logger.warning(f"Error parsing chunk: {str(e)}")
                        continue
                        
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error during streaming: {str(e)}")
            yield f"Error: API streaming request failed - {str(e)}"
        except httpx.RequestError as e:
            logger.error(f"Request error during streaming: {str(e)}")
            yield f"Error: Failed to connect to the model API for streaming - {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error during streaming: {str(e)}")
            yield f"Error: Failed to generate streaming response - {str(e)}"
    
    def _format_tools_for_openai(self, tool_descriptions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format tool descriptions for the OpenAI API format.
        
        Args:
            tool_descriptions: List of tool descriptions
            
        Returns:
            List of tool descriptions in OpenAI format
        """
        openai_tools = []
        
        for tool in tool_descriptions:
            # Convert to OpenAI function format
            openai_tool = {
                "name": tool.get("name", ""),
                "description": tool.get("description", ""),
                "parameters": tool.get("input_schema", {})
            }
            openai_tools.append(openai_tool)
        
        return openai_tools
