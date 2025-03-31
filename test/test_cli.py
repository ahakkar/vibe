import pytest
import sounddevice as sd
from unittest.mock import patch, MagicMock
import os
import time


with patch.dict(
    "sys.modules",
    {
        "pyfiglet": MagicMock(),
        "blessed": MagicMock(),
        "dotenv": MagicMock(),
        "sounddevice": MagicMock(),
        "numpy": MagicMock(),
        "scipy": MagicMock(),
        "matplotlib": MagicMock(),
        "pandas": MagicMock(),
        "sklearn": MagicMock(),
        "joblib": MagicMock(),
        "text_gen": MagicMock(),
        "tts": MagicMock(),
        "stt": MagicMock(),
    },
):
    from cli import CommandLineService


class TestCommandLineService:

    def setup_method(self):
        self.app = MagicMock()
        self.cli_instance = CommandLineService(self.app)
        self.cli_instance.text_gen_service = MagicMock()
        self.cli_instance.textToSpeech = MagicMock()
        self.cli_instance.term = MagicMock()

    @pytest.mark.unit()
    def test_cli_init(self):
        """
        Test CLI initialization.
        """
        assert self.cli_instance is not None


    @pytest.mark.skip()
    def test_play_audio_success(self):
        """
        Test the play_audio method when playing audio successfully.
        """
        with patch.object(sd, "play") as mock_play:
            self.cli_instance.play_audio(b"\x00\x01\x02\x03", samplerate=44100)
            mock_play.assert_called_once_with(b"\x00\x01\x02\x03", samplerate=44100)


    @pytest.mark.skip()
    def test_play_audio_failure(self):
        """
        Test the play_audio method when an error occurs.
        """
        with patch.object(sd, "play", side_effect=sd.PortAudioError("Playback Error")):
            with pytest.raises(sd.PortAudioError):
                self.cli_instance.play_audio(b"\x00\x01\x02\x03", samplerate=44100)


    @pytest.mark.unit()
    def test_run_all_services(self):
        """
        Test the run_all_services method to ensure it calls run_keyboard_command with all_services=True.
        """
        with patch.object(self.cli_instance, "run_keyboard_command") as mock_run_keyboard_command:
            self.cli_instance.run_all_services()
            mock_run_keyboard_command.assert_called_once_with(all_services=True)


    @pytest.mark.unit()
    def test_llm_text_generate(self):
        """
        Test the llm_text_generate method to ensure it generates text and optionally synthesizes it.
        """
        input_text = "Hello, world!"
        mock_llm_output = [{"choices": [{"delta": {"content": "Hello, world!"}}]}]

        with patch.object(
            self.cli_instance.text_gen_service, "chat_generate", return_value=mock_llm_output
        ):
            with patch.object(self.cli_instance.textToSpeech, "synthesize") as mock_synthesize:
                with patch.object(self.cli_instance.term, "inkey", side_effect=[None] * 10):
                    self.cli_instance.llm_text_generate(input_text, synthesize=True)
                    mock_synthesize.assert_called_with("Hello, world!")


    def run_text_to_speech_service(self):
        """
        Test the text_to_speech
        """
        input_text = input("Enter text: ")
        print(f"[DEBUG] Input received: {input_text}")
        self.llm_text_generate(input_text, synthesize=True)
        print("[DEBUG] Called llm_text_generate successfully")


    @pytest.mark.unit()
    def test_run_keyboard_command(self):
        mock_f12 = MagicMock()
        mock_f12.name = "KEY_F12"

        mock_esc = MagicMock()
        mock_esc.name = "KEY_ESCAPE"

        with patch.object(
            self.cli_instance.term, "inkey", side_effect=[mock_f12, mock_esc]
        ), patch.object(self.cli_instance, "_flush_input_buffer") as mock_flush, patch.object(
            self.cli_instance, "_toggle_recording"
        ) as mock_toggle, patch.object(
            self.cli_instance, "exit"
        ) as mock_exit, patch(
            "time.sleep", return_value=None
        ):
            self.cli_instance.run_keyboard_command()

            mock_flush.assert_called_once()
            mock_toggle.assert_called_once_with(False)

            mock_exit.assert_called_once()
