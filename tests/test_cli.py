import pytest
from unittest.mock import patch, MagicMock
import os

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

    assert isinstance(THEME, dict), f"Expected THEME to be a dictionary, but got {type(THEME)}"
    assert THEME == expected_theme, f"THEME does not match the expected value. Expected: {expected_theme}, but got: {THEME}"

@pytest.fixture
def cli():
    """
    Fixture for the CLI class.
    """
    cli_instance = CommandLineService()
    yield cli_instance

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

def test_run_all_services(cli):
    """
    Test the run_all_services method to ensure it calls run_keyboard_command with all_services=True.
    """
    with patch.object(cli, "run_keyboard_command") as mock_run_keyboard_command:
        cli.run_all_services()
        mock_run_keyboard_command.assert_called_once_with(all_services=True)