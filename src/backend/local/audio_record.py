import pyaudio
import threading
import time
import numpy as np
import os
import wave

class AudioRecordingService:
    """
    Service for recording audio using the PyAudio library.
    """

    def __init__(self, device_index):
        """
        Initialize the audio recording service.

        :param int device_index: Index of the audio input device to use.
        """
        self.sample_rate = 16_000
        self.channels = 1
        self.CHUNK = 1024
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.frames = []
        self.recording = False
        self.device_index = device_index
        self.recording_thread = None

    def start_recording(self):
        """
        Start recording audio from the specified input device.
        """
        if self.recording:
            print("Already recording audio.")
            return

        self.frames = []
        try:
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.CHUNK,
                input_device_index=self.device_index,
            )
        except Exception as e:
            print(f"Failed to open audio stream: {e}")
            print("Please check the audio device index.")
            return
        
        self.recording = True

        # Start a new thread for recording
        self.recording_thread = threading.Thread(target=self._record_audio)
        self.recording_thread.start()

    def _record_audio(self):
        """
        Record audio data in a separate thread.
        """
        try:
            while self.recording:
                data = self.stream.read(self.CHUNK, exception_on_overflow=False)
                self.frames.append(data)
        except IOError as e:
            print(f"Error recording: {e}")
        finally:
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()

    def stop_recording(self, save_audio=False):
        """
        Stop recording audio and optionally save the recorded audio to a file.

        :param bool save_audio: Whether to save the recorded audio to a file, defaults to False.
        :return np.ndarray: The recorded audio data as a NumPy array.
        """
        if not self.recording:
            print("Not recording.")
            return

        self.recording = False
        if self.recording_thread:
            self.recording_thread.join()  # Wait for the thread to finish
        time.sleep(0.1)
        print("Finished recording.")

        if self.stream:
            self.stream.stop_stream()
            self.stream.close()

        if not self.frames:
            print("No audio frames recorded.")
            return None

        # Convert frames to NumPy array for direct processing
        audio_data = (
            np.frombuffer(b"".join(self.frames), dtype=np.int16).astype(np.float32)
            / 32768.0
        )

        if save_audio:
            self.save_audio_to_file()

        return audio_data
    

    def save_audio_to_file(self):
        """
        Save the recorded audio to a file.
        """
        # Determine the correct .env path based if running in Docker

        if os.getenv("RUNNING_IN_DOCKER"):
            save_path = os.path.join("/usr/src/app", os.getenv("OUTPUT_FILENAME"))
        else:
            save_path = os.path.join(os.path.dirname(__file__), os.getenv("OUTPUT_FILENAME"))

        try:
            with wave.open(save_path, "wb") as wave_file:
                wave_file.setnchannels(self.channels)
                wave_file.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
                wave_file.setframerate(self.sample_rate)
                wave_file.writeframes(b"".join(self.frames))
            print(f"Audio saved to {save_path}")
        except Exception as e:
            print(f"Failed to save audio file: {e}")
            

    def terminate_audio(self):
        """
        Terminate the PyAudio instance and ensure the recording thread is properly terminated.
        """
        if self.recording:
            self.stop_recording()

        if self.recording_thread and self.recording_thread.is_alive():
            self.recording_thread.join()

        self.audio.terminate()