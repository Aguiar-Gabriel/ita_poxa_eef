import types
from datetime import datetime
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from data_treatment import get_metar_features

class Dummy:
    def __init__(self, temp=25, dewpt=20, wind_str="N at 10 knots"):
        self.time = datetime(2023, 1, 1, 12, 0, 0)
        self.temp = types.SimpleNamespace(string=lambda unit: f"{temp} C")
        self.dewpt = types.SimpleNamespace(string=lambda unit: f"{dewpt} C")
        self.wind_str = wind_str
        self.wind = lambda: self.wind_str
        self.press = types.SimpleNamespace(string=lambda unit: "1010 mb")
    def peak_wind(self):
        return None
    def wind_shift(self):
        return None
    def visibility(self, m):
        return None
    def runway_visual_range(self, m):
        return None
    def present_weather(self):
        return None
    def sky_conditions(self):
        return None


def test_get_metar_features_prefix():
    metar = Dummy()
    features = get_metar_features(metar, name="pref")
    assert 'pref_wind_gust' in features
    assert 'pref_wind_direction' in features
