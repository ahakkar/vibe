from collections import deque
import logging
from typing import Optional
import numpy as np
import os
import pyaudio
import sounddevice as sd
import threading
import time
import wave

from local.constants import Srv

class AudioBuffer:
    def __init__(self, max_duration_seconds=5, sample_rate=16_000):
        self.sample_rate = sample_rate
        self.sample_width = 2
        self.max_frames = max_duration_seconds * sample_rate
        self.buffer = deque(maxlen=self.max_frames)

    def add_chunk(self, chunk: np.ndarray):
        """
        Add a chunk of audio data
        """
        self.buffer.extend(chunk)

    def get_all(self):
        """
        Return complete buffer as numpy array
        """
        return np.array(self.buffer, dtype=np.int16)

    def get_last(self, num_samples):
        """
        Get last N samples
        """
        return np.array(list(self.buffer)[-num_samples:], dtype=np.int16)


class AudioStreamService:
    def __init__(self, app):
        self._app = app
        self.logger = logging.getLogger(__name__)
        self.is_recording = False

        self._main_buffer = AudioBuffer()
        self._speech_buffer = []
        self._sample_rate = 16_000
        self._blocksize = 1024
        self._channels = 1

        self._input_device_name = os.getenv("INPUT_DEVICE_NAME")
        self._input_device_index = self._get_device_index(self._input_device_name, "input")

        self.audio_stream = None

    def start_listening(self):
        """        
        """

        if not self.is_recording:
            self.is_recording = True
            self.audio_stream = sd.InputStream(
                device=self._input_device_index,
                samplerate=self._sample_rate,
                blocksize=self._blocksize,
                channels=self._channels,
                callback=self.audio_callback,
            )
            self.audio_stream.start()
            self._stream()

    def stop_listening(self):
        """
        """

        if self.is_recording:
            self.is_recording = False
            if self.audio_stream:
                self.audio_stream.stop_stream()
                self.audio_stream.close()
        

    def _stream(self):
        while True:
            if not self.is_recording:
                break

            audio_chunk = self._main_buffer.read_latest()
            self._speech_buffer.add_chunk(audio_chunk)

            # Check for speech end
            if vad.detect_end(audio_chunk):
                audio_text = self._app.get_service(Srv.STT).transcribe(
                    self.speech_buffer
                )
                self._speech_buffer.clear()

                intent = self._app.get_service(Srv.IR).recognize_intent(audio_text)

                if intent != None:
                    intent_response = self._app.get_service(Srv.IR).process_intent(
                        intent
                    )
                    self._app.get_service(Srv.TTS).synthesize(intent_response)

                else:
                    self._app.text_gen(audio_text, True)

    def audio_callback(self, indata, frames, time, status):
        """
        Adds a blocksize chunk to main buffer or pads the incomplete chunk with zeros to reach blocksize
        """
        if frames == self._blocksize:
            self._main_buffer.add_chunk(indata)
        else:
            padding = np.zeros((self._blocksize - frames, indata.shape[1]))
            padded_data = np.concatenate((indata, padding), axis=0)
            self._main_buffer.add_chunk(padded_data)

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