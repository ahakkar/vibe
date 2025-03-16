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
    from backend.service1.src.text_gen import TextGenService, MODEL_NAME, LLM_MODEL_PATH


@pytest.fixture
def text_gen_service():
    """
    Fixture for the TextGenService class.
    """
    return TextGenService()


@pytest.mark.unit()
def test_constants():
    """
    Test the constants MODEL_NAME and LLM_MODEL_PATH.
    """
    assert MODEL_NAME == "Gemma2:2b_unsloth.Q4_K_M"
    assert LLM_MODEL_PATH == f"/models/{MODEL_NAME}.gguf"


@pytest.mark.unit()
def test_init_default_values():
    """
    Test the default values of the TextGenService class.
    """
    text_gen_service = TextGenService()
    assert text_gen_service.max_new_tokens == 100
    assert text_gen_service.temperature == 0.6
    assert text_gen_service.top_p == 0.95
    assert text_gen_service.top_k == 40
    assert text_gen_service.repeat_penalty == 1.2
    assert text_gen_service.do_sample is True
    assert isinstance(text_gen_service.llm_model, MagicMock)


# Checks that LLM gives a response
@pytest.mark.unit()
def test_text_generate(text_gen_service):
    """
    Test the chat_generate method of the TextGenService class.
    """
    with patch.object(text_gen_service.llm_model, "__call__", return_value=MagicMock()):
        result = text_gen_service.chat_generate(
            "Hello"
        )  # This is a placeholder, the actual input can be decided later
        assert result is not None


# # Checks that the response time is less than 5 seconds
@pytest.mark.perf()
@pytest.mark.parametrize(
    "question",
    [
        "Mikä on Suomen Pääkaupunki?",
        "Onko Turussa hyvä asua?",
        "Missä Joulupukki asuu?",
    ],
)
def test_text_generate_response_time(text_gen_service, question):
    """
    Test the chat_generate method of the TextGenService class.
    """
    with patch.object(
        text_gen_service.llm_model,
        "__call__",
        return_value={"choices": [{"text": "response"}]},
    ):
        start_time = time.time()
        text_gen_service.chat_generate(question)
        first_token_time = time.time()
        assert (first_token_time - start_time) < 5
