from __future__ import annotations

import typing
from typing import Self

from sqlalchemy.orm import Mapped, mapped_column, relationship

from forecast.db.models.base import Base

if typing.TYPE_CHECKING:
    from forecast.db.models import WeatherJournal
    from forecast.services.models.city import CityTuple


class City(Base):
    __tablename__ = 'city'

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column()
    latitude: Mapped[float] = mapped_column()
    longitude: Mapped[float] = mapped_column()
    country_name: Mapped[str] = mapped_column()
    population: Mapped[int] = mapped_column()

    hourly_history: Mapped[list[WeatherJournal]] = relationship(
        back_populates='city'
    )

    @classmethod
    def from_city_named_tuple(cls, data: CityTuple) -> Self:
        # NOTE: I am not sure if it will be fast enough, consider reordering the df columns in a similar fashion done in the metoestat provider as well as the weather history model
        new_city = cls(
            name=data.city,
            latitude=data.latitude,
            longitude=data.longitude,
            country_name=data.country,
            population=data.population,
        )

        return new_city
