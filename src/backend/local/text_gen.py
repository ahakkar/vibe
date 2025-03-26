import sys
import os
from llama_cpp import Llama

# Suppress llama.cpp warnings from console output
# e.g. llama_new_context_with_model: n_ctx_per_seq (2048) < n_ctx_train (8192) -- the full capacity of the model will not be utilized
sys.stderr = open(os.devnull, "w")


class TextGenService:
    """
    Text generation service for a fine-tuned Gemma 2:2B GGUF model.
    """

    def __init__(
        self,
        max_new_tokens=100,
        temperature=0.6,
        top_p=0.95,
        top_k=40,
        repeat_penalty=1.2,
        do_sample=True,
    ):
        """
        Initializes the text generation service with the specified parameters.

        :param int max_new_tokens: The maximum number of new tokens to generate, defaults to 100
        :param float temperature: The sampling temperature, higher values mean more random completions, defaults to 0.6
        :param float top_p: The cumulative probability for nucleus sampling, defaults to 0.95
        :param int top_k: The number of highest probability vocabulary tokens to keep for top-k filtering, defaults to 40
        :param float repeat_penalty: The penalty for repeated tokens, defaults to 1.2
        :param bool do_sample: Whether to use sampling; if False, greedy decoding is used, defaults to True
        """
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k
        self.repeat_penalty = repeat_penalty
        self.do_sample = do_sample

        # Load GGUF model using llama.cpp
        self.llm_model = Llama(
            model_path=os.getenv("LLM_MODEL_PATH"),
            chat_format="gemma",
            verbose=True,
            n_ctx=2048,
            n_threads=6,
        )

    def chat_generate(self, user_input, system_prompt=""):
        """
        Generates a response in a chat-like format, ensuring correct system message handling.

        :param str user_input: The input text from the user.
        :param str system_prompt: The system prompt to guide the model's responses, defaults to "".
        :return generator: A generator that yields the model's response in a streaming fashion.
        """

        if not system_prompt:
            system_prompt = "Olet tekoälyavustaja. Vastaat aina mahdollisimman avuliaasti ja ystävällisesti. Pidä vastauksesi lyhyinä ja ytimekkäinä."

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input},
        ]

        try:
            generator = self.llm_model.create_chat_completion(
                messages=messages,
                max_tokens=self.max_new_tokens,
                temperature=self.temperature,
                top_p=self.top_p,
                top_k=self.top_k,
                stream=True,
                repeat_penalty=self.repeat_penalty,
            )
            return generator

        except Exception as e:
            return f"Error in chat generation: {e}"
