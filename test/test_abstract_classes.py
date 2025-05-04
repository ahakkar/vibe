from src.backend.abstract_classes import (
    TextToSpeechInterface,
    SpeechToTextInterface,
    TextGenerationInterface,
    IntentRecognitionInterface,
)
from dataclasses import dataclass
from abc import ABCMeta


class TestAbstractClasses:
    def test_text_to_speech_interface(self):
        TextToSpeechInterface.__abstractmethods__ = set()

        @dataclass
        class MockTextToSpeech(TextToSpeechInterface):
            pass

        mockTextToSpeech = MockTextToSpeech()
        mock_text = "Moi"
        result = mockTextToSpeech.synthesize(mock_text)
        assert isinstance(TextToSpeechInterface, ABCMeta)
        assert result is None

    def test_speech_to_text_interface(self):
        SpeechToTextInterface.__abstractmethods__ = set()

        @dataclass
        class MockSpeechToText(SpeechToTextInterface):
            pass

        mockSpeechToText = MockSpeechToText()
        mock_audio_data = None
        result = mockSpeechToText.transcribe(mock_audio_data)
        assert isinstance(SpeechToTextInterface, ABCMeta)
        assert result is None

    def test_text_generation_interface(self):
        TextGenerationInterface.__abstractmethods__ = set()

        @dataclass
        class MockTextGeneration(TextGenerationInterface):
            pass

        mockTextGeneration = MockTextGeneration()
        mock_user_input = None
        mock_system_prompt = None
        result = mockTextGeneration.generate(mock_user_input, mock_system_prompt)
        assert isinstance(TextGenerationInterface, ABCMeta)
        assert result is None

    def test_intent_recognition_interface(self):
        IntentRecognitionInterface.__abstractmethods__ = set()

        @dataclass
        class MockIntentRecognition(IntentRecognitionInterface):
            pass

        mockIntentRecognition = MockIntentRecognition()
        mock_text = None
        mock_lang = None
        result = mockIntentRecognition.recognize_intent(mock_text, mock_lang)
        assert isinstance(IntentRecognitionInterface, ABCMeta)
        assert result is None
