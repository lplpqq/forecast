from datetime import datetime
from typing import NamedTuple


class Weather(NamedTuple):
    data_source: str

    date: datetime
    temperature: float  # temperature (°C)
    pressure: float  # surface pressure (hPa)
    wind_speed: float  # wind speed (m/s)
    wind_direction: float  # wind direction (degrees)
    humidity: float  # humidity (%)
    clouds: int  # cloud coverage (%)
    precipitation: float  # accumulated liquid equivalent precipitation (mm)
    snow: int  # accumulated snowfall (mm)
