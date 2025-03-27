import requests

coords_url = "https://nominatim.openstreetmap.org/search?city="
weather_url = "https://api.open-meteo.com/v1/forecast?"

#Only gets current temperature for now

class Weather:

    def get_current_weather(self, location="Tampere") -> str:

        latitude, longitude = self._get_coordinates(location=location)

        temperature = self._get_weather_from_coords(longitude=longitude, latitude=latitude)

        if temperature is None:
            return "Lämpötilan haku epäonnistui."
        else:
            return f"Nykyinen lämpötila paikassa {location} on {temperature} astetta celsiusta"

    def _get_coordinates(self, location="Tampere"):

        headers = {
            "User-Agent": "SLT Vibe"
        }

        response = requests.get(f"{coords_url}{location}&format=json", headers=headers)
        
        if response.status_code == 200:
            data = response.json()

            if len(data) > 0:
                latitude = data[0]["lat"]
                longitude = data[0]["lon"]
                return latitude, longitude
            else:
                
                #Location not found
                return None, None
        else:
            print(f"Error: Unable to fetch data (Status Code: {response.status_code})")
            return None, None
        
    #Default coords for tampere
    def _get_weather_from_coords(self, latitude=61.4980214, longitude=23.7603118):
        response = requests.get(f"{weather_url}latitude={latitude}&longitude={longitude}&current_weather=true")

        if response.status_code == 200:
            data = response.json()

            current_weather = data.get("current_weather", {})
            temperature = current_weather.get("temperature")
            
            return temperature
