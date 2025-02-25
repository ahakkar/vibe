import numpy as np
import sounddevice as sd
import sox
import threading
import queue
from piper.voice import PiperVoice

MODEL_PATH = "/models/fi_FI-harri-medium.onnx"


class TextToSpeech:
    def __init__(self, device_index=1):
        self.model_path = MODEL_PATH
        self.voice = PiperVoice.load(self.model_path)
        self.device_index = device_index
        self.stream = None
        self.piper_sample_rate = self.voice.config.sample_rate
        self.output_sample_rate = 44100  # Desired output sample rate
        self.sentence_queue = queue.Queue()
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._process_queue)
        self._thread.start()

    def initialize_stream(self):
        try:
            self.stream = sd.OutputStream(
                device=self.device_index,
                samplerate=self.output_sample_rate,
                channels=1,
                dtype="int16",
            )
            self.stream.start()
            # print(f"Audio stream initialized with sample rate: {self.output_sample_rate}")
        except sd.PortAudioError as e:
            print(f"Error initializing audio stream: {e}")
            self.stream = None

    def resample_audio(self, audio_data, orig_sample_rate, target_sample_rate):
        # Use SoX to resample the audio data in memory
        tfm = sox.Transformer()
        tfm.set_output_format(rate=target_sample_rate)
        resampled_audio = tfm.build_array(
            input_array=audio_data, sample_rate_in=orig_sample_rate
        )
        return resampled_audio.astype(np.int16)

    def synthesize(self, text):
        self.sentence_queue.put(text)

    def _process_queue(self):
        while not self._stop_event.is_set():
            try:
                text = self.sentence_queue.get(timeout=1)
                self._synthesize_text(text)
            except queue.Empty:
                continue

    def _synthesize_text(self, text):
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
            print("Audio stream is not available.")

    def stop(self):
        self._stop_event.set()
        self._thread.join()
        if self.stream is not None:
            self.stream.close()