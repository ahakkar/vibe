import logging
import numpy as np
import os
import queue
import sounddevice as sd
import sox
import threading
from io import BytesIO
import wave

from piper.voice import PiperVoice
from abstract_classes import TextToSpeechInterface


class TextToSpeech(TextToSpeechInterface):
    """
    A Text-to-Speech (TTS) service that converts text to speech using the PiperVoice model.
    This class handles audio output through a specified device and manages audio streams
    using threading and a queue for efficient processing.

    The TTS service runs a separate thread to process text-to-speech synthesis requests
    from a queue, allowing for asynchronous operation and smooth audio playback.
    """

    def __init__(self, project_root, device_index=1):
        """
        Initialize the TextToSpeech service.

        :param Path project_root: The path of the project root
        :param int device_index: The index of the audio output device to use, defaults to 1
        """
        self.logger = logging.getLogger(__name__)

        model_path = (
            str(project_root)
            + "/"
            + os.getenv("MODEL_FOLDER")
            + "/"
            + os.getenv("TTS_MODEL")
        )

        self.voice = PiperVoice.load(model_path)
        self.device_index = device_index
        self.stream = None
        self.piper_sample_rate = self.voice.config.sample_rate
        self.output_sample_rate = 44100  # Desired output sample rate
        self.sentence_queue = queue.Queue()
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._process_queue)
        self._thread.start()

    def initialize_stream(self):
        """
        Initialize the audio output stream.
        """
        try:
            self.stream = sd.OutputStream(
                device=self.device_index,
                samplerate=self.output_sample_rate,
                channels=1,
                dtype="int16",
            )
            self.stream.start()
            self.logger.info(
                f"Audio stream initialized with sample rate: {self.output_sample_rate}"
            )
        except sd.PortAudioError as e:
            self.logger.error(f"Error initializing audio stream: {e}")
            self.stream = None

    def resample_audio(self, audio_data, orig_sample_rate, target_sample_rate):
        """
        Resample the audio data to the target sample rate.

        :param np.ndarray audio_data: The original audio data
        :param int orig_sample_rate: The original sample rate of the audio data
        :param int target_sample_rate: The target sample rate for the audio data
        :return np.ndarray resampled_audio: The resampled audio data
        """
        # Use SoX to resample the audio data in memory
        tfm = sox.Transformer()
        tfm.set_output_format(rate=target_sample_rate)
        resampled_audio = tfm.build_array(
            input_array=audio_data, sample_rate_in=orig_sample_rate
        )
        return resampled_audio.astype(np.int16)

    def synthesize(self, text):
        """
        Add text to the synthesis queue.

        :param str text: The text to synthesize
        """
        self.sentence_queue.put(text)

    def synthesize_to_buffer(self, text: str) -> BytesIO:
        """
        Synthesize the text to buffer to send to web
        """
        full_audio = bytearray()

        for audio_bytes in self.voice.synthesize_stream_raw(text):
            full_audio.extend(audio_bytes)

        int_data = np.frombuffer(full_audio, dtype=np.int16)

        print(f"Int data: {int_data}")
        if self.output_sample_rate != self.piper_sample_rate:
            int_data = self.resample_audio(
                int_data, self.piper_sample_rate, self.output_sample_rate
            )
        print(f"Resample int data: {int_data}")
        buffer = BytesIO()
        with wave.open(buffer, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.output_sample_rate)
            wf.writeframes(int_data.tobytes())
        print(f"Buffer: {buffer}")
        buffer.seek(0)
        print(f"Buffer 0: {buffer}")
        return buffer

    def _process_queue(self):
        """
        Process the synthesis queue and synthesize text to speech.
        """
        while not self._stop_event.is_set():
            try:
                text = self.sentence_queue.get(timeout=1)
                self._synthesize_text(text)
            except queue.Empty:
                continue

    def _synthesize_text(self, text):
        """
        Synthesize the given text to speech.

        :param str text: The text to synthesize
        """
        if self.stream is None:
            self.initialize_stream()
        if self.stream is not None:
            self.stream.start()
            for audio_bytes in self.voice.synthesize_stream_raw(text):
                int_data = np.frombuffer(audio_bytes, dtype=np.int16)
                if self.output_sample_rate != self.piper_sample_rate:
                    # Resample the audio data to match the output stream's sample rate
                    int_data = self.resample_audio(
                        int_data, self.piper_sample_rate, self.output_sample_rate
                    )
                self.stream.write(int_data)
            self.stream.stop()
        else:
            self.logger.error("Audio stream is not available.")

    def stop(self):
        """
        Stop the TextToSpeech service and clean up resources.
        """
        self._stop_event.set()
        self.sentence_queue.queue.clear()  # Clear the queue to stop any pending synthesis
        if self.stream is not None:
            self.stream.abort()  # Stop the audio stream immediately
        self._thread.join()  # Wait for the processing thread to finish
        self._stop_event.clear()  # Reset the stop event for future use

    def update_device_index(self, device_index=1):
        """
        Update the device index

        :param int device_index: The index of the audio output device to use, defaults to 1
        """
        self.device_index = device_index
