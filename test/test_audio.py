import pytest
import os
import wave
import numpy as np
from unittest.mock import patch, MagicMock


# Mock the imports of the modules that are not installed
with patch.dict(
    "sys.modules",
    {
        "pyaudio": MagicMock(),
        "threading": MagicMock(),
        "time": MagicMock(),
        "sounddevice": MagicMock(),
    },
): 
    from src.backend.local.audio import AudioService


class TestAudioService:

    def setup_method(self):
        """
        Setup method to run before each test
        """
        self.app = MagicMock()
        self.audio_service = AudioService(self.app)
        self.audio_service.input_device_index = 7
        self.audio_service.output_device_index = 8

    def teardown_method(self):
        """
        Teardown method to run after each test
        """
        self.audio_service.terminate_audio()
    
    @pytest.mark.unit()
    def test_audio_service_init(self):
        """
        Test the initialization of the AudioService class
        Assert initial values of the class attributes
        """
        assert self.audio_service.sample_rate == 16_000
        assert self.audio_service.channels == 1
        assert self.audio_service.CHUNK == 1024
        assert self.audio_service.audio is not None
        assert self.audio_service.stream is None
        assert self.audio_service.frames == []
        assert self.audio_service.input_device_index == 7
        assert self.audio_service.output_device_index == 8
        
        assert self.audio_service.is_recording is False
        assert self.audio_service.recording_thread is None

    @pytest.mark.unit()
    def test_start_recording_when_already_recording(self):
        """
        Test the start_recording method of the AudioService class
        when already recording
        Assert that the method prints "Already recording audio."
        """
        self.audio_service.is_recording = True

        with patch("builtins.print") as mock_print:
            self.audio_service.start_recording()
            mock_print.assert_called_once_with("Already recording audio.")

    @pytest.mark.unit()
    def test_start_recording(self):
        """
        Test the try path of start_recording method of the AudioService class
        Mock the audio stream with a bytes-like object
        Assert that audio.open is called once
        Assert that the recording state is True
        Assert that the recording thread is alive
        """
        mock_audio_stream = MagicMock()
        mock_audio_stream.read.return_value = b"\x00\x01"

        with patch.object(
            self.audio_service.audio, "open", return_value=mock_audio_stream
        ) as mock_open:
            self.audio_service.start_recording()
            mock_open.assert_called_once()
            assert self.audio_service.is_recording is True
            assert self.audio_service.recording_thread.is_alive()

    @pytest.mark.unit()
    def test_start_recording_error(self):
        """
        Test the start_recording method of the AudioService class
        when the service has device error
        Assert that the term will called once with Please check the audio device index
        Assert that the term will called with Failed to open audio stream: Device Error
        """
        with patch.object(
            self.audio_service.audio, "open", side_effect=Exception("Device Error")
        ) as mock_open, patch("builtins.print") as mock_print:
            self.audio_service.start_recording()
            mock_open.assert_called_once()
            assert self.audio_service.is_recording is False

            mock_print.assert_any_call("Failed to open audio stream: Device Error")
            mock_print.assert_any_call("Please check the audio device index.")

    @pytest.mark.unit()
    def test_stop_recording(self):
        """
        Test the stop_recording method of the AudioService class
        Mock the audio stream with a bytes-like object
        Assert that the recording state is False
        Assert that the recording thread is not alive
        Assert that the returned data is the same as the mocked audio stream return value
        """
        mock_audio_stream = MagicMock()
        mock_audio_stream.read.return_value = b"\x00\x01"

        with patch.object(self.audio_service.audio, "open", return_value=mock_audio_stream):
            self.audio_service.start_recording()
            data = self.audio_service.stop_recording()
            assert self.audio_service.is_recording is False
            assert self.audio_service.recording_thread.is_alive()

    @pytest.mark.unit()
    def test_save_audio_try(self, tmpdir):
        """
        Test that the function successfully runs through the try block.
        Mock the os.path.join function to return the save_path
        Mock the wave.open to return MagicMock object
        Mock wave_file attributes
        Assert wave_open is called with the save_path in write mode
        Assert that save message is printed to terminal
        """
        save_path = os.path.join(tmpdir, "audio.wav")
        mock_wave_file = MagicMock()
        mock_wave_file.setnchannels(1)
        mock_wave_file.setsampwidth(2)
        mock_wave_file.setframerate(16000)
        mock_wave_file.writeframes(b"\x00\x01\x02\x03\x04\x05")

        with patch("os.path.join", return_value=save_path), patch(
            "wave.open", return_value=mock_wave_file
        ) as mock_wave_open, patch("builtins.print") as mock_print:
            self.audio_service.save_audio_to_file()
            mock_wave_open.assert_called_once_with(save_path, "wb")

        mock_print.assert_called_once_with(f"Audio saved to {save_path}")


    @pytest.mark.unit()
    def test_save_audio_exeption(self, tmpdir):
        """
        Test that the function raises an exception.
        Set tmp directory
        Mock the frames attribute
        Mock the os.path.join function to return the save_path
        Mock the wave.open function to raise an exception
        Assert that no .wav file is saved
        Assert that the exception is raised and message is printed
        """
        save_path = os.path.join(tmpdir, "audio.wav")
        mock_frames = [b"\x00\x01", b"\x02\x03", b"\x04\x05"]
        self.audio_service.frames = mock_frames

        with patch("os.path.join", return_value=save_path), patch(
            "wave.open", side_effect=Exception("Test exception")), patch(
                "builtins.print") as mock_print:
            self.audio_service.save_audio_to_file()

        mock_print.assert_called_with(f"Failed to save audio file: Test exception")
        assert not os.path.exists(save_path)


    @pytest.mark.unit()
    def test_terminate_audio(self):
        """
        Test the terminate_audio method of the AudioService class
        Mock the recording state and thread state
        Assert that stop_recording is called if recording is True
        Assert that join is called if the recording thread is alive
        Assert that audio.terminate is called
        """
        with patch.object(
            self.audio_service, "stop_recording"
        ) as mock_stop_recording, patch.object(
            self.audio_service, "audio"
        ) as mock_audio, patch.object(
            self.audio_service, "recording_thread"
        ) as mock_recording_thread:
            self.audio_service.is_recording = True
            mock_recording_thread.is_alive.return_value = True

            self.audio_service.terminate_audio()

            mock_stop_recording.assert_called_once()
            mock_recording_thread.join.assert_called_once()
            mock_audio.terminate.assert_called_once()


    @pytest.mark.unit()
    def test_terminate_audio_not_recording(self):
        """
        Test the terminate_audio method when not recording
        Mock the recording state and thread state
        Assert that stop_recording is not called if recording is False
        Assert that join is not called if the recording thread is not alive
        Assert that audio.terminate is called
        """
        with patch.object(
            self.audio_service, "stop_recording"
        ) as mock_stop_recording, patch.object(
            self.audio_service, "audio"
        ) as mock_audio, patch.object(
            self.audio_service, "recording_thread"
        ) as mock_recording_thread:
            self.audio_service.recording = False
            mock_recording_thread.is_alive.return_value = False

            self.audio_service.terminate_audio()

            mock_stop_recording.assert_not_called()
            mock_recording_thread.join.assert_not_called()
            mock_audio.terminate.assert_called_once()

    @pytest.mark.skip()
    def test_query_devices(self):
        """
        Test the query_devices method of the AudioService class
        Mock the sounddevice.query_devices function
        Assert that the function returns the expected value
        """
        mock_devices = [
            {"name": "Device 1", "max_input_channels": 2},
            {"name": "Device 2", "max_input_channels": 1},
        ]
        self.audio_service.query_devices = MagicMock(return_value=mock_devices)

        devices = self.audio_service.query_devices()
        assert devices == mock_devices

    @pytest.mark.skip()
    def test_get_device_index(self):
        pass
