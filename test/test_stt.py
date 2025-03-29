import pytest
import os
import numpy as np  
from unittest.mock import patch, MagicMock

# Mock the imports of the modules that are not installed
with patch.dict(
    "sys.modules",
    {
        "torch": MagicMock(),
        "torchaudio": MagicMock(),
        "onnxruntime": MagicMock(),
        "transformers": MagicMock(),
    },
):
    from src.backend.local.stt import SpeechToTextService

class TestSTTService:

    def setup_method(self):
        """
        Setup method to run before each test
        """
        self.project_root = "/path/to/project/root"
        with patch.dict(
            os.environ,
            {
                "MODEL_FOLDER": "test_model_folder",
                "PROCESSOR": "test_processor",
                "ONNX_MODEL": "test_onnx_model",
            },
        ):
            self.stt_service = SpeechToTextService(self.project_root)

    def teardown_method(self):
        """
        Teardown method to run after each test
        """
        self.stt_service = None
        os.environ.pop("MODEL_FOLDER", None)
        os.environ.pop("PROCESSOR", None)
        os.environ.pop("ONNX_MODEL", None)
        self.project_root = None

    @pytest.mark.unit()
    def test_speech_to_text_service_init_try(self):
        """
        Test the try block of initialization of the STT class
        Assert that the processor and ort_session are not None
        """
        assert self.stt_service.processor is not None
        assert self.stt_service.ort_session is not None

    @pytest.mark.skip()
    def test_speech_to_text_service_init_except(self):
        """
        Test the except block of initialization of the STT class
        Assert that the processor and ort_session are not None
        """
        with patch.object(
            Wav2Vec2Processor, "from_pretrained", side_effect=Exception("Error")
            ), patch.object(ort, "InferenceSession", side_effect=Exception("Error")):
            assert self.stt_service.processor is not None
            assert self.stt_service.ort_session is not None


    @pytest.mark.skip()
    def test_transcribe(self):
        """
        Test the process_audio method of the SpeechToTextService class
        Mock the run (ONNX model inference return value)
        Mock batch_decode (transcription return value)
        Assert process_audio return value is the mocked transcription
        """
        audio_data = np.random.randn(16000).astype(np.float32)

        with patch.object(
            stt_service.ort_session, "run", return_value=[np.random.randn(1, 100, 32)]
        ) as mock_run, patch.object(
            stt_service.processor, "batch_decode", return_value=["test transcription"]
        ) as mock_decode:
            result = stt_service.process_audio(audio_data)
            mock_run.assert_called_once()
            mock_decode.assert_called_once()
            assert result == "test transcription"