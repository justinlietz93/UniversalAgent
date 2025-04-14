"""
Web Scraper Tool for the Universal Agent.

This module provides a tool for scraping content from URLs.
"""
import logging
import json
import re
from typing import Dict, Any, List, Optional, Union, Tuple
from urllib.parse import urlparse, urljoin

import httpx
from bs4 import BeautifulSoup

from src.universal_agent.tools.base_tool import BaseTool
from src.universal_agent.interfaces.types import ToolParams, ToolResult

logger = logging.getLogger(__name__)

class WebScraperTool(BaseTool):
    """
    Tool for scraping content from web pages.
    
    This tool allows fetching content from specific URLs and extracting text, 
    headings, tables, or specific elements.
    """
    
    def __init__(self):
        """Initialize the web scraper tool."""
        super().__init__(
            id="web_scraper",
            name="Web Scraper",
            description="Scrape content from a specified URL. Can extract text, headings, tables, or specific elements from a web page."
        )
        
        # Initialize HTTP client
        self._client = httpx.AsyncClient(timeout=60.0)
    
    def get_parameter_schema(self) -> Dict[str, Any]:
        """
        Get the schema for the parameters expected by this tool.
        
        Returns:
            Dict[str, Any]: JSON Schema for parameters.
        """
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL to scrape content from."
                },
                "extraction_type": {
                    "type": "string",
                    "description": "The type of content to extract.",
                    "enum": ["text", "headings", "table", "element", "full"],
                    "default": "text"
                },
                "element_selector": {
                    "type": "string",
                    "description": "CSS selector for specific element extraction (only used when extraction_type is 'element')."
                },
                "max_length": {
                    "type": "integer",
                    "description": "Maximum length of text to extract (applies to 'text' and 'full' extraction types).",
                    "default": 10000
                }
            },
            "required": ["url"]
        }
    
    async def execute(self, params: ToolParams) -> ToolResult:
        """
        Scrape content from a URL with the given parameters.
        
        Args:
            params (ToolParams): Parameters for the scraping operation.
                - url (str): The URL to scrape.
                - extraction_type (str, optional): Type of content to extract ('text', 'headings', 'table', 'element', or 'full').
                - element_selector (str, optional): CSS selector for specific element extraction.
                - max_length (int, optional): Maximum length of text to extract.
        
        Returns:
            ToolResult: The scraped content.
        """
        try:
            # Validate parameters
            validation_error = self.validate_parameters(params)
            if validation_error:
                return self.create_error_result(validation_error)
            
            # Extract parameters
            url = params.get("url")
            extraction_type = params.get("extraction_type", "text")
            element_selector = params.get("element_selector", "")
            max_length = params.get("max_length", 10000)
            
            # Validate URL
            if not self._is_valid_url(url):
                return self.create_error_result(f"Invalid URL: {url}")
            
            # Fetch page content
            page_content = await self._fetch_page(url)
            
            # Extract content based on extraction type
            extracted_content = self._extract_content(page_content, extraction_type, element_selector, max_length)
            
            # Return results
            result = {
                "url": url,
                "extraction_type": extraction_type
            }
            
            if extraction_type == "table":
                result["tables"] = extracted_content
            elif extraction_type == "headings":
                result["headings"] = extracted_content
            elif extraction_type == "element":
                result["element"] = extracted_content
            else:
                result["content"] = extracted_content
            
            return self.create_success_result(result)
        
        except Exception as e:
            logger.error(f"Error in web scraping: {str(e)}")
            return self.create_error_result(f"Web scraping failed: {str(e)}")
    
    def _is_valid_url(self, url: str) -> bool:
        """
        Check if a URL is valid.
        
        Args:
            url (str): The URL to check.
        
        Returns:
            bool: True if the URL is valid, False otherwise.
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    async def _fetch_page(self, url: str) -> str:
        """
        Fetch the content of a web page.
        
        Args:
            url (str): The URL to fetch.
        
        Returns:
            str: The page content.
        """
        # Setup custom headers to mimic a browser
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
        
        # Fetch the page
        response = await self._client.get(url, headers=headers, follow_redirects=True)
        response.raise_for_status()
        
        # Return the page content
        return response.text
    
    def _extract_content(
        self, 
        html_content: str, 
        extraction_type: str, 
        element_selector: str = "", 
        max_length: int = 10000
    ) -> Union[str, List[Dict[str, Any]]]:
        """
        Extract content from HTML based on extraction type.
        
        Args:
            html_content (str): The HTML content to extract from.
            extraction_type (str): Type of content to extract.
            element_selector (str, optional): CSS selector for specific element extraction.
            max_length (int, optional): Maximum length of text to extract.
        
        Returns:
            Union[str, List[Dict[str, Any]]]: The extracted content.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
        
        if extraction_type == "text":
            # Extract main text content
            text = soup.get_text(separator="\n", strip=True)
            
            # Clean up text (remove extra whitespace)
            lines = [line.strip() for line in text.split("\n") if line.strip()]
            text = "\n".join(lines)
            
            # Truncate if necessary
            if len(text) > max_length:
                text = text[:max_length] + "..."
            
            return text
        
        elif extraction_type == "headings":
            # Extract all headings (h1-h6)
            headings = []
            for tag in soup.find_all(re.compile(r"h[1-6]")):
                level = int(tag.name[1])
                headings.append({
                    "level": level,
                    "text": tag.get_text(strip=True)
                })
            
            return headings
        
        elif extraction_type == "table":
            # Extract tables
            tables = []
            for table in soup.find_all("table"):
                extracted_table = {
                    "header": [],
                    "rows": []
                }
                
                # Extract header row
                thead = table.find("thead")
                if thead:
                    header_cells = thead.find_all("th")
                    if not header_cells:
                        header_cells = thead.find_all("td")
                    
                    extracted_table["header"] = [cell.get_text(strip=True) for cell in header_cells]
                
                # If no thead, try to get header from first row
                if not extracted_table["header"]:
                    first_row = table.find("tr")
                    if first_row:
                        header_cells = first_row.find_all("th")
                        if not header_cells:
                            header_cells = first_row.find_all("td")
                        
                        extracted_table["header"] = [cell.get_text(strip=True) for cell in header_cells]
                
                # Extract table rows
                tbody = table.find("tbody") or table
                rows = tbody.find_all("tr")
                
                # Skip the first row if it was used as header
                start_idx = 1 if not thead and extracted_table["header"] else 0
                
                for row in rows[start_idx:]:
                    cells = row.find_all(["td", "th"])
                    extracted_table["rows"].append([cell.get_text(strip=True) for cell in cells])
                
                tables.append(extracted_table)
            
            return tables
        
        elif extraction_type == "element":
            # Extract specific element using CSS selector
            if not element_selector:
                return "No element selector provided."
            
            elements = soup.select(element_selector)
            
            if not elements:
                return "No elements found matching the selector."
            
            # Return text content of all matching elements
            extracted = []
            for element in elements:
                extracted.append(element.get_text(separator="\n", strip=True))
            
            return "\n\n".join(extracted)
        
        elif extraction_type == "full":
            # Extract full page content (cleaned)
            content = {
                "title": soup.title.string if soup.title else "",
                "headings": [],
                "text": "",
                "links": []
            }
            
            # Extract headings
            for tag in soup.find_all(re.compile(r"h[1-6]")):
                level = int(tag.name[1])
                content["headings"].append({
                    "level": level,
                    "text": tag.get_text(strip=True)
                })
            
            # Extract main text
            text = soup.get_text(separator="\n", strip=True)
            lines = [line.strip() for line in text.split("\n") if line.strip()]
            text = "\n".join(lines)
            
            # Truncate if necessary
            if len(text) > max_length:
                text = text[:max_length] + "..."
            
            content["text"] = text
            
            # Extract links
            for link in soup.find_all("a"):
                href = link.get("href")
                link_text = link.get_text(strip=True)
                
                if href and link_text:
                    content["links"].append({
                        "text": link_text,
                        "href": href
                    })
            
            return content
        
        # Default case
        return "Unsupported extraction type."
