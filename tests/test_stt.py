import pytest
import os
import numpy as np
from unittest.mock import patch, MagicMock
from STT import AudioRecordingService, SpeechToTextService

@pytest.fixture
def audio_service():
    return AudioRecordingService(device_index=7)

@pytest.fixture
def stt_service():
    return SpeechToTextService()

def test_start_recording(audio_service):
    with patch.object(audio_service.audio, 'open', return_value=MagicMock()) as mock_open:
        audio_service.start_recording()
        mock_open.assert_called_once()
        assert audio_service.recording is True
        assert audio_service.recording_thread.is_alive()

""" def test_stop_recording(audio_service):
    with patch.object(audio_service.audio, 'open', return_value=MagicMock()) as mock_open:
        audio_service.start_recording()
        audio_service.stop_recording()
        assert audio_service.recording is False
        assert not audio_service.recording_thread.is_alive()

def test_save_audio_to_file(audio_service):
    audio_service.frames = [b'\x00\x01', b'\x02\x03']
    with patch('wave.open', new_callable=MagicMock) as mock_wave_open:
        audio_service.save_audio_to_file('test.wav')
        mock_wave_open.assert_called_once_with('test.wav', 'wb')

def test_process_audio(stt_service):
    audio_data = np.random.randn(16000).astype(np.float32)
    with patch.object(stt_service.ort_session, 'run', return_value=[np.random.randn(1, 100, 32)]) as mock_run:
        with patch.object(stt_service.processor, 'batch_decode', return_value=["test transcription"]) as mock_decode:
            result = stt_service.process_audio(audio_data)
            mock_run.assert_called_once()
            mock_decode.assert_called_once()
            assert result == "test transcription" """
