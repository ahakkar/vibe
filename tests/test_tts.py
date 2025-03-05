import pytest
import numpy as np
import sounddevice as sd
from unittest.mock import patch, MagicMock

# Mock the imports of the modules that are not installed
with patch.dict(
    "sys.modules",
    {
        "sox": MagicMock(),
        "piper.voice": MagicMock(),
    },
):
    from backend.service1.src.tts import TextToSpeech, MODEL_PATH


@pytest.fixture
def tts():
    """
    Fixture for the TextToSpeech class.
    """
    tts_instance = TextToSpeech()
    yield tts_instance
    tts_instance.stop()


def test_constants():
    """
    Test the constant values.
    """
    assert MODEL_PATH == "/models/fi_FI-harri-medium.onnx"


def test_test_to_speech_init(tts):
    """
    Test the initialization of the TextToSpeech class.
    """
    assert tts.model_path == MODEL_PATH
    assert tts.voice is not None
    assert tts.device_index == 1
    assert tts.stream is None
    assert tts.piper_sample_rate == tts.voice.config.sample_rate
    assert tts.output_sample_rate == 44100
    assert tts.sentence_queue is not None
    assert tts._stop_event is not None
    assert tts._thread is not None


# Tests check the correct actions of the individual methods against mock objects.
# def test_initialize_stream_success(tts):
#     """
#     Test the initialize_stream method when the stream is successfully initialized.
#     """
#     with patch.object(sd, "OutputStream", return_value=MagicMock()) as mock_stream:
#         tts.initialize_stream()
#         mock_stream.assert_called_once_with(
#             device=1, samplerate=44100, channels=1, dtype="int16"
#         )
#         assert tts.stream is not None


# def test_initialize_stream_failure(tts):
#     """
#     Test the initialize_stream method when the stream initialization fails.
#     """
#     with patch.object(sd, "OutputStream", side_effect=sd.PortAudioError("Test Error")):
#         tts.initialize_stream()
#         assert tts.stream is None


# def test_synthesize_with_stream(tts):
#     """
#     Test the synthesize method when the stream is available.
#     """
#     tts.stream = MagicMock()
#     tts.voice.synthesize_stream_raw = MagicMock(return_value=[b"\x00\x01", b"\x02\x03"])
#     with patch.object(
#         np, "frombuffer", return_value=np.array([1, 2], dtype=np.int16)
#     ) as mock_frombuffer:
#         tts.synthesize("test text")
#         tts.stream.start.assert_called_once()
#         assert tts.stream.write.call_count == 2
#         tts.stream.stop.assert_called_once()


# def test_synthesize_without_stream(tts):
#     """
#     Test the synthesize method when the stream is not available.
#     """
#     with patch.object(tts, "initialize_stream") as mock_initialize_stream:
#         tts.stream = None
#         tts.synthesize("test text")
#         mock_initialize_stream.assert_called_once()
#         assert tts.stream is None


# def test_synthesize_stream_initialization_failure(tts):
#     """
#     Test the synthesize method when the stream initialization fails.
#     """
#     with patch.object(tts, "initialize_stream") as mock_initialize_stream:
#         tts.stream = None
#         mock_initialize_stream.side_effect = lambda: setattr(tts, "stream", None)
#         tts.synthesize("test text")
#         mock_initialize_stream.assert_called_once()
#         assert tts.stream is None
