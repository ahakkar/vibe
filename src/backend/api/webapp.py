from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
import uvicorn
from io import BytesIO
import soundfile as sf
from pydantic import BaseModel


class TextInput(BaseModel):
    input_text: str


class AudioFileInput(BaseModel):
    audioFile: UploadFile = File(...)


class WebApp:
    def __init__(self, app):
        self.app = app
        self.appAPI = FastAPI()
        self.appAPI.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        self._setup_routes()

    def _setup_routes(self):
        @self.appAPI.post("/api/intent")
        async def intent_recognition_api(payload: TextInput):
            try:
                input_text = payload.input_text
                intent_response = self.app.intent_recognition_web(input_text)
                return JSONResponse(content={"response": intent_response}, status_code=200)
            except Exception as e:
                self.app.logger.error(f"[post api/intent] Error: {e}")
                return JSONResponse(content={"Intent recognition error": str(e)}, status_code=500)

        @self.appAPI.post("/api/text")
        async def text_gen_api(payload: TextInput):
            try:
                input_text = payload.input_text
                full_text = self.app.text_gen_web(input_text)
                return JSONResponse(content={"response": full_text}, status_code=200)
            except Exception as e:
                self.app.logger.error(f"[post api/text] Error: {e}")
                return JSONResponse(content={"Text generation error": str(e)}, status_code=500)

        @self.appAPI.post("/api/tts")
        async def text_to_speech_api(payload: TextInput):
            try:
                input_text = payload.input_text

                audio_buffer: BytesIO = self.app.text_to_speech_web(input_text)
                if not isinstance(audio_buffer, BytesIO):
                    raise TypeError("Expected BytesIO from text_to_speech_web")

                return StreamingResponse(
                    audio_buffer,  # stream the buffer directly
                    media_type="audio/wav", 
                    headers={"Content-Disposition": "inline; filename=tts.wav"}
                )
            except Exception as e:
                self.app.logger.error(f"[post api/tts] Error: {e}")
                return JSONResponse(content={"Text to speech error": str(e)}, status_code=500)

        @self.appAPI.post("/api/stt")
        async def speech_to_text_api(payload: AudioFileInput):
            try:
                audioFile = payload.audioFile
                audio_bytes = await audioFile.read()
                audio_data, sample_rate = sf.read(BytesIO(audio_bytes), dtype="float32")

                recorded_sentence = self.app.speech_to_text(audio_data)
                return JSONResponse(content={"response": recorded_sentence}, status_code=200)
            except Exception as e:
                self.app.logger.error(f"[post api/stt] Error: {e}")
                return JSONResponse(content={"Speech to text error": str(e)}, status_code=500)

    def run_server(self):
        uvicorn.run(self.appAPI, host="0.0.0.0", port=5000, log_level="critical")
