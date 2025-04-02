import pytest

from pathlib import Path
from unittest.mock import MagicMock, patch
from src.backend.local.ir_service import IrService


class TestIrService:

    def setup_method(self):
        """Setup method to run before each test."""
        self.app = MagicMock()
        self.root = Path(__file__).parent.parent / "src" / "backend"
        with patch("pathlib.Path.__new__", return_value=self.root):
            self.ir_service = IrService(self.app)

    def teardown_method(self):
        """ """
        pass

    @pytest.mark.unit
    @pytest.mark.parametrize(
        "text, expected_intent",
        [
            ("kerro päivän uutiset", "GetNews"),
            ("kerro tämän päivän uutiset", "GetNews"),
        ],
    )
    def test_recognize_intent_news(self, text, expected_intent):
        """Test intent recognition for news requests."""
        result = self.ir_service.recognize_intent(text, "fi")
        assert result.intent.name == expected_intent

    @pytest.mark.skip()
    @pytest.mark.unit
    @pytest.mark.parametrize(
        "text, expected_intent",
        [
            ("paljonko kello on", "GetTime"),
            ("kuinka paljo kello on", "GetTime"),
            ("mitä kello on", "GetTime"),
        ],
    )
    def test_recognize_intent_time(self, text, expected_intent):
        """Test intent recognition for time requests with multiple inputs."""
        result = self.ir_service.recognize_intent(text, "fi")
        assert result.intent.name == expected_intent
