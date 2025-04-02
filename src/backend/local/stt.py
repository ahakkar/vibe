import logging
import os
import torch
import numpy as np
import onnxruntime as ort

from abstract_classes import SpeechToTextInterface
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
from typing import Union


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

        try:
            model_path = (
                str(project_root)
                + "/"
                + os.getenv("MODEL_FOLDER")
                + "/"
                + os.getenv("DEFAULT_MODEL")
            )
            self.processor = Wav2Vec2Processor.from_pretrained(model_path)
            self.model = Wav2Vec2ForCTC.from_pretrained(model_path)
        except Exception as e:
            self.logger.error(f"Failed to open wav2vec processor: {model_path}\n{e}")

    def transcribe(self, audio_data: Union[np.ndarray, torch.Tensor]) -> str:
        """
        Transcribe raw audio data to string.

        Method mostly copied from https://github.com/COMP-SE-610-620/FiLos/blob/main/backend/services/speech_to_text.py

        :param audio_data: Input audio as either numpy array or PyTorch tensor
        :return: Transcribed text
        """
        # Normalize and add batch dimension based on input type
        waveform = (audio_data - audio_data.mean()) / audio_data.std()
        if isinstance(audio_data, torch.Tensor):
            waveform_np = waveform.unsqueeze(0).cpu().numpy()
        else:
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
