from __future__ import annotations

from datetime import datetime
from typing import Self

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from forecast.db.models.base import Base
from forecast.db.models.location import Location
from forecast.providers.models import Weather


class HistoricalHourlyWeather(Base):
    __tablename__ = 'hitstorical_hourly_weather'

    id: Mapped[int] = mapped_column(primary_key=True)
    data_source: Mapped[str] = mapped_column()

    date: Mapped[datetime] = mapped_column(DateTime)
    temperature: Mapped[float] = mapped_column()
    apparent_temperature: Mapped[float] = mapped_column(nullable=True)
    pressure: Mapped[float] = mapped_column()
    wind_speed: Mapped[float] = mapped_column()
    wind_gust_speed: Mapped[float] = mapped_column()
    wind_direction: Mapped[float] = mapped_column()
    humidity: Mapped[float] = mapped_column()
    clouds: Mapped[float] = mapped_column(nullable=True)
    precipitation: Mapped[float] = mapped_column()
    snow: Mapped[float] = mapped_column()

    location_id: Mapped[int] = mapped_column(ForeignKey('location.id'))
    location: Mapped[Location] = relationship(back_populates='hourly_history')

    @classmethod
    def from_weather_tuple(cls, base: Weather, location_id: int) -> Self:
        return cls(**base._asdict(), location_id=location_id)
