# Web Search and Scraping Tools

The Universal Agent provides two powerful tools for interacting with web content: the Web Search Tool and the Web Scraper Tool. These tools allow agents to search for information on the web and extract content from specific URLs.

## Web Search Tool

The Web Search Tool uses the Google Custom Search API to perform web searches and return relevant results.

### Configuration

To use the Web Search Tool, you need to set up Google Custom Search:

1. Create a Google Custom Search Engine (CSE) at [https://cse.google.com/cse/](https://cse.google.com/cse/)
2. Get your Search Engine ID (cx) from the CSE control panel
3. Create a Google API key at [https://console.developers.google.com/](https://console.developers.google.com/)
4. Configure the Universal Agent with your API key and Search Engine ID:

```json
{
  "credentials": {
    "google_api_key": "YOUR_API_KEY",
    "google_cx": "YOUR_SEARCH_ENGINE_ID"
  }
}
```

### Usage

You can use the Web Search Tool in two ways:

#### 1. Directly via the API

```python
from src.universal_agent.tools.web_search_tool import WebSearchTool

# Create the tool with credentials
search_tool = WebSearchTool(
    api_key="YOUR_API_KEY",
    search_engine_id="YOUR_SEARCH_ENGINE_ID"
)

# Execute a search
result = await search_tool.execute({
    "query": "latest AI developments",
    "num_results": 5
})

# Process results
if result.success:
    for item in result.data["results"]:
        print(f"Title: {item['title']}")
        print(f"Link: {item['link']}")
        print(f"Snippet: {item['snippet']}")
        print("---")
```

#### 2. Via natural language with the Universal Agent

```python
from src.universal_agent.core.agent import UniversalAgent
from src.universal_agent.router.router import Router
from src.universal_agent.tools.web_search_tool import WebSearchTool

# Create a router
router = Router()

# Create and register the search tool
search_tool = WebSearchTool(
    api_key="YOUR_API_KEY",
    search_engine_id="YOUR_SEARCH_ENGINE_ID"
)
router.register_tool(search_tool)

# Create the agent with the router
agent = UniversalAgent(router=router)

# Use natural language to execute searches
result = await agent.execute("Search for the latest AI developments")
print(result.message)
```

### Parameters

The Web Search Tool accepts the following parameters:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | Yes | - | The search query |
| `num_results` | integer | No | 3 | Number of results to return (max: 10) |

## Web Scraper Tool

The Web Scraper Tool allows extracting content from specific URLs, including text, headings, tables, and specific elements.

### Usage

#### 1. Directly via the API

```python
from src.universal_agent.tools.web_scraper_tool import WebScraperTool

# Create the tool
scraper_tool = WebScraperTool()

# Scrape text from a URL
result = await scraper_tool.execute({
    "url": "https://example.com",
    "extraction_type": "text"
})

# Process results
if result.success:
    print(result.data["content"])
```

#### 2. Via natural language with the Universal Agent

```python
from src.universal_agent.core.agent import UniversalAgent
from src.universal_agent.router.router import Router
from src.universal_agent.tools.web_scraper_tool import WebScraperTool

# Create a router
router = Router()

# Create and register the scraper tool
scraper_tool = WebScraperTool()
router.register_tool(scraper_tool)

# Create the agent with the router
agent = UniversalAgent(router=router)

# Use natural language to extract content
result = await agent.execute("Extract the main content from https://example.com")
print(result.message)
```

### Parameters

The Web Scraper Tool accepts the following parameters:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `url` | string | Yes | - | The URL to scrape |
| `extraction_type` | string | No | "text" | Type of content to extract: "text", "headings", "table", "element", or "full" |
| `element_selector` | string | No | - | CSS selector for specific element extraction (only used when extraction_type is "element") |
| `max_length` | integer | No | 10000 | Maximum length of text to extract |

### Extraction Types

The Web Scraper Tool supports several extraction types:

#### Text Extraction

Extracts the main text content from the page.

```python
result = await scraper_tool.execute({
    "url": "https://example.com",
    "extraction_type": "text"
})
```

#### Headings Extraction

Extracts all headings (h1-h6) from the page.

```python
result = await scraper_tool.execute({
    "url": "https://example.com",
    "extraction_type": "headings"
})
```

#### Table Extraction

Extracts all tables from the page.

```python
result = await scraper_tool.execute({
    "url": "https://example.com",
    "extraction_type": "table"
})
```

#### Element Extraction

Extracts specific elements based on a CSS selector.

```python
result = await scraper_tool.execute({
    "url": "https://example.com",
    "extraction_type": "element",
    "element_selector": "div.content p"
})
```

#### Full Page Extraction

Extracts title, headings, text, and links from the page.

```python
result = await scraper_tool.execute({
    "url": "https://example.com",
    "extraction_type": "full"
})
```

## Combining Web Search and Scraping

The Web Search and Scraper tools can be combined to create powerful workflows:

```python
# Search for information
search_result = await search_tool.execute({
    "query": "latest AI research papers",
    "num_results": 3
})

# Extract content from the first result
if search_result.success and search_result.data["results"]:
    first_result_url = search_result.data["results"][0]["link"]
    
    scrape_result = await scraper_tool.execute({
        "url": first_result_url,
        "extraction_type": "text"
    })
    
    if scrape_result.success:
        print(f"Content from {first_result_url}:")
        print(scrape_result.data["content"])
```

## Security and Ethical Considerations

When using the Web Search and Scraper tools, please consider the following:

1. **Rate Limiting**: The Google Custom Search API has usage limits. Be mindful of the number of requests you make.
2. **Website Terms of Service**: Always respect the terms of service of websites you scrape. Some websites prohibit scraping.
3. **Privacy**: Be careful when handling personal or sensitive information that might be returned in search results or scraped content.
4. **User-Agent**: The Web Scraper Tool uses a standard user-agent. Some websites may block or limit requests from automated tools.

## Troubleshooting

### Web Search Issues

- **API Key or Search Engine ID Not Found**: Ensure you've properly configured the credentials.
- **Quota Exceeded**: You may have exceeded your daily quota for the Google Custom Search API.
- **No Results**: The search query may be too specific or the search engine might not have indexed relevant content.

### Web Scraper Issues

- **Invalid URL**: Ensure the URL is properly formatted and includes the protocol (http:// or https://).
- **Connection Errors**: The website may be down, blocking requests, or have security measures that prevent scraping.
- **CSS Selector Not Found**: When using element extraction, make sure the CSS selector matches elements on the page.
- **Content Not Extracted**: The website may use JavaScript to render content dynamically, which won't be accessible to the basic scraper.
