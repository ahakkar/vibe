from abc import ABC, abstractmethod

import numpy as np


class TextToSpeechInterface(ABC):
    @abstractmethod
    def synthesize(self, text: str) -> None:
        """
        Convert text to speech and play it.

        Parameters:
        text (str): The input text to be converted to speech.
        """
        pass


class SpeechToTextInterface(ABC):
    @abstractmethod
    def transcribe(self, audio_data: np.ndarray) -> str:
        """
        Convert speech from an audio file to text.

        :param np.ndarray audio_data: The raw audio data to process.
        :return str: The transcribed text from the audio data.
        """
        pass


class TextGenerationInterface(ABC):
    @abstractmethod
    def generate(self, user_input: str, system_prompt="") -> str:
        """
        Generates a response in a chat-like format, ensuring correct system message handling.

        :param str user_input: The input text from the user.
        :param str system_prompt: The system prompt to guide the model's responses, defaults to "".
        :return generator: A generator that yields the model's response in a streaming fashion.
        """
        pass


class IntentRecognitionInterface(ABC):
    @abstractmethod
    def recognize_intent(self, text: str, lang: str) -> dict:
        """
        Parse natural language text into structured intent data.

        Parameters:
        text (str): Input text from the user.
        lang (str): Input text language.

        Returns:
        dict: Structured intent.
        """
        pass


# not used atm
class TranslatorInterface(ABC):
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
