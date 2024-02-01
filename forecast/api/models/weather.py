from datetime import datetime

from pydantic import BaseModel


class WeatherData(BaseModel):
    date: datetime
    temperature: float
    pressure: float
    wind_speed: float
    wind_direction: float
    humidity: float
    precipitation: float
    snow: float

    class Config:
        from_attributes = True


class WeatherResponse(BaseModel):
    data: list[WeatherData]
    next_date: datetime | None
