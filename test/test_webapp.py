import pytest
import wave
import io
from pathlib import Path
from unittest.mock import MagicMock, patch
from io import BytesIO
from fastapi.testclient import TestClient

with patch.dict("sys.modules", {"uvicorn": MagicMock(), "soundfile": MagicMock()}):
    from src.backend.api.webapp import WebApp, TextInput
import numpy as np


class MockApp:
    def __init__(self):
        self.logger = MockLogger()

    def intent_recognition_web(self, text):
        return f"Intent for: {text}"

    def text_gen_web(self, text):
        return f"Generated text for: {text}"

    def text_to_speech_web(self, text):
        return BytesIO(b"mock_audio_data")

    def speech_to_text(self, audio_data):
        return "Transcribed text"

    def process_recording_web(self, text):
        return BytesIO(b"mock_audio_data")


class MockLogger:
    def error(self, message):
        print(message)


@pytest.fixture
def mock_app():
    return MockApp()


@pytest.fixture
def client(mock_app):
    web_app = WebApp(mock_app)
    return TestClient(web_app.appAPI)


class TestWebapp:
    def setup_method(self):
        """Setup method to run before each test."""
        pass

    @pytest.mark.unit()
    def test_intent_recognition_api(self, client):
        test_data = {"input_text": "Kerro päivän uutiset"}
        response = client.post("/api/intent", json=test_data)
        assert response.status_code == 200
        assert response.json() == {"response": "Intent for: Kerro päivän uutiset"}

    @pytest.mark.unit()
    def test_text_gen_api(self, client):
        test_data = {"input_text": "Moi, mitä kuuluu?"}
        response = client.post("/api/text", json=test_data)
        assert response.status_code == 200
        assert response.json() == {"response": "Generated text for: Moi, mitä kuuluu?"}

    @pytest.mark.unit()
    def test_text_to_speech_api(self, client):
        test_data = {"input_text": "Moi, mitä kuuluu?"}
        response = client.post("/api/tts", json=test_data)
        assert response.status_code == 200
        assert response.content == b"mock_audio_data"
        assert response.headers["content-type"] == "audio/wav"

    @pytest.mark.unit()
    def test_speech_to_text_api(self, client):
        sample_rate = 16000
        duration = 0.1
        samples = (
            np.sin(2 * np.pi * np.arange(sample_rate * duration) * 440 / sample_rate)
            * 0.5
        )
        samples = (samples * 32767).astype(np.int16)

        with io.BytesIO() as wav_file:
            with wave.open(wav_file, "wb") as wf:
                wf.setnchannels(1)  # Mono
                wf.setsampwidth(2)  # 2 bytes (16-bit)
                wf.setframerate(sample_rate)
                wf.writeframes(samples.tobytes())
            wav_file.seek(0)

            files = {"audio": ("test_audio.wav", wav_file, "audio/wav")}
            response = client.post("/api/stt", files=files)

        assert response.status_code == 200
        assert response.json() == {"response": "Transcribed text"}

    @pytest.mark.unit()
    def test_all_services_api(self, client):
        sample_rate = 16000
        duration = 0.1
        samples = (
            np.sin(2 * np.pi * np.arange(sample_rate * duration) * 440 / sample_rate)
            * 0.5
        )
        samples = (samples * 32767).astype(np.int16)

        with io.BytesIO() as wav_file:
            with wave.open(wav_file, "wb") as wf:
                wf.setnchannels(1)  # Mono
                wf.setsampwidth(2)  # 2 bytes (16-bit)
                wf.setframerate(sample_rate)
                wf.writeframes(samples.tobytes())
            wav_file.seek(0)

            files = {"audio": ("test_audio.wav", wav_file, "audio/wav")}
            response = client.post("/api/all", files=files)

        assert response.status_code == 200
        assert response.content == b"mock_audio_data"
        assert response.headers["content-type"] == "audio/wav"

    @pytest.mark.unit()
    def test_error_handling(self, client, mock_app):
        def raise_error(text):
            return ValueError("Test error")

        mock_app.intent_recognition_web = raise_error

        test_data = {"input_text": "error test"}
        response = client.post("/api/intent", json=test_data)

        assert response.status_code == 500
        assert "Intent recognition error" in response.json()

    # def _create_wav_file(self):

    #         return files
