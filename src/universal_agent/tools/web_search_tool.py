"""
Web Search Tool for the Universal Agent.

This module provides a tool for performing web searches using Google Custom Search API.
"""
import logging
import json
import os
from typing import Dict, Any, List, Optional, Union

import httpx
from bs4 import BeautifulSoup

from src.universal_agent.tools.base_tool import BaseTool
from src.universal_agent.interfaces.types import ToolParams, ToolResult
from src.config import API_ENDPOINTS, get_credential

logger = logging.getLogger(__name__)

class WebSearchTool(BaseTool):
    """
    Tool for performing web searches using Google Custom Search API.
    
    This tool allows searching the web and returning relevant results.
    """
    
    def __init__(self, api_key: str = None, search_engine_id: str = None):
        """
        Initialize the web search tool.
        
        Args:
            api_key (str, optional): Google API key. If not provided, will try to get from environment.
            search_engine_id (str, optional): Google Custom Search Engine ID. If not provided, will try to get from environment.
        """
        super().__init__(
            id="web_search",
            name="Web Search",
            description="Search the web for information on a topic. Useful for finding current information or answering questions about recent events, facts, or other topics."
        )
        
        # Get API key and search engine ID
        self._api_key = api_key or get_credential("google_api_key")
        self._cx = search_engine_id or get_credential("google_cx")
        
        # Get API endpoint and parameters
        self._api_config = API_ENDPOINTS.get("search", {})
        self._api_url = self._api_config.get("url", "https://www.googleapis.com/customsearch/v1")
        self._default_num_results = self._api_config.get("params", {}).get("default_num_results", 3)
        self._max_results = self._api_config.get("params", {}).get("max_results", 10)
        
        # Initialize HTTP client
        self._client = httpx.AsyncClient(timeout=30.0)
    
    def get_parameter_schema(self) -> Dict[str, Any]:
        """
        Get the schema for the parameters expected by this tool.
        
        Returns:
            Dict[str, Any]: JSON Schema for parameters.
        """
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to execute. For best results, make this specific and concise."
                },
                "num_results": {
                    "type": "integer",
                    "description": f"Number of results to return (default: {self._default_num_results}, max: {self._max_results}).",
                    "default": self._default_num_results,
                    "minimum": 1,
                    "maximum": self._max_results
                }
            },
            "required": ["query"]
        }
    
    async def execute(self, params: ToolParams) -> ToolResult:
        """
        Execute a web search with the given parameters.
        
        Args:
            params (ToolParams): Parameters for the search.
                - query (str): The search query.
                - num_results (int, optional): Number of results to return.
        
        Returns:
            ToolResult: The search results.
        """
        try:
            # Validate parameters
            validation_error = self.validate_parameters(params)
            if validation_error:
                return self.create_error_result(validation_error)
            
            # Extract parameters
            query = params.get("query")
            num_results = min(
                params.get("num_results", self._default_num_results),
                self._max_results
            )
            
            # Check if API key and search engine ID are available
            if not self._api_key or not self._cx:
                return self.create_error_result(
                    "API key or search engine ID not configured. Please provide 'google_api_key' and 'google_cx' credentials."
                )
            
            # Execute search
            search_results = await self._execute_search(query, num_results)
            
            # Return results
            return self.create_success_result({
                "query": query,
                "results": search_results
            })
        
        except Exception as e:
            logger.error(f"Error in web search: {str(e)}")
            return self.create_error_result(f"Web search failed: {str(e)}")
    
    async def _execute_search(self, query: str, num_results: int) -> List[Dict[str, Any]]:
        """
        Execute a search using the Google Custom Search API.
        
        Args:
            query (str): The search query.
            num_results (int): Number of results to return.
        
        Returns:
            List[Dict[str, Any]]: List of search results.
        """
        # Prepare parameters
        params = {
            "key": self._api_key,
            "cx": self._cx,
            "q": query,
            "num": min(num_results, 10)  # API limit is 10 per request
        }
        
        # Make request
        response = await self._client.get(self._api_url, params=params)
        response.raise_for_status()
        
        # Parse response
        data = response.json()
        
        # Process results
        processed_results = []
        
        # Check if search information is available
        if "searchInformation" in data:
            total_results = int(data["searchInformation"].get("totalResults", 0))
            if total_results == 0:
                return []
        
        # Extract results
        items = data.get("items", [])
        for item in items[:num_results]:
            result = {
                "title": item.get("title", ""),
                "link": item.get("link", ""),
                "snippet": item.get("snippet", ""),
                "display_link": item.get("displayLink", "")
            }
            
            processed_results.append(result)
        
        return processed_results
