import pytest

from pathlib import Path
from unittest.mock import MagicMock, patch
from src.backend.local.weather import Forecast, Weather
import test.weather_test_consts as weather_constants





class TestWeatherService:
    def setup_method(self):
        """Setup method to run before each test."""
        self.root = Path(__file__).parent.parent / "src" / "backend"
        with patch("pathlib.Path.__new__", return_value=self.root):
            self.weather = Weather()
            self.weather._get_coordinates = MagicMock()
            self.weather._get_current_weather_from_coords = MagicMock()
            self.weather._get_forecast_from_coords = MagicMock()

    def test_get_current_weather_with_none_coords(self):
        self.weather._get_coordinates.return_value = None
        
        result = self.weather.get_current_weather(location="this place does not exist")

        assert result is None

    def test_get_current_weather_no_weather_data(self):
        self.weather._get_coordinates.return_value = (61.4980214, 23.7603118)
        self.weather._get_current_weather_from_coords.return_value = None, None, None

        result = self.weather.get_current_weather(location="Tampere")
        
        assert result == f"Säätietojen hakeminen epäonnistui."

    def test_get_current_weather_success_zero_precipitation(self):
        self.weather._get_coordinates.return_value = (61.4980214, 23.7603118)
        self.weather._get_current_weather_from_coords.return_value = 10.0, 0.0, 3

        result = self.weather.get_current_weather(location="Tampere")

        assert f"Paikassa Tampere on pilvistä, 10.0 astetta celsiusta."

    def test_get_current_weather_success_some_precipitation(self):
        self.weather._get_coordinates.return_value = (61.4980214, 23.7603118)
        self.weather._get_current_weather_from_coords.return_value = 10.0, 2.0, 3

        result = self.weather.get_current_weather(location="Tampere")

        assert f"Paikassa Tampere on pilvistä, 10.0 astetta celsiusta. Sateen määrä 2.0 millimetriä."

    def test_get_forecast_too_many_skip_days(self):
        
        result = self.weather.get_forecast(location = "Tampere", days = 1, skip_days = 3, frequency = 3)

        assert result is None

    def test_get_forecast_equal_days_skip_days(self):
        
        result = self.weather.get_forecast(location = "Tampere", days = 1, skip_days = 1, frequency = 3)

        assert result is None

    def test_get_forecast_no_days(self):
        self.weather._get_coordinates.return_value = (61.4980214, 23.7603118)
        self.weather._get_forecast_from_coords.return_value = Forecast([],[],[],[])

        result = self.weather.get_forecast(location = "Tampere", days = 0, skip_days = -1, frequency = 3)

        assert result == []

    def test_get_forecast_no_coords(self):
        self.weather._get_coordinates.return_value = None
        
        result = self.weather.get_forecast(location = "Not a real place", days = 1, skip_days = 0, frequency = 3)
        
        assert result is None

    def test_get_forecast_no_forecast(self):
        self.weather._get_coordinates.return_value = (61.4980214, 23.7603118)
        self.weather._get_forecast_from_coords.return_value = None
        
        result = self.weather.get_forecast(location = "Tampere", days = 1, skip_days = 0, frequency = 3)

        assert result is None


    #TODO: Figure a way to fix the tests to work without being dependant on current time
    """ def test_get_forecast_single_success(self):

            self.weather._get_coordinates.return_value = (61.4980214, 23.7603118)

            self.weather._get_forecast_from_coords.return_value = Forecast(weather_constants.TEST_TIMES_24,
                                                                        weather_constants.TEST_TEMPERATURES_24,
                                                                        weather_constants.TEST_WEATHER_CODES_24,
                                                                        weather_constants.TEST_PRECIPITATION_ZEROS_24)

            result = self.weather.get_forecast(location = "Tampere", days = 1, skip_days = 0, frequency = 6)

            assert result == ["Kello 0: pilvistä, 0.0 astetta celsiusta.",
                            "Kello 6: pilvistä, 0.0 astetta celsiusta.",
                            "Kello 12: pilvistä, 0.0 astetta celsiusta.",
                            "Kello 18: pilvistä, 0.0 astetta celsiusta."]
    

    def test_get_forecast_single_success_with_rain(self):

        
            self.weather._get_coordinates.return_value = (61.4980214, 23.7603118)

            self.weather._get_forecast_from_coords.return_value = Forecast(weather_constants.TEST_TIMES_24,
                                                                            weather_constants.TEST_TEMPERATURES_24,
                                                                            weather_constants.TEST_WEATHER_CODES_24,
                                                                            weather_constants.TEST_PRECIPITATION_TENS_24)

            result = self.weather.get_forecast(location = "Tampere", days = 1, skip_days = 0, frequency = 6)

            assert result == ["Kello 0: pilvistä, 0.0 astetta celsiusta. Sateen todennäköisyys 10 prosenttia.",
                                "Kello 6: pilvistä, 0.0 astetta celsiusta. Sateen todennäköisyys 10 prosenttia.",
                                "Kello 12: pilvistä, 0.0 astetta celsiusta. Sateen todennäköisyys 10 prosenttia.",
                                "Kello 18: pilvistä, 0.0 astetta celsiusta. Sateen todennäköisyys 10 prosenttia."] """
        
    def teardown_method(self):
        """ """
        pass
