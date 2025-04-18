import argparse
import logging
import os
import sys
import shutil
import time
import local.constants


from local.constants import Srv
from local.constants import APP_LOG_FILE
from dotenv import load_dotenv
from local.cli import CommandLineService
from local.ir_service import IrService
from local.text_gen import TextGenService
from local.tts import TextToSpeech
from local.audio import AudioService
from local.stt import SpeechToTextService
from local.weather import Weather
from local.yle import YleNewsApi
from api.webapp import WebApp
from pathlib import Path


class AppManager:
    def __init__(self):
        """
        Initialize app manager
        """
        self.logger = logging.getLogger(__name__)
        logfile_name = APP_LOG_FILE

        logging.basicConfig(filename=logfile_name, level=logging.INFO)
        self.logger.info(f"APP start at {time.asctime()}")

        desc = [
            "App runs by default on background. Enable web server with --web",
            "And command line interface with --cli argument",
        ]

        # https://docs.python.org/3/library/argparse.html
        parser = argparse.ArgumentParser(prog="SLT-VIBE", usage="\n".join(desc))
        parser.add_argument("--cli", action="store_true", help="Enable CLI")
        parser.add_argument("--web", action="store_true", help="Enable Web server")
        self.args = parser.parse_args()

        # Determine the correct .env path based if running in Docker
        if os.getenv("RUNNING_IN_DOCKER"):
            self.root = os.path.join("/")
            self.ENV_PATH = os.path.join(self.root, "usr/src")
        else:
            self.root = self._find_project_root()
            self.ENV_PATH = os.path.join(self.root, "src/backend")

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

    def toggle_recording(self, all):
        """
        Toggle recording state and process audio if recording is stopped.

        This function looks to be a bit to complex and could be refactored/
        broken down to smaller functions.

        :param bool all_services: If True, the program will run all services
        """
        if self.services[Srv.AUDIO].is_recording:
            audio_data = self.services[Srv.AUDIO].stop_recording()
            if audio_data is not None:
                self._process_recording(audio_data, all)
            elif self.args.cli:
                self.services[Srv.CLI].print_text("No audio recorded.")

        else:
            self.services[Srv.AUDIO].start_recording()

    def _process_recording(self, recording, all):
        """
        Transcribe audio with STT, detect intent, provide response based on
        intent or if no intent was detected, provide an answer with text gen.

        :param NDArray[floating[Any]] recording: The recorded audio data
        """

        audio_text = self.services[Srv.STT].transcribe(recording)
        self.logger.info("Text:", audio_text)

        if all:
            intent = self.services[Srv.IR].recognize_intent(audio_text)

            # Intent is recognized, handle it
            if intent != None:
                intent_response = self.services[Srv.IR].process_intent(intent)
                if self.args.cli:
                    self.services[Srv.CLI].print_text(intent_response)
                self.logger.info(
                    "f[_process_recording] Intent response: {intent_response}"
                )
                self.services[Srv.TTS].synthesize(intent_response)
            # If no intent is recognized, pass user prompt to LLM
            else:
                self.text_gen(audio_text, True)

    def get_service(self, service_name: Srv):
        """
        Get an already initialized service with enum so other sections of app
        can utilize the service.

        :param Srv service_name: enum from constants.py
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
        self.logger.info(f"APP shutdown at {time.asctime()}")
        sys.exit(0)

    def run(self):
        """
        Starts the app
        """

        if self.args.cli:
            self._run_cli()

        # Could run as a background if we had voice activation detection

        # Could perhaps run the web server here too
        elif self.args.web:
            self._run_web()

    def _run_cli(self):
        """
        Run the Command Line Service
        """
        try:
            self.services[Srv.CLI] = CommandLineService(self)
            self.services[Srv.CLI].display_cli()
            self.exit()
        except Exception as e:
            self.logger.error(
                f"[_run_cli] Error while running CLI service: {e} at line {e.lineno}"
            )
            self.exit()

    def _run_web(self):
        webApp = WebApp(self)
        webApp.run_server()

    def speech_to_text(self, audio) -> str:
        """
        Run the speech to text service

        :param np.ndarray audio: The audio data that will be transcribed

        :return str: The recorded sentence that is transcribed from audio data
        """

        return self.services[Srv.STT].transcribe(audio)

    def text_to_speech(self, input_text: str):
        """
        Run the text to speech service

        :param str input_text: result from llm, intents etc.
        """

        self.services[Srv.TTS].synthesize(input_text)

    def intent_recognition(self, input_text: str):
        """
        Run the intent recognition service

        :param str input_text: user input, either STT'd text or plain text
        """

        intent = self.services[Srv.IR].recognize_intent(input_text)
        if intent == None:
            self.services[Srv.CLI].print_text("Intenttiä ei havaittu\n", None, False)
        else:
            intent_response = self.services[Srv.IR].process_intent(
                intent, input=input_text
            )
            self.logger.info(
                f"[intent_recognition] Intent: {intent.intent.name}, response: {intent_response}"
            )
            self.services[Srv.CLI].print_text(intent_response)

    def text_gen(self, input_text: str, synthesize: bool = False):
        """
        The language model generates text based on user's input text
        Print the language model's generated text

        :param str input_text: The user's input text
        :param bool synthesize: If True, synthesize the generated text
        """
        llm_output = self.services[Srv.TEXT_GEN].generate(input_text)
        sentence = ""

        for token in llm_output:
            text = token["choices"][0]["delta"].get("content", "")
            sentence += text

            # Check if the sentence is complete
            if synthesize and (
                any(punc in sentence for punc in local.constants.PUNCTATIONS)
            ):
                sentence = sentence.strip()
                self.services[Srv.TTS].synthesize(sentence)
                sentence = ""

            self.services[Srv.CLI].print_text(text, None, False)

        self.services[Srv.CLI].print_separator()

        return
    
    def text_gen_web(self, input_text: str):
        """
        The language model generates text based on user's input text

        :param str input_text: The user's input text
        :return str: Language generated output
        """
        llm_output = self.services[Srv.TEXT_GEN].generate(input_text)
        full_text = "".join(
            token["choices"][0]["delta"].get("content", "")
            for token in llm_output
        )
        return full_text
    
    def text_to_speech_web(self, input_text: str):
        """
        Run the text to speech service

        :param str input_text: result from llm, intents etc.
        """

        return self.services[Srv.TTS].synthesize_to_buffer(input_text)
    

    def intent_recognition_web(self, input_text: str):
        """
        Run the intent recognition service in the web version

        :param str input_text: user input, either STT'd text or plain text
        :return str: The intent recongition responsed user's intent
        """
        intent = self.services[Srv.IR].recognize_intent(input_text)
        intent_response = ""
        if intent == None:
            intent_response = "Intenttiä ei havaittu\n"
        else:
            intent_response = self.services[Srv.IR].process_intent(intent, input=input_text)
            self.logger.info(
                f"[intent_recognition] Intent: {intent.intent.name}, response: {intent_response}"
            )
        return intent_response

    def _load_services(self):
        """
        This function loads all the services based on the chosen input and output devices
        """

        try:
            self.services[Srv.AUDIO] = AudioService(self)
        except Exception as e:
            self.logger.error(f"Failed to load audio service: {e}")
            self.exit()

        try:
            self.services[Srv.STT] = SpeechToTextService(self.root)
        except Exception as e:
            self.logger.error(f"Failed to load stt service: {e}")
            self.exit()

        try:
            self.services[Srv.TTS] = TextToSpeech(
                self.root, device_index=self.services[Srv.AUDIO].output_device_index
            )
        except Exception as e:
            self.logger.error(f"Failed to load tts service: {e}")
            self.exit()

        try:
            self.services[Srv.TEXT_GEN] = TextGenService(self.root)
        except Exception as e:
            self.logger.error(f"Failed to load text gen service: {e}")
            self.exit()

        try:
            self.services[Srv.IR] = IrService(self)
        except Exception as e:
            self.logger.error(f"Failed to load ir service: {e}")
            self.exit()

        try:
            self.services[Srv.WEATHER] = Weather()
        except Exception as e:
            self.logger.error(f"Failed to load weather service: {e}")

        try:
            self.services[Srv.NEWS] = YleNewsApi()
        except Exception as e:
            self.logger.error(f"Failed to load yle news service: {e}")
            self.exit()

    def _setup_env(self):
        """
        Set up env file if it doesn't exist, the user can choose input and output devices.
        """

        env_file_path = os.path.join(self.ENV_PATH, ".env")

        if not os.path.exists(env_file_path):
            self.logger.info(
                f".env not found, creating one based on .env.example to {env_file_path}"
            )
            self._create_env_file()

        self.logger.info(f"env path: {self.ENV_PATH}")
        self.logger.info(f"loading env, result: {load_dotenv(env_file_path)}")

    def _create_env_file(self):
        """
        Create an .env file based on .env.default
        """
        source_path = os.path.join(self.ENV_PATH, ".env.default")

        env_file_path = os.path.join(self.ENV_PATH, ".env")
        try:
            shutil.copy2(source_path, env_file_path)

        except IOError as e:
            self.logger.error(f"Error writing to .env file ({self.ENV_PATH}): {e}")
        except OSError as e:
            self.logger.error(f"OS Error writing to .env file ({self.ENV_PATH}): {e}")
        except Exception as e:
            self.logger.error(
                f"An unexpected error occurred while writing to .env: {e}"
            )

    def _find_project_root(self) -> Path:
        """
        Look iteratively through parent folders to find README.md
        which should be at project root.

        :return Path: the current project root
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
