import argparse
import os
import sys
import abstract_classes
import local.constants
from pathlib import Path
from local.cli import CommandLineService
from local.ir_service import IrService
from local.text_gen import TextGenService
from local.tts import TextToSpeech
from local.audio import AudioService
from local.stt import SpeechToTextService
from dotenv import load_dotenv


class AppManager:
    def __init__(self):
        desc = [
            "App runs by default on background. Enable web server with --web",
            "And command line interface with --cli argument",
        ]

        # https://docs.python.org/3/library/argparse.html
        parser = argparse.ArgumentParser(prog="SLT-VIBE", usage="\n".join(desc))
        parser.add_argument("--cli", action="store_true", help="Enable CLI")
        parser.add_argument("--web", action="store_true", help="Enable Web server")
        self.args = parser.parse_args()

        self.root = self._find_project_root()

        # Determine the correct .env path based if running in Docker
        if os.getenv("RUNNING_IN_DOCKER"):
            self.ENV_PATH = os.path.join("/usr/src/app", ".env")
        else:
            self.ENV_PATH = self.root / ".env"

        self.services = {
            "stt": None,
            "tts": None,
            "text_gen": None,
            "ir": None,
            "audio": None,
            "cli": None,
        }

        self._setup_env()
        self._load_services()
        self._run()

    def get_service(self, service_name: str):
        return self.services.get(service_name)

    def exit(self):
        """
        Exit the program
        """
        if self.services["cli"]:
            self.services["cli"].print_text("Exiting the program.")
        self.services["audio"].terminate_audio()
        self.services["tts"].stop()
        sys.exit(0)

    def _run(self):
        """
        Starts the app
        """

        if self.args.cli:
            try:
                self.services["cli"] = CommandLineService(self)
                self.services["cli"].display_neon_title()
                self.services["cli"].display_services()
            except Exception as e:
                print(f"Failed to load cli service: {e}")

        # Could run as a background if we had voice activation detection

        # Could perhaps run the web server here too

    def toggle_recording(self, all):
        """
        Toggle recording state and process audio if recording is stopped.

        :param all_services: bool, If True, the program will run all services
        """
        if not self.services["audio"].recording:
            result = self.services["audio"].stop_and_process_recording()
            if result:
                if all:
                    audio_text = self.services("stt").transcribe(result)
                    # TODO call IR here first

                    # Then process it and pass to LLM
                    llm_text = self.services["llm"].generate(audio_text)
                    pass
            else:
                self.services["cli"].print_text("No audio recorded.")

        else:
            self.services["audio"].start_recording()

    def speech_to_text(self, audio) -> str:
        """
        Run the speech to text service
        """

        return self.services["stt"].transcribe(audio)

    def text_to_speech(self, text):
        """
        Run the text to speech service
        """

        self.services["tts"].synthesize(text)

    def text_gen(self, input_text, synthesize=False):
        """
        The language model generates text based on user's input text
        Print the language model's generated text

        :param input_text: str, The user's input text
        :param synthesize: bool, If True, synthesize the generated text
        """
        llm_output = self.services["llm"].generate(input_text)
        sentence = ""

        for token in llm_output:
            text = token["choices"][0]["delta"].get("content", "")
            sentence += text

            # Check if the sentence is complete
            if synthesize and (
                any(punc in sentence for punc in local.constants.PUNCTATIONS)
            ):
                self.services["tts"].synthesize(sentence)
                sentence = ""

            self.services["cli"].print_text(text)

        return

    def _load_services(self):
        """
        This function loads all the services based on the chosen input and output devices
        """

        try:
            self.services["audio"] = AudioService()
        except Exception as e:
            print(f"Failed to load audio service: {e}")

        if self.args.cli:
            if os.getenv("STT_ENABLED"):
                try:
                    self.services["stt"] = SpeechToTextService(self.root)
                except Exception as e:
                    print(f"Failed to load STT service: {e}")

            elif os.getenv("TTS_ENABLED"):
                print("Loading TTS")
                self.services["tts"] = TextToSpeech(
                    device_index=self.output_device_index
                )

            elif os.getenv("LLM_ENABLED"):
                print("Loading Text Gen")
                self.services["text_gen"] = TextGenService()

            elif os.getenv("IR_ENABLED"):
                print("Loading IR")
                self.services["ir"] = IrService()

        else:
            self.services["stt"] = SpeechToTextService(self.root)
            self.services["tts"] = TextToSpeech(device_index=self.output_device_index)
            self.services["text_gen"] = TextGenService()
            self.services["ir"] = IrService()

    def _setup_env(self):
        """
        Set up env file if it doesn't exist, the user can choose input and output devices.
        """

        if not os.path.exists(self.ENV_PATH):
            self._create_env_file()

        load_dotenv(self.ENV_PATH)

    def _create_env_file(self):
        """
        Create env file by setting default input and output device names
        """

        try:
            with open(self.ENV_PATH, "w") as f:
                f.write("INPUT_DEVICE_NAME=None\n")
                f.write("OUTPUT_DEVICE_NAME=None\n")
                f.write("STT_ENABLED=False\n")
                f.write("TTS_ENABLED=False\n")
                f.write("LLM_ENABLED=False\n")
                f.write('LLM_MODEL="google_gemma-3-1b-it-Q4_0.gguf"\n')
                f.write('MODEL_PATH="models"\n')
                f.write('ONNX_MODEL="wav2vec2_model.onnx"\n')
                f.write('PROCESSOR="wav2vec2_processor"\n')
                f.write('OUTPUT_FILENAME="recorded_audio.wav"\n')

        except IOError as e:
            print(f"Error writing to .env file ({self.ENV_PATH}): {e}")
        except OSError as e:
            print(f"OS Error writing to .env file ({self.ENV_PATH}): {e}")
        except Exception as e:
            print(f"An unexpected error occurred while writing to .env: {e}")

    def _find_project_root(self) -> Path:
        current_path = Path(__file__).resolve()

        while True:
            if (current_path / "README.md").exists():
                return current_path
            elif current_path == "/":
                return None
            else:
                current_path = current_path.parent


if __name__ == "__main__":
    app = AppManager()
    app.run()
