import pytest
from unittest.mock import patch, MagicMock
from text_generation import TextGenLlamaService

@pytest.fixture
def text_gen_service():
    return TextGenLlamaService()

def test_text_generate(text_gen_service):
    with patch.object(text_gen_service.llm_model, '__call__', return_value={"choices": [{"text": "Generated text"}]}):
        result = text_gen_service.text_generate("Hello")
        assert result == "Generated text"

""" def test_chat_generate(text_gen_service):
    mock_response = MagicMock()
    mock_response.__iter__.return_value = iter([{"choices": [{"delta": {"content": "Generated text"}}]}])
    with patch.object(text_gen_service.llm_model, 'create_chat_completion', return_value=mock_response):
        result = list(text_gen_service.chat_generate("Hello"))
        assert result[0]["choices"][0]["delta"]["content"] == "Generated text" """