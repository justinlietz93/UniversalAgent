import pytest
from unittest.mock import patch, MagicMock
import asyncio

# Mock the Transformers classes to avoid dependencies
class MockTokenizer:
    def __init__(self, *args, **kwargs):
        pass
        
    def __call__(self, text, **kwargs):
        return {"input_ids": [[1, 2, 3]]}
    
    def decode(self, token_ids, **kwargs):
        # Return test-specific output based on the input
        if "echo" in str(kwargs):
            return '{"tool_id": "echo", "params": {"message": "Hello World"}}'
        else:
            return '{"tool_id": "file_read", "params": {"file_path": "/path/to/file"}}'

class MockModel:
    def __init__(self, *args, **kwargs):
        pass
        
    def generate(self, **kwargs):
        return [[1, 2, 3]]

# Patch transformers imports
@pytest.fixture(autouse=True)
def mock_transformers():
    with patch("src.universal_agent.utils.nlp_parser.T5Tokenizer") as mock_tokenizer, \
         patch("src.universal_agent.utils.nlp_parser.T5ForConditionalGeneration") as mock_model:
        
        mock_tokenizer.from_pretrained = MagicMock(return_value=MockTokenizer())
        mock_model.from_pretrained = MagicMock(return_value=MockModel())
        
        yield

# Now import NlpParser after patching the dependencies
from src.universal_agent.utils.nlp_parser import NlpParser

@pytest.mark.asyncio
async def test_nlp_parser():
    # Test cases for NLP parsing
    test_cases = [
        ("Run the echo tool with message 'Hello World'", {"tool_id": "echo", "params": {"message": "Hello World"}}),
        ("Execute the file_read tool with file_path '/path/to/file'", {"tool_id": "file_read", "params": {"file_path": "/path/to/file"}}),
    ]
    
    nlp_parser = NlpParser()
    
    for command, expected_output in test_cases:
        # Patch the tokenizer decode method to return appropriate test data
        with patch.object(nlp_parser.tokenizer, 'decode', return_value=f'{{"tool_id": "{expected_output["tool_id"]}", "params": {str(expected_output["params"]).replace("\'", "\"")}}}'): 
            result = await nlp_parser.parse(command)
            
            assert result["tool_id"] == expected_output["tool_id"]
            assert result["params"] == expected_output["params"]
