import pytest
import numpy as np
from unittest.mock import patch, MagicMock

# Mock the imports of the modules that are not installed
with patch.dict(
    "sys.modules",
    {
        "torch": MagicMock(),
        "torchaudio": MagicMock(),
        "pyaudio": MagicMock(),
        "onnxruntime": MagicMock(),
        "transformers": MagicMock(),
        "blessed": MagicMock(),
    },
):
    from backend.service1.src.stt import (
        AudioRecordingService,
        SpeechToTextService,
        ONNX_MODEL_PATH,
        PROCESSOR_PATH,
        OUTPUT_FILENAME,
        term,
    )


@pytest.fixture
def audio_service():
    """
    Fixture for the AudioRecordingService class
    """
    audio_service_instance = AudioRecordingService(device_index=7)
    yield audio_service_instance
    audio_service_instance.stop_recording()


@pytest.fixture
def stt_service():
    """
    Fixture for the SpeechToTextService class
    """
    return SpeechToTextService()


def test_constants():
    """
    Test the constants defined in the STT module
    """
    assert ONNX_MODEL_PATH == "/models/wav2vec2_model.onnx"
    assert PROCESSOR_PATH == "/models/wav2vec2_processor"
    assert OUTPUT_FILENAME == "recorded_audio.wav"
    assert term is not None


def test_audio_recording_service_init(audio_service):
    """
    Test the initialization of the AudioRecordingService class
    """
    assert audio_service.sample_rate == 16_000
    assert audio_service.channels == 1
    assert audio_service.CHUNK == 1024
    assert audio_service.audio is not None
    assert audio_service.stream is None
    assert audio_service.frames == []
    assert audio_service.recording is False
    assert audio_service.device_index == 7
    assert audio_service.recording_thread is None


def test_speech_to_text_service_init(stt_service):
    """
    Test the initialization of the SpeechToTextService class
    """
    assert stt_service.processor is not None
    assert stt_service.ort_session is not None


# Tests check the correct actions of the individual methods against mock objects.
@pytest.mark.skip()
def test_start_recording(audio_service):
    """
    Test the start_recording method of the AudioRecordingService class
    """
    with patch.object(
        audio_service.audio, "open", return_value=MagicMock()
    ) as mock_open:
        audio_service.start_recording()
        mock_open.assert_called_once()
        assert audio_service.recording is True
        assert audio_service.recording_thread.is_alive()


@pytest.mark.skip()
def test_stop_recording(audio_service):
    """
    Test the stop_recording method of the AudioRecordingService class
    """
    with patch.object(
        audio_service.audio, "open", return_value=MagicMock()
    ) as mock_open:
        audio_service.start_recording()
        audio_service.stop_recording()
        assert audio_service.recording is False
        assert not audio_service.recording_thread.is_alive()


@pytest.mark.skip()
def test_save_audio_to_file(audio_service):
    """
    Test the save_audio_to_file method of the AudioRecordingService class
    """
    audio_service.frames = [b"\x00\x01", b"\x02\x03"]
    with patch("wave.open", new_callable=MagicMock) as mock_wave_open:
        audio_service.save_audio_to_file("test.wav")
        mock_wave_open.assert_called_once_with("test.wav", "wb")


@pytest.mark.skip()
def test_process_audio(stt_service):
    """
    Test the process_audio method of the SpeechToTextService class
    """
    audio_data = np.random.randn(16000).astype(np.float32)
    with patch.object(
        stt_service.ort_session, "run", return_value=[np.random.randn(1, 100, 32)]
    ) as mock_run:
        with patch.object(
            stt_service.processor, "batch_decode", return_value=["test transcription"]
        ) as mock_decode:
            result = stt_service.process_audio(audio_data)
            mock_run.assert_called_once()
            mock_decode.assert_called_once()
            assert result == "test transcription"
