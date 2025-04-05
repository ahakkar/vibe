import logging
from typing import Any, Dict, Optional
import requests
import json
import os

from local.constants import TTV_PAGES
from local.baseform import Baseform

#For quick testing
#from baseform import Baseform
#from constants import TTV_PAGES

# TODO: Remove page numbers from returned strings
# TODO: Create a way to access articles based on the page numbers

class YlePage:

    def __init__(self):
        self.subpages = {}
        self.content = []

    def _add_subpage(self, title: str, page_number: int):

        self.subpages[title] = page_number

    def _add_content(self, line: str):

        self.content.append(line)

    def get_titles(self):
        
        return_list = []
        for title in self.subpages:
            return_list.append(title)

    def get_content(self):
        return self.content
    
    #TODO: Improve to use finnwordnet?
    def _find_page_from_input(self, input: str):
        """
        Finds the most similiar article title to user input by simply comparing words
        Returns None if fails to find a related article

        :param str input: The user input
        :return int: The page number for the most similar article
        """


        b = Baseform()

        input_words = input.lower().split()
        input_baseforms = set(b.get_baseform(word) for word in input_words)

        most_similiar = None
        most_common_words = 0


        for title in self.subpages:
            
            title_words = title.lower().split()
            title_baseforms = set(b.get_baseform(word) for word in title_words)

            intersection = input_baseforms & title_baseforms

            if len(intersection) > most_common_words:
                most_similiar = title
                most_common_words = len(intersection)

        if most_similiar is not None:
            return self.subpages.get(most_similiar)
        
        else:
            print("Failed to find article")
            return None
    
        
            






class YleNewsApi:

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        self.YLE_APP_ID = os.getenv("YLE_APP_ID")
        self.YLE_APP_KEY = os.getenv("YLE_APP_KEY")
        self.YLE_TTV_URL = os.getenv("YLE_TTV_URL")

        if not self.YLE_APP_ID:
            self.logger.error(f"[yle.py:__init__] Missing YLE_APP_ID from .env file")

        if not self.YLE_APP_KEY:
            self.logger.error(f"[yle.py:__init__] Missing YLE_APP_KEY from .env file")

        if not self.YLE_TTV_URL:
            self.logger.error(f"[yle.py:__init__] Missing YLE_TTV_URL from .env file")

    def get_instruction_string(self) -> str:
        """
        Example string that can be read for the user when asking for news,
        so that the user knows (current) options in TTV_PAGES dict

        return str: Instruction to fetch the news
        """

        return "Mistä aiheesta haluat kuulla uutisia: pääuutiset, kotimaa, ulkomaat, talous vai urheilu?"

    def parse_user_input(self, input: str) -> list:
        """
        Finds from user input what news the user wants to hear (can be multiple topics)
        Returns the teletext page(s) as a list of strings

        :param input: User input what news the user wants to hear

        :return list: The teletext page(s)
        """

        b = Baseform()

        words = input.lower().split()

        return_list = []

        for word in words:
            # Use baseform of words to deal with different user inputs
            word_baseform = b.get_baseform(word)

            if TTV_PAGES.get(word_baseform) is not None:

                tts_list = self.get_news(TTV_PAGES.get(word_baseform))

                return_list.extend(tts_list)

        if len(return_list) == 0:
            return_list.append("Anteeksi, en ymmärtänyt mitä uutisia haluat kuulla.")
            return_list.append(self.get_instruction_string())

        return return_list

    def get_news(self, page_number: int = 100) -> str:
        """
        Gets the teletext news from input page number as a list of strings

        :param int page_number: The page number to get the page data
        """

        page_data = self._get_page_data(page_number=page_number)

        if page_data is None:
            return ["Uutisten hakeminen epäonnistui."]

        else:
            
            return self._parse_json(page_data)

    def _get_page_data(self, page_number: int = 100) -> Optional[Dict[str, Any]]:
        """
        Get the page data from given page number

        :param int page_number: The page number to get the page data

        :return json: The response that get from the api
        """
        url = f"{self.YLE_TTV_URL}{page_number}.json?app_id={self.YLE_APP_ID}&app_key={self.YLE_APP_KEY}"
        try:
            response = requests.get(url)
            response.raise_for_status()  # Bad responses error
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"[yle.py:_get_page_data: Error fetching Yle data: {e}")
            return None

    def _parse_json(self, json_data) -> list[Any]:
        """
        Print the json data

        :param json json_data: The data that needs to be printed
        :return YlePage: returns yle page object
        """
        teletext = json_data["teletext"]["page"]["subpage"][0]
        content = teletext["content"][0]
        lines = content["line"]

        page = YlePage()
        


        for line in lines:
            for _, value in line.items():
                if len(value) > 2:
                    
                    words = value.split()

                    if words[0].isdigit():
                        title = ' '.join(words[1:])                        
                        page._add_subpage(title=title, page_number=int(words[0]))

                    else:
                        page._add_content(line = value)

        return page
    
