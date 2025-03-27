import argparse
import os
import sys
import shutil
import abstract_classes
import local.constants
import traceback

from local.constants import Srv
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

        # Determine the correct .env path based if running in Docker
        if os.getenv("RUNNING_IN_DOCKER"):
            self.ENV_PATH = os.path.join("/usr/src/app", ".env")
        else:
            self.ENV_PATH = self.root / ".env"

        self.services = {
            Srv.STT: None,
            Srv.TTS: None,
            Srv.TEXT_GEN: None,
            Srv.IR: None,
            Srv.AUDIO: None,
            Srv.CLI: None,
            Srv.WEATHER: None,
            Srv.NEWS: None,
        }

        self._setup_env()
        self._load_services()
        self._run()

    def toggle_recording(self, all):
        """
        Toggle recording state and process audio if recording is stopped.
        
        This function looks to be a bit to complex and could be refactored/
        broken down to smaller functions.

        :param all_services: bool, If True, the program will run all services
        """
        if not self.services[Srv.AUDIO].is_recording:
            result = self.services[Srv.AUDIO].stop_and_process_recording()
            if result and all:
                self._process_recording(result)
            elif self.args.cli:                
                self.services[Srv.CLI].print_text("No audio recorded.")

        else:
            self.services[Srv.AUDIO].start_recording()
            
    def _process_recording(self, recording):
        """
        Transcribe audio with STT, detect intent, provide response based on
        intent or if no intent was detected, provide an answer with text gen.
        
        :param recording - NDArray[floating[Any]]
        """
         
        audio_text = self.services[Srv.STT].transcribe(recording)            
        intent = self.services[Srv.IR].recognize_intent(audio_text)

        # Intent is recognized, handle it
        if intent != None:
            intent_response = self.services[Srv.IR].process_intent(intent)
            if self.args.cli:
                self.services[Srv.CLI].print_text(intent_response)
            self.services[Srv.TTS].synthesize(intent_response)
        # If no intent is recognized, pass user prompt to LLM
        else:
            llm_text = self.services[Srv.TEXT_GEN].generate(audio_text)
            self.services[Srv.TTS].synthesize(llm_text)

    def get_service(self, service_name: Srv):
        """
        Get an already initialized service with enum so other sections of app
        can utilize the service.
        
        :param service_name Srv enum from constants.py
        """
        return self.services.get(service_name)

    def exit(self):
        """
        Exit the program gracefully with cleanup
        """
        if self.services[Srv.CLI]:
            self.services[Srv.CLI].print_text("Exiting the program.")
        self.services[Srv.AUDIO].terminate_audio()
        self.services[Srv.TTS].stop()
        sys.exit(0)

    def _run(self):
        """
        Starts the app
        """

        if self.args.cli:
            try:
                self.services[Srv.CLI] = CommandLineService(self)
                # self.services[Srv.CLI].display_neon_title()
                self.services[Srv.CLI].display_cli()
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

        return self.services[Srv.STT].transcribe(audio)

    def text_to_speech(self, input_text: str):
        """
        Run the text to speech service
        :param input_text result from llm, intents etc.
        """

        self.services[Srv.TTS].synthesize(input_text)

    def intent_recognition(self, input_text: str):
        """
        Run the intent recognition service
        :param input_text user input, either STT'd text or plain text
        """

        intent = self.services[Srv.IR].recognize_intent(input_text)
        if intent == None:
            self.services[Srv.CLI].print_text("Intenttiä ei havaittu\n", None, False)
        else:
            intent_response = self.services[Srv.IR].process_intent(intent)
            self.services[Srv.CLI].print_text(f"Intent: {intent.intent.name}, response:\n{intent_response}")          
   

    def text_gen(self, input_text: str, synthesize:bool = False):
        """
        The language model generates text based on user's input text
        Print the language model's generated text

        :param input_text: str, The user's input text
        :param synthesize: bool, If True, synthesize the generated text
        """
        llm_output = self.services[Srv.TEXT_GEN].generate(input_text)
        sentence = "LLM: "

        for token in llm_output:
            text = token["choices"][0]["delta"].get("content", "")
            sentence += text

            # Check if the sentence is complete
            if synthesize and (
                any(punc in sentence for punc in local.constants.PUNCTATIONS)
            ):
                self.services[Srv.TTS].synthesize(sentence)
                sentence = ""

            self.services[Srv.CLI].print_text(text, None, False)

        self.services[Srv.CLI].print_separator()

        return

    def _load_services(self):
        """
        This function loads all the services based on the chosen input and output devices
        """

        try:
            self.services[Srv.AUDIO] = AudioService(self)
        except Exception as e:
            print(f"Failed to load audio service: {e}")

        try:
            self.services[Srv.STT] = SpeechToTextService(self.root)
        except Exception as e:
            print(f"Failed to load stt service: {e}")

        try:
            self.services[Srv.TTS] = TextToSpeech(
                self, device_index=self.services[Srv.AUDIO].output_device_index
            )
        except Exception as e:
            print(f"Failed to load tts service: {e}")
    
        try:
            self.services[Srv.TEXT_GEN] = TextGenService(self.root)
        except Exception as e:
            print(f"Failed to text gen service: {e}")

        try:
            self.services[Srv.IR] = IrService(self)
        except Exception as e:
            print(f"Failed to load ir service: {e}")

        try:
            self.services[Srv.WEATHER] = Weather()
        except Exception as e:
            print(f"Failed to load weather service: {e}")
    
        try:
            self.services[Srv.NEWS] = YleNewsApi()
        except Exception as e:
            print(f"Failed to load yle news service: {e}")
 
    def _setup_env(self):
        """
        Set up env file if it doesn't exist, the user can choose input and output devices.
        """

        if not os.path.exists(self.ENV_PATH):
            self._create_env_file()

        print(f"env path: {self.ENV_PATH}")
        print(f"loading env, result: {load_dotenv(self.ENV_PATH)}")

    def _create_env_file(self):
        """
        Create an .env file based on .env.default
        """
        source_path = os.path.join(self.root, ".env.default")
        
        try:
            shutil.copy2(source_path, self.ENV_PATH)
            print("Default .env file copied successfully.")
            print("Default .env file copied successfully.")

        except IOError as e:
            print(f"Error writing to .env file ({self.ENV_PATH}): {e}")
        except OSError as e:
            print(f"OS Error writing to .env file ({self.ENV_PATH}): {e}")
        except Exception as e:
            print(f"An unexpected error occurred while writing to .env: {e}")

    def _find_project_root(self) -> Path:
        """
        Look iteratively through parent folders to find README.md
        which should be at project root.
        """
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
