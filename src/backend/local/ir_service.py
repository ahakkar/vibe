import logging
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
        self.logger = logging.getLogger(__name__)

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
            try:
                page_data = self.app.get_service(Srv.NEWS).get_news(100)
                page_data = [data.strip() for data in page_data]
                page_data_str = "".join(page_data)
                return page_data_str
            except Exception as e:
                self.logger.error(f"Uutisten hakeminen epäonnistui: {e}")
                return "Uutisten hakeminen epäonnistui."
        elif result.intent.name == "GetCurrentWeather":
            try:
                weather_data = self.app.get_service(Srv.WEATHER).get_current_weather()
                return weather_data
            except Exception as e:
                self.logger.error(f"Sään hakeminen epäonnistui: {e}")

                return "Sään hakeminen epäonnistui."
        elif result.intent.name == "GetTime":
            try:
                return "Ajan hakemista ei ole vielä toteutettu."
            except Exception as e:
                self.logger.error(f"Ajan hakeminen epäonnistui: {e}")
                return "Ajan hakeminen epäonnistui."

        self.logger.info(f"Tuntematon intent havaittu: {result.intent.name}")
        return f"Tuntematon intent havaittu: {result.intent.name}"
