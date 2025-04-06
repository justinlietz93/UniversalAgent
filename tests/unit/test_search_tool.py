import unittest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
import aiohttp # Still needed for exception types

# Ensure the src directory is in the Python path
import os
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from src.universal_agent.tools.search_tool import GoogleSearchTool
from src.config import API_ENDPOINTS

# Use IsolatedAsyncioTestCase for async tests
class TestGoogleSearchTool(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        """Set up for test methods."""
        self.api_key = "test_api_key"
        self.cx = "test_cx"
        self.tool = GoogleSearchTool(api_key=self.api_key, cx=self.cx)

    def test_initialization(self):
        """Test tool initialization."""
        self.assertIsInstance(self.tool, GoogleSearchTool)
        self.assertEqual(self.tool._name, "google_search")
        self.assertEqual(self.tool.api_key, self.api_key)
        self.assertEqual(self.tool.cx, self.cx)
        self.assertIn("query", self.tool._input_schema["required"])
        self.assertIn("results", self.tool._output_schema["properties"])

    # Patch the internal helper method now, not aiohttp.ClientSession
    @patch('src.universal_agent.tools.search_tool.GoogleSearchTool._perform_search_request', new_callable=AsyncMock)
    async def test_run_success(self, mock_perform_request): # Make test async
        """Test successful run of the search tool."""
        mock_response_json = {
            "items": [
                {"title": "Result 1", "link": "http://example.com/1", "snippet": "Snippet 1", "displayLink": "example.com"},
                {"title": "Result 2", "link": "http://example.com/2", "snippet": "Snippet 2", "displayLink": "example.com"}
            ],
            "searchInformation": {"totalResults": "12345"}
        }
        # Configure the mock helper method's return value
        mock_perform_request.return_value = mock_response_json

        kwargs = {"query": "test query", "num_results": 2}
        result = await self.tool.run(**kwargs) # Use await

        self.assertNotIn("error", result, f"Expected no error, but got: {result.get('error')}")
        self.assertIn("results", result)
        self.assertEqual(len(result["results"]), 2)
        self.assertEqual(result["total_results"], 12345)
        expected_url = API_ENDPOINTS.get("search", {}).get("url", "https://www.googleapis.com/customsearch/v1")
        expected_params = {"q": "test query", "key": self.api_key, "cx": self.cx, "num": 2, "safe": "medium"}
        # Assert the helper method was called correctly
        mock_perform_request.assert_called_once_with(expected_url, expected_params)


    async def test_run_missing_query(self): # Make test async
        """Test running the tool with a missing query."""
        kwargs = {}
        result = await self.tool.run(**kwargs) # Use await
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Query is required")

    @patch('src.universal_agent.tools.search_tool.GoogleSearchTool._perform_search_request', new_callable=AsyncMock)
    async def test_run_api_error(self, mock_perform_request): # Make test async
        """Test handling of API errors."""
        # Configure the mock helper method to raise ClientResponseError
        mock_perform_request.side_effect = aiohttp.ClientResponseError(
            MagicMock(), (), status=400, message="Bad Request"
        )

        kwargs = {"query": "test query"}
        result = await self.tool.run(**kwargs) # Use await

        self.assertIn("error", result)
        self.assertEqual(result["error"], "Search API error: 400")


    @patch('src.universal_agent.tools.search_tool.GoogleSearchTool._perform_search_request', new_callable=AsyncMock)
    async def test_run_network_error(self, mock_perform_request): # Make test async
        """Test handling of network errors during API call."""
        # Configure the mock helper method to raise ClientError
        mock_perform_request.side_effect = aiohttp.ClientError("Network connection failed")

        kwargs = {"query": "test query"}
        result = await self.tool.run(**kwargs) # Use await

        self.assertIn("error", result)
        self.assertTrue(result["error"].startswith("Search failed due to network error:"))
        self.assertIn("Network connection failed", result["error"])

    @patch('src.universal_agent.tools.search_tool.GoogleSearchTool._perform_search_request', new_callable=AsyncMock)
    async def test_run_num_results_clamping(self, mock_perform_request): # Make test async
        """Test that num_results is clamped correctly."""
        mock_response_json = {"items": [], "searchInformation": {"totalResults": "0"}}
        mock_perform_request.return_value = mock_response_json

        # Test num_results below minimum
        await self.tool.run(query="test", num_results=0) # Use await
        params_zero = mock_perform_request.call_args_list[0].args[1] # Get params from first call
        self.assertEqual(params_zero['num'], 1)

        # Test num_results above maximum
        await self.tool.run(query="test", num_results=20) # Use await
        params_twenty = mock_perform_request.call_args_list[1].args[1] # Get params from second call
        max_results = API_ENDPOINTS.get("search", {}).get("params", {}).get("max_results", 10)
        self.assertEqual(params_twenty['num'], max_results)

# No need for if __name__ == '__main__': unittest.main() when using discover
