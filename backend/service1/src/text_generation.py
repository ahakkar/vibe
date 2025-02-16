# With a python version 3.12 or lower, required libraries are transformers, torch, and sentencepiece.
from llama_cpp import Llama

MODEL_NAME = "Ahma-3B-Instruct.Q4_K_S"  # Replace with the specific model you want
LLM_MODEL_PATH = f"/models/{MODEL_NAME}.gguf"

class TextGenLlamaService:
    def __init__(
        self,
        max_new_tokens=30,
        no_repeat_ngram_size=2,
        tempreature=0.2,
        top_p=0.95,
        top_k=40,
        do_sample=True,
    ):
        """
        Initialize the TextGenerationService
        :param max_new_tokens: int, the maximum number of tokens that the language model can generate
        :param no_repeat_ngram_size: int, the number of ngram that prevent repetition
        :param temperature: float, controls the determinism of the language model, the lower the value the more determinisitc the output, and vice versa
        :param top_p: float, determines properbility threshold. The higher the value, the more diverse and creative response. the lower the value, the more predictable
        :param top_k: int, manages the selection range for the next word in a sequence.
        :param do_sample: bool, enable sampling to prevent deterministic
        """
        self.max_new_tokens = max_new_tokens
        self.no_repeat_ngram_size = no_repeat_ngram_size
        self.temperature = tempreature
        self.top_p = top_p
        self.top_k = top_k
        self.do_sample = do_sample
        self.llm_model = Llama(
            LLM_MODEL_PATH, chat_format="llama-2", verbose=False, n_ctx=2048
        )

    def text_generate(self, input):
        """
        Small language model will generate text based given user input
        :param input: String, given user input
        :return: String, llm responded output
        """

        llm_output = self.llm_model(
            input,
            max_tokens=self.max_new_tokens,
            temperature=self.temperature,
            top_p=self.top_p,
            top_k=self.top_k,
            repeat_penalty=1.1,
        )

        return llm_output["choices"][0]["text"]

    def chat_generate(self, input, message=""):
        """
        Small language model will generate text based given user input with instructed message.
        :param input: String, given user input
        :param message: String, message which instructs how language model should behave
        :return: Generator object, llm responded output
        Usage:
        textGenLlamaService = TextGenLlamaService()
            for token in textGenLlamaService.chat_generate("Moi, mitä kuulu"):
                text = token["choices"][0]["delta"].get("content", "")
                print(text, end="", flush=True)
        """

        if message == "":
            message = "Olet Kari. Olet käyttäjän ystävä. Sinä olet iloinen ja hauska ystävä. Puhu positiivisesti"
        messages = [
            {
                "role": "assistant",
                "content": "Olet Kari. Olet käyttäjän ystävä. Sinä olet iloinen ja hauska ystävä. Puhu positiivisesti",
            },
            {"role": "user", "content": input},
        ]

        llm_output = self.llm_model.create_chat_completion(
            messages=messages,
            max_tokens=self.max_new_tokens,
            temperature=self.temperature,
            top_p=self.top_p,
            top_k=self.top_k,
            stream=True,
            repeat_penalty=1.1,
        )

        return llm_output
