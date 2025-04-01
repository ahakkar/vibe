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
    from stt import SpeechToTextService


@patch.dict(
    os.environ,
    {
        "MODEL_FOLDER": "models",
        "PROCESSOR": "test_processor",
        "ONNX_MODEL": "test_onnx_model",
    },
)
class TestSTTService:

    def setup_method(self):
        """
        Setup method to run before each test
        """
        self.project_root = "root/path"

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
        with patch.object(
            Wav2Vec2Processor, "from_pretrained", return_value=MagicMock()
        ), patch.object(ort, "InferenceSession", return_value=MagicMock()):
            self.stt_service = SpeechToTextService(self.project_root)

        assert self.stt_service.processor is not None
        assert self.stt_service.ort_session is not None

    @pytest.mark.unit()
    @patch("logging.Logger.error")
    @patch.object(ort, "InferenceSession", side_effect=Exception("Error"))
    @patch.object(Wav2Vec2Processor, "from_pretrained", return_value=MagicMock())
    def test_speech_to_text_service_init_except_onnx(
        self,
        mock_from_pretrained,
        mock_inference_session,
        mock_logger,
    ):
        """
        Test the processor except block of initialization of the STT class
        """

        self.stt_service = SpeechToTextService(self.project_root)
        mock_logger.assert_called_with(
            "[stt.py:__init__] Failed to open wav2vec processor: root/path/models/test_processor\nError"
        )

    @pytest.mark.unit()
    @patch("logging.Logger.error")
    @patch.object(ort, "InferenceSession", side_effect=Exception("Error"))
    @patch.object(Wav2Vec2Processor, "from_pretrained", return_value=MagicMock())
    def test_speech_to_text_service_init_except_onnx(
        self,
        mock_from_pretrained,
        mock_inference_session,
        mock_logger,
    ):
        """
        Test the onnx except block of initialization of the STT class
        """

        self.stt_service = SpeechToTextService(self.project_root)
        mock_logger.assert_called_with(
            "[stt.py:__init__] Failed to open wav2vec onnx file: root/path/models/test_onnx_model\nError"
        )

    @pytest.mark.skip()
    def test_transcribe(self):
        """
        Test the process_audio method of the SpeechToTextService class
        Mock the run (ONNX model inference return value)
        Mock batch_decode (transcription return value)
        Assert transcribe return value is the mocked transcription
        """
        self.project_root = Path(__file__).parent.parent
        with patch.dict(
            os.environ,
            {
                "MODEL_FOLDER": "models",
                "PROCESSOR": "wav2vec2_processor",
                "ONNX_MODEL": "wav2vec2_model.onnx",
            },
        ):

            self.stt_service = SpeechToTextService(self.project_root)

        audio_data = np.random.randn(16000).astype(np.float32)

        with patch.object(
            self.stt_service.ort_session,
            "run",
            return_value=[np.random.randn(1, 100, 32)],
        ) as mock_run, patch.object(
            self.stt_service.processor,
            "batch_decode",
            return_value=["test transcription"],
        ) as mock_decode:
            result = self.stt_service.transcribe(audio_data)
            mock_run.assert_called_once()
            mock_decode.assert_called_once()
            assert result == "test transcription"
