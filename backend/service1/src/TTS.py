import numpy as np
import sounddevice as sd
from piper.voice import PiperVoice


MODEL_PATH = "/models/fi_FI-harri-medium.onnx"


class TextToSpeech:
    def __init__(self):
        self.model_path = MODEL_PATH
        self.voice = PiperVoice.load(self.model_path)
        self.stream = None

    def initialize_stream(self):
        try:
            self.stream = sd.OutputStream(
                samplerate=self.voice.config.sample_rate, channels=1, dtype="int16"
            )
        except sd.PortAudioError as e:
            print(f"Error initializing audio stream: {e}")
            self.stream = None

    def synthesize(self, text):
        if self.stream is None:
            self.initialize_stream()
        if self.stream is not None:
            self.stream.start()
            for audio_bytes in self.voice.synthesize_stream_raw(text):
                int_data = np.frombuffer(audio_bytes, dtype=np.int16)
                self.stream.write(int_data)
            self.stream.stop()
        else:
            print("Audio stream is not available.")
