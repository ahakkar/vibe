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
from local.chroma import Chroma
from local.context_manager import ContextManager
from local.tts import TextToSpeech
from local.audio import AudioService
from local.stt import SpeechToTextService
from local.weather import Weather
from local.yle import YleNewsApi


from pathlib import Path


class AppManager:
    def __init__(self):
        """
        Initialize app manager
        """

        # Determine the correct .env and logs path based if running in Docker
        if os.getenv("RUNNING_IN_DOCKER"):
            self.root = os.path.join("/")
            self.ENV_PATH = os.path.join(self.root, "usr/src")
            self.LOG_PATH = os.path.join(self.root, "usr/src/logs")
        else:
            self.root = self._find_project_root()
            self.ENV_PATH = os.path.join(self.root, "src/backend")
            self.LOG_PATH = os.path.join(self.root, "logs")

        self.logger = logging.getLogger(__name__)
        logfile_name = APP_LOG_FILE

        logging.basicConfig(
            level=logging.INFO,
            format="{asctime}.{msecs:03.0f} - {levelname} - {message}",
            style="{",
            datefmt="%Y-%m-%d %H:%M:%S",
            handlers=[logging.FileHandler(os.path.join(self.LOG_PATH, logfile_name))],
        )
        self.logger.info(f"APP start")

        desc = [
            "App runs by default on background. Enable web server with --web",
            "And command line interface with --cli argument",
        ]

        # https://docs.python.org/3/library/argparse.html
        parser = argparse.ArgumentParser(prog="SLT-VIBE", usage="\n".join(desc))
        parser.add_argument("--cli", action="store_true", help="Enable CLI")
        parser.add_argument("--web", action="store_true", help="Enable Web server")
        self.args = parser.parse_args()

        self.services = {
            Srv.STT: None,
            Srv.TTS: None,
            Srv.TEXT_GEN: None,
            Srv.RAG: None,
            Srv.CONTEXT_MANAGER: None,
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

    def exit_and_save(self):
        """
        Exit the program gracefully with cleanup
        """
        if self.services[Srv.CLI]:
            self.services[Srv.CLI].print_text("Saving context and exiting the program.")

        context_from_conversation = self.services[Srv.CONTEXT_MANAGER].summarizer()
        self.services[Srv.RAG].save_to_db(context_from_conversation)

        self.services[Srv.AUDIO].terminate_audio()
        self.services[Srv.TTS].stop()
        self.logger.info(f"APP shutdown at {time.asctime()}")
        sys.exit(0)

    def exit(self):
        """
        Exit the program gracefully with cleanup
        """
        if self.services[Srv.CLI]:
            self.services[Srv.CLI].print_text("Exiting the program.")
        self.services[Srv.AUDIO].terminate_audio()
        self.services[Srv.TTS].stop()
        self.logger.info(f"APP shutdown")
        sys.exit(0)

    def run(self):
        """
        Starts the app
        """

        if self.args.cli:
            self._run_cli()

        # Could run as a background if we had voice activation detection

        # Could perhaps run the web server here too

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

    def speech_to_text(self, audio) -> str:
        """
        Run the speech to text service

        :param np.ndarray audio: The audio data that will be transcribed

        :return str: The recorded sentence that is transcribed from audio data
        """
        self.logger.info("PERF : [speech_to_text] Transcribing audio")
        return self.services[Srv.STT].transcribe(audio)

    def text_to_speech(self, input_text: str):
        """
        Run the text to speech service

        :param str input_text: result from llm, intents etc.
        """
        self.logger.info("PERF : [text_to_speech] Synthesizing text")
        self.services[Srv.TTS].synthesize(input_text)

    def intent_recognition(self, input_text: str):
        """
        Run the intent recognition service

        :param str input_text: user input, either STT'd text or plain text
        """
        self.logger.info("PERF : [intent_recognition] Recognizing intent")
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
        self.logger.info("PERF : [text_gen] Generating text")
        context = self.services[Srv.RAG].retrieve_similar_entries(input_text)

        # print("\nContext:", context, "\n")

        assistant_input = ""
        if len(self.services[Srv.CONTEXT_MANAGER].messages):
            assistant_input = self.services[Srv.CONTEXT_MANAGER].messages[-1]["content"]

        # print("\nAssistant input:", assistant_input)

        llm_output = self.services[Srv.TEXT_GEN].generate(
            input_text, context, assistant_input
        )
        sentence = ""

        for token in llm_output:
            text = token["choices"][0]["delta"].get("content", "")
            sentence += text

            if synthesize and (
                any(punc in sentence for punc in local.constants.PUNCTATIONS)
            ):
                sentence = sentence.strip()
                self.services[Srv.TTS].synthesize(sentence)
                sentence = ""

            self.services[Srv.CLI].print_text(text, None, False)

        self.services[Srv.CONTEXT_MANAGER].messages.extend(
            [
                {"role": "user", "content": input_text},
                {"role": "assistant", "content": sentence.strip()},
            ]
        )

        self.services[Srv.CLI].print_separator()

        return

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
            self.services[Srv.RAG] = Chroma(self.root)
        except Exception as e:
            self.logger.error(f"Failed to load rag service: {e}")
            self.exit()

        try:
            self.services[Srv.CONTEXT_MANAGER] = ContextManager(self.root)
        except Exception as e:
            self.logger.error(f"Failed to load text context management service: {e}")
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
