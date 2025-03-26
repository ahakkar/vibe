
import os
import time
from local.ir_service import IrService
from local.text_gen import TextGenService
from local.tts import TextToSpeech
from local.audio_record import AudioRecordingService
from local.stt import SpeechToTextService
from dotenv import load_dotenv, set_key

class AppManager:
    def __init__(self):
        # Determine the correct .env path based if running in Docker
        if os.getenv("RUNNING_IN_DOCKER"):
            self.ENV_PATH = os.path.join("/usr/src/app", ".env")
        else:
            self.ENV_PATH = os.path.join(os.path.dirname(__file__), ".env")
            
        print("app initializing")
        self._setup_env()
        self._load_services
        
    
    def run(self):
        pass
    
    
    def _load_services(self):
        """
        This function loads all the services based on the chosen input and output devices
        """

        input_device_name = os.getenv("INPUT_DEVICE_NAME")
        output_device_name = os.getenv("OUTPUT_DEVICE_NAME")

        self.input_device_index = self._get_device_index(input_device_name, "input")
        self.output_device_index = self._get_device_index(output_device_name, "output")
        
        if os.getenv("STT_ENABLED"):
             self.stt_service = SpeechToTextService()
        elif os.getenv("TTS_ENABLED"):
             self.tts_service = TextToSpeech(device_index=self.output_device_index)
        elif os.getenv("LLM_ENABLED"):
             self.text_gen_service = TextGenService()
        elif os.getenv("IR_ENABLED"):
            self.ir_service = IrService()     
        
        self.audio_service = AudioRecordingService(device_index=self.input_device_index)
       
       
    
    
    def _setup_env(self):
        """
        Set up env file if it doesn't exist, the user can choose input and output devices.
        """
        
        if not os.path.exists(self.ENV_PATH):
            self.create_env_file()
            # self.display_settings_menu(self.ENV_PATH)
            
        load_dotenv(self.ENV_PATH)
            
    
    def _create_env_file(self):
        """
        Create env file by setting default input and output device names
        """
        with open(self.ENV_PATH, "w") as f:
            f.write("INPUT_DEVICE_NAME=None\n")
            f.write("OUTPUT_DEVICE_NAME=None\n")
            f.write("STT_ENABLED=False\n")
            f.write("TTS_ENABLED=False\n")
            f.write("LLM_ENABLED=False\n")
            f.write("ONNX_MODEL_PATH=\"/models/wav2vec2_model.onnx\"")
            f.write("PROCESSOR_PATH=\"/models/wav2vec2_processor\"")
            f.write("OUTPUT_FILENAME=\"recorded_audio.wav\"")
            
    
if __name__ == "__main__":
    app = AppManager()
    app.run()
    