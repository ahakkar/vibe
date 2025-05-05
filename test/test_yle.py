import pytest

from pathlib import Path
from unittest.mock import MagicMock, patch
from src.backend.local.yle import YleNewsApi, YlePage
import test.yle_test_consts as consts


class TestYlePage:
    def setup_method(self):
        """Setup method to run before each test."""
        self.root = Path(__file__).parent.parent / "src" / "backend"
        with patch("pathlib.Path.__new__", return_value=self.root):
            self.app = MagicMock()
            self.yle_page = YlePage(self.app)

    def teardown_method(self):
        pass

    def test_init_yle_page(self):
        assert isinstance(self.yle_page.subpages, dict)
        assert isinstance(self.yle_page.content, list)
        assert self.yle_page.app == self.app

    def test_add_subpage(self):
        title = "kotimaa"
        page_number = 1
        self.yle_page._add_subpage(title, page_number)
        assert len(self.yle_page.subpages) == 1
        assert self.yle_page.subpages[title] == page_number

    def test_add_content(self):
        line = 1
        self.yle_page._add_content(line)
        assert len(self.yle_page.content) == line
        assert self.yle_page.content[-1] == line

    def test_get_titles(self):
        title = "kotimaa"
        page_number = 1
        self.yle_page._add_subpage(title, page_number)
        result_list = self.yle_page._get_titles()
        assert result_list == [title]

    def test_get_titles_emtpy(self):
        result_list = self.yle_page._get_titles()
        assert result_list == []
    

    def test_get_content(self):
        line = 1
        self.yle_page._add_content(line)
        content = self.yle_page._get_content()
        assert content == [1]

    def test_get_content_empty(self):
        content = self.yle_page._get_content()
        assert content == []

    def test_find_page_from_input(self):
        pass


class TestYleNewsApi:
    def setup_method(self):
        """Setup method to run before each test."""
        self.root = Path(__file__).parent.parent / "src" / "backend"
        with patch("pathlib.Path.__new__", return_value=self.root):
            self.app = MagicMock()
            self.yle_news_api = YleNewsApi(self.app)

    def fake_baseform(self, word):
        if word == "pääuutiset":
            return "pääuutinen"
        elif word == "urheilusta":
            return "urheilu"
        else:
            return word

    def test_get_instruction_string(self):

        result = self.yle_news_api.get_instruction_string()

        assert (
            result
            == "Mistä aiheesta haluat kuulla uutisia: pääuutiset, kotimaa, ulkomaat, talous vai urheilu?"
        )

    def test_parse_user_input(self):

        self.app.get_service.return_value.get_baseform.side_effect = self.fake_baseform
        self.yle_news_api._get_news = MagicMock(return_value=consts.TEST_NEWS_LIST)

        result = self.yle_news_api.parse_user_input("Kerro pääuutiset")

        assert result == consts.TEST_NEWS_LIST

    def test_parse_user_input_fail(self):
        self.app.get_service.return_value.get_baseform.side_effect = self.fake_baseform

        result = self.yle_news_api.parse_user_input("Kerro uutiset aiheesta ei ole")

        assert result == consts.TEST_FAIL_LIST

    def teardown_method(self):
        """ """
        pass
