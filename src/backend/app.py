import argparse
import os
import sys
import abstract_classes
import local.constants
import traceback


from dotenv import load_dotenv
from local.cli import CommandLineService
from local.ir_service import IrService
from local.text_gen import TextGenService
from local.tts import TextToSpeech
from local.audio import AudioService
from local.stt import SpeechToTextService
from local.weather import Weather
from local.yle import YleNewsApi
from pathlib import Path



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
        self.synthesize = False

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
        print("loaded services OK!")
        self._run()

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
                    intent = self.services("ir").recognize_intent(audio_text)
                    
                    # Intent is recognized, handle it
                    if intent != None:
                        intent_response = self.services("ir").process_intent(intent)
                        self.services["tts"].synthesize(intent_response)
                    # If no intent is recognized, pass user prompt to LLM
                    else:   
                        llm_text = self.services["llm"].generate(audio_text)
                        self.services["tts"].synthesize(llm_text)
                    
            else:
                self.services["cli"].print_text("No audio recorded.")

        else:
            self.services["audio"].start_recording()

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
                #self.services["cli"].display_neon_title()
                self.services["cli"].display_cli()
                self.exit()
            except Exception as e:
                print(f"Error while running CLI service: {e}")
                traceback.print_exc()
                self.exit()

        # Could run as a background if we had voice activation detection

        # Could perhaps run the web server here too

    def speech_to_text(self, audio) -> str:
        """
        Run the speech to text service
        """

        return self.services["stt"].transcribe(audio)

    def text_to_speech(self, input_text):
        """
        Run the text to speech service
        """

        self.services["tts"].synthesize(input_text)
        
    def intent_recognition(self, input_text):
        """
        Run the intent recognition service
        """

        intent = self.services["ir"].recognize_intent(input_text)
        if intent == None:
            self.services["cli"].print_text("Intenttiä ei havaittu\n", None, False)
        else:
            self.services["cli"].print_text(f"{intent.intent.name}\n", None, False)
            

    def text_gen(self, input_text):
        """
        The language model generates text based on user's input text
        Print the language model's generated text

        :param input_text: str, The user's input text
        :param synthesize: bool, If True, synthesize the generated text
        """
        llm_output = self.services["text_gen"].generate(input_text)
        sentence = "LLM: "

        for token in llm_output:
            text = token["choices"][0]["delta"].get("content", "")
            sentence += text

            # Check if the sentence is complete
            if self.synthesize and (
                any(punc in sentence for punc in local.constants.PUNCTATIONS)
            ):
                self.services["tts"].synthesize(sentence)
                sentence = ""

            self.services["cli"].print_text(text, None, False)

        self.services["cli"].print_separator()
        
        return

    def _load_services(self):
        """
        This function loads all the services based on the chosen input and output devices
        """

        try:
            self.services["audio"] = AudioService(self)
        except Exception as e:
            print(f"Failed to load audio service: {e}")
            traceback.print_exc()

        try:
            self.services["stt"] = SpeechToTextService(self.root)
        except Exception as e:
            print(f"Failed to load stt service: {e}")
            traceback.print_exc()

        try:
            self.services["tts"] = TextToSpeech(
                self, device_index=self.services["audio"].output_device_index
            )
        except Exception as e:
            print(f"Failed to load tts service: {e}")
            traceback.print_exc()

        try:
            self.services["text_gen"] = TextGenService(self.root)
        except Exception as e:
            print(f"Failed to text gen service: {e}")
            traceback.print_exc()

        try:
            self.services["ir"] = IrService(self)
        except Exception as e:
            print(f"Failed to load ir service: {e}")
            traceback.print_exc()
            
        try:
            self.services["weather"] = Weather()
        except Exception as e:
            print(f"Failed to load weather service: {e}")
            traceback.print_exc()
            
        try:
            self.services["news"] = YleNewsApi()
        except Exception as e:
            print(f"Failed to load yle news service: {e}")
            traceback.print_exc()

    def get_env(self, key):
        """Retrieve an environment variable by its key."""
        return self.env_vars.get(key)

    def _setup_env(self):
        """
        Set up env file if it doesn't exist, the user can choose input and output devices.
        """

        if not os.path.exists(self.ENV_PATH):
            self._create_env_file()

        print(f"env path: {self.ENV_PATH}")
        print(f"loading env, result: {load_dotenv(self.ENV_PATH)}")
        self.env_vars = dict(os.environ)

    def _create_env_file(self):
        """
        Create env file by setting default input and output device names
        """

        try:
            with open(self.ENV_PATH, "w") as f:
                f.write("INPUT_DEVICE_NAME=None\n")
                f.write("OUTPUT_DEVICE_NAME=None\n")
                f.write('LLM_MODEL="Gemma2:2b_unsloth.Q4_K_M.gguf"\n')
                f.write('TTS_MODEL="fi_FI-harri-medium.onnx"\n')
                f.write('MODEL_FOLDER="models"\n')
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
