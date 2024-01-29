from __future__ import annotations

import typing

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm.properties import ForeignKey

from forecast.models.base import Base
from forecast.models.city import City

if typing.TYPE_CHECKING:
    from forecast.models.historical_hourly_weather import HistoricalHourlyWeather


class Location(Base):
    __tablename__ = 'location'

    id: Mapped[int] = mapped_column(primary_key=True)

    latidute: Mapped[float] = mapped_column()
    longitude: Mapped[float] = mapped_column()

    city_id: Mapped[int] = mapped_column(ForeignKey('city.id'))
    city: Mapped[City] = relationship(back_populates='locations')

    hourly_history: Mapped[list[HistoricalHourlyWeather]] = relationship(
        back_populates='location'
    )
