"""
Base adapter module for the Universal LLM Tool Wrapper Interface.

This module defines the base adapter class that all LLM provider adapters must extend.
"""
import abc
import logging
from typing import Dict, List, Any, Optional, Union, Tuple

logger = logging.getLogger(__name__)

class BaseLLMAdapter(abc.ABC):
    """
    Abstract base class for LLM provider adapters.
    
    This class defines the interface that all LLM provider adapters must implement.
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
        Initialize the LLM adapter.
        
        Args:
            provider: The LLM provider name
            credentials: Authentication credentials for the LLM provider
            config: Optional configuration parameters
            capabilities: Optional provider capabilities
            tool_capabilities: Optional tool calling capabilities
        """
        self.provider = provider
        self.credentials = credentials
        self.config = config or {}
        self.capabilities = capabilities or {}
        self.tool_capabilities = tool_capabilities or {}
        self.client = None
        
        # Tool invocation mode: 'native' or 'prompt_engineered'
        self._tool_invocation_mode = None
        
        # Initialize the client
        self._initialize_client()
    
    @property
    def tool_invocation_mode(self) -> str:
        """
        Get the tool invocation mode for this adapter.
        
        Returns:
            'native' if the LLM supports native tool calling, 'prompt_engineered' otherwise
        """
        if not self._tool_invocation_mode:
            # Determine the tool invocation mode if not already set
            self._tool_invocation_mode = self._determine_tool_invocation_mode()
        
        return self._tool_invocation_mode
    
    @abc.abstractmethod
    def _initialize_client(self) -> None:
        """
        Initialize the LLM client.
        
        This method should set up the client for the specific LLM provider.
        """
        pass
    
    @abc.abstractmethod
    def _determine_tool_invocation_mode(self) -> str:
        """
        Determine the appropriate tool invocation mode for this LLM.
        
        Returns:
            'native' if the LLM supports native tool calling, 'prompt_engineered' otherwise
        """
        pass
    
    @abc.abstractmethod
    async def generate_response(
        self, 
        prompt: str,
        tool_descriptions: List[Dict[str, Any]]
    ) -> str:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: The input prompt for the LLM
            tool_descriptions: List of tool descriptions
            
        Returns:
            The response from the LLM
        """
        pass
    
    @abc.abstractmethod
    async def extract_tool_call(self, response: str) -> Optional[Dict[str, Any]]:
        """
        Extract a tool call from the LLM response.
        
        Args:
            response: The response from the LLM
            
        Returns:
            A dictionary containing the tool call information, or None if no tool call is found
        """
        pass
    
    @abc.abstractmethod
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
        pass
    
    @abc.abstractmethod
    async def generate_streaming_response(
        self, 
        prompt: str,
        tool_descriptions: List[Dict[str, Any]]
    ) -> Any:
        """
        Generate a streaming response from the LLM.
        
        Args:
            prompt: The input prompt for the LLM
            tool_descriptions: List of tool descriptions
            
        Returns:
            A stream of response chunks from the LLM
        """
        pass
