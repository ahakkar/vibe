import os
import time
import torch
import torchaudio
import numpy as np
import pyaudio
import onnxruntime as ort
import threading
from transformers import Wav2Vec2Processor
import wave
from blessed import Terminal

ONNX_MODEL_PATH = "/models/wav2vec2_model.onnx"
PROCESSOR_PATH = "/models/wav2vec2_processor"

term = Terminal()


class AudioRecordingService:
    def __init__(self, device_index=7):
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
        if self.recording:
            print(term.center("Already recording!"))
            return

        self.frames = []
        try:
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.CHUNK,
                input_device_index=self.device_index
            )
        except Exception as e:
            print(term.center(f"Failed to open audio stream: {e}"))
            print(term.center(term.bold("Please check the audio device index.")))
            return
        self.recording = True
        print(term.center("Recording..."))

        # Start a new thread for recording
        self.recording_thread = threading.Thread(target=self._record_audio)
        self.recording_thread.start()

    def _record_audio(self):
        try:
            while self.recording:
                data = self.stream.read(self.CHUNK, exception_on_overflow=False)
                self.frames.append(data)
        except IOError as e:
            print(term.center(f"Error recording: {e}"))

    def stop_recording(self):
        if not self.recording:
            print(term.center("Not recording."))
            return

        self.recording = False
        self.recording_thread.join()  # Wait for the thread to finish
        time.sleep(0.1)
        print(term.center("Finished recording."))
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        
        if not self.frames:
            print(term.center("No audio frames recorded."))
            return None

        # Convert frames to NumPy array for direct processing
        audio_data = np.frombuffer(b"".join(self.frames), dtype=np.int16).astype(np.float32) / 32768.0

        # Determine the correct .env path based if running in Docker
        if os.getenv("RUNNING_IN_DOCKER"):
            save_path = os.path.join("/usr/src/app", "recorded_audio.wav")
        else:
            save_path = os.path.join(os.path.dirname(__file__), "recorded_audio.wav")
        
        # Save the recorded audio to a file for debugging
        save_path = os.path.join("/usr/src/app", "recorded_audio.wav")
        self.save_audio_to_file(save_path)
        
        return audio_data

    def save_audio_to_file(self, filename):
        try:
            wave_file = wave.open(filename, "wb")
            wave_file.setnchannels(self.channels)
            wave_file.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
            wave_file.setframerate(self.sample_rate)
            wave_file.writeframes(b"".join(self.frames))
            wave_file.close()
            print(term.center(f"Audio saved to {filename}"))
        except Exception as e:
            print(term.center(f"Failed to save audio file: {e}"))

    def terminate_audio(self):
        self.audio.terminate()


class SpeechToTextService:
    def __init__(self):
        self.processor = Wav2Vec2Processor.from_pretrained(PROCESSOR_PATH)
        self.ort_session = ort.InferenceSession(ONNX_MODEL_PATH)

    def process_audio(self, audio_data: np.ndarray) -> str:
        """
        Process raw audio data using the ONNX model.
        """
        # Normalize the audio data (Is this necessary?)
        audio_data = (audio_data - audio_data.mean()) / audio_data.std()

        # Reshape to match expected input shape
        waveform = torch.tensor(audio_data).unsqueeze(0)

        # Preprocess the input for the model
        inputs = self.processor(
            waveform.numpy(),
            sampling_rate=16000,
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
        recorded_sentence = self.processor.batch_decode(recorded_ids.numpy(), skip_special_tokens=False)[0]
        
        return recorded_sentence
