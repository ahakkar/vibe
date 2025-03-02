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
    from backend.service1.src.cli import THEME

# Test case for the THEME
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


# Assuming the CommandLineService class is defined as follows
class CommandLineService:
    def create_env_file(self):
        """
        Create env file by setting default input and output device names
        """
        if not os.path.exists(ENV_PATH):
            with open(ENV_PATH, "w") as f:
                f.write("INPUT_DEVICE_NAME=None\n")
                f.write("OUTPUT_DEVICE_NAME=None\n")


# Test for the create_env_file method
def test_create_env_file_when_not_exists():
    # Ensure that the ENV_PATH doesn't exist before the test
    if os.path.exists(ENV_PATH):
        os.remove(ENV_PATH)

    # Create an instance of CommandLineService
    cls = CommandLineService()

    # Mock the open() function to simulate writing to a file
    with patch('builtins.open', mock_open()) as mock_file:
        with patch('os.path.exists', return_value=False):  # Mocking that the file doesn't exist
            cls.create_env_file()

            # Check that the file was created (open was called)
            mock_file.assert_called_once_with(ENV_PATH, 'w')

            # Check that the correct content was written to the file
            mock_file().write.assert_any_call("INPUT_DEVICE_NAME=None\n")
            mock_file().write.assert_any_call("OUTPUT_DEVICE_NAME=None\n")


def test_create_env_file_when_exists():
    # Make sure the ENV_PATH exists before the test
    with open(ENV_PATH, 'w') as f:
        f.write("INPUT_DEVICE_NAME=None\n")
        f.write("OUTPUT_DEVICE_NAME=None\n")

    # Create an instance of CommandLineService
    cls = CommandLineService()

    # Mock the open() function to simulate writing to a file
    with patch('builtins.open', mock_open()) as mock_file:
        with patch('os.path.exists', return_value=True):  # Mocking that the file exists
            cls.create_env_file()

            # Check that the open() method was not called since the file already exists
            mock_file.assert_not_called()

    # Clean up the test file after running the test
    os.remove(ENV_PATH)
