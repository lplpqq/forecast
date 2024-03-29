from __future__ import annotations

import typing
from datetime import datetime
from typing import Self

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from forecast.db.models.base import Base
from forecast.providers.models import Weather

if typing.TYPE_CHECKING:
    from forecast.db.models.city import City


class WeatherJournal(Base):
    __tablename__ = 'weather_journal'
    # __table_args__ = (
    #     Index('idx_weather_journal_date', 'date'),
    #     Index('idx_weather_journal_temperature', 'temperature'),
    #     Index('idx_weather_journal_precipitation', 'precipitation'),
    # )

    id: Mapped[int] = mapped_column(primary_key=True)

    data_source: Mapped[str] = mapped_column()
    date: Mapped[datetime] = mapped_column(DateTime, index=True)
    temperature: Mapped[float] = mapped_column(nullable=True, index=True)
    pressure: Mapped[float] = mapped_column(nullable=True)
    wind_speed: Mapped[float] = mapped_column(nullable=True)
    wind_direction: Mapped[float] = mapped_column(nullable=True)
    humidity: Mapped[float] = mapped_column(nullable=True)
    clouds: Mapped[float] = mapped_column(nullable=True)
    precipitation: Mapped[float] = mapped_column(nullable=True, index=True)
    snow: Mapped[float] = mapped_column(nullable=True)

    city_id: Mapped[int] = mapped_column(ForeignKey('city.id'))
    city: Mapped[City] = relationship(back_populates='hourly_history')

    @classmethod
    def from_weather_tuple(cls, weather: Weather, city_id: int) -> Self:
        return cls(
            data_source=weather.data_source,
            date=weather.date,
            temperature=weather.temperature,
            pressure=weather.pressure,
            wind_speed=weather.wind_speed,
            wind_direction=weather.wind_direction,
            humidity=weather.humidity,
            clouds=weather.clouds,
            precipitation=weather.precipitation,
            snow=weather.snow,
            city_id=city_id,
        )
