import logging
from typing import Optional
import numpy as np
import os
import pyaudio
import sounddevice as sd
import threading
import time
import wave


class AudioService:
    """
    Service for recording audio using the PyAudio library.
    """

    def __init__(self, app):
        """
        Initialize the audio recording service.
        """

        self.app = app
        self.logger = logging.getLogger(__name__)

        input_device_name = os.getenv("INPUT_DEVICE_NAME")
        output_device_name = os.getenv("OUTPUT_DEVICE_NAME")

        self.sample_rate = 16_000
        self.channels = 1
        self.CHUNK = 1024
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.frames = []
        self.input_device_index = self._get_device_index(input_device_name, "input")
        self.output_device_index = self._get_device_index(output_device_name, "output")

        self.is_recording = False
        self.recording_thread = None

    def start_recording(self) -> Optional[bool]:
        """
        Start recording audio from the specified input device.

        :return was it recording or not already?
        """
        if self.is_recording:
            self.logger.info(f"Already recording audio.")
            return True

        self.frames = []
        try:
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.CHUNK,
                input_device_index=self.input_device_index,
            )
        except Exception as e:
            self.is_recording = False
            self.logger.error(
                f"Failed to open audio stream: {e}\nPlease check the audio device index."
            )
            return None

        # Start a new thread for recording
        self.recording_thread = threading.Thread(target=self._record_audio)
        self.logger.info(f"Start recording.")
        self.is_recording = True
        self.recording_thread.start()

        return False

    def _record_audio(self):
        """
        Record audio data in a separate thread.
        """
        try:
            while self.is_recording:
                data = self.stream.read(self.CHUNK, exception_on_overflow=False)
                self.frames.append(data)
        except IOError as e:
            self.logger.error(f"Error while recording: {e}")
        finally:
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()

    def stop_recording(self, save_audio: bool = False) -> Optional[np.ndarray]:
        """
        Stop recording audio and optionally save the recorded audio to a file.

        :param bool save_audio: Whether to save the recorded audio to a file, defaults to False.
        :return np.ndarray audio_data: The recorded audio data as a NumPy array.
        """
        if not self.is_recording:
            self.logger.info(f"Not recording.")
            return None

        self.is_recording = False
        if self.recording_thread:
            self.recording_thread.join()  # Wait for the thread to finish
        time.sleep(0.1)

        self.logger.info(f"Finished recording.")

        if self.stream:
            self.stream.stop_stream()
            self.stream.close()

        if not self.frames:
            self.logger.info(f"No audio frames recorded.")
            return None

        # Convert frames to NumPy array for direct processing
        audio_data = (
            np.frombuffer(b"".join(self.frames), dtype=np.int16).astype(np.float32)
            / 32768.0
        )

        if save_audio:
            self.save_audio_to_file()

        return audio_data

    def save_audio_to_file(self) -> bool:
        """
        Save the recorded audio to a file.

        :return is save operation successful?
        """
        # Determine the correct .env path based if running in Docker

        if os.getenv("RUNNING_IN_DOCKER"):
            save_path = os.path.join("/usr/src", os.getenv("OUTPUT_FILENAME"))
        else:
            save_path = os.path.join(
                os.path.dirname(__file__), os.getenv("OUTPUT_FILENAME")
            )

        try:
            with wave.open(save_path, "wb") as wave_file:
                wave_file.setnchannels(self.channels)
                wave_file.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
                wave_file.setframerate(self.sample_rate)
                wave_file.writeframes(b"".join(self.frames))

            self.logger.info(f"Audio saved to {save_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save audio file: {e}")
            return False

    def terminate_audio(self):
        """
        Terminate the PyAudio instance and ensure the recording thread is properly terminated.
        """
        if self.is_recording:
            self.stop_recording()

        if self.recording_thread and self.recording_thread.is_alive():
            self.recording_thread.join()

        self.audio.terminate()

    def get_query_devices(self):
        """
        Get the available query devices

        :return (DeviceList | dict[str, Any]): Information about query devices
        """
        return sd.query_devices()

    def _get_device_index(self, device_name, device_type):
        """
        Get the device index for a given device name

        :param str device_name: The device name to look up
        :param str device_type: The device type (input or output)

        :return Optional[int]: int, The device index, or None if not found
        """
        devices = sd.query_devices()
        for i, device in enumerate(devices):
            if device["name"] == device_name and (
                (device_type == "input" and device["max_input_channels"] > 0)
                or (device_type == "output" and device["max_output_channels"] > 0)
            ):
                return i
        return None
