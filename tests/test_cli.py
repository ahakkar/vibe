import pytest
from unittest.mock import patch, MagicMock, mock_open
import os


ENV_PATH = 'test.env'

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
    from backend.service1.src.cli import THEME, ENV_PATH, CommandLineService, APP_TITLE

def test_theme():
    expected_theme = {
        "title": "bold underline",
        "menu": "bold",
        "option": "bold cyan",
        "input": "bold yellow",
        "error": "bold red",
        "success": "bold green",
    }

    assert THEME == expected_theme, f"THEME does not match the expected value. Expected: {expected_theme}, but got: {THEME}"

    for key, value in expected_theme.items():
        assert key in THEME, f"Key '{key}' is missing in THEME"
        assert THEME[key] == value, f"Value for key '{key}' is incorrect. Expected: '{value}', got: '{THEME[key]}'"


class CommandLineService:
    def create_env_file(self):
        """
        Create env file by setting default input and output device names
        """
        if not os.path.exists(ENV_PATH):
            with open(ENV_PATH, "w") as f:
                f.write("INPUT_DEVICE_NAME=None\n")
                f.write("OUTPUT_DEVICE_NAME=None\n")


def test_create_env_file_when_not_exists():
    if os.path.exists(ENV_PATH):
        os.remove(ENV_PATH)

    cls = CommandLineService()

    with patch('builtins.open', mock_open()) as mock_file:
        with patch('os.path.exists', return_value=False): 
            cls.create_env_file()

            mock_file.assert_called_once_with(ENV_PATH, 'w')

            mock_file().write.assert_any_call("INPUT_DEVICE_NAME=None\n")
            mock_file().write.assert_any_call("OUTPUT_DEVICE_NAME=None\n")


def test_create_env_file_when_exists():
    with open(ENV_PATH, 'w') as f:
        f.write("INPUT_DEVICE_NAME=None\n")
        f.write("OUTPUT_DEVICE_NAME=None\n")

    cls = CommandLineService()

    with patch('builtins.open', mock_open()) as mock_file:
        with patch('os.path.exists', return_value=True): 
            cls.create_env_file()

            mock_file.assert_not_called()

    os.remove(ENV_PATH)

@pytest.fixture
def test_display_neon_title():
    with patch('pyfiglet.figlet_format', return_value="Mocked ASCII Title") as mock_figlet:
        
        app = CommandLineService()

        app.term.red = MagicMock()
        app.term.magenta = MagicMock()
        app.term.blue = MagicMock()
        app.term.cyan = MagicMock()
        app.term.green = MagicMock()
        app.term.yellow = MagicMock()
        app.term.fullscreen = MagicMock()
        app.term.cbreak = MagicMock()
        app.term.hidden_cursor = MagicMock()
        app.term.inkey = MagicMock(return_value=None)
        
        app.display_neon_title()

        mock_figlet.assert_called_once_with("Your App Title")  
        
        app.term.fullscreen.assert_called_once()
        app.term.cbreak.assert_called_once()
        app.term.hidden_cursor.assert_called_once()
