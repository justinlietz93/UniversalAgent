"""Tests for the web search and scraper tools."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any

from src.universal_agent.tools.web_search_tool import WebSearchTool
from src.universal_agent.tools.web_scraper_tool import WebScraperTool


@pytest.fixture
def mock_search_tool():
    """Create a mock web search tool instance for testing."""
    with patch('httpx.AsyncClient') as mock_client:
        tool = WebSearchTool(api_key="test_api_key", search_engine_id="test_cx")
        tool._client = AsyncMock()
        return tool


@pytest.fixture
def mock_scraper_tool():
    """Create a mock web scraper tool instance for testing."""
    with patch('httpx.AsyncClient') as mock_client:
        tool = WebScraperTool()
        tool._client = AsyncMock()
        return tool


@pytest.mark.asyncio
async def test_search_tool_validation(mock_search_tool):
    """Test parameter validation in web search tool."""
    # Test missing required parameter
    result = await mock_search_tool.execute({})
    assert result.success is False
    assert "query" in result.error.lower()
    
    # Test valid parameters
    mock_search_tool._execute_search = AsyncMock(return_value=[])
    result = await mock_search_tool.execute({"query": "test query"})
    assert result.success is True
    mock_search_tool._execute_search.assert_called_once()


@pytest.mark.asyncio
async def test_search_tool_execution(mock_search_tool):
    """Test search tool execution with mocked API response."""
    # Setup mock response
    mock_search_result = [
        {
            "title": "Test Result",
            "link": "https://example.com",
            "snippet": "This is a test result.",
            "display_link": "example.com"
        }
    ]
    mock_search_tool._execute_search = AsyncMock(return_value=mock_search_result)
    
    # Execute search
    result = await mock_search_tool.execute({
        "query": "test query",
        "num_results": 1
    })
    
    # Verify result
    assert result.success is True
    assert result.data["query"] == "test query"
    assert len(result.data["results"]) == 1
    assert result.data["results"][0]["title"] == "Test Result"


@pytest.mark.asyncio
async def test_search_api_call(mock_search_tool):
    """Test the search API call."""
    # Setup mock response
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "items": [
            {
                "title": "Result 1",
                "link": "https://example.com/1",
                "snippet": "Snippet 1",
                "displayLink": "example.com"
            },
            {
                "title": "Result 2",
                "link": "https://example.com/2",
                "snippet": "Snippet 2",
                "displayLink": "example.com"
            }
        ],
        "searchInformation": {
            "totalResults": "2"
        }
    }
    mock_response.raise_for_status = MagicMock()
    mock_search_tool._client.get = AsyncMock(return_value=mock_response)
    
    # Execute search
    results = await mock_search_tool._execute_search("test query", 2)
    
    # Verify results
    assert len(results) == 2
    assert results[0]["title"] == "Result 1"
    assert results[1]["title"] == "Result 2"
    
    # Verify API call
    mock_search_tool._client.get.assert_called_once()
    args, kwargs = mock_search_tool._client.get.call_args
    assert args[0] == mock_search_tool._api_url
    assert kwargs["params"]["q"] == "test query"
    assert kwargs["params"]["num"] == 2


@pytest.mark.asyncio
async def test_scraper_tool_validation(mock_scraper_tool):
    """Test parameter validation in web scraper tool."""
    # Test missing required parameter
    result = await mock_scraper_tool.execute({})
    assert result.success is False
    assert "url" in result.error.lower()
    
    # Test invalid URL
    mock_scraper_tool._is_valid_url = MagicMock(return_value=False)
    result = await mock_scraper_tool.execute({"url": "invalid-url"})
    assert result.success is False
    assert "invalid url" in result.error.lower()


@pytest.mark.asyncio
async def test_scraper_tool_text_extraction(mock_scraper_tool):
    """Test text extraction with the scraper tool."""
    # Mock URL validation and page fetching
    mock_scraper_tool._is_valid_url = MagicMock(return_value=True)
    mock_scraper_tool._fetch_page = AsyncMock(return_value="""
    <html>
        <head><title>Test Page</title></head>
        <body>
            <h1>Test Heading</h1>
            <p>This is a test paragraph.</p>
            <p>This is another paragraph.</p>
        </body>
    </html>
    """)
    
    # Test text extraction
    result = await mock_scraper_tool.execute({
        "url": "https://example.com",
        "extraction_type": "text"
    })
    
    # Verify result
    assert result.success is True
    assert "Test Heading" in result.data["content"]
    assert "test paragraph" in result.data["content"].lower()


@pytest.mark.asyncio
async def test_scraper_tool_headings_extraction(mock_scraper_tool):
    """Test headings extraction with the scraper tool."""
    # Mock URL validation and page fetching
    mock_scraper_tool._is_valid_url = MagicMock(return_value=True)
    mock_scraper_tool._fetch_page = AsyncMock(return_value="""
    <html>
        <head><title>Test Page</title></head>
        <body>
            <h1>Main Heading</h1>
            <h2>Subheading 1</h2>
            <p>Some content.</p>
            <h2>Subheading 2</h2>
            <p>More content.</p>
            <h3>Sub-subheading</h3>
        </body>
    </html>
    """)
    
    # Test headings extraction
    result = await mock_scraper_tool.execute({
        "url": "https://example.com",
        "extraction_type": "headings"
    })
    
    # Verify result
    assert result.success is True
    assert len(result.data["headings"]) == 4
    assert result.data["headings"][0]["text"] == "Main Heading"
    assert result.data["headings"][0]["level"] == 1
    assert result.data["headings"][3]["text"] == "Sub-subheading"
    assert result.data["headings"][3]["level"] == 3


@pytest.mark.asyncio
async def test_scraper_tool_table_extraction(mock_scraper_tool):
    """Test table extraction with the scraper tool."""
    # Mock URL validation and page fetching
    mock_scraper_tool._is_valid_url = MagicMock(return_value=True)
    mock_scraper_tool._fetch_page = AsyncMock(return_value="""
    <html>
        <head><title>Test Page</title></head>
        <body>
            <table>
                <thead>
                    <tr>
                        <th>Header 1</th>
                        <th>Header 2</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Cell 1,1</td>
                        <td>Cell 1,2</td>
                    </tr>
                    <tr>
                        <td>Cell 2,1</td>
                        <td>Cell 2,2</td>
                    </tr>
                </tbody>
            </table>
        </body>
    </html>
    """)
    
    # Test table extraction
    result = await mock_scraper_tool.execute({
        "url": "https://example.com",
        "extraction_type": "table"
    })
    
    # Verify result
    assert result.success is True
    assert len(result.data["tables"]) == 1
    assert result.data["tables"][0]["header"] == ["Header 1", "Header 2"]
    assert len(result.data["tables"][0]["rows"]) == 2
    assert result.data["tables"][0]["rows"][0] == ["Cell 1,1", "Cell 1,2"]


@pytest.mark.asyncio
async def test_scraper_tool_element_extraction(mock_scraper_tool):
    """Test specific element extraction with the scraper tool."""
    # Mock URL validation and page fetching
    mock_scraper_tool._is_valid_url = MagicMock(return_value=True)
    mock_scraper_tool._fetch_page = AsyncMock(return_value="""
    <html>
        <head><title>Test Page</title></head>
        <body>
            <div class="content">
                <p>This is the first paragraph in the content div.</p>
                <p>This is the second paragraph.</p>
            </div>
            <div class="footer">
                <p>This is footer content.</p>
            </div>
        </body>
    </html>
    """)
    
    # Test element extraction
    result = await mock_scraper_tool.execute({
        "url": "https://example.com",
        "extraction_type": "element",
        "element_selector": "div.content p"
    })
    
    # Verify result
    assert result.success is True
    assert "first paragraph" in result.data["element"].lower()
    assert "second paragraph" in result.data["element"].lower()
    assert "footer content" not in result.data["element"].lower()
