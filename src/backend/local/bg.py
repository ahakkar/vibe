import logging
import pprint
import signal
import traceback
import torch

from local.audio_stream import AudioStreamService
from local.constants import Srv
from typing import Tuple
from silero_vad import load_silero_vad, read_audio, get_speech_timestamps


class BackgroundService:
    def __init__(self, app):
        self._logger = logging.getLogger(__name__)
        self._app = app
        self._model = load_silero_vad(True)        
        self._audioservice = AudioStreamService(self._app)        
        signal.signal(signal.SIGINT, self._signal_handler)

    def start(self):        
        self._audioservice.start_listening()

    def stop(self):
        self._audioservice.stop_listening()

    def test_with_audio_file(self):
        self._sampling_rate = 16_000

        try:
            self._logger.info("Processing audio file")

            test_audio = str(self._app.root) + "/temp/vad_test.wav"
            wav: Tuple[torch.Tensor, int] = read_audio(
                test_audio, sampling_rate=self._sampling_rate
            )

            self._logger.info(f"WAV shape: {wav.shape}, dtype: {wav.dtype}")

            speech_timestamps: list[dict[str, int]] = get_speech_timestamps(
                wav, self._model, sampling_rate=self._sampling_rate
            )

            for ts in speech_timestamps:
                print(f"slicing audio, timestamps: {ts}")
                try:
                    slice = self._slice_audio(wav, ts)
                    sentence = self._app.get_service(Srv.STT).transcribe(slice)
                    print(sentence)
                except Exception as e:
                    self._logger.error(f"slicing failed: {e}")

        except Exception as e:
            self._logger.error(f"Error while processing audio file timestamps {e}")

    def _slice_audio(self, audio: torch.Tensor, ts: dict[str, int]) -> torch.Tensor:
        """
        Slices a PyTorch tensor (audio) based on provided start and end sample indices.

        :param wav: A tuple containing the audio tensor and sampling rate.
        :param start
        :param end
        :return PyTorch tensor representing the speech segment.
        """

        return audio[ts["start"] : ts["end"]]

    def _signal_handler(self, signal, frame):
        """
        Handle the SIGINT signal (Ctrl+C) to gracefully terminate the program.

        :param int signal: The signal number.
        :param int frame: The current stack frame.
        """
        self.stop()
        self._app.exit()