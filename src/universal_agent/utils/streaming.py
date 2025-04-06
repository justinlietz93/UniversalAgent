"""
Streaming support module for the Universal LLM Tool Wrapper Interface.

This module provides classes for handling streaming responses from LLMs,
including token accumulation and tool call detection.
"""
import logging
import json
import re
from typing import Dict, Any, List, Optional, Tuple, AsyncGenerator

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
# Use absolute import from src
from src.config import REGEX_PATTERNS

logger = logging.getLogger(__name__)

class StreamBuffer:
    """
    Buffer for accumulating and processing streaming response chunks.
    
    This class handles the accumulation of response chunks and detection
    of tool calls in the accumulated content.
    """
    
    def __init__(self):
        """Initialize the stream buffer."""
        self.buffer = ""
        self.tool_call_detected = False
        self.complete_tool_call = None
        # Get regex patterns from config
        self.tool_call_start_pattern = re.compile(REGEX_PATTERNS["tool_call"]["start"])
        self.tool_call_end_pattern = re.compile(REGEX_PATTERNS["tool_call"]["end"])
        # JSON extraction patterns
        self.json_extraction_patterns = {
            pattern_name: re.compile(pattern) 
            for pattern_name, pattern in REGEX_PATTERNS["json_extraction"].items()
        }
    
    def process_chunk(self, chunk: str) -> Tuple[str, Optional[Dict[str, Any]]]:
        """
        Process a response chunk.
        
        Args:
            chunk: The response chunk to process
            
        Returns:
            A tuple containing the displayable text and the tool call if detected
        """
        # Add the chunk to the buffer
        self.buffer += chunk
        
        # Check if we've already detected a complete tool call
        if self.complete_tool_call:
            return chunk, None
        
        # Check if we need to start looking for a tool call
        if not self.tool_call_detected:
            if self.tool_call_start_pattern.search(self.buffer):
                self.tool_call_detected = True
                logger.debug("Tool call start detected in stream")
        
        # If we're looking for a tool call, check if it's complete
        if self.tool_call_detected:
            tool_call = self._extract_tool_call()
            if tool_call:
                self.complete_tool_call = tool_call
                logger.info("Complete tool call detected in stream")
                return chunk, tool_call
        
        return chunk, None
    
    def _extract_tool_call(self) -> Optional[Dict[str, Any]]:
        """
        Extract a complete tool call from the buffer.
        
        Returns:
            The extracted tool call or None if not complete
        """
        # Try each extraction pattern in order
        
        # Try to extract JSON block (```json ... ```)
        json_block_match = self.json_extraction_patterns["json_block"].search(self.buffer, re.DOTALL)
        if json_block_match:
            try:
                json_str = json_block_match.group(1)
                tool_call = json.loads(json_str)
                return self._normalize_tool_call(tool_call)
            except json.JSONDecodeError:
                logger.debug("Failed to parse JSON block")
        
        # Try to extract OpenAI-style tool call
        openai_match = self.json_extraction_patterns["openai_function"].search(self.buffer, re.DOTALL)
        if openai_match:
            try:
                # Wrap in proper JSON structure for parsing
                json_str = '{' + openai_match.group(0) + '}'
                tool_call = json.loads(json_str)
                return self._normalize_tool_call(tool_call)
            except json.JSONDecodeError:
                logger.debug("Failed to parse OpenAI function call")
        
        # Try to extract Gemini-style tool call
        gemini_match = self.json_extraction_patterns["gemini_tool_calls"].search(self.buffer, re.DOTALL)
        if gemini_match:
            try:
                # Wrap in proper JSON structure for parsing
                json_str = '{"tool_calls": [' + gemini_match.group(1) + ']}'
                tool_call = json.loads(json_str)
                return self._normalize_tool_call(tool_call)
            except json.JSONDecodeError:
                logger.debug("Failed to parse Gemini tool calls")
        
        # Try to extract XML-style tool call
        xml_match = self.json_extraction_patterns["xml_tool"].search(self.buffer, re.DOTALL)
        if xml_match:
            try:
                tool_content = xml_match.group(1)
                # Try to parse as JSON if it looks like JSON
                if tool_content.strip().startswith('{'):
                    tool_call = json.loads(tool_content)
                    return self._normalize_tool_call(tool_call)
                else:
                    # Parse XML content using the XML parser
                    tool_call = self._parse_xml_tool_call(tool_content)
                    if tool_call:
                        return tool_call
            except json.JSONDecodeError:
                logger.debug("Failed to parse XML tool content as JSON")
        
        # No complete tool call found
        return None
    
    def _parse_xml_tool_call(self, xml_content: str) -> Optional[Dict[str, Any]]:
        """
        Parse an XML-style tool call using a proper XML parser.
        
        Args:
            xml_content: The XML content to parse
            
        Returns:
            The parsed tool call or None if parsing fails
        """
        ET = None
        try:
            from defusedxml import ElementTree as DefusedET
            ET = DefusedET
            logger.debug("Using defusedxml for secure XML parsing.")
        except ImportError:
            logger.warning("defusedxml not found. Falling back to standard xml.etree.ElementTree. Consider installing defusedxml for enhanced security.")
            try:
                import xml.etree.ElementTree as StandardET
                ET = StandardET
            except ImportError:
                logger.error("XML parsing failed: Neither defusedxml nor xml.etree.ElementTree found.")
                return None

        if ET is None: # Should not happen if the second try block succeeded, but defensive check
             logger.error("XML parsing failed: No valid ElementTree implementation found.")
             return None

        try:
            # Wrap the XML content in a root element to ensure it's well-formed
            wrapped_xml = f"<root>{xml_content}</root>"
            # Parse XML content using the selected ElementTree implementation
            # Use defusedxml's recommended parsing method if available
            if hasattr(ET, 'fromstring'):
                 root = ET.fromstring(wrapped_xml)
            else: # Fallback for standard ElementTree if fromstring isn't the primary method (though it usually is)
                 # This part might need adjustment based on the exact standard ET API if needed
                 logger.warning("Using alternative parsing method for standard ElementTree.")
                 parser = ET.XMLParser()
                 parser.feed(wrapped_xml)
                 root = parser.close()

            # Extract tool name
            name_elem = root.find(".//name")
            if name_elem is None or not name_elem.text:
                logger.warning("XML tool call missing required 'name' element")
                return None
                
            tool_name = name_elem.text.strip()
            
            # Extract arguments
            args_elem = root.find(".//arguments")
            arguments = {}
            
            if args_elem is not None:
                # First try to see if arguments contain JSON
                if args_elem.text and args_elem.text.strip().startswith('{'):
                    try:
                        arguments = json.loads(args_elem.text)
                        logger.debug("Successfully parsed JSON arguments from XML")
                    except json.JSONDecodeError:
                        logger.debug("Failed to parse arguments as JSON, continuing with XML parsing")
                
                # If not JSON or JSON parsing failed, parse as XML
                if not arguments:
                    # Process nested elements within arguments
                    for child in args_elem:
                        # Get element text, defaulting to empty string
                        value = child.text or ""
                        value_str = child.text.strip() if child.text else ""
                        processed_value = value_str # Default to string

                        # Attempt type conversions with error handling
                        try:
                            if value_str.lower() in ('true', 'false'):
                                processed_value = value_str.lower() == 'true'
                            elif value_str.isdigit() or (value_str.startswith('-') and value_str[1:].isdigit()):
                                processed_value = int(value_str)
                            # More robust float check
                            elif re.match(r'^-?\d+(\.\d+)?([eE][-+]?\d+)?$', value_str):
                                processed_value = float(value_str)
                        except ValueError:
                            logger.debug(f"Could not convert value '{value_str}' for tag '{child.tag}', keeping as string.")
                            processed_value = value_str # Revert to string on error

                        # Handle explicit type attributes (optional, enhance later if needed)
                        # elif child.get('type') == 'array':
                            # Array type (process nested items) - Placeholder for future enhancement
                            # processed_value = [] # Placeholder
                        # elif child.get('type') == 'object':
                            # Object type (process nested properties) - Placeholder for future enhancement
                            # processed_value = {} # Placeholder

                        # Add to arguments dictionary
                        arguments[child.tag] = processed_value

            return {
                "tool": tool_name,
                "arguments": arguments
            }

        except ET.ParseError as pe:
            logger.error(f"XML ParseError: {pe}")
            logger.debug(f"Invalid XML content: {xml_content}")
            return None
        except Exception as e:
            logger.exception(f"Unexpected error parsing XML tool call: {str(e)}") # Use exception for full trace
            logger.debug(f"XML content: {xml_content}")
            return None
    
    def _normalize_tool_call(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize a tool call to a standard format.
        
        Args:
            tool_call: The tool call to normalize
            
        Returns:
            The normalized tool call
        """
        # Different providers use different formats
        # Normalize to a standard format: {"tool": "name", "arguments": {...}}
        
        normalized = {}
        
        # Handle OpenAI format
        if "function_call" in tool_call:
            func_call = tool_call["function_call"]
            normalized["tool"] = func_call.get("name", "")
            try:
                arguments = json.loads(func_call.get("arguments", "{}"))
                normalized["arguments"] = arguments
            except json.JSONDecodeError:
                normalized["arguments"] = {}
        
        # Handle Gemini format
        elif "tool_calls" in tool_call and len(tool_call["tool_calls"]) > 0:
            tool_info = tool_call["tool_calls"][0]
            if "function" in tool_info:
                normalized["tool"] = tool_info["function"].get("name", "")
                try:
                    arguments = json.loads(tool_info["function"].get("arguments", "{}"))
                    normalized["arguments"] = arguments
                except json.JSONDecodeError:
                    normalized["arguments"] = {}
        
        # Handle Anthropic format
        elif "tool_use" in tool_call:
            tool_use = tool_call["tool_use"]
            normalized["tool"] = tool_use.get("name", "")
            normalized["arguments"] = tool_use.get("parameters", {})
        
        # Handle direct format
        elif "tool" in tool_call and "arguments" in tool_call:
            normalized = tool_call
        
        # Handle name and args format
        elif "name" in tool_call and "args" in tool_call:
            normalized["tool"] = tool_call["name"]
            normalized["arguments"] = tool_call["args"]
        
        return normalized
    
    def reset(self) -> None:
        """Reset the buffer and tool call detection state."""
        self.buffer = ""
        self.tool_call_detected = False
        self.complete_tool_call = None


class StreamProcessor:
    """
    Processor for handling streaming responses.
    
    This class processes streaming responses from LLMs and detects tool calls.
    """
    
    def __init__(self):
        """Initialize the stream processor."""
        self.buffer = StreamBuffer()
    
    async def process_stream(
        self, 
        stream: AsyncGenerator[str, None],
        tool_callback: Optional[callable] = None
    ) -> AsyncGenerator[str, None]:
        """
        Process a streaming response.
        
        Args:
            stream: The streaming response
            tool_callback: Optional callback for when a tool call is detected
            
        Returns:
            An async generator yielding processed chunks
        """
        # Reset the buffer
        self.buffer.reset()
        
        # Process each chunk in the stream
        async for chunk in stream:
            displayable_text, tool_call = self.buffer.process_chunk(chunk)
            
            # If a tool call was detected, call the callback
            if tool_call and tool_callback:
                await tool_callback(tool_call)
            
            # Yield the displayable text
            yield displayable_text
    
    def extract_tool_call(self) -> Optional[Dict[str, Any]]:
        """
        Extract a tool call from the buffer.
        
        Returns:
            The extracted tool call or None if not found
        """
        return self.buffer.complete_tool_call


class StreamingManager:
    """
    Manager for streaming responses.
    
    This class provides a unified interface for processing streaming responses.
    """
    
    def __init__(self):
        """Initialize the streaming manager."""
        self.processor = StreamProcessor()
    
    async def process_streaming_response(
        self, 
        stream: AsyncGenerator[str, None],
        on_tool_call: Optional[callable] = None
    ) -> AsyncGenerator[str, None]:
        """
        Process a streaming response.
        
        Args:
            stream: The streaming response
            on_tool_call: Optional callback for when a tool call is detected
            
        Returns:
            An async generator yielding processed chunks
        """
        async for chunk in self.processor.process_stream(stream, on_tool_call):
            yield chunk
    
    def get_detected_tool_call(self) -> Optional[Dict[str, Any]]:
        """
        Get the detected tool call.
        
        Returns:
            The detected tool call or None if not found
        """
        return self.processor.extract_tool_call()
