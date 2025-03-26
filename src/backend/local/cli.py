import os
import time
import signal
from dotenv import set_key
import pyfiglet
import local.constants


class CommandLineService:
    """
    Service for handling command-line interactions and application flow.
    """

    def __init__(self, app):
        """
        Initialize the command-line service and set up the signal handler for SIGINT.
        """
        from blessed import Terminal
        
        self.term = Terminal()
        self.app = app
        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, signal, frame):
        """
        Handle the SIGINT signal (Ctrl+C) to gracefully terminate the program.

        :param int signal: The signal number.
        :param frame: The current stack frame.
        """
        self.app.exit()

    def print_text(self, msg, color=None):
        print(self.term.center(msg))

    def display_neon_title(self):
        """
        Display the neon title for the application
        """
        app_ascii_title = pyfiglet.figlet_format(local.constants.APP_TITLE)
        title_flicker_colors = [
            self.term.red,
            self.term.magenta,
            self.term.blue,
            self.term.cyan,
            self.term.green,
            self.term.yellow,
        ]
        title_chars = [[char for char in line] for line in app_ascii_title.split("\n")]

        color_index = 0
        with self.term.fullscreen(), self.term.cbreak(), self.term.hidden_cursor():
            while True:
                self._print_title(title_chars, title_flicker_colors, color_index)
                if self.term.inkey(timeout=0.1):
                    break
                color_index += 1
                time.sleep(0.1)

    def display_settings_menu(self, ENV_PATH):
        """
        Display the settings menu for the user to choose input and output devices
        """
        print(self.term.clear)
        print(self.term.move_y(self.term.height // 2 - 5))
        print(self.term.center(self.term.bold_underline("Settings Menu")))
        print(self.term.move_down(2))

        input_device_name = self._select_device("input")
        output_device_name = self._select_device("output")

        set_key(ENV_PATH, "INPUT_DEVICE_NAME", input_device_name)
        set_key(ENV_PATH, "OUTPUT_DEVICE_NAME", output_device_name)
        os.chmod(ENV_PATH, 0o644)

        print(
            self.term.center(
                self.term.bold_green("Settings successfully saved to .env file!")
            )
        )
        time.sleep(1)

    def display_services(self):
        """
        Display the services available to the user.
        There are 4 services:
        1. All services (Speech to text, Language model, Text to speech)
        2. Only speech to text service
        3. Only language model service
        4. Only text to speech service
        """
        while True:
            print(self.term.clear)
            print(self.term.move_down(2))
            print(self.term("Available services:\n"))
            print(
                self.term(
                    "1: All services (Speech to text, Language model, Text to speech)"
                )
            )
            print(self.term("2: Only speech to text service"))
            print(self.term("3: Only language model service"))
            print(self.term("4: Only text to speech service"))

            command_input = input(
                self.term("Choose service (from 1 to 4) or exit:")
            ).strip()

            if command_input == "exit":
                self.app.exit()
            elif command_input == "1":
                self._toggle_recording(True)
            elif command_input == "2":
                self._toggle_recording()
            elif command_input == "3":
                inp = self._input_text("text generation")
                self.app.text_gen(inp)
            elif command_input == "4":
                inp = self._input_text("text to speech")
                self.app.text_to_speech()

    def _toggle_recording(self, all=False):
        """
        This function will run the keyboard command to start and stop recording or exit the program.

        :param all: bool, If True, the program will run all services
        """
        print(
            self.term.center(
                "Press F12 once to start and again to stop recording. Press 'Esc' to go back."
            )
        )

        with self.term.cbreak(), self.term.hidden_cursor():
            while True:
                key = self.term.inkey(timeout=1)
                if key.name == "KEY_ESCAPE":
                    self.app.exit()
                    return
                elif key.name == "KEY_F12":
                    self._flush_input_buffer()
                    self.app.toggle_recording(all)

                time.sleep(0.5)

    def _input_text(self, service_name: str) -> str:
        """
        Query text input from user
        """
        input_text = ""

        while True:
            input_text = input(
                self.term.center(
                    f"Write something for {service_name} service or 'back': "
                )
            ).strip()
            if input_text.lower() == "back":
                break

        return input_text

    def _flush_input_buffer(self):
        """
        Flush the input buffer to clear any queued key events to prevent spamming
        """
        while self.term.inkey(timeout=0.1):
            pass

    def _print_separator(self):
        """
        Print a terminal width separator line
        """
        print()
        print(self.term.center("-" * self.term.width))

    def _print_title(self, title_chars, colors, color_index):
        """
        Print the neon title with flickering colors
        """
        print(self.term.clear)
        print(self.term.move_y(self.term.height // 3))
        for line in title_chars:
            styled_line = "".join(
                colors[color_index % len(colors)](char) if char.strip() else char
                for char in line
            )
            print(self.term.center(styled_line))
        print(self.term.move_y(self.term.height - 3))
        print(self.term.center(self.term.bold_yellow("Press any key to continue...")))

    def _select_device(self, device_type):
        """
        Select the device name for input or output devices

        :param device_type: str, The device type (input or output)
        :return: str, The selected device name
        """
        devices = self.get_service("audio").query_devices()

        print(
            self.term.center(
                self.term.bold(f"Available {device_type.capitalize()} Devices:")
            )
        )
        # Print the available input/output devices
        for i, device in enumerate(devices):
            if (device_type == "input" and device["max_input_channels"] > 0) or (
                device_type == "output" and device["max_output_channels"] > 0
            ):
                print(self.term.center(self.term.cyan(f"{i}: {device['name']}")))
        print()

        while True:
            index = input(
                self.term.center(
                    self.term.bold_yellow(
                        f"Select {device_type.capitalize()} Device Index: "
                    )
                )
            ).strip()
            if index.isdigit() and int(index) in range(len(devices)):
                selected_device = devices[int(index)]
                # Check that the selected device of appropriate type
                if (
                    device_type == "input" and selected_device["max_input_channels"] > 0
                ) or (
                    device_type == "output"
                    and selected_device["max_output_channels"] > 0
                ):
                    return selected_device["name"]
                else:
                    print(
                        self.term.bold_red(
                            f"Selected device is not a valid {device_type} device."
                        )
                    )
            else:
                print(
                    self.term.bold_red(
                        "Invalid input. Please enter a valid device index."
                    )
                )
