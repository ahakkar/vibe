from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from pydantic import BaseModel

class TextInput(BaseModel):
    input_text: str

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
                return JSONResponse(content={"Text generations error": str(e)}, status_code=500)
            
        @self.appAPI.post("/api/text")
        async def text_gen_api(payload: TextInput):
            try:
                input_text = payload.input_text
                full_text = self.app.text_gen_web(input_text)
                return JSONResponse(content={"response": full_text}, status_code=200)
            except Exception as e:
                return JSONResponse(content={"Text generation error": str(e)}, status_code=500)
            
        

    def run_server(self):
        uvicorn.run(self.appAPI, host="0.0.0.0", port=5000)
    