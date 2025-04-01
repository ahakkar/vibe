import pytest

from pathlib import Path
from unittest.mock import MagicMock, patch
from src.backend.local.weather import Forecast, Weather

class TestWeatherService:
    def setup_method(self):
        """Setup method to run before each test."""
        self.app = MagicMock()
        self.root = Path(__file__).parent.parent / "src" / "backend"
        with patch("pathlib.Path.__new__", return_value=self.root):
            self.ir_service = Weather(self.app)

    def teardown_method(self):
        """ """
        pass

