import logging
import os
import pytz
import requests

from datetime import datetime, timedelta
from timezonefinder import TimezoneFinder
from typing import Optional, Tuple
from local.constants import WEATHER_CODES, WEEKDAYS


class Forecast:
    def __init__(self, time_list, temperature_list, code_list, rain_list):
        """
        Initialize the Forecast service

        :param time_list: The list of the time
        :param temperature_list: The list of the temperature
        :param code_list: The list of code
        :param rain_list: The list of rain's probability
        """
        self.logger = logging.getLogger(__name__)

        self.time_list = time_list
        self.temperature_list = temperature_list
        self.code_list = code_list
        self.rain_probability_list = rain_list

    def _parse_forecast(
        self, freq: int, latitude: float, longitude: float
    ) -> list[str]:
        """
        Parses forecast information into a list of strings for TTS to read

        :param int freq: How frequent forecasts are added to list (1 = every hour, 3 = every 3rd hour)
        :param float latitude: Latitude coordinates
        :param float longitude: Longitude coordinates

        :return [str]: List of Forecast data.
        Return format: Kello {hour}: {weather type}, {temperature} astetta celsiusta. Sateen todennäköisyys {probability} prosenttia.
        """

        forecast_data = []

        timezone_finder = TimezoneFinder()
        coords_timezone = timezone_finder.timezone_at(
            lng=float(longitude), lat=float(latitude)
        )

        current_time = datetime.now(pytz.timezone(coords_timezone))

        # Remove timezone info to compare with timezone unaware datetime object
        current_time = datetime.now(pytz.timezone(coords_timezone)).replace(tzinfo=None)

        for i in range(0, len(self.time_list), freq):

            # Forecast hour in utc form
            hour_utc = datetime.strptime(self.time_list[i], "%Y-%m-%dT%H:%M")

            time_diff = current_time - hour_utc

            # Skips forecasts that are for over one over ago (e.g. so at 17.15 still shows 17 forecast)
            if time_diff > timedelta(hours=1):
                continue

            temperature = self.temperature_list[i]

            weather = WEATHER_CODES[self.code_list[i]]

            rain_probability = self.rain_probability_list[i]

            if len(self.time_list) <= 24:

                forecast_data.append(
                    f"Kello {hour_utc.hour}: {weather}, {temperature} astetta celsiusta. Sateen todennäköisyys {rain_probability} prosenttia."
                )

            # If forecast for more than 1 day, add weekday for clarity
            else:

                weekday = WEEKDAYS[hour_utc.weekday()]

                forecast_data.append(
                    f"{weekday} kello {hour_utc.hour}: {weather}, {temperature} astetta celsiusta. Sateen todennäköisyys {rain_probability} prosenttia."
                )

        return forecast_data


class Weather:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._coords_url = os.getenv("COORDS_URL")
        self._weather_url = os.getenv("WEATHER_URL")

        try:
            if self._coords_url == None or self._weather_url == None:
                raise Exception
        except Exception as e:
            self.logger.error("Missing .env COORDS_URL or WEATHER_URL from .env")

    """
    Returns a string ready for TTS to read current weather data
    """

    def get_current_weather(self, location: str = "Tampere") -> str:
        """
        Get the current weather in given location

        :param str location: The given location, defaults to Tampere

        :return str: The current weather in given location
        """

        latitude, longitude = self._get_coordinates(location=location)

        if latitude is None or longitude is None:
            return f"Sijaintia {location} ei löytynyt."

        temperature, precipitation, weather_code = (
            self._get_current_weather_from_coords(
                longitude=longitude, latitude=latitude
            )
        )

        if temperature is None or precipitation is None or weather_code is None:
            return f"Säätietojen hakeminen epäonnistui."

        if precipitation > 0:
            return f"Paikassa {location} on {WEATHER_CODES[weather_code]}, {temperature} astetta celsiusta. Sateen määrä {precipitation} millimetriä."

        else:
            return f"Paikassa {location} on {WEATHER_CODES[weather_code]}, {temperature} astetta celsiusta."

    def get_forecast(
        self, location: str = "Tampere", days: int = 1, frequency: int = 3
    ) -> Optional[list[str]]:
        """
        Returns a list of weather forecast strings ready for TTS to read
        Does not return already happened forecasts (except less than 1 hour old)

        :param str location: Location name to fetch forecast for. Can be in Finnish
        :param int days: How many days' forecast (1 = only today)
        :param int frequency: Frequency in hours for forecasts (1 = forecast every hour)

        :return [str]: List of Forecast data
        """

        latitude, longitude = self._get_coordinates(location=location)

        if latitude is None or longitude is None:
            return [f"Sijaintia {location} ei löytynyt."]

        forecast = self._get_forecast_from_coords(latitude, longitude, days)

        if not forecast:
            return None

        forecast_data = forecast._parse_forecast(
            freq=frequency, latitude=latitude, longitude=longitude
        )

        return forecast_data

    def _get_coordinates(self, location="Tampere") -> Optional[tuple[float, float]]:
        """
        Uses nominatim API to get coordinates for searched location

        :param str location: The location to get coordinates

        :return Optional[float, float]: The latitude and longitude of the given location. Otherwise return None
        """

        headers = {"User-Agent": "SLT Vibe"}

        response = requests.get(
            f"{self._coords_url}{location}&format=json", headers=headers
        )

        if response.status_code == 200:
            data = response.json()

            if len(data) > 0:
                latitude = data[0]["lat"]
                longitude = data[0]["lon"]
                return latitude, longitude
            else:

                # Location not found
                return None
        else:
            self.logger.error(
                f"Unable to fetch data (Status Code: {response.status_code})"
            )
            return None

    def _get_current_weather_from_coords(
        self, latitude: float = 61.4980214, longitude: float = 23.7603118
    ) -> Optional[Tuple[str, str, str]]:
        """
        Uses open meteo API to get temperature, rain amount and weather code for input coords

        :param float latitude: Latitude coordinates to get the current weather
        :param float longitude: Longitude coordinates to get the current weather

        :return Optional[str, str, str]: The temperature, precipitation, and weather code
        """

        response = requests.get(
            f"{self._weather_url}latitude={latitude}&longitude={longitude}&current=temperature_2m,precipitation,weather_code"
        )

        if response.status_code == 200:
            data = response.json()

            current_weather = data.get("current", {})
            temperature = current_weather.get("temperature_2m")
            precipitation = current_weather.get("precipitation")
            weather_code = current_weather.get("weather_code")

            return temperature, precipitation, weather_code

        else:
            self.logger.error(
                f"Vallitsevan sään hakeminen koordinaateilla epäonnistui: {self._weather_url}\n{latitude}\n{longitude}"
            )
            return None

    def _get_forecast_from_coords(
        self, latitude: float = 61.4980214, longitude: float = 23.7603118, days: int = 1
    ) -> Optional[Forecast]:
        """
        Uses open meteo API to create a Forecast object for location in coords and duration of input days

        :param float latitude: Latitude coordinates to get the forecast
        :param float longitude: Longitude coordinates to get the forecast

        :return Forecast: The class forecast
        """
        response = requests.get(
            f"{self._weather_url}latitude={latitude}&longitude={longitude}&hourly=temperature_2m,weather_code,precipitation_probability&forecast_days={days}"
        )

        if response.status_code == 200:
            data = response.json()

            hourly_weather = data.get("hourly", {})
            time = hourly_weather.get("time")
            temperature = hourly_weather.get("temperature_2m")
            code = hourly_weather.get("weather_code")
            rain = hourly_weather.get("precipitation_probability")

            return Forecast(time, temperature, code, rain)
        else:
            self.logger.error(
                f"Säätietojen hakeminen koordinaateilla epäonnistui: {self._weather_url}\n{latitude}\n{longitude}\n"
            )
            return None
