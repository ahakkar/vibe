from enum import Enum

APP_TITLE = "SLT-VIBE"


class Srv(Enum):
    STT = "Speech to Text Service"
    TTS = "Text to Speech Service"
    TEXT_GEN = "Text Generation Service"
    IR = "Intent Recognition Service"
    AUDIO = "Audio Service"
    CLI = "Command Line Interface"
    WEATHER = "Open weather API"
    NEWS = "Yle Teksti-TV API"


THEME = {
    "title": "bold underline",
    "menu": "bold",
    "option": "bold cyan",
    "input": "bold yellow",
    "error": "bold red",
    "success": "bold green",
}

PUNCTATIONS = ["...", ".", "!", "?", ":", ";"]
