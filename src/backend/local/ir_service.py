from typing import Optional
from abstract_classes import IntentRecognitionInterface
from pathlib import Path
from hassil import RecognizeResult, recognize
from hassil import Intents
import os.path

from local.constants import Srv


class IrService(IntentRecognitionInterface):
    def __init__(self, app):
        """
        Load supported intents. hassil has multiple different options, ie. from_files, from_yaml, from_dict. from_yaml is used for simplicity for starter. In that case all intents are defined in the same YAML file.

        :param app: app
        """
        self.app = app

        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = Path(project_root) / "local" / "intents" / "fi.yaml"

        with open(filepath, "r", encoding="utf-8") as f:
            self.intents = Intents.from_yaml(f)

    def recognize_intent(self, text: str, lang="fi") -> Optional[RecognizeResult]:
        """
        Uses recognize() to return first match. recognize() has a bunch of optional params which could be used to fine tune the process.

        Discards most contents of a RecognizeResult and returns only the essential information.

        :param str text:
        :param str lang:

        :return
        """

        return recognize(text, self.intents)

    def process_intent(self, result: RecognizeResult) -> str:
        """
        Matches the intents with fi.yaml by string and calls the related
        class methods to provide response for each intent.

        :param RecognizeResult result: Whole recognized intent result from hassil library

        :return str: The processed intent
        """
        if result.intent.name == "GetNews":
            page_data = self.app.get_service(Srv.NEWS).get_news(100)
            page_data = [ data.strip() for data in page_data]
            page_data_str = "".join(page_data)
            return page_data_str
        elif result.intent.name == "GetCurrentWeather":
            weather_data = self.app.get_service(Srv.WEATHER).get_current_weather()
            return weather_data
        elif result.intent.name == "GetTime":
            return "Ajan hakemista ei ole vielä toteutettu."

        return f"Tuntematon intent havaittu: {result.intent.name}"
