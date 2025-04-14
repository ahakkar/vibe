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
    @patch.object(Wav2Vec2Processor, "from_pretrained", return_value=MagicMock())
    @patch.object(ort, "InferenceSession", return_value=MagicMock())
    def test_speech_to_text_service_init_try(
        self,
        mock_from_pretrained,
        mock_inference_session,
    ):
        """
        Test the try block of initialization of the STT class
        Assert that the processor and ort_session are not None
        """

        self.stt_service = SpeechToTextService(self.project_root)

        assert self.stt_service.processor is not None
        assert self.stt_service.ort_session is not None

    @pytest.mark.unit()
    @patch("logging.Logger.error")
    @patch.object(ort, "InferenceSession", return_value=MagicMock())
    @patch.object(Wav2Vec2Processor, "from_pretrained", side_effect=Exception("Error"))
    def test_speech_to_text_service_init_except_processor(
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
            "Failed to open wav2vec processor: root/path/models/test_processor\nError"
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
            "Failed to open wav2vec onnx file: root/path/models/test_onnx_model\nError"
        )

    @pytest.mark.skip()
    @pytest.mark.unit()
    @patch("torch.tensor", return_value=MagicMock())
    @patch.object(Wav2Vec2Processor, "from_pretrained", return_value=MagicMock())
    @patch.object(ort, "InferenceSession", return_value=MagicMock())
    def test_speech_to_text_service_transcribe(
        self,
        mock_inference_session,
        mock_processor,
        mock_torch_tensor,
    ):
        """
        Test the transcribe method of the SpeechToTextService class with torch mocked.
        """

        self.stt_service = SpeechToTextService(self.project_root)

        mock_processor_instance = mock_processor.return_value
        mock_processor_instance.return_tensors = "np"
        mock_processor_instance.batch_decode.return_value = ["test"]

        mock_onnx_session = mock_inference_session.return_value
        mock_onnx_session.get_inputs.return_value = [
            MagicMock(name="input_values"),
            MagicMock(name="attention_mask"),
        ]
        mock_onnx_session.run.return_value = [np.array([[0.1, 0.9]])]

        result = self.stt_service.transcribe(np.array([1.0, 2.0, 3.0]))

        mock_processor.assert_called_once()
        mock_onnx_session.run.assert_called_once()
        mock_processor_instance.batch_decode.assert_called_once()

        assert result == "test"
