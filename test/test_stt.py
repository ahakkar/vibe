import pytest
import os
import numpy as np
import onnxruntime as ort
from pathlib import Path  
from unittest.mock import patch, MagicMock
from transformers import Wav2Vec2Processor


# Mock the imports of the modules that are not installed
with patch.dict(
    "sys.modules",
    {
        "torch": MagicMock(),
        "torchaudio": MagicMock(),
    },
):
    from src.backend.local.stt import SpeechToTextService

class TestSTTService:

    def setup_method(self):
        """
        Setup method to run before each test
        """
        self.project_root = Path(__file__).resolve()
        print(self.project_root)
        print(os.getenv("MODEL_FOLDER"))
        print(os.getenv("PROCESSOR"))
        print(os.getenv("ONNX_MODEL"))
        self.stt_service = SpeechToTextService(self.project_root)

    def teardown_method(self):
        """
        Teardown method to run after each test
        """
        self.stt_service = None
        self.project_root = None

    @pytest.mark.unit()
    def test_speech_to_text_service_init_try(self):
        """
        Test the try block of initialization of the STT class
        Assert that the processor and ort_session are not None
        """      
        assert self.stt_service.processor is not None
        assert self.stt_service.ort_session is not None
        print(self.stt_service.processor.config.name_or_path)
        print(self.stt_service.ort_session.get_model_path())

    @pytest.mark.unit()
    def test_speech_to_text_service_init_except(self):
        """
        Test the except block of initialization of the STT class
        Assert that the processor and ort_session are not None
        """
        with patch.object(
            Wav2Vec2Processor, "from_pretrained", side_effect=Exception("Error")
            ), patch.object(ort, "InferenceSession", side_effect=Exception("Error")
            ), patch("builtins.print") as mock_print:
            mock_print.assert_any_call(
                "Failed to wav2vec processor: test_model_folder/test_processor\nError")
            mock_print.assert_any_call(
                "Failed to wav2vec onnx file: test_model_folder/test_onnx_model\nError")


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
            self.stt_service.ort_session, "run", return_value=[np.random.randn(1, 100, 32)]
        ) as mock_run, patch.object(
            self.stt_service.processor, "batch_decode", return_value=["test transcription"]
        ) as mock_decode:
            result = self.stt_service.process_audio(audio_data)
            mock_run.assert_called_once()
            mock_decode.assert_called_once()
            assert result == "test transcription"