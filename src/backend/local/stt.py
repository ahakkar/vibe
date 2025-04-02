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
            model_path = "/home/antti/.cache/huggingface/hub/models--Finnish-NLP--wav2vec2-large-uralic-voxpopuli-v2-finnish/snapshots/72cda0634358fb4cb11da6c09cea9fad6f0cf073"
            self.processor = Wav2Vec2Processor.from_pretrained(model_path)
            self.model = Wav2Vec2ForCTC.from_pretrained(model_path)
        except Exception as e:
            self.logger.error(f"Failed to open wav2vec processor: {model_path}\n{e}")

    def transcribe(self, audio_data: Union[np.ndarray, torch.Tensor]) -> str:
        """
        Process raw audio data using the ONNX model.

        :param audio_data: Input audio as either numpy array or PyTorch tensor
        :return: Transcribed text
        """
        # Normalize and add batch dimension based on input type
        waveform = (audio_data - audio_data.mean()) / audio_data.std()
        if isinstance(audio_data, torch.Tensor):
            waveform_np = waveform.unsqueeze(0).cpu().numpy()
        else:
            waveform_np = np.expand_dims(waveform, axis=0)

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

    def transcribe2(self, audio_data: Union[np.ndarray, torch.Tensor]) -> str:
        """
        Process raw audio data using the ONNX model.

        :param audio_data: Input audio as either numpy array or PyTorch tensor
        :return: Transcribed text
        """
        # Normalize and add batch dimension based on input type
        waveform = (audio_data - audio_data.mean()) / audio_data.std()
        if isinstance(audio_data, torch.Tensor):
            waveform_np = waveform.unsqueeze(0).cpu().numpy()
        else:
            waveform_np = np.expand_dims(waveform, axis=0)

        # Preprocess the input for the model
        inputs = self.processor(
            waveform_np,
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

        # Decode the output
        recorded_ids = torch.argmax(torch.tensor(ort_outs[0]), dim=-1)
        recorded_sentence = self.processor.batch_decode(
            recorded_ids.numpy(), skip_special_tokens=True
        )[0]

        return recorded_sentence
