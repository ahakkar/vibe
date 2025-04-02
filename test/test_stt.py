import pytest
import os
import numpy as np
import onnxruntime as ort

from pathlib import Path
from unittest.mock import patch, MagicMock
from transformers import Wav2Vec2Processor


# Mock the imports of the modules that are not installed
""" with patch.dict(
    "sys.modules",
    {
        "torch": MagicMock(),
        "torchaudio": MagicMock(),
    },
): """
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
    def test_speech_to_text_service_init_except_processor(self):
        """
        Test the processor except block of initialization of the STT class
        """
        with patch.object(
            Wav2Vec2Processor, "from_pretrained", side_effect=Exception("Error")
        ), patch.object(ort, "InferenceSession", return_value=MagicMock()), patch(
            "builtins.print"
        ) as mock_print:

            self.stt_service = SpeechToTextService(self.project_root)
            mock_print.assert_called_with(
                "Failed to wav2vec processor: root/path/models/test_processor\nError"
            )

    @pytest.mark.unit()
    def test_speech_to_text_service_init_except_onnx(self):
        """
        Test the onnx except block of initialization of the STT class
        """
        with patch.object(
            Wav2Vec2Processor, "from_pretrained", return_value=MagicMock()
        ), patch.object(ort, "InferenceSession", side_effect=Exception("Error")), patch(
            "builtins.print"
        ) as mock_print:

            self.stt_service = SpeechToTextService(self.project_root)
            mock_print.assert_called_with(
                "Failed to wav2vec onnx file: root/path/models/test_onnx_model\nError"
            )


    @pytest.mark.int()
    @pytest.mark.parametrize(
        "test_input, expected_output",
[
    (
        np.ndarray([0.0, 0.0, 0.0, -0.00125122, -0.00076294, -0.0005188]),
        "Moi minä olen Harri"
    ),
]
    )
    def test_tts(self, test_input, expected_output):
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

        audio_data = test_input
        result = self.stt_service.transcribe(audio_data)
            
        assert result == expected_output


