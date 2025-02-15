import numpy as np
import sounddevice as sd
import sox
from piper.voice import PiperVoice

MODEL_PATH = "/models/fi_FI-harri-medium.onnx"
DEVICE_INDEX = 1  # Change this to the correct device index (see sd.query_devices())


class TextToSpeech:
    def __init__(self):
        self.model_path = MODEL_PATH
        self.voice = PiperVoice.load(self.model_path)
        self.stream = None
        self.piper_sample_rate = self.voice.config.sample_rate
        self.output_sample_rate = 44100  # Desired output sample rate

    def initialize_stream(self):
        try:
            device_index = DEVICE_INDEX  # Index for your audio device
            print("Listing available audio devices:")
            for i, device_info in enumerate(sd.query_devices()):
                print(f"Device {i}: {device_info['name']}")
            device_info = sd.query_devices(device_index)
            print(f"Using device: {device_info['name']}")
            self.stream = sd.OutputStream(
                device=device_index,
                samplerate=self.output_sample_rate,
                channels=1,
                dtype="int16"
            )
            self.stream.start()
            print(f"Audio stream initialized with sample rate: {self.output_sample_rate}")
        except sd.PortAudioError as e:
            print(f"Error initializing audio stream: {e}")
            self.stream = None

    def resample_audio(self, audio_data, orig_sample_rate, target_sample_rate):
        # Use SoX to resample the audio data in memory
        tfm = sox.Transformer()
        tfm.set_output_format(rate=target_sample_rate)
        resampled_audio = tfm.build_array(input_array=audio_data, sample_rate_in=orig_sample_rate)
        return resampled_audio.astype(np.int16)

    def synthesize(self, text):
        if self.stream is None:
            self.initialize_stream()
        if self.stream is not None:
            self.stream.start()
            for audio_bytes in self.voice.synthesize_stream_raw(text):
                int_data = np.frombuffer(audio_bytes, dtype=np.int16)
                if self.output_sample_rate != self.piper_sample_rate:
                    # Resample the audio data to match the output stream's sample rate
                    int_data = self.resample_audio(int_data, self.piper_sample_rate, self.output_sample_rate)
                self.stream.write(int_data)
            self.stream.stop()
        else:
            print("Audio stream is not available.")