import pytest

from pathlib import Path
from unittest.mock import MagicMock, patch, call
from src.backend.local.ir_service import IrService
from abstract_classes import IntentRecognitionInterface


class MockIntent:
    def __init__(self):
        self.name = None


class MockRecognizeResult:
    def __init__(self):
        self.intent = MockIntent()


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

    @pytest.mark.unit()
    def test_irservice_init(self):
        assert isinstance(self.ir_service, IntentRecognitionInterface)
        assert self.ir_service.app is not None
        assert self.ir_service.logger is not None
        assert self.ir_service.intents is not None

    @pytest.mark.unit()
    @pytest.mark.parametrize(
        "text, expected_intent",
        [
            ("kerro päivän uutiset", "GetNews"),
            ("kerro tämän päivän uutiset", "GetNews"),
            ("kerro lisää", "GetNews"),
            ("lue uutinen kotimaasta", "GetNews"),
            ("kerro uutinen ulkomaasta", "GetNews"),
        ],
    )
    def test_recognize_intent_news(self, text, expected_intent):
        """Test intent recognition for news requests."""
        result = self.ir_service.recognize_intent(text, "fi")
        assert result.intent.name == expected_intent

    @pytest.mark.unit()
    @pytest.mark.parametrize(
        "text, expected_intent",
        [
            ("millainen sää on", "GetCurrentWeather"),
            ("millainen sää on nyt", "GetCurrentWeather"),
        ],
    )
    def test_recognize_intent_current_weather(self, text, expected_intent):
        """
        Test intent recognition for current weather requests with multiple inputs.
        """
        result = self.ir_service.recognize_intent(text, "fi")
        assert result.intent.name == expected_intent

    @pytest.mark.unit()
    @pytest.mark.parametrize(
        "text, expected_intent",
        [
            ("millainen sää on nyt Tamperella", "GetCurrentWeatherAtLocation"),
            ("millainen sää on nyt Helsingissä", "GetCurrentWeatherAtLocation"),
            ("millainen sää on nyt Espanja", "GetCurrentWeatherAtLocation"),
            ("millainen sää on nyt Parisissa Ranska", "GetCurrentWeatherAtLocation"),
        ],
    )
    def test_recognize_intent_current_weather_at_location(self, text, expected_intent):
        """
        Test intent recognition for current weather at location requests with multiple inputs.
        """
        result = self.ir_service.recognize_intent(text, "fi")
        assert result.intent.name == expected_intent

    @pytest.mark.unit()
    @pytest.mark.parametrize(
        "text, expected_intent",
        [
            ("millainen sää on ylihuomenna", "GetForecast"),
            ("millainen sää on tällä viikolla", "GetForecast"),
        ],
    )
    def test_recognize_intent_forecast(self, text, expected_intent):
        """
        Test intent recognition for forecast requests with multiple inputs.
        """
        result = self.ir_service.recognize_intent(text, "fi")
        assert result.intent.name == expected_intent

    @pytest.mark.unit()
    @pytest.mark.parametrize(
        "text, expected_intent",
        [
            ("millainen sää on huomenna Helsingissä", "GetForecastAtLocation"),
            ("millainen sää on tällä viikolla Espanja", "GetForecastAtLocation"),
            ("millainen sää on tänään Parisissa Ranska", "GetForecastAtLocation"),
        ],
    )
    def test_recognize_intent_forecast_at_location(self, text, expected_intent):
        """
        Test intent recognition for forecast at location requests with multiple inputs.
        """
        result = self.ir_service.recognize_intent(text, "fi")
        assert result.intent.name == expected_intent

    @pytest.mark.unit()
    @pytest.mark.parametrize(
        "text, expected_intent",
        [
            ("paljonko kello on", "GetTime"),
            ("kuinka paljon kello on", "GetTime"),
            ("mitä kello on", "GetTime"),
        ],
    )
    def test_recognize_intent_time(self, text, expected_intent):
        """Test intent recognition for time requests with multiple inputs."""
        result = self.ir_service.recognize_intent(text, "fi")
        assert result.intent.name == expected_intent

    @pytest.mark.unit()
    @pytest.mark.parametrize("name", [None, "GetIncorrect"])
    def test_process_intent_incorrect_intent_name(self, name):
        mockRecognizeResult = MockRecognizeResult()
        mockRecognizeResult.intent.name = name
        result = self.ir_service.process_intent(mockRecognizeResult)
        assert result == f"Tuntematon intent havaittu: {name}"

    @pytest.mark.unit()
    def test_process_intent_news(self):
        mockRecognizeResult = MockRecognizeResult()
        mockRecognizeResult.intent.name = "GetNews"
        with patch.object(self.ir_service.logger, "info", return_value=None):
            result = self.ir_service.process_intent(mockRecognizeResult, "some")
            # assert self.ir_service.logger.info.call_count == 3
            # calls = [
            #     call("PERF : [News] Fetching news"),
            #     call("PERF : [News] Done fetching news"),
            #     call("Tuntematon intent havaittu: GetNews"),
            # ]
            # self.ir_service.logger.info.assert_has_calls(calls)
            assert result is None
