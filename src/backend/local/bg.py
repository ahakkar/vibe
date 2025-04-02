import signal
from silero_vad import load_silero_vad, read_audio, get_speech_timestamps


class BackgroundService:
    def __init__(self, app):
        self._app = app
        self.model = load_silero_vad(True)
        signal.signal(signal.SIGINT, self._app.exit())

    def start(self):
        pass

    def stop(self):
        pass
