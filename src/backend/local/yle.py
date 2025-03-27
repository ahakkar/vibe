import requests
import json

APP_ID = ""
APP_KEY = ""
ADDRESS = "https://external.api.yle.fi/v1/teletext/pages/"

class YleNewsApi:

    def get_page_data(self, page_number=100):
        url = f"{ADDRESS}{page_number}.json?app_id={APP_ID}&app_key={APP_KEY}"
        try:
            response = requests.get(url)
            response.raise_for_status()  # Bad responses error
            return response.json()  
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Yle data: {e}")
            return None  
        
    def parse_json(self, json_data):
        """
        """        
        teletext = json_data["teletext"]["page"]["subpage"][0]
        content = teletext["content"][0]
        lines = content["line"]

        for line in lines:
            for _, value in line.items():
                if len(value) > 2:
                    print(value)