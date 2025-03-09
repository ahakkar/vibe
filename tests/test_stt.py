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
) as sttModules:
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
    return AudioRecordingService(device_index=7)

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

def test_start_recording_when_already_recording(audio_service):
    """
    Test the start_recording method of the AudioRecordingService class when the service is already recording
    """
    audio_service.recording = True
    audio_service.start_recording()
    term.center.assert_called_with("Already recording!")

def test_start_recording_success(audio_service, mocker):
    """
    Test the start_recording method of the AudioRecordingService class
    """
    mock_open = mocker.patch.object(audio_service.audio, "open", return_value=MagicMock())
    audio_service.start_recording()
    mock_open.assert_called_once()
    assert audio_service.recording is True
    term.center.assert_called_with("Recording...")
    assert audio_service.recording_thread.is_alive()

    # Stop recording
    audio_service.recording = False
    audio_service.recording_thread.join() 
    audio_service.stream.stop_stream()
    audio_service.stream.close()

def test_start_recording_device_error(audio_service, mocker):
    """
    Test the start_recording method of the AudioRecordingService class when device error occurs
    """
    mock_open = mocker.patch.object(audio_service.audio, "open", side_effect=Exception("Device Error"))
    audio_service.start_recording()
    mock_open.assert_called_once()
    assert audio_service.recording is False

    term.bold.assert_called_once_with("Please check the audio device index.")

    term.center.assert_any_call("Failed to open audio stream: Device Error")
    term.center.assert_any_call(term.bold("Please check the audio device index."))

def test_stop_recording(audio_service, mocker):
    """
    Test the stop_recording method of the AudioRecordingService class
    """
    mocker.patch.object(audio_service.audio, "open", return_value=MagicMock())
    audio_service.start_recording()

    # Stop recording
    audio_service.recording = False
    audio_service.recording_thread.join() 
    audio_service.stream.stop_stream()
    audio_service.stream.close()

    assert audio_service.recording is False
    assert not audio_service.recording_thread.is_alive()

def test_save_audio_to_file_path(audio_service, mocker):
    """
    Test the save_audio_to_file method of the AudioRecordingService class
    """
    mock_getenv = mocker.patch("os.getenv")
    mock_join = mocker.patch("os.path.join")
    mock_dirname = mocker.patch("os.path.dirname")

    mock_wave_file = MagicMock()
    mock_wave_file._file = MagicMock()

    for docker_env, expected_path in [
        (True, "/usr/src/app/recorded_audio.wav"),
        (False, "/backend/service1/src/recorded_audio.wav")
    ]:
        mock_getenv.return_value = docker_env
        mock_join.return_value = expected_path
        mock_dirname.return_value = "/mock/dir"

        audio_service.save_audio_to_file()

        if docker_env:
            mock_join.assert_called_with("/usr/src/app", "recorded_audio.wav")
        else:
            mock_join.assert_called_with("/mock/dir", "recorded_audio.wav")

@pytest.mark.skip()
def test_save_audio_to_file_failed(audio_service):
    """
    Test save_audio_to_file method of the SpeechToTextService class when the audio service fails to start recording.
    """
    audio_service.save_audio_to_file()
    term.center.assert_called_with("Failed to save audio file:")

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