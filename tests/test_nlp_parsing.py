import unittest
from src.universal_agent.utils.nlp_parser import parse_nl_command

class TestNLPParsing(unittest.TestCase):
    def test_parse_nl_command(self):
        # Test cases for NLP parsing
        test_cases = [
            ("Run the echo tool with message 'Hello World'", ("echo", {"message": "Hello World"})),
            ("Execute the file_read tool with file_path '/path/to/file'", ("file_read", {"file_path": "/path/to/file"})),
        ]
        
        for command, expected_output in test_cases:
            tool_name, params = parse_nl_command(command)
            self.assertEqual(tool_name, expected_output[0])
            self.assertEqual(params, expected_output[1])

if __name__ == '__main__':
    unittest.main()
