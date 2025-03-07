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
    audio_service_instance.terminate_audio()


@pytest.fixture
def stt_service():
    """
    Fixture for the SpeechToTextService class
    """
    return SpeechToTextService()


@pytest.mark.unit()
def test_constants():
    """
    Test the constants defined in the STT module
    """
    assert ONNX_MODEL_PATH == "/models/wav2vec2_model.onnx"
    assert PROCESSOR_PATH == "/models/wav2vec2_processor"
    assert OUTPUT_FILENAME == "recorded_audio.wav"
    assert term is not None


@pytest.mark.unit()
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

@pytest.mark.unit()
def test_speech_to_text_service_init(stt_service):
    """
    Test the initialization of the SpeechToTextService class
    """
    assert stt_service.processor is not None
    assert stt_service.ort_session is not None


@pytest.mark.unit()
def test_start_recording(audio_service):
    """
    Test the start_recording method of the AudioRecordingService class
    """
    mock_audio_stream = MagicMock()
    mock_audio_stream.read.return_value = b'\x00\x01'  # Mock bytes-like object

    with patch.object(
        audio_service.audio, "open", return_value=mock_audio_stream
    ) as mock_open:
        audio_service.start_recording()
        mock_open.assert_called_once()
        assert audio_service.recording is True
        assert audio_service.recording_thread.is_alive()


@pytest.mark.unit()
def test_stop_recording(audio_service):
    """
    Test the stop_recording method of the AudioRecordingService class
    """
    mock_audio_stream = MagicMock()
    mock_audio_stream.read.return_value = b'\x00\x01'  # Mock bytes-like object

    with patch.object(
        audio_service.audio, "open", return_value=mock_audio_stream
    ) as mock_open:
        audio_service.start_recording()
        audio_service.stop_recording()
        assert audio_service.recording is False
        assert not audio_service.recording_thread.is_alive()


@pytest.mark.skip()
def test_save_audio_to_file_local(audio_service):
    """
    Test the save_audio_to_file method of the AudioRecordingService class
    """
    pass
    



@pytest.mark.skip()
def test_save_audio_to_file_docker(audio_service):
    """
    Test the save_audio_to_file method of the AudioRecordingService class when running in Docker
    """
    pass
  

@pytest.mark.unit()
def test_terminate_audio(audio_service):
    """
    Test the terminate_audio method of the AudioRecordingService class
    """
    with patch.object(audio_service, 'stop_recording') as mock_stop_recording, \
         patch.object(audio_service, 'audio') as mock_audio, \
         patch.object(audio_service, 'recording_thread') as mock_recording_thread:
        
        # Mock the recording state and thread state
        audio_service.recording = True
        mock_recording_thread.is_alive.return_value = True

        audio_service.terminate_audio()

        # Assert that stop_recording is called if recording is True
        mock_stop_recording.assert_called_once()

        # Assert that join is called if the recording thread is alive
        mock_recording_thread.join.assert_called_once()

        # Assert that audio.terminate is called
        mock_audio.terminate.assert_called_once()


@pytest.mark.unit()
def test_terminate_audio_not_recording(audio_service):
    """
    Test the terminate_audio method when not recording
    """
    with patch.object(audio_service, 'stop_recording') as mock_stop_recording, \
         patch.object(audio_service, 'audio') as mock_audio, \
         patch.object(audio_service, 'recording_thread') as mock_recording_thread:
        
        # Mock the recording state and thread state
        audio_service.recording = False
        mock_recording_thread.is_alive.return_value = False

        audio_service.terminate_audio()

        # Assert that stop_recording is not called if recording is False
        mock_stop_recording.assert_not_called()

        # Assert that join is not called if the recording thread is not alive
        mock_recording_thread.join.assert_not_called()

        # Assert that audio.terminate is called
        mock_audio.terminate.assert_called_once()


@pytest.mark.unit()
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
