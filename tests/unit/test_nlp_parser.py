import pytest
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
    # In a real test, you'd check the structure of result
    # For now, just verify it doesn't error
    assert result is not None
