# With a python version 3.12 or lower, required libraries are transformers, torch, and sentencepiece.
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_NAME = "TurkuNLP/gpt3-finnish-small"  # Replace with the specific model you want


class TextGenerationService:
    def __init__(
        self,
        max_new_tokens=100,
        no_repeat_ngram_size=2,
        tempreature=0.7,
        top_p=0.9,
        top_k=50,
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

        # Load the LLM model and tokenizer
        self.llm_tokenizer = AutoTokenizer.from_pretrained(
            MODEL_NAME, padding_side="left"
        )
        self.llm_model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)

    def text_generate(self, input):
        """
        Small language model will generate text based given user input
        :param input: String, given user input
        :return: String, llm responded output
        """

        # Process the translated text with the LLM
        llm_tokenized_inputs = self.llm_tokenizer(
            input, return_tensors="pt", padding=True, truncation=True
        )

        # Generate the output with adjusted parameters to prevent repetition
        outputs = self.llm_model.generate(
            **llm_tokenized_inputs,
            max_new_tokens=self.max_new_tokens,
            no_repeat_ngram_size=self.no_repeat_ngram_size,
            temperature=self.temperature,
            top_p=self.top_p,
            top_k=self.top_k,
            do_sample=self.do_sample,
        )

        # Decode the LLM output
        llm_output = self.llm_tokenizer.decode(outputs[0], skip_special_tokens=True)

        return llm_output
