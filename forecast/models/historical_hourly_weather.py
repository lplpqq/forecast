from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from forecast.models.base import Base
from forecast.models.location import Location


class HistoricalHourlyWeather(Base):
    __tablename__ = 'hitstorical_hourly_weather'

    id: Mapped[int] = mapped_column(primary_key=True)

    date: Mapped[datetime] = mapped_column(DateTime)
    pressure: Mapped[float] = mapped_column()
    wind_speed: Mapped[float] = mapped_column()
    wind_gust_speed: Mapped[float] = mapped_column()
    wind_dir: Mapped[float] = mapped_column()
    temperature: Mapped[float] = mapped_column()
    feelslike_temp: Mapped[float] = mapped_column()
    humidity: Mapped[float] = mapped_column()
    clouds: Mapped[float] = mapped_column()
    visibility: Mapped[float] = mapped_column()
    precipitation: Mapped[float] = mapped_column()
    snow: Mapped[float] = mapped_column()

    location_id: Mapped[int] = mapped_column(ForeignKey('location.id'))
    location: Mapped[Location] = relationship(back_populates='hourly_history')
