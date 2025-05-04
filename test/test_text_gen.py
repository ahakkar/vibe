import pytest
import os
import time

from pathlib import Path
from unittest.mock import patch, MagicMock
from abstract_classes import TextGenerationInterface

# Mock the imports of the modules that are not installed
with patch.dict(
    "sys.modules",
    {
        "llama_cpp": MagicMock(),
    },
):
    from text_gen import TextGenService


class TestTextGenService:

    def setup_method(self):
        """
        Setup method to run before each test
        """
        self.root = Path(__file__).parent.parent
        with patch.dict(
            os.environ,
            {
                "MODEL_FOLDER": "models",
                "LLM_MODEL": "google_gemma-3-1b-it-Q4_0.gguf",
            },
        ):
            self.text_gen_service = TextGenService(self.root)

    def teardown_method(self):
        """
        Teardown method to run after each test
        """
        self.text_gen_service = None
        self.root = None

    @pytest.mark.unit()
    def test_init_default_values(self):
        """
        Test the default values of the TextGenService class.
        """
        assert isinstance(self.text_gen_service, TextGenerationInterface)
        assert self.text_gen_service.max_new_tokens == 100
        assert self.text_gen_service.temperature == 0.6
        assert self.text_gen_service.top_p == 0.95
        assert self.text_gen_service.top_k == 40
        assert self.text_gen_service.repeat_penalty == 1.2
        assert self.text_gen_service.do_sample is True

    # Checks that LLM gives a response
    @pytest.mark.unit()
    def test_text_generate(self):
        """
        Test the chat_generate method of the TextGenService class.
        """
        with patch.object(
            self.text_gen_service.llm_model, "__call__", return_value=MagicMock()
        ):
            result = self.text_gen_service.generate(
                "Hello"
            )  # This is a placeholder, the actual input can be decided later
            assert result is not None

    # Checks that the response time is less than 5 seconds
    # Applicable when the llama.cpp is not mocked
    @pytest.mark.skip()
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
            first_token_time = (
                time.time()
            )  # Need to fix to record actually the first token
            assert (first_token_time - start_time) < 5
