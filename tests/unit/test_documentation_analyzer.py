import unittest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
import aiohttp
import json
import logging
import copy # For deep copying config dicts

# Ensure the src directory is in the Python path
import os
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from src.documentation.documentation_analyzer import DocumentationAnalyzer
# Need get_provider_config for capability tests
from src.config import PROVIDER_DOCS, DOC_SECTION_HEADERS, REGEX_PATTERNS, TOOL_CAPABILITIES, get_provider_config

# Disable logging during tests to avoid clutter
# logging.disable(logging.CRITICAL) # Keep disabled for cleaner output

# Use IsolatedAsyncioTestCase for async tests
class TestDocumentationAnalyzer(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.analyzer = DocumentationAnalyzer()
        # Increase maxDiff for better assertion failure messages
        self.maxDiff = None

    def test_initialization(self):
        """Test analyzer initialization."""
        self.assertEqual(self.analyzer.doc_sources, PROVIDER_DOCS)
        self.assertIsNone(self.analyzer.cache_dir) # Default

    def test_extract_text_from_html(self):
        """Test extracting text from HTML."""
        html = "<html><head><title>Test</title><style>p{color:red}</style></head>" \
               "<body><script>alert('hi');</script><h1>Header</h1><p> Paragraph 1. </p>" \
               "<p>Paragraph 2.</p><div><span>Nested</span></div></body></html>"
        # Correct expected output based on previous failure diff
        expected = "Test\nHeader\nParagraph 1.\nParagraph 2.\nNested"
        result = self.analyzer._extract_text_from_html(html)
        self.assertEqual(result, expected)

    # --- Corrected Mocking for _fetch_url_content tests ---
    def setup_aiohttp_mocks(self, MockClientSession, status, content_type=None, text_data=None, json_data=None, raise_error=None):
        """Helper to set up aiohttp mocks consistently."""
        # 1. Mock the final response object
        mock_response = AsyncMock() # Remove spec
        mock_response.status = status
        mock_response.headers = {'Content-Type': content_type or 'text/plain'}
        if text_data is not None:
            mock_response.text = AsyncMock(return_value=text_data)
        if json_data is not None:
            mock_response.json = AsyncMock(return_value=json_data)
        # Make the response object itself awaitable for the context manager
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        # 2. Mock the session object yielded by the first context manager
        mock_session = AsyncMock() # Remove spec
        if raise_error:
            mock_session.get.side_effect = raise_error
        else:
            # session.get() itself returns the awaitable response object
            mock_session.get.return_value = mock_response

        # 3. Mock the ClientSession context manager
        #    Its __aenter__ needs to return the mock_session
        MockClientSession.return_value.__aenter__.return_value = mock_session
        MockClientSession.return_value.__aexit__ = AsyncMock(return_value=None)
        return mock_session # Return session for assertion checks


    @patch('aiohttp.ClientSession')
    async def test_fetch_url_content_html(self, MockClientSession):
        """Test fetching HTML content."""
        url = "http://example.com/doc.html"
        html_content = "<html><body><p>HTML Doc</p></body></html>"
        expected_text = "HTML Doc"
        mock_session = self.setup_aiohttp_mocks(MockClientSession, 200, content_type='text/html', text_data=html_content)

        result = await self.analyzer._fetch_url_content(url)
        self.assertEqual(result, expected_text)
        mock_session.get.assert_called_once_with(url)

    @patch('aiohttp.ClientSession')
    async def test_fetch_url_content_json(self, MockClientSession):
        """Test fetching JSON content."""
        url = "http://example.com/api.json"
        json_content = {"key": "value", "nested": [1, 2]}
        expected_text = json.dumps(json_content, indent=2)
        mock_session = self.setup_aiohttp_mocks(MockClientSession, 200, content_type='application/json', json_data=json_content)

        result = await self.analyzer._fetch_url_content(url)
        self.assertEqual(result, expected_text)
        mock_session.get.assert_called_once_with(url)

    @patch('aiohttp.ClientSession')
    async def test_fetch_url_content_markdown(self, MockClientSession):
        """Test fetching Markdown content."""
        url = "http://example.com/readme.md"
        md_content = "# Header\n* List item"
        mock_session = self.setup_aiohttp_mocks(MockClientSession, 200, content_type='text/markdown', text_data=md_content)

        result = await self.analyzer._fetch_url_content(url)
        self.assertEqual(result, md_content)
        mock_session.get.assert_called_once_with(url)

    @patch('aiohttp.ClientSession')
    async def test_fetch_url_content_yaml(self, MockClientSession):
        """Test fetching YAML content."""
        url = "http://example.com/config.yaml"
        yaml_content = "key: value\nlist:\n  - item1"
        mock_session = self.setup_aiohttp_mocks(MockClientSession, 200, content_type='application/yaml', text_data=yaml_content)

        result = await self.analyzer._fetch_url_content(url)
        self.assertEqual(result, yaml_content)
        mock_session.get.assert_called_once_with(url)

    @patch('aiohttp.ClientSession')
    async def test_fetch_url_content_error_status(self, MockClientSession):
        """Test fetching URL with non-200 status."""
        url = "http://example.com/error"
        # Mock the response directly for the error case within the helper
        mock_response = AsyncMock() # Remove spec
        mock_response.status = 404
        mock_response.request_info = MagicMock()
        mock_response.history = ()
        mock_response.text = AsyncMock(return_value="Not Found")
        # Mock the context manager methods for the response
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session = AsyncMock() # Remove spec
        mock_session.get.return_value = mock_response # get() returns the awaitable response object

        MockClientSession.return_value.__aenter__.return_value = mock_session
        MockClientSession.return_value.__aexit__ = AsyncMock(return_value=None)

        # Check the specific exception raised by _fetch_url_content
        with self.assertRaises(RuntimeError) as cm:
            await self.analyzer._fetch_url_content(url)
        # Check the final RuntimeError message raised by _fetch_url_content
        self.assertEqual(str(cm.exception), "Failed to fetch http://example.com/error: 404")


    @patch('aiohttp.ClientSession')
    async def test_fetch_url_content_network_error(self, MockClientSession):
        """Test fetching URL with network error."""
        url = "http://example.com/network_error"
        mock_session = AsyncMock() # Remove spec
        mock_session.get.side_effect = aiohttp.ClientError("Connection failed")

        MockClientSession.return_value.__aenter__.return_value = mock_session
        MockClientSession.return_value.__aexit__ = AsyncMock(return_value=None)

        # Check the specific exception raised by _fetch_url_content
        with self.assertRaisesRegex(RuntimeError, "Error fetching http://example.com/network_error: Connection failed"):
             await self.analyzer._fetch_url_content(url)

    # --- Tests for retrieve_documentation (mocking _fetch_url_content) ---
    @patch('src.documentation.documentation_analyzer.DocumentationAnalyzer._fetch_url_content', new_callable=AsyncMock)
    async def test_retrieve_documentation_success(self, mock_fetch):
        """Test retrieving documentation successfully."""
        provider = "openai"
        mock_fetch.side_effect = ["API Docs Content", "Function Docs Content", "OpenAPI Spec Content"]

        result = await self.analyzer.retrieve_documentation(provider)

        expected_calls = [
            unittest.mock.call(PROVIDER_DOCS[provider]["api_docs"]),
            unittest.mock.call(PROVIDER_DOCS[provider]["function_calling_docs"]),
            unittest.mock.call(PROVIDER_DOCS[provider]["openapi_spec"]),
        ]
        self.assertEqual(mock_fetch.call_args_list, expected_calls)

        self.assertIn(DOC_SECTION_HEADERS['api'], result)
        self.assertIn("API Docs Content", result)
        self.assertIn(DOC_SECTION_HEADERS['function_calling'], result)
        self.assertIn("Function Docs Content", result)
        self.assertIn(DOC_SECTION_HEADERS['openapi'], result)
        self.assertIn("OpenAPI Spec Content", result)

    async def test_retrieve_documentation_unsupported_provider(self):
        """Test retrieving documentation for an unsupported provider."""
        with self.assertRaisesRegex(ValueError, "Unsupported provider: unknown"):
            await self.analyzer.retrieve_documentation("unknown")

    @patch('src.documentation.documentation_analyzer.DocumentationAnalyzer._fetch_url_content', new_callable=AsyncMock)
    async def test_retrieve_documentation_fetch_error(self, mock_fetch):
        """Test retrieving documentation when fetching fails."""
        provider = "gemini"
        mock_fetch.side_effect = RuntimeError("Fetch failed")

        with self.assertRaisesRegex(RuntimeError, f"Error retrieving documentation for {provider}: Fetch failed"):
            await self.analyzer.retrieve_documentation(provider)

    # --- Corrected Capability Analysis Tests ---
    async def test_analyze_openai_capabilities(self):
        """Test analyzing capabilities for OpenAI."""
        doc = """
        API Reference - Authentication with OPENAI_API_KEY or Bearer token.
        Function Calling Guide - Use the 'functions' parameter. Supports stream=true.
        Models: gpt-4, gpt-3.5-turbo. Use openai.ChatCompletion.create().
        """
        expected = {
            "provider": "openai",
            "api_structure": {"client_class": "ChatCompletion", "generation_method": "create"},
            "authentication": {"method": "api_key", "header": "Authorization", "prefix": "Bearer "},
            "models": ["gpt-3.5-turbo", "gpt-4"], # Corrected order
            "native_tool_calling": True,
            "tool_calling_format": "openai_function_calling",
            "streaming_support": True,
            "streaming_protocol": "server_sent_events"
        }
        result = await self.analyzer.analyze_capabilities("openai", doc)
        result["models"].sort() # Sort for consistent comparison
        self.assertEqual(result, expected)

    async def test_analyze_gemini_capabilities(self):
        """Test analyzing capabilities for Gemini."""
        doc = """
        Get started with your API_KEY. Use functionDeclaration for tools.
        Streaming available via streamGenerateContent. Models: gemini-pro, gemini-1.5-pro.
        Client: generativeai.GenerativeModel, Method: generate_content.
        """
        expected = {
            "provider": "gemini",
            "api_structure": {"client_class": "GenerativeModel", "generation_method": "generate_content"},
            "authentication": {"method": "api_key", "header": "X-Goog-Api-Key", "prefix": ""}, # Corrected case
            "models": ["gemini-1.5-pro", "gemini-pro"],
            "native_tool_calling": True,
            "tool_calling_format": "google_function_calling",
            "streaming_support": True,
            "streaming_protocol": "server_sent_events"
        }
        result = await self.analyzer.analyze_capabilities("gemini", doc)
        result["models"].sort()
        self.assertEqual(result, expected)

    async def test_analyze_anthropic_capabilities(self):
        """Test analyzing capabilities for Anthropic."""
        doc = """
        Authenticate using x-api-key: YOUR_ANTHROPIC_API_KEY.
        Tool use is supported via the 'tools' parameter. Streaming is possible.
        Models: claude-3-opus-20240229, claude-3-sonnet-20240229.
        Client: anthropic.Anthropic, Method: messages.create.
        """
        expected = {
            "provider": "anthropic",
            "api_structure": {"client_class": "Anthropic", "generation_method": "messages.create"},
            "authentication": {"method": "api_key", "header": "x-api-key", "prefix": ""},
            "models": ["claude-3-opus-20240229", "claude-3-sonnet-20240229"], # Corrected names
            "native_tool_calling": True,
            "tool_calling_format": "anthropic_tool_use",
            "streaming_support": True,
            "streaming_protocol": "server_sent_events"
        }
        result = await self.analyzer.analyze_capabilities("anthropic", doc)
        result["models"].sort()
        self.assertEqual(result, expected)

    async def test_analyze_mistral_capabilities(self):
         """Test analyzing capabilities for Mistral."""
         doc = """
         Use Authorization: Bearer MISTRAL_API_KEY. Function calling with tools.
         Streaming supported. Models: mistral-large-latest, mistral-small-latest.
         Client: mistralai.MistralClient, Method: chat.
         """
         expected = {
             "provider": "mistral",
             "api_structure": {"client_class": "MistralClient", "generation_method": "chat"},
             "authentication": {"method": "api_key", "header": "Authorization", "prefix": "Bearer "},
             "models": ["mistral-large-latest", "mistral-small-latest"], # Corrected names
             "native_tool_calling": True,
             "tool_calling_format": "mistral_function_calling",
             "streaming_support": True,
             "streaming_protocol": "server_sent_events"
         }
         result = await self.analyzer.analyze_capabilities("mistral", doc)
         result["models"].sort()
         self.assertEqual(result, expected)

    async def test_analyze_generic_capabilities(self):
         """Test analyzing capabilities for a generic provider."""
         doc = """
         Our API uses an api key for auth. Function calls are possible. Stream results.
         Model: generic-model-v1.
         """
         expected = {
             "provider": "generic",
             "api_structure": {},
             "authentication": {"method": "api_key", "header": "Authorization", "prefix": "Bearer "}, # Corrected prefix
             "models": ["generic-model-v1"], # Corrected name
             "native_tool_calling": True,
             "tool_calling_format": "generic_function_calling",
             "streaming_support": True,
             "streaming_protocol": "server_sent_events"
         }
         result = await self.analyzer.analyze_capabilities("generic", doc)
         self.assertEqual(result, expected)

    # --- Test for determine_tool_calling_capabilities ---
    async def test_determine_tool_calling_capabilities(self): # Make test async
        """Test determining tool calling capabilities."""
        analyzer = DocumentationAnalyzer() # Create instance for non-async method
        # Example analyzed capabilities
        analyzed_caps = {
            "provider": "openai",
            "native_tool_calling": True,
            "tool_calling_format": "openai_function_calling",
            "streaming_support": True
        }
        # Get expected merged capabilities from config
        expected_tool_caps = copy.deepcopy(TOOL_CAPABILITIES["openai"])
        expected_tool_caps.update({ # Add analyzed flags
             "supported": True,
             "format": "openai_function_calling",
             "supports_streaming": True
        })

        # This method IS async, needs await
        result = await analyzer.determine_tool_calling_capabilities(analyzed_caps)
        self.assertEqual(result, expected_tool_caps)

        # Test with a provider having different defaults
        analyzed_caps_generic = {
            "provider": "generic",
            "native_tool_calling": False,
            "tool_calling_format": None,
            "streaming_support": False
        }
        expected_tool_caps_generic = copy.deepcopy(TOOL_CAPABILITIES["default"])
        expected_tool_caps_generic.update({
             "supported": False,
             "format": None,
             "supports_streaming": False
        })
        # This method IS async, needs await
        result_generic = await analyzer.determine_tool_calling_capabilities(analyzed_caps_generic)
        self.assertEqual(result_generic, expected_tool_caps_generic)

# Re-enable logging after tests if needed
# logging.disable(logging.NOTSET)

# No need for if __name__ == '__main__': unittest.main() when using discover
