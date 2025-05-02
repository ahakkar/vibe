import os
from transformers import BartForConditionalGeneration, BartTokenizer


class ContextManager:

    def __init__(self, project_root):
        """
        Initialize the context management service.

        :param Path project_root: The path of the project root
        """
        try:
            sum_filepath = (
                str(project_root)
                + "/"
                + os.getenv("MODEL_FOLDER")
                + "/"
                + os.getenv("SUMMARIZER")
            )
            self.messages = []

            self.model = BartForConditionalGeneration.from_pretrained(
                sum_filepath, local_files_only=True
            )
            self.tokenizer = BartTokenizer.from_pretrained(
                sum_filepath, local_files_only=True
            )
        except Exception as e:
            print(f"Error loading model: {e}")
            raise

    def summarizer(self):
        """
        Summarizes the conversation history using the BART model.
        The conversation history is combined into a single string, and the BART model is used to generate a summary.
        The summary is returned as a string.

        :return str: The summarized conversation history.
        """
        messages_combined = " ".join(
            [
                (
                    f"Käyttäjä: {convo['content']}"
                    if convo["role"] == "user"
                    else f"Avustaja: {convo['content']}"
                )
                for convo in self.messages
            ]
        )

        inputs = self.tokenizer(
            messages_combined,
            return_tensors="pt",
            max_length=1024,
            truncation=True,
            padding="longest",
        ).to(self.model.device)

        summary_ids = self.model.generate(
            inputs["input_ids"],
            max_length=100,
            min_length=30,
            length_penalty=2.0,
            num_beams=4,
            early_stopping=True,
        )
        return self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
