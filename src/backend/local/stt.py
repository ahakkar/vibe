import logging
import os
import torch
import numpy as np
import onnxruntime as ort

from transformers import Wav2Vec2Processor
from abstract_classes import SpeechToTextInterface


class SpeechToTextService(SpeechToTextInterface):
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
            + os.getenv("PROCESSOR")
        )
        onnx_filepath = (
            str(project_root)
            + "/"
            + os.getenv("MODEL_FOLDER")
            + "/"
            + os.getenv("ONNX_MODEL")
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
        recorded_sentence = self.processor.batch_decode(
            recorded_ids.numpy(), skip_special_tokens=False
        )[0]

        return recorded_sentence
