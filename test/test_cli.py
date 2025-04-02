import pytest
import signal
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
        self.cli_instance.term = MagicMock()
        self.cli_instance.term.width = 50

    def teardown_method(self):
        self.cli_instance.term = None
        self.cli_instance = None
        self.app = None


    @pytest.mark.unit()
    def test_cli_init(self):
        """
        Test CLI initialization.
        """
        assert self.cli_instance is not None
        assert self.cli_instance.term is not None
        assert self.cli_instance.term.width == 50
        assert self.cli_instance.app is not None

    @pytest.mark.skip()
    @pytest.mark.unit()
    def test_cli_signal_handler(self):
        """
        Test that the SIGINT signal handler is set correctly.
        """
        with patch("signal.signal") as mock_signal:
            CommandLineService(self.app)
            mock_signal.assert_called_once_with(signal.SIGINT, self.cli_instance._signal_handler)
    
    @pytest.mark.unit()
    def test_print_text(self):
        """
        Test case for constants used in the CLI.
        """
        with patch("builtins.print") as mock_print:
            self.cli_instance.print_text("test",None ,False)
            mock_print.assert_called_once_with("test", end="")
        with patch("builtins.print") as mock_print, \
             patch("term.ljust", return_value="test") as mock_ljust:
            self.cli_instance.print_text("test",None ,True)
            mock_print.assert_called_once_with("test")

    @pytest.mark.unit()
    def test_display_neon_title(self):
        """
        Test case for CLI displaying the neon title.
        """
        pass

    @pytest.mark.unit()
    def test_display_settings_menu(self):
        """
        Test case for CLI displaying the settings menu.
        """
        pass

    @pytest.mark.unit()
    def test_display_cli(self):
        """
        Test case for CLI setting up the environment file.
        """
        pass

    @pytest.mark.unit()
    def test_toggle_recording(self):
        """
        Test case for CLI setting up the environment file.
        """
        pass
    
    @pytest.mark.unit()
    def test_input_from_user(self):
        """
        Test case for CLI input from user.
        """
        with patch.object(self.cli_instance.term, "input") as mock_input:
            mock_input.return_value = "test input"
            result = self.cli_instance._input_from_user()
            assert result == "test input"

    @pytest.mark.skip()
    @pytest.mark.unit()
    def test_flush_input_buffer(self):
        """
        Test case for CLI flushing the input buffer.
        """
        with patch.object(self.cli_instance.term, "flush") as mock_flush:
            self.cli_instance._flush_input_buffer()
            mock_flush.assert_called_once()

    @pytest.mark.unit()
    def test_print_separator(self):
        """
        Test case for CLI printing a separator.
        """
        with patch("builtins.print") as mock_print:
            self.cli_instance.print_separator()
            mock_print.assert_called_once_with("-" * 50)

    @pytest.mark.unit()
    def test_print_title(self):
        """
        Test case for CLI printing a title.
        """
        pass

    @pytest.mark.unit()
    def test_print_devices(self):
        pass
    
    @pytest.mark.unit()
    def test_select_devices(self):
        pass

    @pytest.mark.skip()
    @pytest.mark.unit()
    def test_run_keyboard_command(self):
        mock_f12 = MagicMock()
        mock_f12.name = "KEY_F12"

        mock_esc = MagicMock()
        mock_esc.name = "KEY_ESCAPE"

        with patch.object(
            self.cli_instance.term, "inkey", side_effect=[mock_f12, mock_esc]
        ), patch.object(
            self.cli_instance, "_flush_input_buffer"
        ) as mock_flush, patch.object(
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