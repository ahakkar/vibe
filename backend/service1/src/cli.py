import os
import time
import pyfiglet
import sounddevice as sd
from blessed import Terminal
from dotenv import load_dotenv, set_key
from text_generation import TextGenLlamaService
from TTS import TextToSpeech
from STT import AudioRecordingService, SpeechToTextService

# Define the theme
THEME = {
    "title": "bold underline",
    "menu": "bold",
    "option": "bold cyan",
    "input": "bold yellow",
    "error": "bold red",
    "success": "bold green",
}

# Determine the correct .env path based if running in Docker
if os.getenv("RUNNING_IN_DOCKER"):
    ENV_PATH = os.path.join("/usr/src/app", ".env")
else:
    ENV_PATH = os.path.join(os.path.dirname(__file__), ".env")


def create_env_file():
    f = open(ENV_PATH, 'w')
    # Initialize with default values if .env file does not exist
    f.write("INPUT_DEVICE_INDEX=0\n")
    f.write("OUTPUT_DEVICE_INDEX=0\n")
    f.close()

def display_neon_title(term):
    app_ascii_title = pyfiglet.figlet_format("Voice CLI")

    # Define colors for a neon effect
    title_flicker_colors = [term.red, term.magenta, term.blue, term.cyan, term.green, term.yellow]

    # Split the title into individual characters
    title_lines = app_ascii_title.split("\n")
    title_chars = [[char for char in line] for line in title_lines]

    color_index = 0

    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        while True:
            print(term.clear)
            print(term.move_y(term.height // 3))

            for line in title_chars:
                styled_line = ""
                for char in line:
                    if char.strip():  # Apply color effect only to non-space characters
                        styled_line += title_flicker_colors[color_index % len(title_flicker_colors)](char)
                    else:
                        styled_line += char
                print(term.center(styled_line))

            # Display the "Press any key to continue..." message
            print(term.move_y(term.height - 3))
            print(term.center(term.bold_yellow("Press any key to continue...")))

            # Check if a key has been pressed
            if term.inkey(timeout=0.1):
                break

            color_index += 1
            time.sleep(0.1)  # Adjust speed of color changing

def display_settings_menu(term):
    print(term.clear)
    print(term.move_y(term.height // 2 - 5))
    print(term.center(term.bold_underline("Settings Menu")))
    print(term.move_down(2))

    # List available input devices
    print(term.center(term.bold("Available Input Devices:")))
    input_devices = sd.query_devices()
    for i, device in enumerate(input_devices):
        if device['max_input_channels'] > 0:
            print(term.center(term.cyan(f"{i}: {device['name']}")))  
    print()

    # Prompt for input device
    print(term.center(term.bold_yellow("Select Input Device Index: ")), end="")
    input_device_index = input().strip()
    while not input_device_index.isdigit() or int(input_device_index) not in range(len(input_devices)):
        print(term.bold_red("Invalid input. Please enter a valid device index."))
        print(term.bold_yellow("Select Input Device Index: "), end="")
        input_device_index = input().strip()

    # List available output devices
    print(term.center(term.bold("Available Output Devices:")))
    output_devices = sd.query_devices()
    for i, device in enumerate(output_devices):
        if device['max_output_channels'] > 0:
            print(term.center(term.cyan(f"{i}: {device['name']}")))
    print()

    # Prompt for output device
    print(term.center(term.bold_yellow("Select Output Device Index: ")), end="")
    output_device_index = input().strip()
    while not output_device_index.isdigit() or int(output_device_index) not in range(len(output_devices)):
        print(term.bold_red("Invalid input. Please enter a valid device index."))
        print(term.bold_yellow("Select Output Device Index: "), end="")
        output_device_index = input().strip()

    # Save settings to .env file
    set_key(ENV_PATH, "INPUT_DEVICE_INDEX", input_device_index)
    set_key(ENV_PATH, "OUTPUT_DEVICE_INDEX", output_device_index)

    # Explicitly set the file permissions to ensure accessibility after set_key
    os.chmod(ENV_PATH, 0o644)

    print(term.center(term.bold_green("Settings successfully saved to .env file!")))

    time.sleep(1) # Pause for a second before continuing

def run_cli():
    term = Terminal()

    # Check if .env file exists
    if not os.path.exists(ENV_PATH):
        print(term.center(term.bold_red("No .env file found. Opening settings menu...")))
        time.sleep(1)
        create_env_file()
        display_settings_menu(term)

    # Display loading message
    print(term.clear)
    print(term.move_y(term.height // 2))
    print(term.center(term.bold("Loading application...")))

    # Load environment variables again after potentially creating .env
    load_dotenv(ENV_PATH)

    input_device_index = int(os.getenv("INPUT_DEVICE_INDEX"))
    output_device_index = int(os.getenv("OUTPUT_DEVICE_INDEX"))

    textGenLlamaService = TextGenLlamaService()
    audio_service = AudioRecordingService(device_index=input_device_index)
    stt_service = SpeechToTextService()
    textToSpeech = TextToSpeech(device_index=output_device_index)

    display_neon_title(term)

    print(term.move_down(2))
    print(term.center("Press F12 once to start and again to stop recording. Press 'Esc' to exit."))

    with term.cbreak(), term.hidden_cursor():
        while True:
            key = term.inkey(timeout=1)

            # Check if the user wants to exit
            if key.name == "KEY_ESCAPE":
                print(term.center(term.bold_red("Exiting the program.")))
                audio_service.terminate_audio()
                break

            elif key.name == "KEY_F12":
                if audio_service.recording:
                    audio_data = audio_service.stop_recording()
                    if audio_data is not None:
                        recorded_text = stt_service.process_audio(audio_data)
                        print(term.center(term.bold_green(f"Recorded Text: {recorded_text}")))
                        llm_output = textGenLlamaService.text_generate(recorded_text)
                        print(term.center(term.bold_green(llm_output)))
                        textToSpeech.synthesize(llm_output)
                    else:
                        print(term.center(term.bold_red("No audio data recorded.")))
                else:
                    audio_service.start_recording()

            time.sleep(0.5)  # Adjust the sleep time as needed