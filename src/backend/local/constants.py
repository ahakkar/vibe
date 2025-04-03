from enum import Enum

APP_TITLE = "SLT-VIBE"
APP_LOG_FILE = "vibe.log"


class Srv(Enum):
    STT = "Speech to Text Service"
    TTS = "Text to Speech Service"
    TEXT_GEN = "Text Generation Service"
    RAG = "RAG context management service"
    IR = "Intent Recognition Service"
    AUDIO = "Audio Service"
    CLI = "Command Line Interface"
    WEATHER = "Open weather API"
    NEWS = "Yle Teksti-TV API"


# Currently very short dict of topics and corrensponding teletext pages
TTV_PAGES = {
    "pääuutinen": 100,
    "kotimaa": 102,
    "ulkomaa": 130,
    "talous": 160,
    "urheilu": 201,
}


THEME = {
    "title": "bold underline",
    "menu": "bold",
    "option": "bold cyan",
    "input": "bold yellow",
    "error": "bold red",
    "success": "bold green",
}

PUNCTATIONS = ["...", ".", "!", "?", ":", ";"]

WEATHER_CODES = {
    0: "selkeää",
    1: "enimmäkseen selkeää",
    2: "puolipilvistä",
    3: "pilvistä",
    45: "sumua",
    48: "jäätävää sumua",
    51: "heikkoa tihkusadetta",
    53: "kohtalaista tihkusadetta",
    55: "voimakasta tihkusadetta",
    61: "heikkoa vesisadetta",
    63: "kohtalaista vesisadetta",
    65: "voimakasta vesisadetta",
    66: "heikkoa jäätävää sadetta",
    67: "voimakasta jäätävää sadetta",
    71: "kevyttä lumisadetta",
    73: "kohtalaista lumisadetta",
    75: "voimakasta lumisadetta",
    77: "lumijyvässadetta",
    80: "heikkoja sadekuuroja",
    81: "kohtalaisia sadekuuroja",
    82: "voimakkaita sadekuuroja",
    85: "heikkoja lumikuuroja",
    86: "vahvoja lumikuuroja",
    95: "ukkosta",
    96: "ukkosta ja heikkoja raekuuroja",
    97: "ukkosta ja vahvoja raekuuroja",
}
