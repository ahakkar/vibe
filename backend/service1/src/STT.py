import os
import torch
import torchaudio
import pyaudio
import wave
import onnxruntime as ort
from transformers import Wav2Vec2Processor

LANG_ID = "fi"
ONNX_MODEL_PATH = "/models/wav2vec2_model.onnx"
PROCESSOR_PATH = "/models/wav2vec2_processor"


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
        self.processor = Wav2Vec2Processor.from_pretrained(PROCESSOR_PATH)
        self.ort_session = ort.InferenceSession(ONNX_MODEL_PATH)

    def record_audio(self):
        """
        Record audio from device and save it to a file.
        """
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

        # Process the audio file using the ONNX model
        self.process_audio(self.OUTPUT_FILE)

    def process_audio(self, audio_file_path: str):
        """
        Process the audio file using the ONNX model.
        """
        # Load the audio file using torchaudio
        waveform, sample_rate = torchaudio.load(audio_file_path, format="wav")

        # Preprocess the input for the model
        inputs = self.processor(
            waveform.squeeze().numpy(),
            sampling_rate=16_000,
            return_tensors="np",
            padding=True,
        )

        # Include the attention_mask in the inputs
        ort_inputs = {
            self.ort_session.get_inputs()[0].name: inputs.input_values,
            self.ort_session.get_inputs()[1].name: inputs.attention_mask,
        }

        # Perform inference using the ONNX model
        ort_outs = self.ort_session.run(None, ort_inputs)

        # Get recorded audio as text
        recorded_ids = torch.argmax(torch.tensor(ort_outs[0]), dim=-1)
        recorded_sentence = self.processor.batch_decode(recorded_ids.numpy())[0]

        print(f"Transcription: {recorded_sentence}")