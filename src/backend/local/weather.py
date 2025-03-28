import requests
from datetime import datetime, timedelta
from typing import Tuple

#These required from pip to get timezone
from timezonefinder import TimezoneFinder
import pytz

COORDS_URL = "https://nominatim.openstreetmap.org/search?city="
WEATHER_URL = "https://api.open-meteo.com/v1/forecast?"



#TODO: move elsewhere
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
    97: "ukkosta ja vahvoja raekuuroja"

}



class Forecast:


    def __init__(self, time_list, temperature_list, code_list, rain_list):
        self.time_list = time_list
        self.temperature_list = temperature_list
        self.code_list = code_list
        self.rain_probability_list = rain_list

    """
    Parses forecast information into a list of strings for TTS to read
    format: Kello {hour}: {weather type}, {temperature} astetta celsiusta. Sateen todennäköisyys {probability} prosenttia.
    Parameters: 
    freq(int): How freaquent forecasts are added to list (1 = every hour, 3 = every 3rd hour)
    latitude & longitude coordinates
    Returns:
    list: list of parsed forecast strings

    """
    def parse_forecast(self, freq, latitude, longitude):

        return_list = []

        timezone_finder = TimezoneFinder()
        coords_timezone = timezone_finder.timezone_at(lng=float(longitude), lat=float(latitude))

        current_time = datetime.now(pytz.timezone(coords_timezone))

        #Remove timezone info to compare with timezone unaware datetime object
        current_time = datetime.now(pytz.timezone(coords_timezone)).replace(tzinfo=None)

        for i in range(0, len(self.time_list), freq):

            
            #Forecast hour in utc form
            hour_utc = datetime.strptime(self.time_list[i], "%Y-%m-%dT%H:%M")
            

            time_diff = current_time - hour_utc

            #Skips forecasts that are for over one over ago (e.g. so at 17.15 still shows 17 forecast)
            if time_diff > timedelta(hours=1):
                continue

            temperature = self.temperature_list[i]

            weather = WEATHER_CODES[self.code_list[i]]

            rain_probability = self.rain_probability_list[i]

            return_list.append(f"Kello {hour_utc.hour}: {weather}, {temperature} astetta celsiusta. Sateen todennäköisyys {rain_probability} prosenttia.")

        return return_list




        



class Weather:

    """
    Returns a string ready for TTS to read current weather data 
    """
    def get_current_weather(self, location="Tampere") -> str:

        latitude, longitude = self._get_coordinates(location=location)

        if latitude is None or longitude is None:
            return f"Sijaintia {location} ei löytynyt."

        temperature, precipitation, weather_code = self._get_current_weather_from_coords(
            longitude=longitude, latitude=latitude
        )

        if (temperature is None or precipitation is None or weather_code is None):
            return f"Säätietojen hakeminen epäonnistui."

        if precipitation > 0:
            return f"Paikassa {location} on {WEATHER_CODES[weather_code]}, {temperature} astetta celsiusta. Sateen määrä {precipitation} millimetriä."
        
        else:
            return f"Paikassa {location} on {WEATHER_CODES[weather_code]}, {temperature} astetta celsiusta."
    

    """
    Returns a list of weather forecast strings ready for TTS to read
    Does not return already happened forecasts (except less than 1 hour old)

    Parameters:
    location(string): Location name to fetch forecast for. Can be in Finnish
    days(int): How many days' forecast (1 = only today)
    frequency(int): Frequency in hours for forecasts (1 = forecast every hour)
    """
    def get_forecast(self, location="Tampere", days=1, frequency = 3):

        latitude, longitude = self._get_coordinates(location=location)

        if latitude is None or longitude is None:
            return f"Sijaintia {location} ei löytynyt."

        forecast = self._get_forecast_from_coords(latitude, longitude, days)

        return forecast.parse_forecast(freq=frequency, latitude = latitude, longitude = longitude)




    """
    Uses nominatim API to get coordinates for searched location
    """ 
    def _get_coordinates(self, location="Tampere"):

        headers = {"User-Agent": "SLT Vibe"}

        response = requests.get(f"{COORDS_URL}{location}&format=json", headers=headers)

        if response.status_code == 200:
            data = response.json()

            if len(data) > 0:
                latitude = data[0]["lat"]
                longitude = data[0]["lon"]
                return latitude, longitude
            else:

                # Location not found
                return None, None
        else:
            print(f"Error: Unable to fetch data (Status Code: {response.status_code})")
            return None, None

    
    
    """
    Uses open meteo API to get temperature, rain amount and weather code for input coords
    """
    def _get_current_weather_from_coords(self, latitude=61.4980214, longitude=23.7603118):
      
        response = requests.get(
            f"{WEATHER_URL}latitude={latitude}&longitude={longitude}&current=temperature_2m,precipitation,weather_code"
        )

        if response.status_code == 200:
            data = response.json()

            current_weather = data.get("current", {})
            temperature = current_weather.get("temperature_2m")
            precipitation = current_weather.get("precipitation")
            weather_code = current_weather.get("weather_code")

            return temperature, precipitation, weather_code
        
        else:
            return None, None, None
        
    """
    Uses open meteo API to create a Forecast object for location in coords and duration of input days
    """
    def _get_forecast_from_coords(self, latitude=61.4980214, longitude=23.7603118, days=1) -> Forecast:
        response = requests.get(
            f"{WEATHER_URL}latitude={latitude}&longitude={longitude}&hourly=temperature_2m,weather_code,precipitation_probability&forecast_days={days}"
        )

        if response.status_code == 200:
            data = response.json()

            hourly_weather = data.get("hourly", {})
            time = hourly_weather.get("time")
            temperature = hourly_weather.get("temperature_2m")
            code = hourly_weather.get("weather_code")
            rain = hourly_weather.get("precipitation_probability")

            return Forecast(time, temperature, code, rain)
