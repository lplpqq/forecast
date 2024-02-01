from datetime import datetime

from pydantic import BaseModel


class WeatherData(BaseModel):
    id: int
    date: datetime
    temperature: float
    # NOTE: Those are nullable, I am not sure whether the projection model will return them as well, therefore, nullable
    # apparent_temperature: float
    pressure: float
    wind_speed: float
    wind_gust_speed: float
    wind_direction: float
    humidity: float
    # clouds: float
    precipitation: float
    snow: float

    class Config:
        from_attributes = True


class WeatherResponse(BaseModel):
    data: list[WeatherData]
    next_cursor_id: int | None
