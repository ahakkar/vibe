import requests
import json
import os

from local.baseform import Baseform

# TODO: Move to env
APP_ID = os.getenv("APP_ID")
APP_KEY = os.getenv("APP_KEY")
ADDRESS = "https://external.api.yle.fi/v1/teletext/pages/"

# Currently very short dict of topics and corrensponding teletext pages
# TODO: Move elsewhere
PAGES = {
    "pääuutinen": 100,
    "kotimaa": 102,
    "ulkomaa": 130,
    "talous": 160,
    "urheilu": 201,
}

# TODO: Remove page numbers from returned strings

# TODO: Create a way to access articles based on the page numbers


class YleNewsApi:

    def get_instruction_string(self):
        """
        Example string that can be read for the user when asking for news,
        so that the user knows (current) options in PAGES dict

        return str: Instruction to fetch the news
        """

        return "Mistä aiheesta haluat kuulla uutisia: pääuutiset, kotimaa, ulkomaat, talous vai urheilu?"

    def parse_user_input(self, input):
        """
        Finds from user input what news the user wants to hear (can be multiple topics)
        Returns the teletext page(s) as a list of strings

        :param input: User input what news the user wants to hear

        :return [str]: The teletext page(s)
        """

        b = Baseform()

        words = input.split()

        return_list = []

        for word in words:

            # Use baseform of words to deal with different user inputs
            word_baseform = b.get_baseform(word)

            if PAGES.get(word_baseform) is not None:

                tts_list = self.get_news(PAGES.get(word_baseform))

                return_list.extend(tts_list)

        if len(return_list) == 0:
            return_list.append("Anteeksi, en ymmärtänyt mitä uutisia haluat kuulla.")
            return_list.append(self.get_instruction_string())

        return return_list

    def get_news(self, page_number=100):
        """
        Gets the teletext news from input page number as a list of strings

        :param int page_number: The page number to get the page data
        """

        page_data = self._get_page_data(page_number=page_number)

        if page_data is None:
            return ["Uutisten hakeminen epäonnistui."]

        else:
            return self._parse_json(page_data)

    def get_page_data(self, page_number=100):
        """
        Get the page data from given page number

        :param int page_number: The page number to get the page data

        :return json: The response that get from the api
        """
        url = f"{ADDRESS}{page_number}.json?app_id={APP_ID}&app_key={APP_KEY}"
        try:
            response = requests.get(url)
            response.raise_for_status()  # Bad responses error
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Yle data: {e}")
            return None

    def _parse_json(self, json_data):
        """
        Print the json data

        :param json json_data: The data that needs to be printed
        """
        teletext = json_data["teletext"]["page"]["subpage"][0]
        content = teletext["content"][0]
        lines = content["line"]

        return_list = []

        for line in lines:
            for _, value in line.items():
                if len(value) > 2:
                    return_list.append(value)

        return return_list
