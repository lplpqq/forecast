from typing import NamedTuple


class CityTuple(NamedTuple):
    city: str
    latitude: float
    longitude: float
    country: str
    population: int
