import logging
import pprint
import signal
import traceback
from silero_vad import load_silero_vad, read_audio, get_speech_timestamps

class BackgroundService:
    def __init__(self, app):
        self._logger = logging.getLogger(__name__)
        self._app = app
        self._model = load_silero_vad(True)
        self._sampling_rate = 16_000
        signal.signal(signal.SIGINT, self._signal_handler)

    def start(self):    
        try:
            self._logger.info("Processing audio file")
            test_audio = str(self._app.root) + "/temp/vad_test.wav"            
            wav = read_audio(test_audio, sampling_rate=self._sampling_rate)

            self._logger.info(f"WAV shape: {wav.shape}, dtype: {wav.dtype}") 
            speech_timestamps = get_speech_timestamps(
                wav, self._model, sampling_rate=self._sampling_rate
            )

            print(speech_timestamps)

        except Exception as e:
            self._app.log_exception('Error while processing audio file', e)            
            self._app.exit()
        return

    def stop(self):
        pass

    def _signal_handler(self, signal, frame):
        """
        Handle the SIGINT signal (Ctrl+C) to gracefully terminate the program.

        :param int signal: The signal number.
        :param int frame: The current stack frame.
        """
        self._app.exit()
