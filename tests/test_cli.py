import pytest
from unittest.mock import patch, MagicMock

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
