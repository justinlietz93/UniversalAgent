import unittest
from unittest.mock import patch
import logging

# Ensure the src directory is in the Python path
import os
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from src.universal_agent.utils.streaming import StreamBuffer
from src.config import REGEX_PATTERNS # Needed for StreamBuffer init

# Disable logging during tests to avoid clutter
logging.disable(logging.CRITICAL)

class TestStreamBufferXMLParsing(unittest.TestCase):
    """Tests specifically for the _parse_xml_tool_call method."""

    def setUp(self):
        """Set up a StreamBuffer instance."""
        # We need to initialize StreamBuffer to access the private method
        # The regex patterns are needed for init but not directly for this test focus
        self.buffer = StreamBuffer()

    def test_parse_simple_xml(self):
        """Test parsing a simple valid XML tool call."""
        xml_content = "<name>get_weather</name><arguments><location>London</location><unit>celsius</unit></arguments>"
        expected = {"tool": "get_weather", "arguments": {"location": "London", "unit": "celsius"}}
        result = self.buffer._parse_xml_tool_call(xml_content)
        self.assertEqual(result, expected)

    def test_parse_xml_with_types(self):
        """Test parsing XML with different data types."""
        xml_content = """
        <name>update_settings</name>
        <arguments>
            <enabled>true</enabled>
            <retries>3</retries>
            <threshold>0.75</threshold>
            <mode>auto</mode>
        </arguments>
        """
        expected = {
            "tool": "update_settings",
            "arguments": {
                "enabled": True,
                "retries": 3,
                "threshold": 0.75,
                "mode": "auto"
            }
        }
        result = self.buffer._parse_xml_tool_call(xml_content)
        self.assertEqual(result, expected)

    def test_parse_xml_with_negative_numbers(self):
        """Test parsing XML with negative integer and float."""
        xml_content = """
        <name>adjust_value</name>
        <arguments>
            <delta_int>-10</delta_int>
            <delta_float>-5.5</delta_float>
        </arguments>
        """
        expected = {
            "tool": "adjust_value",
            "arguments": {
                "delta_int": -10,
                "delta_float": -5.5
            }
        }
        result = self.buffer._parse_xml_tool_call(xml_content)
        self.assertEqual(result, expected)

    def test_parse_xml_empty_args(self):
        """Test parsing XML with empty arguments tag."""
        xml_content = "<name>ping</name><arguments></arguments>"
        expected = {"tool": "ping", "arguments": {}}
        result = self.buffer._parse_xml_tool_call(xml_content)
        self.assertEqual(result, expected)

    def test_parse_xml_no_args_tag(self):
        """Test parsing XML with no arguments tag."""
        xml_content = "<name>status_check</name>"
        # Should still parse the name, args will be empty
        expected = {"tool": "status_check", "arguments": {}}
        result = self.buffer._parse_xml_tool_call(xml_content)
        self.assertEqual(result, expected)

    def test_parse_xml_malformed(self):
        """Test parsing malformed XML."""
        xml_content = "<name>test</name><arguments><param1>value1</param2></arguments>" # Mismatched tag
        result = self.buffer._parse_xml_tool_call(xml_content)
        self.assertIsNone(result, "Malformed XML should return None")

    def test_parse_xml_missing_name(self):
        """Test parsing XML missing the name tag."""
        xml_content = "<arguments><param>value</param></arguments>"
        result = self.buffer._parse_xml_tool_call(xml_content)
        self.assertIsNone(result, "XML missing name should return None")

    def test_parse_xml_with_json_args(self):
        """Test parsing XML where arguments contain a JSON string."""
        json_args = '{"city": "Paris", "days": 5, "details": {"temp": true, "wind": false}}'
        xml_content = f"<name>get_forecast</name><arguments>{json_args}</arguments>"
        expected = {
            "tool": "get_forecast",
            "arguments": {"city": "Paris", "days": 5, "details": {"temp": True, "wind": False}} # Use Python booleans
        }
        result = self.buffer._parse_xml_tool_call(xml_content)
        self.assertEqual(result, expected)

    def test_parse_xml_with_invalid_json_args(self):
        """Test parsing XML with invalid JSON in arguments tag."""
        # JSON is invalid (missing closing brace)
        json_args = '{"city": "Paris", "days": 5'
        xml_content = f"<name>get_forecast</name><arguments>{json_args}</arguments>"
        # Should fall back to parsing arguments as XML tags (none exist here)
        expected = {"tool": "get_forecast", "arguments": {}}
        result = self.buffer._parse_xml_tool_call(xml_content)
        self.assertEqual(result, expected)

    @patch('importlib.import_module')
    def test_fallback_to_standard_xml_parser(self, mock_import):
        """Test fallback to standard XML parser when defusedxml is not available."""
        # Simulate ImportError for defusedxml
        def side_effect(module_name):
            if module_name == 'defusedxml':
                raise ImportError
            # Allow importing standard xml.etree.ElementTree
            elif module_name == 'xml.etree.ElementTree':
                import xml.etree.ElementTree as ET
                return ET
            raise ImportError # Should not happen for this test
        mock_import.side_effect = side_effect

        # Need to reload the module to trigger the import attempts again
        import importlib
        from src.universal_agent.utils import streaming
        importlib.reload(streaming)
        buffer = streaming.StreamBuffer() # Create new instance after reload

        xml_content = "<name>simple_tool</name><arguments><p1>val1</p1></arguments>"
        expected = {"tool": "simple_tool", "arguments": {"p1": "val1"}}
        result = buffer._parse_xml_tool_call(xml_content)
        self.assertEqual(result, expected)

# Re-enable logging
logging.disable(logging.NOTSET)

# Note: Tests for process_chunk and _extract_tool_call focusing on XML
# could be added here as well, but these focus on the core parsing logic.

if __name__ == '__main__':
    unittest.main()
