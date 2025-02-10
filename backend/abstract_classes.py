from abc import ABC, abstractmethod


class TextToSpeech(ABC):
    @abstractmethod
    def synthesize(self, text: str) -> None:
        """
        Convert text to speech and play it.

        Parameters:
        text (str): The input text to be converted to speech.
        """
        pass


class SpeechToText(ABC):
    @abstractmethod
    def transcribe(self, audio_file: str) -> str:
        """
        Convert speech from an audio file to text.

        Parameters:
        audio_file (str): The path to the audio file to be transcribed.

        Returns:
        str: The transcribed text.
        """
        pass


class TextGeneration(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str:
        """
        Generate text based on the given prompt.

        Parameters:
        prompt (str): The input text prompt for the language model.

        Returns:
        str: The generated text output.
        """
        pass


class Translator(ABC):
    @abstractmethod
    def translate(self, text: str, source_language: str, target_language: str) -> str:
        """
        Translate text from the source language to the target language.

        Parameters:
        text (str): The input text to be translated.
        source_language (str): The language of the input text.
        target_language (str): The language of the output text.

        Returns:
        str: The translated text.
        """
        pass
