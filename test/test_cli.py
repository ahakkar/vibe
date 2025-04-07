import pytest
from unittest.mock import patch, MagicMock
import time


with patch.dict(
    "sys.modules",
    {
        "blessed": MagicMock(),
        # "pyfiglet": MagicMock(),
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
    from src.backend.local.cli import CommandLineService


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

    @pytest.mark.unit()
    def test_print_text(self):
        """
        Test case for constants used in the CLI.
        """
        with patch("builtins.print") as mock_print:
            self.cli_instance.print_text("test", None, False)

            mock_print.assert_called_once_with("test", end="")

        with patch("builtins.print") as mock_print, patch.object(
            self.cli_instance.term, "ljust", return_value="test"
        ):
            self.cli_instance.print_text("test", None, True)

            mock_print.assert_called_once_with("test")

    @pytest.mark.unit()
    def test_display_neon_title(self):
        """
        Test case for CLI displaying the neon title.
        """
        self.cli_instance._print_title = MagicMock()
        with patch("pyfiglet.figlet_format", return_value="test"), patch.object(
            self.cli_instance.term, "inkey", side_effect=[True, False]
        ):
            self.cli_instance.display_neon_title()

            self.cli_instance.term.inkey.assert_called_once()
            self.cli_instance._print_title.assert_called_once()

    @pytest.mark.skip()  # Something wrong with the mock
    @pytest.mark.unit()
    def test_display_settings_menu_success(self):
        """
        Test case for successfully displaying the settings menu and saving settings.
        """
        self.cli_instance._select_device = MagicMock(
            side_effect=["InputDevice", "OutputDevice"]
        )
        mock_set_key = MagicMock()

        with patch("os.path.join", return_value="/mock/path/.env"), patch(
            "dotenv.set_key"
        ) as mock_set_key, patch("time.sleep", return_value=None):
            self.cli_instance.display_settings_menu()

            self.cli_instance._select_device.assert_any_call("input")
            self.cli_instance._select_device.assert_any_call("output")
            mock_set_key.assert_any_call(
                "/mock/path/.env", "INPUT_DEVICE_NAME", "InputDevice"
            )
            mock_set_key.assert_any_call(
                "/mock/path/.env", "OUTPUT_DEVICE_NAME", "OutputDevice"
            )

    @pytest.mark.unit()
    def test_display_settings_menu_no_devices(self):
        """
        Test case for displaying the settings menu when no devices are detected.
        """
        self.cli_instance._select_device = MagicMock(side_effect=[None, None])
        mock_logger_error = MagicMock()

        with patch.object(self.cli_instance.logger, "error", mock_logger_error), patch(
            "time.sleep", return_value=None
        ), patch("builtins.print") as mock_print:
            self.cli_instance.display_settings_menu()

            self.cli_instance._select_device.assert_any_call("input")
            self.cli_instance._select_device.assert_any_call("output")
            mock_logger_error.assert_called_once_with("No audio devices detected")
            mock_print.assert_any_call(
                self.cli_instance.term.ljust(
                    self.cli_instance.term.bold("No audio devices detected.")
                )
            )

    @pytest.mark.unit()
    @pytest.mark.parametrize(
        "selection, function, parameter",
        [
            ("0", "display_settings_menu", None),
            ("1", "_toggle_recording", True),
            ("2", "_toggle_recording", None),
            ("3", "_input_text_gen", None),
            ("4", "_input_tts", None),
            ("5", "_input_ir", None),
        ],
    )
    def test_display_cli(self, selection, function, parameter):
        """
        Test case for CLI quitting the application.
        """
        self.cli_instance.testing = True
        with patch("builtins.input", side_effect=[selection, "q"]), patch.object(
            self.cli_instance, function
        ) as mock_function:
            self.cli_instance.display_cli()
            if parameter is not None:
                mock_function.assert_called_once_with(parameter)
            else:
                mock_function.assert_called_once()
        self.cli_instance.testing = False

    @pytest.mark.unit()
    @pytest.mark.parametrize("all_services", [True, False])
    def test_toggle_recording(self, all_services):
        """
        Test case for CLI toggling recording functionality.
        """
        mock_f12 = MagicMock()
        mock_f12.name = "KEY_F12"

        mock_esc = MagicMock()
        mock_esc.name = "KEY_ESCAPE"

        with patch.object(
            self.cli_instance.term, "inkey", side_effect=[mock_f12, mock_esc]
        ), patch.object(
            self.cli_instance, "_flush_input_buffer"
        ) as mock_flush, patch.object(
            self.app, "toggle_recording"
        ) as mock_toggle_recording, patch.object(
            time, "sleep"
        ), patch.object(
            self.app, "exit"
        ) as mock_exit, patch(
            "builtins.print"
        ):
            self.cli_instance._toggle_recording(all_services)

            mock_flush.assert_called_once()
            mock_toggle_recording.assert_called_once_with(all_services)
            mock_exit.assert_called_once()

    @pytest.mark.unit()
    @pytest.mark.parametrize(
        "prompt, called",
        [
            ("test", True),
            ("b", False),
            ("back", False),
        ],
    )
    def test_input_from_user(self, prompt, called):
        """
        Test case for CLI input from user.
        """
        self.cli_instance.testing = True
        service_method = MagicMock()
        with patch("builtins.input", return_value=prompt.lower()):
            self.cli_instance._input_from_user(prompt, service_method)

            if called:
                service_method.assert_called_once_with("test")
            else:
                service_method.assert_not_called()
        self.cli_instance.testing = False

    @pytest.mark.skip()
    @pytest.mark.unit()
    def test_flush_input_buffer(self):
        """
        Test case for CLI flushing the input buffer.
        """
        with patch.object(self.cli_instance.term, "flush") as mock_flush:
            self.cli_instance._flush_input_buffer()
            mock_flush.assert_called_once()

    @pytest.mark.skip()
    @pytest.mark.unit()
    def test_print_separator(self):
        """
        Test case for CLI printing a separator.
        """
        with patch("builtins.print") as mock_print:
            self.cli_instance.print_separator()
            mock_print.assert_called_once_with("-" * 50)

    @pytest.mark.skip()
    @pytest.mark.unit()
    def test_print_title(self):
        """
        Test case for CLI printing a title.
        """
        pass

    @pytest.mark.skip()
    @pytest.mark.unit()
    def test_print_devices(self):
        pass

    @pytest.mark.skip()
    @pytest.mark.unit()
    def test_select_devices(self):
        pass
