"""
Documentation analyzer for the Universal LLM Tool Wrapper Interface.

This module provides functionality for retrieving and analyzing LLM provider
documentation to determine capabilities and configuration requirements.
"""
import logging
import re
import json
from typing import Dict, Any, List, Optional, Tuple
import aiohttp
from bs4 import BeautifulSoup

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))) # Add project root to path
# Use absolute import from src
from src.config import (
    PROVIDER_DOCS,
    DOC_SECTION_HEADERS,
    REGEX_PATTERNS, 
    AUTH_CONFIG, 
    TOOL_CAPABILITIES,
    get_provider_config
)

logger = logging.getLogger(__name__)

class DocumentationAnalyzer:
    """
    Analyzer for LLM provider documentation.
    
    This class retrieves and analyzes documentation from LLM providers to
    determine their capabilities and configuration requirements.
    """
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize the documentation analyzer.
        
        Args:
            cache_dir: Optional directory for caching documentation
        """
        self.cache_dir = cache_dir
        self.doc_sources = PROVIDER_DOCS
    
    async def retrieve_documentation(self, provider: str) -> str:
        """
        Retrieve documentation for a provider.
        
        Args:
            provider: The provider name (e.g., 'gemini', 'openai')
            
        Returns:
            The documentation content as a string
            
        Raises:
            ValueError: If the provider is not supported
            RuntimeError: If there is an error retrieving the documentation
        """
        logger.info(f"Retrieving documentation for provider: {provider}")
        
        # Check if provider is supported
        if provider.lower() not in self.doc_sources:
            raise ValueError(f"Unsupported provider: {provider}")

        # Get documentation sources for the provider
        doc_sources = self.doc_sources[provider.lower()]
        
        # Try to retrieve documentation from multiple sources
        combined_docs = ""
        
        try:
            # Retrieve API documentation
            api_docs = await self._fetch_url_content(doc_sources["api_docs"])
            combined_docs += f"{DOC_SECTION_HEADERS['api']}\n{api_docs}\n\n"
            
            # Retrieve function calling documentation
            function_docs = await self._fetch_url_content(doc_sources["function_calling_docs"])
            combined_docs += f"{DOC_SECTION_HEADERS['function_calling']}\n{function_docs}\n\n"
            
            # Try to retrieve OpenAPI spec if available
            if provider.lower() == "openai" and "openapi_spec" in doc_sources:
                openapi_spec = await self._fetch_url_content(doc_sources["openapi_spec"])
                combined_docs += f"{DOC_SECTION_HEADERS['openapi']}\n{openapi_spec}\n\n"
            
            logger.info(f"Successfully retrieved documentation for {provider}")
            return combined_docs
            
        except Exception as e:
            logger.error(f"Error retrieving documentation for {provider}: {str(e)}")
            raise RuntimeError(f"Error retrieving documentation for {provider}: {str(e)}")

    async def _make_request(self, session: aiohttp.ClientSession, url: str) -> aiohttp.ClientResponse:
        """Internal helper to make the HTTP request."""
        # This method exists primarily to be easily mocked in tests
        async with session.get(url) as response:
            # Ensure the response object is returned while still in the session context
            # We need to make sure the response object can be used outside the context
            # This might involve reading the content here or ensuring the mock handles it
            await response.read() # Read the body to allow using response outside context
            return response

    async def _fetch_url_content(self, url: str) -> str:
        """
        Fetch content from a URL using aiohttp.
        
        Args:
            url: The URL to fetch
            
        Returns:
            The content as a string
            RuntimeError: If there is an error fetching the content
        """
        try:
            async with aiohttp.ClientSession() as session:
                # Use the helper method to make the request
                response = await self._make_request(session, url)

                if response.status != 200:
                    # Raise the specific aiohttp error if possible
                    raise aiohttp.ClientResponseError(
                        response.request_info,
                        response.history,
                        status=response.status,
                        message=await response.text(), # Get error message from response
                        headers=response.headers
                    )

                content_type = response.headers.get('Content-Type', '')

                # Corrected indentation and structure
                if 'text/html' in content_type:
                    html = await response.text()
                    return self._extract_text_from_html(html)
                elif 'application/json' in content_type:
                    json_data = await response.json()
                    return json.dumps(json_data, indent=2)
                elif 'text/markdown' in content_type or url.endswith('.md'):
                    return await response.text()
                elif 'application/yaml' in content_type or url.endswith('.yaml') or url.endswith('.yml'):
                    return await response.text()
                else:
                    # Default to reading text if content type is unknown/unhandled
                    return await response.text()
        except aiohttp.ClientResponseError as e:
             # Re-raise specific HTTP errors
             logger.error(f"HTTP error fetching {url}: {e.status} {e.message}")
             raise RuntimeError(f"Failed to fetch {url}: {e.status}") from e
        except aiohttp.ClientError as e:
             # Handle other client errors (network, connection, etc.)
             logger.error(f"Client error fetching {url}: {str(e)}")
             raise RuntimeError(f"Error fetching {url}: {str(e)}") from e
        except Exception as e:
             # Catch any other unexpected errors
             logger.exception(f"Unexpected error fetching {url}: {str(e)}")
             raise RuntimeError(f"Error fetching {url}: {str(e)}") from e

    def _extract_text_from_html(self, html: str) -> str:
        """
        Extract text content from HTML.
        
        Args:
            html: The HTML content
            
        Returns:
            The extracted text
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
        
        # Get text
        text = soup.get_text()
        
        # Break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # Remove blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text
    
    async def analyze_capabilities(self, provider: str, documentation: str) -> Dict[str, Any]:
        """
        Analyze provider capabilities from documentation.
        
        Args:
            provider: The provider name
            documentation: The documentation content
            
        Returns:
            A dictionary of provider capabilities
            
        Raises:
            ValueError: If the provider is not supported
        """
        logger.info(f"Analyzing capabilities for provider: {provider}")
        
        # Initialize capabilities dictionary
        capabilities = {
            "provider": provider,
            "api_structure": {},
            "authentication": {},
            "models": [],
            "native_tool_calling": False,
            "tool_calling_format": None,
            "streaming_support": False,
            "streaming_protocol": None
        }
        
        # Analyze based on provider
        if provider.lower() == "gemini":
            capabilities = await self._analyze_gemini_capabilities(documentation, capabilities)
        elif provider.lower() == "openai":
            capabilities = await self._analyze_openai_capabilities(documentation, capabilities)
        elif provider.lower() == "anthropic":
            capabilities = await self._analyze_anthropic_capabilities(documentation, capabilities)
        elif provider.lower() == "mistral":
            capabilities = await self._analyze_mistral_capabilities(documentation, capabilities)
        else:
            capabilities = await self._analyze_generic_capabilities(documentation, capabilities)
        
        logger.info(f"Capability analysis complete for {provider}")
        return capabilities
    
    async def _analyze_gemini_capabilities(self, documentation: str, capabilities: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze Gemini-specific capabilities.
        
        Args:
            documentation: The documentation content
            capabilities: The capabilities dictionary to update
            
        Returns:
            Updated capabilities dictionary
        """
        # Check for API key authentication
        if "API_KEY" in documentation or "apiKey" in documentation:
            auth_config = get_provider_config("gemini", "auth")
            capabilities["authentication"].update(auth_config)
        
        # Check for native tool calling support
        if "function_calling" in documentation or "functionDeclaration" in documentation:
            capabilities["native_tool_calling"] = True
            capabilities["tool_calling_format"] = "google_function_calling"
        
        # Check for streaming support
        if "streamGenerateContent" in documentation or "stream=true" in documentation.lower():
            capabilities["streaming_support"] = True
            capabilities["streaming_protocol"] = "server_sent_events"
        
        # Extract model information
        model_pattern = REGEX_PATTERNS["model_extraction"]["gemini"]
        models = re.findall(model_pattern, documentation)
        capabilities["models"] = list(set(models))
        
        # Extract API structure
        if "generativeai.GenerativeModel" in documentation:
            capabilities["api_structure"]["client_class"] = "GenerativeModel"
            capabilities["api_structure"]["generation_method"] = "generate_content"
        
        return capabilities
    
    async def _analyze_openai_capabilities(self, documentation: str, capabilities: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze OpenAI-specific capabilities.
        
        Args:
            documentation: The documentation content
            capabilities: The capabilities dictionary to update
            
        Returns:
            Updated capabilities dictionary
        """
        # Check for API key authentication
        if "OPENAI_API_KEY" in documentation or "Bearer" in documentation:
            auth_config = get_provider_config("openai", "auth")
            capabilities["authentication"].update(auth_config)
        
        # Check for native tool calling support
        if "function_calling" in documentation or "functions" in documentation:
            capabilities["native_tool_calling"] = True
            capabilities["tool_calling_format"] = "openai_function_calling"
        
        # Check for streaming support
        if "stream=true" in documentation.lower() or "streaming responses" in documentation.lower():
            capabilities["streaming_support"] = True
            capabilities["streaming_protocol"] = "server_sent_events"
        
        # Extract model information
        model_pattern = REGEX_PATTERNS["model_extraction"]["openai"]
        models = re.findall(model_pattern, documentation)
        capabilities["models"] = list(set(models))
        
        # Extract API structure
        if "openai.ChatCompletion" in documentation:
            capabilities["api_structure"]["client_class"] = "ChatCompletion"
            capabilities["api_structure"]["generation_method"] = "create"
        
        return capabilities
    
    async def _analyze_anthropic_capabilities(self, documentation: str, capabilities: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze Anthropic-specific capabilities.
        
        Args:
            documentation: The documentation content
            capabilities: The capabilities dictionary to update
            
        Returns:
            Updated capabilities dictionary
        """
        # Check for API key authentication
        if "ANTHROPIC_API_KEY" in documentation or "x-api-key" in documentation:
            auth_config = get_provider_config("anthropic", "auth")
            capabilities["authentication"].update(auth_config)
        
        # Check for native tool calling support
        if "tool_use" in documentation or "tools" in documentation:
            capabilities["native_tool_calling"] = True
            capabilities["tool_calling_format"] = "anthropic_tool_use"
        
        # Check for streaming support
        if "stream=true" in documentation.lower() or "streaming" in documentation.lower():
            capabilities["streaming_support"] = True
            capabilities["streaming_protocol"] = "server_sent_events"
        
        # Extract model information
        model_pattern = REGEX_PATTERNS["model_extraction"]["anthropic"]
        models = re.findall(model_pattern, documentation)
        capabilities["models"] = list(set(models))
        
        # Extract API structure
        if "anthropic.Anthropic" in documentation:
            capabilities["api_structure"]["client_class"] = "Anthropic"
            capabilities["api_structure"]["generation_method"] = "messages.create"
        
        return capabilities
    
    async def _analyze_mistral_capabilities(self, documentation: str, capabilities: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze Mistral-specific capabilities.
        
        Args:
            documentation: The documentation content
            capabilities: The capabilities dictionary to update
            
        Returns:
            Updated capabilities dictionary
        """
        # Check for API key authentication
        if "MISTRAL_API_KEY" in documentation or "Authorization" in documentation:
            auth_config = get_provider_config("mistral", "auth")
            capabilities["authentication"].update(auth_config)
        
        # Check for native tool calling support
        if "function_calling" in documentation or "tools" in documentation:
            capabilities["native_tool_calling"] = True
            capabilities["tool_calling_format"] = "mistral_function_calling"
        
        # Check for streaming support
        if "stream=true" in documentation.lower() or "streaming" in documentation.lower():
            capabilities["streaming_support"] = True
            capabilities["streaming_protocol"] = "server_sent_events"
        
        # Extract model information
        model_pattern = REGEX_PATTERNS["model_extraction"]["mistral"]
        models = re.findall(model_pattern, documentation)
        capabilities["models"] = list(set(models))
        
        # Extract API structure
        if "mistralai.MistralClient" in documentation:
            capabilities["api_structure"]["client_class"] = "MistralClient"
            capabilities["api_structure"]["generation_method"] = "chat"
        
        return capabilities
    
    async def _analyze_generic_capabilities(self, documentation: str, capabilities: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze capabilities for a generic provider.
        
        Args:
            documentation: The documentation content
            capabilities: The capabilities dictionary to update
            
        Returns:
            Updated capabilities dictionary
        """
        # Check for API key authentication
        if "api key" in documentation.lower() or "apikey" in documentation.lower():
            auth_config = get_provider_config("default", "auth")
            capabilities["authentication"].update(auth_config)
        
        # Check for native tool calling support
        if "function" in documentation.lower() and ("call" in documentation.lower() or "tool" in documentation.lower()):
            capabilities["native_tool_calling"] = True
            capabilities["tool_calling_format"] = "generic_function_calling"
        
        # Check for streaming support
        if "stream" in documentation.lower() or "streaming" in documentation.lower():
            capabilities["streaming_support"] = True
            capabilities["streaming_protocol"] = "server_sent_events"
        
        # Extract model information (generic regex for model names)
        model_pattern = REGEX_PATTERNS["model_extraction"]["generic"]
        models = re.findall(model_pattern, documentation.lower())
        capabilities["models"] = list(set(models))
        
        return capabilities
    
    async def determine_tool_calling_capabilities(self, capabilities: Dict[str, Any]) -> Dict[str, Any]:
        """
        Determine tool calling capabilities.
        
        Args:
            capabilities: Provider capabilities
            
        Returns:
            Tool calling capabilities
        """
        provider = capabilities.get("provider", "").lower()
        
        # Start with default tool capabilities
        tool_capabilities = {
            "supported": capabilities.get("native_tool_calling", False),
            "format": capabilities.get("tool_calling_format", None),
            "supports_streaming": capabilities.get("streaming_support", False)
        }
        
        # Get provider-specific tool capabilities
        provider_tool_capabilities = get_provider_config(provider, "tool_capabilities")
        tool_capabilities.update(provider_tool_capabilities)
        
        return tool_capabilities
