import pytest
import os
import wave
import numpy as np
from unittest.mock import patch, MagicMock



# Mock the imports of the modules that are not installed
with patch.dict(
    "sys.modules",
    {
        "torch": MagicMock(),
        "torchaudio": MagicMock(),
        "onnxruntime": MagicMock(),
        "pyaudio": MagicMock(),
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
    Assert the values of the constants
    """
    assert ONNX_MODEL_PATH == "/models/wav2vec2_model.onnx"
    assert PROCESSOR_PATH == "/models/wav2vec2_processor"
    assert OUTPUT_FILENAME == "recorded_audio.wav"
    assert term is not None


@pytest.mark.unit()
def test_audio_recording_service_init(audio_service):
    """
    Test the initialization of the AudioRecordingService class
    Assert initial values of the class attributes
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
    Assert that the processor and ort_session are not None
    """
    assert stt_service.processor is not None
    assert stt_service.ort_session is not None


@pytest.mark.unit()
def test_start_recording_when_already_recording(audio_service):
    audio_service.recording = True
    audio_service.start_recording()
    term.center.assert_called_with("Already recording!")


@pytest.mark.unit()
def test_start_recording(audio_service):
    """
    Test the start_recording method of the AudioRecordingService class
    Mock the audio stream with a bytes-like object
    Assert that audio.open is called once
    Assert that the recording state is True
    Assert that the recording thread is alive
    """
    mock_audio_stream = MagicMock()
    mock_audio_stream.read.return_value = b'\x00\x01'

    with patch.object(
        audio_service.audio, "open", return_value=mock_audio_stream
    ) as mock_open:
        audio_service.start_recording()
        mock_open.assert_called_once()
        assert audio_service.recording is True
        assert audio_service.recording_thread.is_alive()


@pytest.mark.unit()
def test_start_recording_device_error(audio_service):
    with patch.object(audio_service.audio, "open", side_effect=Exception("Device Error")) as mock_open:
        audio_service.start_recording()
        mock_open.assert_called_once()
        assert audio_service.recording is False

        term.bold.assert_called_once_with("Please check the audio device index.")

        term.center.assert_any_call("Failed to open audio stream: Device Error")
        term.center.assert_any_call(term.bold("Please check the audio device index."))


@pytest.mark.unit()
def test_stop_recording(audio_service):
    """
    Test the stop_recording method of the AudioRecordingService class
    Mock the audio stream with a bytes-like object
    Assert that the recording state is False
    Assert that the recording thread is not alive
    Assert that the returned data is the same as the mocked audio stream return value
    """
    mock_audio_stream = MagicMock()
    mock_audio_stream.read.return_value = b'\x00\x01'

    with patch.object(
        audio_service.audio, "open", return_value=mock_audio_stream):
        audio_service.start_recording()
        data = audio_service.stop_recording()
        assert audio_service.recording is False
        assert not audio_service.recording_thread.is_alive()
        print(data)



@pytest.mark.unit()
def test_save_audio_try(audio_service, tmpdir):
    """
    Test that the function successfully runs through the try block.
    Set tmp directory
    Mock the frames attribute
    Mock the os.path.join function to return the save_path
    Mock the wave.open function to raise an exception
    Assert that save message is printed to terminal
    Assert that .wav file is saved
    Assert that the contents of the saved file are correct
    """
    save_path = os.path.join(tmpdir, OUTPUT_FILENAME)
    mock_frames = [b'\x00\x01', b'\x02\x03', b'\x04\x05']
    audio_service.frames = mock_frames

    with patch("os.path.join", return_value=save_path):

        audio_service.save_audio_to_file()
    
    audio_service.frames = [] # Reset the frames
    assert term.center.called_with(f"Audio saved to {save_path}")
    assert os.path.exists(save_path)

    with wave.open(save_path, 'rb') as wf:
        assert wf.getnchannels() == audio_service.channels
        assert wf.getsampwidth() == 2
        assert wf.getframerate() == audio_service.sample_rate
        assert wf.readframes(wf.getnframes()) == b''.join(mock_frames)


@pytest.mark.unit()
def test_save_audio_exeption(audio_service, tmpdir):
    """
    Test that the function raises an exception.
    Set tmp directory
    Mock the frames attribute
    Mock the os.path.join function to return the save_path
    Mock the wave.open function to raise an exception
    Assert that no .wav file is saved
    Assert that the exception is raised and message is printed
    """
    save_path = os.path.join(tmpdir, OUTPUT_FILENAME)
    mock_frames = [b'\x00\x01', b'\x02\x03', b'\x04\x05']
    audio_service.frames = mock_frames

    with patch("os.path.join", return_value=save_path), \
         patch("wave.open", side_effect=Exception("Test exception")):
            audio_service.save_audio_to_file()
    
    audio_service.frames = []

    assert term.center.called_with(f"Failed to save audio file: Test exception")
    assert not os.path.exists(save_path)


@pytest.mark.unit()
def test_terminate_audio(audio_service):
    """
    Test the terminate_audio method of the AudioRecordingService class
    Mock the recording state and thread state
    Assert that stop_recording is called if recording is True
    Assert that join is called if the recording thread is alive
    Assert that audio.terminate is called
    """
    with patch.object(audio_service, 'stop_recording') as mock_stop_recording, \
         patch.object(audio_service, 'audio') as mock_audio, \
         patch.object(audio_service, 'recording_thread') as mock_recording_thread:
        
        audio_service.recording = True
        mock_recording_thread.is_alive.return_value = True

        audio_service.terminate_audio()

        mock_stop_recording.assert_called_once() 
        mock_recording_thread.join.assert_called_once()
        mock_audio.terminate.assert_called_once()


@pytest.mark.unit()
def test_terminate_audio_not_recording(audio_service):
    """
    Test the terminate_audio method when not recording
    Mock the recording state and thread state
    Assert that stop_recording is not called if recording is False
    Assert that join is not called if the recording thread is not alive
    Assert that audio.terminate is called
    """
    with patch.object(audio_service, 'stop_recording') as mock_stop_recording, \
         patch.object(audio_service, 'audio') as mock_audio, \
         patch.object(audio_service, 'recording_thread') as mock_recording_thread:
        
        audio_service.recording = False
        mock_recording_thread.is_alive.return_value = False

        audio_service.terminate_audio()

        mock_stop_recording.assert_not_called()
        mock_recording_thread.join.assert_not_called()
        mock_audio.terminate.assert_called_once()


@pytest.mark.unit()
def test_process_audio(stt_service):
    """
    Test the process_audio method of the SpeechToTextService class
    Mock the run (ONNX model inference return value)
    Mock batch_decode (transcription return value)
    Assert process_audio return value is the mocked transcription
    """
    audio_data = np.random.randn(16000).astype(np.float32)

    with patch.object(
        stt_service.ort_session, "run", return_value=[np.random.randn(1, 100, 32)]
    ) as mock_run, \
         patch.object(
        stt_service.processor, "batch_decode", return_value=["test transcription"]
    ) as mock_decode:
            result = stt_service.process_audio(audio_data)
            mock_run.assert_called_once()
            mock_decode.assert_called_once()
            assert result == "test transcription"
