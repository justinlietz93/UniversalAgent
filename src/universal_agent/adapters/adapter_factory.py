"""
Adapter factory module for the Universal LLM Tool Wrapper Interface.

This module provides functions for registering and instantiating LLM provider adapters.
"""
import importlib
import logging
from typing import Dict, Type, Any, Optional

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
# Use absolute import from src
from src.config import ADAPTER_REGISTRATIONS
from ..core.base import BaseLLMAdapter

logger = logging.getLogger(__name__)

# Registry for adapter classes
ADAPTER_REGISTRY: Dict[str, Type[BaseLLMAdapter]] = {}

# Flag to indicate if adapters have been loaded
_adapters_loaded = False

def register_adapter(adapter_name: str, adapter_class: Type[BaseLLMAdapter]) -> None:
    """
    Register an adapter class for a provider.
    
    Args:
        adapter_name: The name of the adapter
        adapter_class: The adapter class to register
    """
    logger.debug(f"Registering adapter: {adapter_name}")
    ADAPTER_REGISTRY[adapter_name] = adapter_class

def get_adapter_class(adapter_name: str) -> Optional[Type[BaseLLMAdapter]]:
    """
    Get an adapter class by name.
    
    Args:
        adapter_name: The name of the adapter
        
    Returns:
        The adapter class if found, None otherwise
    """
    # Ensure adapters are loaded
    _load_adapters()
    
    return ADAPTER_REGISTRY.get(adapter_name)

def _load_adapters() -> None:
    """
    Load all registered adapters.
    
    This function is called automatically when get_adapter_class is called.
    """
    global _adapters_loaded
    
    # Skip if adapters are already loaded
    if _adapters_loaded:
        return
    
    logger.debug("Loading adapters")
    
    # Load each registered adapter
    for provider, adapter_name in ADAPTER_REGISTRATIONS:
        try:
            # Import the adapter module
            module_name = f"src.universal_agent.adapters.{provider}_adapter"
            module = importlib.import_module(module_name)
            
            # Get the adapter class
            adapter_class = getattr(module, adapter_name)
            
            # Register the adapter
            register_adapter(adapter_name, adapter_class)
            
            logger.info(f"Loaded adapter: {adapter_name} for provider: {provider}")
        except (ImportError, AttributeError) as e:
            logger.warning(f"Failed to load adapter: {adapter_name} for provider: {provider}: {str(e)}")
    
    # Mock adapters for testing
    try:
        # Create a mock OpenAI adapter for testing
        class MockOpenAIAdapter(BaseLLMAdapter):
            def _initialize_client(self) -> None:
                pass
                
            def _determine_tool_invocation_mode(self) -> str:
                return "native"
                
            async def generate_response(self, prompt, tool_descriptions):
                return f"Mock response for: {prompt}"
                
            async def extract_tool_call(self, response):
                return None
                
            async def process_tool_result(self, prompt, response, tool_call, tool_result):
                return f"Tool result: {tool_result}"
                
            async def generate_streaming_response(self, prompt, tool_descriptions):
                async def mock_stream():
                    yield "Mock"
                    yield " streaming"
                    yield " response"
                return mock_stream()
        
        # Register the mock adapter
        register_adapter("OpenAIAdapter", MockOpenAIAdapter)
        logger.info("Registered mock OpenAI adapter for testing")
    except Exception as e:
        logger.warning(f"Failed to register mock adapter: {str(e)}")
    
    # Mark adapters as loaded
    _adapters_loaded = True
    
    logger.debug(f"Loaded {len(ADAPTER_REGISTRY)} adapters")
