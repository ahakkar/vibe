import pytest

from pathlib import Path
from unittest.mock import MagicMock, patch
from src.backend.local.yle import YleNewsApi


class TestYleNewsApi:
    def setup_method(self):
        """Setup method to run before each test."""
        self.root = Path(__file__).parent.parent / "src" / "backend"
        with patch("pathlib.Path.__new__", return_value=self.root):
            self.yle_news_api = YleNewsApi()

    def teardown_method(self):
        """ """
        pass
