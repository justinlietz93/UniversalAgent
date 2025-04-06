"""
Search tool module for the Universal LLM Tool Wrapper Interface.

This module provides search functionality using Google Custom Search API.
"""
import logging
import json
import aiohttp
from typing import Dict, Any, Optional, List
import logging # Ensure logging is imported

# Import config from within the src package
from ...config import API_ENDPOINTS # Relative import from src/universal_agent/tools -> src
from .base_tool import BaseTool # Keep relative import for sibling module

logger = logging.getLogger(__name__)

class GoogleSearchTool(BaseTool):
    """
    Tool for searching the web using Google Custom Search API.
    
    This tool allows searching the web using Google's Custom Search API.
    It requires a Google API key and Custom Search Engine ID (cx).
    
    To use this tool, you need to:
    1. Create a Google Cloud project and enable the Custom Search API
    2. Create a Custom Search Engine at https://programmablesearchengine.google.com/
    3. Get your API key and Search Engine ID
    """
    
    def __init__(self, api_key: str, cx: str):
        """
        Initialize the Google Search tool.
        
        Args:
            api_key: Google API key
            cx: Custom Search Engine ID
        """
        super().__init__()
        self._name = "google_search"
        self._description = "Search the web for information using Google Custom Search"
        self.api_key = api_key
        self.cx = cx
        self.search_config = API_ENDPOINTS.get("search", {})

        # Define input schema
        self._input_schema = {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query"
                },
                "num_results": {
                    "type": "integer",
                    "description": "Number of results to return (max 10)",
                    "default": self.search_config.get("params", {}).get("default_num_results", 3),
                    "minimum": 1,
                    "maximum": self.search_config.get("params", {}).get("max_results", 10)
                },
                "safe_search": {
                    "type": "string",
                    "description": "Safe search level",
                    "enum": ["off", "medium", "high"],
                    "default": "medium"
                }
            },
            "required": ["query"]
        }
        
        # Define output schema
        self._output_schema = {
            "type": "object",
            "properties": {
                "results": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "The title of the search result"
                            },
                            "link": {
                                "type": "string",
                                "description": "The URL of the search result"
                            },
                            "snippet": {
                                "type": "string",
                                "description": "A snippet from the search result"
                            },
                            "source": {
                                "type": "string",
                                "description": "The source of the search result"
                            }
                        }
                    },
                    "description": "Search results"
                },
                "total_results": {
                    "type": "integer",
                    "description": "Estimated total number of results"
                }
            }
        }

    async def _perform_search_request(self, url: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Internal helper to perform the actual aiohttp request."""
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Search API error: {response.status}, {error_text}")
                    # Raise an exception instead of returning error dict to separate concerns
                    raise aiohttp.ClientResponseError(
                        response.request_info,
                        response.history,
                        status=response.status,
                        message=error_text,
                        headers=response.headers
                    )
                data = await response.json()
                return data

    async def run(self, **kwargs) -> Dict[str, Any]:
        """
        Run the search tool.
        
        Args:
            **kwargs: Tool parameters including:
                query: The search query
                num_results: Number of results to return (optional)
                safe_search: Safe search level (optional)
            
        Returns:
            Dictionary containing search results
        """
        # Log execution
        self._log_execution(kwargs)
        
        # Get parameters
        query = kwargs.get("query")
        if not query:
            return {"error": "Query is required"}
        
        num_results = kwargs.get("num_results", 
                               self.search_config.get("params", {}).get("default_num_results", 3))
        
        # Ensure num_results is within limits
        max_results = self.search_config.get("params", {}).get("max_results", 10)
        num_results = min(max(1, num_results), max_results)
        
        safe_search = kwargs.get("safe_search", "medium")
        
        # Prepare request parameters
        url = self.search_config.get("url", "https://www.googleapis.com/customsearch/v1")
        params = {
            "q": query,
            "key": self.api_key,
            "cx": self.cx,
            "num": num_results,
            "safe": safe_search
        }

        try:
            # Call the internal helper method
            data = await self._perform_search_request(url, params)

            # Process results
            results = []
            items = data.get("items", [])
            for item in items:
                results.append({
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                    "source": item.get("displayLink", "")
                })
            
            # Get total results estimate
            total_results = 0
            if "searchInformation" in data and "totalResults" in data["searchInformation"]:
                try:
                    total_results = int(data["searchInformation"]["totalResults"])
                except (ValueError, TypeError):
                    total_results = len(results)
            
            result = {
                "results": results,
                "total_results": total_results
            }
            
            # Log result
            self._log_result(result)
            
            return result

        except aiohttp.ClientResponseError as e:
            # Handle API errors specifically
            logger.error(f"Search API error during execution: {e.status}, {e.message}")
            return {"error": f"Search API error: {e.status}"}
        except aiohttp.ClientError as e:
            # Handle general network/client errors
            logger.error(f"Network error during search execution: {str(e)}")
            return {"error": f"Search failed due to network error: {str(e)}"}
        except Exception as e:
            # Handle other unexpected errors
            logger.exception(f"Unexpected error executing search: {str(e)}") # Use logger.exception for full traceback
            return {"error": f"Search failed: {str(e)}"}
