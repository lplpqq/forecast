from typing import NamedTuple


class CityTuple(NamedTuple):
    city: str
    city_ascii: str
    lat: float
    lng: float
    country: str
    iso2: str
    iso3: str
    admin_name: str
    capital: str
    population: int
    id: str
