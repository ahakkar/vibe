import queue
import os
import pytest
import numpy as np
import sounddevice as sd

from pathlib import Path
from unittest.mock import patch, MagicMock


# Mock the imports of the modules that are not installed
with patch.dict(
    "sys.modules",
    {
        "sox": MagicMock(),
        "piper.voice": MagicMock(),
    },
):
    from tts import TextToSpeech


class TestTextToSpeech:

    def setup_method(self):
        """
        Setup method to run before each test
        """
        self.app = MagicMock()
        self.app.root = Path(__file__).parent.parent

        with patch.dict(
            os.environ,
            {
                "MODEL_FOLDER": "models",
                "TTS_MODEL": "fi_FI-harri-medium.onnx",
            },
        ):
            self.tts = TextToSpeech(self.app, device_index=1)

    def teardown_method(self):
        """
        Teardown method to run after each test
        """
        self.tts.stop()
        self.tts = None
        self.app = None

    @pytest.mark.unit()
    def test_test_to_speech_init(self):
        """
        Test the initialization of the TextToSpeech class.
        """
        assert self.tts.voice is not None
        assert self.tts.device_index == 1
        assert self.tts.stream is None
        assert self.tts.piper_sample_rate == self.tts.voice.config.sample_rate
        assert self.tts.output_sample_rate == 44100
        assert isinstance(self.tts.sentence_queue, queue.Queue)
        assert self.tts._stop_event.is_set() is False
        assert self.tts._thread.is_alive()

    @pytest.mark.unit()
    def test_initialize_stream_success(self):
        """
        Test the initialize_stream method when the stream is successfully initialized.
        """
        with patch("sounddevice.OutputStream") as mock_output_stream:
            mock_stream_instance = MagicMock()
            mock_output_stream.return_value = mock_stream_instance

            self.tts.initialize_stream()

            mock_output_stream.assert_called_once_with(
                device=self.tts.device_index,
                samplerate=self.tts.output_sample_rate,
                channels=1,
                dtype="int16",
            )
            mock_stream_instance.start.assert_called_once()
            assert self.tts.stream == mock_stream_instance

    @pytest.mark.unit()
    def test_initialize_stream_exception(self):
        """
        Test the initialize_stream method when an unexpected exception is raised.
        """
        with patch.object(
            sd, "OutputStream", side_effect=Exception("Unexpected Error")
        ), pytest.raises(Exception, match="Unexpected Error") as exc_info:
            self.tts.initialize_stream()

        assert str(exc_info.value) == "Unexpected Error"
        assert self.tts.stream is None

    @pytest.mark.skip()
    def test_resample_audio(self):
        """
        Test the resample_audio method of the TextToSpeech service
        """
        pass

    @pytest.mark.skip()
    def test_resample_audio_invalid_input(self):
        """
        Test the resample_audio method when invalid input is provided.
        """
        invalid_audio_data = "invalid_data"
        with pytest.raises(TypeError):
            self.tts.resample_audio(invalid_audio_data, 16000, 44100)

    @pytest.mark.unit()
    def test_synthesize(self):
        """
        Test the synthesize method of the TextToSpeech service
        """
        test_text = "Moi, minä olen Harri, miten menee?"
        with patch.object(self.tts.sentence_queue, "put") as mock_put:
            self.tts.synthesize(test_text)
            mock_put.assert_called_once_with(test_text)

    @pytest.mark.unit()
    def test_synthesize_with_empty_text(self):
        """
        Test the synthesize method when an empty string is passed.
        """
        with patch.object(self.tts.sentence_queue, "put") as mock_put:
            self.tts.synthesize("")
            mock_put.assert_called_once_with("")

    @pytest.mark.skip()
    def test_synthesize_text_stream_not_initialized(self):
        """
        Test the _synthesize_text method when the stream is not initialized.
        """
        self.tts.stream = None
        test_text = "Moi, minä olen Harri, miten menee?"
        with patch.object(self.tts.initialize_stream) as mock_initialize_stream, patch(
            "builtins.print"
        ) as mock_print:
            self.tts._synthesize_text(test_text)
            mock_print.assert_called_once_with("Audio stream is not available.")

    @pytest.mark.unit()
    def test_process_queue(self):
        """
        Test the _process_queue method of the TextToSpeech service
        """
        test_text = "Moi, minä olen Harri, miten menee?"
        self.tts.sentence_queue.put(test_text)

        with patch.object(
            self.tts, "_synthesize_text"
        ) as mock_synthesize_text, patch.object(
            self.tts._stop_event, "is_set", side_effect=[False, True]
        ):
            self.tts._process_queue()
            mock_synthesize_text.assert_called_once_with(test_text)

    @pytest.mark.unit()
    def test_process_queue_empty(self):
        """
        Test the _process_queue method of the TextToSpeech service when the queue is empty
        """
        with patch.object(
            self.tts, "_synthesize_text"
        ) as mock_synthesize_text, patch.object(
            self.tts.sentence_queue, "get", side_effect=queue.Empty
        ), patch.object(
            self.tts._stop_event, "is_set", side_effect=[False, True]
        ):
            self.tts._process_queue()

            mock_synthesize_text.assert_not_called()

    @pytest.mark.skip()
    def test_stop_cleans_up_resources(self):
        """
        Test the stop method to ensure it cleans up resources properly.
        """
        # Error: AttributeError: 'collections.deque' object attribute 'clear' is read-only
        with patch.object(self.tts._thread, "join") as mock_join, patch.object(
            self.tts._stop_event, "clear"
        ) as mock_clear, patch.object(
            self.tts.sentence_queue.queue, "clear"
        ) as mock_queue_clear, patch.object(
            self.tts.stream, "abort", create=True
        ) as mock_abort:
            self.tts.stop()

            mock_queue_clear.assert_called_once()
            mock_abort.assert_called_once()
            mock_join.assert_called_once()
            mock_clear.assert_called_once()
