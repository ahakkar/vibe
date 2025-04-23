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

    def process_intent(self, result: RecognizeResult, input=None) -> str:
        """
        Matches the intents with fi.yaml by string and cal  s the related
        class methods to provide response for each intent.

        :param RecognizeResult result: Whole recognized intent result from hassil library

        :return str: The processed intent
        """
        if result.intent.name == "GetNews":

            try:

                if input is None:
                    page_data = self.app.get_service(Srv.NEWS).parse_user_input(
                        "pääuutiset"
                    )
                else:
                    page_data = self.app.get_service(Srv.NEWS).parse_user_input(input)

                    page_data = [data.strip() for data in page_data]
                    page_data_str = " ".join(page_data)

                    return page_data_str

            except Exception as e:
                self.logger.error(f"Uutisten hakeminen epäonnistui: {e}")
                return "Uutisten hakeminen epäonnistui."

        elif result.intent.name == "GetCurrentWeather":
            try:
                weather_data = self.app.get_service(Srv.WEATHER).get_current_weather(location="Tampere")

                if weather_data is None:
                    raise ValueError("Säädataa ei ole (None)")

                return weather_data
            except Exception as e:
                self.logger.error(f"Sään hakeminen epäonnistui: {e}")

                return "Sään hakeminen epäonnistui."
            
        elif result.intent.name == "GetCurrentWeatherAtLocation":
            try:
                location = result.entities["sijainti"].value

                location_baseform = self.app.get_service(Srv.BASEFORM).get_baseform(location)

                weather_data = self.app.get_service(Srv.WEATHER).get_current_weather(location=location_baseform)

                if weather_data is None:
                    raise ValueError("Säädataa ei ole (None)")

                return weather_data
            except Exception as e:
                self.logger.error(f"Sään hakeminen paikasta {location_baseform} epäonnistui: {e}")

                return f"Sään hakeminen epäonnistui paikasta {location_baseform}"
        elif result.intent.name == "GetForecast":
            try:

                time = result.entities["aika"].value

                if time == "tänään":
                    weather_data = self.app.get_service(Srv.WEATHER).get_forecast(
                        location="Tampere", days=1, skip_days=0, frequency=3
                    )
                elif time == "huomenna":
                    weather_data = self.app.get_service(Srv.WEATHER).get_forecast(
                        location="Tampere", days=2, skip_days=1, frequency=3
                    )
                elif time == "ylihuomenna":
                    weather_data = self.app.get_service(Srv.WEATHER).get_forecast(
                        location="Tampere", days=3, skip_days=2, frequency=3
                    )
                elif time == "tällä viikolla":
                    weather_data = self.app.get_service(Srv.WEATHER).get_forecast(
                        location="Tampere", days=7, skip_days=0, frequency=12
                    )
                else:
                    return "Haettua aikaa ei tunnistettu"

                weather_data = [data.strip() for data in weather_data]

                if weather_data is None:
                    raise ValueError("Säädataa ei ole (None)")

                weather_data_str = f"Sääennuste {time} paikassa Tampere: {' '.join(weather_data)}"

                return weather_data_str

            except Exception as e:
                self.logger.error(f"Sään hakeminen epäonnistui: {e}")

                return "Sääennusteen hakeminen epäonnistui."

        elif result.intent.name == "GetForecastAtLocation":
            try:

                time = result.entities["aika"].value
                location = result.entities["sijainti"].value

                location_baseform = self.app.get_service(Srv.BASEFORM).get_baseform(location)

                if time == "tänään":
                    weather_data = self.app.get_service(Srv.WEATHER).get_forecast(
                        location=location_baseform, days=1, skip_days=0, frequency=3
                    )
                elif time == "huomenna":
                    weather_data = self.app.get_service(Srv.WEATHER).get_forecast(
                        location=location_baseform, days=2, skip_days=1, frequency=3
                    )
                elif time == "ylihuomenna":
                    weather_data = self.app.get_service(Srv.WEATHER).get_forecast(
                        location=location_baseform, days=3, skip_days=2, frequency=3
                    )
                elif time == "tällä viikolla":
                    weather_data = self.app.get_service(Srv.WEATHER).get_forecast(
                        location=location_baseform, days=7, skip_days=0, frequency=12
                    )
                else:
                    return "Haettua aikaa ei tunnistettu"
                
                

                weather_data = [data.strip() for data in weather_data]

                if weather_data is None:
                    raise ValueError("Säädataa ei ole (None)")
                
                weather_data_str = f"Sääennuste {time} paikassa {location_baseform}: {' '.join(weather_data)}"

                return weather_data_str
            except Exception as e:
                self.logger.error(f"Sään hakeminen epäonnistui: {e}")

                return "Sääennusteen hakeminen epäonnistui."

        elif result.intent.name == "GetTime":
            try:
                return "Ajan hakemista ei ole vielä toteutettu."
            except Exception as e:
                self.logger.error(f"Ajan hakeminen epäonnistui: {e}")
                return "Ajan hakeminen epäonnistui."

        self.logger.info(f"Tuntematon intent havaittu: {result.intent.name}")
        return f"Tuntematon intent havaittu: {result.intent.name}"
