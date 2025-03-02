import pytest
import time
from unittest.mock import patch, MagicMock

# Mock the imports of the modules that are not installed
with patch.dict(
    "sys.modules",
    {
        "llama_cpp": MagicMock(),
    },
):
    from backend.service1.src.text_gen import TextGenService


@pytest.fixture
def text_gen_service():
    return TextGenService()


# Checks that LLM gives a response
def test_text_generate(text_gen_service):
    with patch.object(text_gen_service.llm_model, "__call__", return_value=MagicMock()):
        result = text_gen_service.text_generate(
            "Hello"
        )  # This is a placeholder, the actual input can be decided later
        assert result is not None


"""
This is Copilot genearated code. I have to modify it to make it work.
def test_init_default_values():
    service = TextGenService()
    assert service.max_new_tokens == 30
    assert service.no_repeat_ngram_size == 2
    assert service.temperature == 0.2
    assert service.top_p == 0.95
    assert service.top_k == 40
    assert service.do_sample is True
    assert isinstance(service.llm_model, Llama)

def test_init_custom_values():
    service = TextGenService(
        max_new_tokens=50,
        no_repeat_ngram_size=3,
        tempreature=0.5,
        top_p=0.9,
        top_k=50,
        do_sample=False,
    )
    assert service.max_new_tokens == 50
    assert service.no_repeat_ngram_size == 3
    assert service.temperature == 0.5
    assert service.top_p == 0.9
    assert service.top_k == 50
    assert service.do_sample is False
    assert isinstance(service.llm_model, Llama)
"""


# Checks that the response time is less than 5 seconds
def test_text_generate_response_time(text_gen_service):
    with patch.object(
        text_gen_service.llm_model,
        "__call__",
        return_value={"choices": [{"text": "response"}]},
    ):
        start_time = time.time()
        result = text_gen_service.text_generate(
            "Hello"
        )  # This is a placeholder, the actual input can be decided later
        end_time = time.time()
        assert result == "response"
        assert (end_time - start_time) < 5
