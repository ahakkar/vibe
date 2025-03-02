import pytest
import numpy as np
import sounddevice as sd
from unittest.mock import patch, MagicMock
from TTS import TextToSpeech


@pytest.fixture
def tts():
    return TextToSpeech()


# Tests check the correct actions of the individual methods against mock objects.


def test_initialize_stream_success(tts):
    with patch.object(sd, "OutputStream", return_value=MagicMock()) as mock_stream:
        tts.initialize_stream()
        mock_stream.assert_called_once_with(
            samplerate=tts.voice.config.sample_rate, channels=1, dtype="int16"
        )
        assert tts.stream is not None


def test_initialize_stream_failure(tts):
    with patch.object(sd, "OutputStream", side_effect=sd.PortAudioError("Test Error")):
        tts.initialize_stream()
        assert tts.stream is None


def test_synthesize_with_stream(tts):
    tts.stream = MagicMock()
    tts.voice.synthesize_stream_raw = MagicMock(return_value=[b"\x00\x01", b"\x02\x03"])
    with patch.object(
        np, "frombuffer", return_value=np.array([1, 2], dtype=np.int16)
    ) as mock_frombuffer:
        tts.synthesize("test text")
        tts.stream.start.assert_called_once()
        assert tts.stream.write.call_count == 2
        tts.stream.stop.assert_called_once()


def test_synthesize_without_stream(tts):
    with patch.object(tts, "initialize_stream") as mock_initialize_stream:
        tts.stream = None
        tts.synthesize("test text")
        mock_initialize_stream.assert_called_once()
        assert tts.stream is None


def test_synthesize_stream_initialization_failure(tts):
    with patch.object(tts, "initialize_stream") as mock_initialize_stream:
        tts.stream = None
        mock_initialize_stream.side_effect = lambda: setattr(tts, "stream", None)
        tts.synthesize("test text")
        mock_initialize_stream.assert_called_once()
        assert tts.stream is None
