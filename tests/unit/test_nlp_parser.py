import pytest
from unittest.mock import patch, MagicMock
import json

class MockTokenizer:
    def __init__(self, *args, **kwargs):
        pass
        
    def __call__(self, text, **kwargs):
        # Returns a dict with a fake tensor
        return {"input_ids": [[1, 2, 3]]}
    
    def decode(self, token_ids, **kwargs):
        # Return a JSON-like string that our parser should be able to process
        if isinstance(token_ids, list):
            # For the read file command, return specific JSON
            return '{"tool_id": "file_reader", "params": {"path": "test.txt"}}'
        return '{"tool_id": "mock_tool", "params": {"key": "value"}}'

class MockModel:
    def __init__(self, *args, **kwargs):
        pass
        
    def generate(self, **kwargs):
        # Return a fake token array that will be decoded by the tokenizer
        return [[1, 2, 3]]

# Patch the Transformers imports
@pytest.fixture(autouse=True)
def mock_transformers():
    """Mock the Transformers library to avoid actual model loading."""
    with patch("src.universal_agent.utils.nlp_parser.T5Tokenizer") as mock_tokenizer, \
         patch("src.universal_agent.utils.nlp_parser.T5ForConditionalGeneration") as mock_model:
        
        # Configure the mocks to return our test classes
        mock_tokenizer.from_pretrained = MagicMock(return_value=MockTokenizer())
        mock_model.from_pretrained = MagicMock(return_value=MockModel())
        
        yield

# Now import NlpParser after we've patched the dependencies
from src.universal_agent.utils.nlp_parser import NlpParser

@pytest.mark.asyncio
async def test_nlp_parser_instantiation():
    """Test that NlpParser can be instantiated."""
    parser = NlpParser()
    assert parser.tokenizer is not None
    assert parser.model is not None

@pytest.mark.asyncio
async def test_nlp_parser_parse():
    """Test the parse method."""
    parser = NlpParser()
    command = "read file 'test.txt'"
    result = await parser.parse(command)
    
    # Test that we get the expected structure from our mock
    assert result is not None
    assert result["tool_id"] == "file_reader"
    assert "params" in result
    assert result["params"]["path"] == "test.txt"

@pytest.mark.asyncio
async def test_nlp_parser_fallback():
    """Test the fallback mechanisms."""
    parser = NlpParser()
    
    # Test the emergency fallback by forcing an exception in the try block
    with patch.object(parser.model, 'generate', side_effect=Exception("Test exception")):
        result = await parser.parse("run code hello.py")
        assert result is not None
        assert "tool_id" in result
        assert result["tool_id"] == "code_runner"  # Should be determined by heuristics
        assert "params" in result
        assert "original_command" in result["params"]
        assert result["params"]["original_command"] == "run code hello.py"

@pytest.mark.asyncio
async def test_nlp_parser_json_fallback():
    """Test fallback for JSON parsing errors."""
    parser = NlpParser()
    
    # Make the tokenizer return invalid JSON
    with patch.object(parser.tokenizer, 'decode', return_value="Not a valid JSON"):
        result = await parser.parse("search for documentation")
        assert result is not None
        assert "tool_id" in result
        assert result["tool_id"] == "search_tool"  # Should be determined by heuristics
        assert "params" in result
