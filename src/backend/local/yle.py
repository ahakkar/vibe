import logging
from typing import Any, Dict, Optional
import requests
import json
import os

from local.constants import TTV_PAGES, TTV_PAGE_NUMS, Srv

# TODO: clean code and fix comments


class YlePage:

    def __init__(self, app):
        """
        Initialize Yle page
        """
        self.subpages = {}
        self.content = []
        self.app = app

    def _add_subpage(self, title: str, page_number: int):
        """
        Add subpage to the subpages dictionary

        :param str title: title of the sub page
        :param int page_number: page number of the subpage
        """
        self.subpages[title] = page_number

    def _add_content(self, line: str):
        """
        Add content's line

        :param str line: The line that will be added
        """
        self.content.append(line)

    def _get_titles(self):
        """
        Get the list of titles
        """
        return_list = []
        for title in self.subpages:
            return_list.append(title)

        return return_list

    def _get_content(self):
        """
        Get the content
        """
        return self.content

    def _find_page_from_input(self, input: str):
        """
        Finds the most similiar article title to user input by simply comparing words
        Returns None if fails to find a related article

        :param str input: The user input
        :return int: The page number for the most similar article
        """


        input_words = input.lower().split()

        #Remove special chars from end of words, eg ":"
        for i, word_check in enumerate(input_words):
            if not word_check[-1].isalpha():
                input_words[i] = word_check[:-1]

            

        input_baseforms = set(self.app.get_service(Srv.BASEFORM).get_baseform(word) for word in input_words)

        most_similiar = None
        most_common_words = 0

        for title in self.subpages:

            title_words = title.lower().split()
            title_baseforms = set(self.app.get_service(Srv.BASEFORM).get_baseform(word) for word in title_words)

            intersection = input_baseforms & title_baseforms

            if len(intersection) > most_common_words:
                most_similiar = title
                most_common_words = len(intersection)

        if most_similiar is not None:
            return self.subpages.get(most_similiar)

        else:
            # print("Failed to find article")
            return None


class YleNewsApi:

    def __init__(self, app):
        """
        Initialize Yle News API
        """
        self.logger = logging.getLogger(__name__)

        self.YLE_APP_ID = os.getenv("YLE_APP_ID")
        self.YLE_APP_KEY = os.getenv("YLE_APP_KEY")
        self.YLE_TTV_URL = os.getenv("YLE_TTV_URL")

        self.app = app

        if not self.YLE_APP_ID:
            self.logger.error(f"[yle.py:__init__] Missing YLE_APP_ID from .env file")

        if not self.YLE_APP_KEY:
            self.logger.error(f"[yle.py:__init__] Missing YLE_APP_KEY from .env file")

        if not self.YLE_TTV_URL:
            self.logger.error(f"[yle.py:__init__] Missing YLE_TTV_URL from .env file")

        self.current_page = None

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

        words = input.lower().split()

        return_list = []

        for word in words:
            # Use baseform of words to deal with different user inputs
            word_baseform = self.app.get_service(Srv.BASEFORM).get_baseform(word)

            if TTV_PAGES.get(word_baseform) is not None:

                tts_list = self._get_news(TTV_PAGES.get(word_baseform))

                return_list.extend(tts_list)

            if self.current_page is not None:

                page_num = self.current_page._find_page_from_input(input=input)

                if page_num is not None:
                    tts_list = self._get_news(page_number=page_num)

                    return_list.extend(tts_list)

        if len(return_list) == 0:
            return_list.append("Anteeksi, en ymmärtänyt mitä uutisia haluat kuulla.")
            return_list.append(self.get_instruction_string())

        return return_list

    def _get_news(self, page_number: int = 100) -> str:
        """
        Gets the teletext news from input page number as a list of strings

        :param int page_number: The page number to get the page data
        """

        page_data = self._get_page_data(page_number=page_number)

        if page_data is None:
            return ["Uutisten hakeminen epäonnistui."]

        else:

            # Updates class variable current_page
            self._parse_json(page_data, page_number=page_number)

            titles = self.current_page._get_titles()

            #Returns the titles from a title/"main" page
            #Currently used main pages listed in TTV_PAGES and TTV_PAGE_NUMS
            #Could be extended
            if len(titles) > 0 and page_number in TTV_PAGE_NUMS:
                titles.append("Haluatko kuulla jostain lisää?")
                return titles
            
            #Other pages have no 
            else:
                return self.current_page._get_content()

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
            self.logger.error(f"[yle.py:_get_page_data]: Error fetching Yle data: {e}")
            return None

    def _parse_json(self, json_data, page_number) -> list[Any]:
        """
        Parse the json data to create an YlePage object
        This is saved as self.current_page


        :param json json_data: The data that needs to be parsed
        :return None
        """
        teletext = json_data["teletext"]["page"]["subpage"][0]
        content = teletext["content"][0]
        lines = content["line"]

        page = YlePage(self.app)

        #If not a main title page save everything as content
        if page_number not in TTV_PAGE_NUMS:
            for line in lines:
                for _, value in line.items():
                    if len(value) > 2:
                        page._add_content(line=value)

        #Otherwise separate into titles and content
        else:
            for line in lines:
                for _, value in line.items():
                    if len(value) > 2:

                        words = value.split()

                        # If line doesnt start with a number save it as content
                        if not words[0].isdigit() or len(words[0]) < 3:
                            page._add_content(line=value)

                        else:

                            i = 0

                            # One line of text can have multiple page numbers
                            # For example: 101 uutiset 160 talous 190 english
                            # Following loop parses these as separate subpages

                            while i < len(words):

                                title = None

                                # Teletext page numbers have 3 digits
                                if words[i].isdigit() and len(words[i]) == 3:
                                    new_page_number = int(words[i])
                                    i += 1

                                    # Add words to title until end of line or another page number is found
                                    while i < len(words) and not (
                                        words[i].isdigit() and len(words[i]) == 3
                                    ):

                                        if title is None:
                                            title = words[i]
                                        else:
                                            title += " "
                                            title += words[i]

                                        i += 1

                                # Ignore one word titles
                                if title is not None and len(title.split()) > 1:
                                    page._add_subpage(
                                        page_number=new_page_number, title=title
                                    )

        self.current_page = page
