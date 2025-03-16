import queue
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


@pytest.mark.unit()
def test_constants():
    """
    Test the constant values.
    """
    assert MODEL_PATH == "/models/fi_FI-harri-medium.onnx"


@pytest.mark.unit()
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
    assert isinstance(tts.sentence_queue, queue.Queue)
    assert tts._stop_event.is_set() is False
    assert tts._thread.is_alive()


# Tests check the correct actions of the individual methods against mock objects.
@pytest.mark.unit()
def test_initialize_stream_success(tts):
    """
    Test the initialize_stream method when the stream is successfully initialized.
    """
    with patch("sounddevice.OutputStream") as mock_output_stream:
        mock_stream_instance = MagicMock()
        mock_output_stream.return_value = mock_stream_instance

        tts.initialize_stream()

        mock_output_stream.assert_called_once_with(
            device=tts.device_index,
            samplerate=tts.output_sample_rate,
            channels=1,
            dtype="int16",
        )
        mock_stream_instance.start.assert_called_once()
        assert tts.stream == mock_stream_instance


@pytest.mark.unit()
def test_initialize_stream_failure(tts):
    """
    Test the initialize_stream method when the stream initialization fails.
    """
    with patch.object(sd, "OutputStream", side_effect=sd.PortAudioError("Test Error")):
        tts.initialize_stream()
        assert tts.stream is None


@pytest.mark.skip()
def test_resample_audio(tts):
    """
    Test the resample_audio method of the TextToSpeech service
    """
    pass


@pytest.mark.unit()
def test_synthesize(tts):
    """
    Test the synthesize method of the TextToSpeech service
    """
    test_text = "Moi, minä olen Harri, miten menee?"
    with patch.object(tts.sentence_queue, "put") as mock_put:
        tts.synthesize(test_text)
        mock_put.assert_called_once_with(test_text)


@pytest.mark.skip()
def test_process_queue(tts):
    """
    Test the _process_queue method of the TextToSpeech service
    """
    test_text = "Moi, minä olen Harri, miten menee?"
    tts.sentence_queue.put(test_text)

    with patch.object(tts, "_synthesize_text") as mock_synthesize_text:
        tts._process_queue()
        mock_synthesize_text.assert_called_once_with(test_text)


@pytest.mark.skip()
def test_synthesize_text(tts):
    """
    Test the _synthesize_text method of the TextToSpeech service
    """
    pass


@pytest.mark.skip()
def test_stop(tts):
    """
    Test the stop method of the TextToSpeech service
    """
    pass
