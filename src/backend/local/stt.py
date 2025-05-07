import logging
import os
import torch
import numpy as np
import onnxruntime as ort

from abstract_classes import SpeechToTextInterface
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
from typing import Union

DEBUG_MODE = True

class Wav2Vec2Service(SpeechToTextInterface):
    """
    Service for converting speech to text using a pre-trained Wav2Vec2 model and ONNX runtime.
    """

    def __init__(self, app):
        """
        Initialize the speech-to-text service.

        :param Path project_root: The path of the project root
        """
        self.logger = logging.getLogger(__name__)
        self._app = app

        model_path = (
            str(self._app.root)
            + "/"
            + os.getenv("MODEL_FOLDER")
            + "/"
            + os.getenv("STT_DEFAULT_MODEL")
        )

        try:
            self.processor = Wav2Vec2Processor.from_pretrained(model_path)
            self.model = Wav2Vec2ForCTC.from_pretrained(model_path)
        except Exception as e:
            self.logger.error(f"Failed to open wav2vec processor: {model_path}\n{e}")
            self._app.exit(1)

    def transcribe(self, audio_data: np.ndarray) -> str:
        """
        Transcribe raw audio data to string.

        Method mostly copied from https://github.com/COMP-SE-610-620/FiLos/blob/main/backend/services/speech_to_text.py

        :param audio_data: Input audio
        :return: Transcribed text
        """
        # Normalize and add batch dimension based on input type
        waveform = (audio_data - audio_data.mean()) / audio_data.std()
        waveform_np = np.expand_dims(waveform, axis=0)

        # Preprocess the input
        inputs = self.processor(
            waveform_np, sampling_rate=16_000, return_tensors="pt", padding=True
        )

        with torch.no_grad():
            logits = self.model(
                inputs.input_values, attention_mask=inputs.attention_mask
            ).logits

        predicted_ids = torch.argmax(logits, dim=-1)
        predicted_sentence = self.processor.batch_decode(predicted_ids)[0]

        return predicted_sentence


class Wav2Vec2ONNXService(SpeechToTextInterface):
    """
    Service for converting speech to text using a pre-trained Wav2Vec2 model and ONNX runtime.
    """

    def __init__(self, project_root):
        """
        Initialize the speech-to-text service.

        :param Path project_root: The path of the project root
        """
        self.logger = logging.getLogger(__name__)

        proc_filepath = (
            str(project_root)
            + "/"
            + os.getenv("MODEL_FOLDER")
            + "/"
            + os.getenv("STT_ONNX_PROCESSOR")
        )
        onnx_filepath = (
            str(project_root)
            + "/"
            + os.getenv("MODEL_FOLDER")
            + "/"
            + os.getenv("STT_ONNX_MODEL")
        )

        try:
            self.processor = Wav2Vec2Processor.from_pretrained(proc_filepath)
        except Exception as e:
            self.logger.error(f"Failed to open wav2vec processor: {proc_filepath}\n{e}")

        try:
            self.ort_session = ort.InferenceSession(onnx_filepath)
        except Exception as e:
            self.logger.error(f"Failed to open wav2vec onnx file: {onnx_filepath}\n{e}")

    def transcribe(self, audio_data: np.ndarray) -> str:
        """
        Process raw audio data using the ONNX model.

        :param np.ndarray audio_data: The audio data that will be transcribed

        :return str recorded_sentence: The recorded sentence that is transcribed from audio data
        """

        audio_data = audio_data.astype(np.float32)
        audio_data = (audio_data - audio_data.mean()) / audio_data.std()

        # Reshape to match expected input shape
        waveform = np.expand_dims(audio_data, axis=0)

        # Preprocess the input for the model
        inputs = self.processor(
            waveform,
            sampling_rate=16000,
            return_tensors="np",
            padding=True,
        )

        # Include the attention_mask in the inputs
        ort_inputs = {
            self.ort_session.get_inputs()[0].name: inputs["input_values"],
            self.ort_session.get_inputs()[1].name: inputs["attention_mask"],
        }

        # Perform inference using the ONNX model
        ort_outs = self.ort_session.run(None, ort_inputs)

        # Get recorded audio as text
        recorded_ids = np.argmax(ort_outs[0], axis=-1)
        recorded_sentence = self.processor.batch_decode(
            recorded_ids, skip_special_tokens=False
        )[0]

        self.logger.info("RETURN : [speech_to_text] Transcribing audio")
        return recorded_sentence
