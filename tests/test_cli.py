import pytest
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
    from backend.service1.src.cli import CommandLineService, THEME


def test_theme():
    """
    Test if THEME dictionary contains the expected values.
    """
    expected_theme = {
        "title": "bold underline",
        "menu": "bold",
        "option": "bold cyan",
        "input": "bold yellow",
        "error": "bold red",
        "success": "bold green",
    }

    assert isinstance(
        THEME, dict
    ), f"Expected THEME to be a dictionary, but got {type(THEME)}"
    assert (
        THEME == expected_theme
    ), f"THEME does not match the expected value. Expected: {expected_theme}, but got: {THEME}"


@pytest.fixture
def cli():
    """
    Fixture for the CLI class.
    """
    cli_instance = CommandLineService()
    cli_instance.text_gen_service = MagicMock()
    cli_instance.textToSpeech = MagicMock()
    cli_instance.term = MagicMock()
    yield cli_instance


@pytest.mark.unit()
def test_cli_init(cli):
    """
    Test CLI initialization.
    """
    assert cli is not None


@pytest.mark.skip()
def test_play_audio_success(cli):
    """
    Test the play_audio method when playing audio successfully.
    """
    with patch.object(sd, "play") as mock_play:
        cli.play_audio(b"\x00\x01\x02\x03", samplerate=44100)
        mock_play.assert_called_once_with(b"\x00\x01\x02\x03", samplerate=44100)


@pytest.mark.skip()
def test_play_audio_failure(cli):
    """
    Test the play_audio method when an error occurs.
    """
    with patch.object(sd, "play", side_effect=sd.PortAudioError("Playback Error")):
        with pytest.raises(sd.PortAudioError):
            cli.play_audio(b"\x00\x01\x02\x03", samplerate=44100)


@pytest.mark.unit()
def test_run_all_services(cli):
    """
    Test the run_all_services method to ensure it calls run_keyboard_command with all_services=True.
    """
    with patch.object(cli, "run_keyboard_command") as mock_run_keyboard_command:
        cli.run_all_services()
        mock_run_keyboard_command.assert_called_once_with(all_services=True)


@pytest.mark.unit()
def test_llm_text_generate(cli):
    """
    Test the llm_text_generate method to ensure it generates text and optionally synthesizes it.
    """
    input_text = "Hello, world!"
    mock_llm_output = [{"choices": [{"delta": {"content": "Hello, world!"}}]}]

    with patch.object(
        cli.text_gen_service, "chat_generate", return_value=mock_llm_output
    ):
        with patch.object(cli.textToSpeech, "synthesize") as mock_synthesize:
            with patch.object(cli.term, "inkey", side_effect=[None] * 10):
                cli.llm_text_generate(input_text, synthesize=True)
                mock_synthesize.assert_called_with("Hello, world!")


@pytest.mark.unit()
def test_run_keyboard_command(cli):

    mock_f12 = MagicMock()
    mock_f12.name = "KEY_F12"

    mock_esc = MagicMock()
    mock_esc.name = "KEY_ESCAPE"

    with patch.object(
        cli.term, "inkey", side_effect=[mock_f12, mock_esc]
    ), patch.object(cli, "_flush_input_buffer") as mock_flush, patch.object(
        cli, "_toggle_recording"
    ) as mock_toggle, patch.object(
        cli, "exit"
    ) as mock_exit, patch(
        "time.sleep", return_value=None
    ):
        cli.run_keyboard_command()

        mock_flush.assert_called_once()
        mock_toggle.assert_called_once_with(False)

        mock_exit.assert_called_once()
