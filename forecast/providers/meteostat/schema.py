from typing import TypeAlias, TypedDict


class Name(TypedDict):
    en: str


class Identifiers(TypedDict):
    national: str
    wmo: str | None
    icao: str | None


class Location(TypedDict):
    latitude: float
    longitude: float
    elevation: int


class Model(TypedDict):
    start: str
    end: str


class Hourly(TypedDict):
    start: str | None
    end: str | None


class Daily(TypedDict):
    start: str
    end: str


class Monthly(TypedDict):
    start: int
    end: int


class Normals(TypedDict):
    start: int | None
    end: int | None


class Inventory(TypedDict):
    model: Model
    hourly: Hourly
    daily: Daily
    monthly: Monthly
    normals: Normals


class MeteostatStation(TypedDict):
    id: str
    name: Name
    country: str
    region: str
    identifiers: Identifiers
    location: Location
    timezone: str
    inventory: Inventory


MeteostatStations: TypeAlias = list[MeteostatStation]
