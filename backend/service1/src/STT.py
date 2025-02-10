import os
import torch
import torchaudio
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC

LANG_ID = "fi"
MODEL_ID = "Finnish-NLP/wav2vec2-large-uralic-voxpopuli-v2-finnish"


class AudioRecordingService:

    def __init__(self):
        """
        Initialize the AudioRecordingService
        """
        self.sample_rate = 16_000
        self.channels = 1
        self.CHUNK = 1024
        self.RECORD_SECONDS = 5
        self.OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "..", "output.wav")

    def record_audio(self):
        """
        Record audio from device and save it to a file.
        """
        import pyaudio
        import wave

        audio = pyaudio.PyAudio()

        stream = audio.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.CHUNK,
        )

        print("Recording...")

        frames = []

        for i in range(0, int(self.sample_rate / self.CHUNK * self.RECORD_SECONDS)):
            data = stream.read(self.CHUNK)
            frames.append(data)

        print("Finished recording.")

        stream.stop_stream()
        stream.close()
        audio.terminate()

        wave_file = wave.open(self.OUTPUT_FILE, "wb")
        wave_file.setnchannels(self.channels)
        wave_file.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        wave_file.setframerate(self.sample_rate)
        wave_file.writeframes(b"".join(frames))
        wave_file.close()

        print(f"Audio saved to {self.OUTPUT_FILE}")


class SpeechToTextService:

    def __init__(self):
        """
        Initialize the SpeechToTextService
        """
        self.processor = Wav2Vec2Processor.from_pretrained(MODEL_ID)
        self.model = Wav2Vec2ForCTC.from_pretrained(MODEL_ID)

    def process_audio(self, audio_file_path: str) -> str:
        """
        Processe the audio file.
        """
        # Load the audio file using torchaudio
        waveform, sample_rate = torchaudio.load(audio_file_path)

        # Preprocess the input for the model
        inputs = self.processor(
            waveform.squeeze().numpy(),
            sampling_rate=16_000,
            return_tensors="pt",
            padding=True,
        )

        # Perform inference
        with torch.no_grad():
            logits = self.model(
                inputs.input_values, attention_mask=inputs.attention_mask
            ).logits

        # Get recorded audio as text
        recorded_ids = torch.argmax(logits, dim=-1)
        recorded_sentence = self.processor.batch_decode(recorded_ids)[0]

        return recorded_sentence
