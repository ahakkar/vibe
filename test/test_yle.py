import pytest

from pathlib import Path
from unittest.mock import MagicMock, patch
from src.backend.local.yle import YleNewsApi
import test.yle_test_consts as consts


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

        assert result == "Mistä aiheesta haluat kuulla uutisia: pääuutiset, kotimaa, ulkomaat, talous vai urheilu?"

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

