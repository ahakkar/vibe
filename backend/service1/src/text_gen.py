from llama_cpp import Llama

MODEL_NAME = "Gemma2:2b_unsloth.Q4_K_M"  # Replace with your actual GGUF model filename
LLM_MODEL_PATH = f"/models/{MODEL_NAME}.gguf"

class TextGenService:
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
        Initializes the text generation service for a fine-tuned Gemma 2:2B GGUF model.
        """
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k
        self.repeat_penalty = repeat_penalty
        self.do_sample = do_sample

        # Load GGUF model using llama.cpp
        self.llm_model = Llama(
            model_path=LLM_MODEL_PATH, chat_format="gemma", verbose=False, n_ctx=2048
        )

    def chat_generate(self, user_input, system_prompt=""):
        """
        Generates a response in a chat-like format, ensuring correct system message handling.
        """
        if not system_prompt:
            system_prompt = (
                "Olet tekoälyavustaja. Vastaat aina mahdollisimman avuliaasti ja ystävällisesti. Pidä vastauksesi lyhyinä ja ytimekkäinä."
            )

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
