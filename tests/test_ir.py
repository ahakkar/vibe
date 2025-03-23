import pytest
from backend.ir import IrService 

class TestIrService:
    def setup_method(self):
        """Setup method to run before each test."""
        self.ir_service = IrService()

    @pytest.mark.parametrize(
        "text, expected_intent",
        [
            ("kerro päivän uutiset", "HaeUutiset"),
            ("kerro tämän päivän uutiset", "HaeUutiset"),
        ],
    )
    def test_recognize_intent_news(self, text, expected_intent):
        """Test intent recognition for news requests."""
        result = self.ir_service.recognize_intent(text, "fi")
        assert result["intent"].name == expected_intent 
        

    @pytest.mark.parametrize(
        "text, expected_intent",
        [
            ("paljonko kello on", "HaeKellonaika"),
            ("kuinka paljo kello on", "HaeKellonaika"),
            ("mitä kello on", "HaeKellonaika"),
        ],
    )
    def test_recognize_intent_time(self, text, expected_intent):
        """Test intent recognition for time requests with multiple inputs."""
        result = self.ir_service.recognize_intent(text, "fi")
        assert result["intent"].name == expected_intent



