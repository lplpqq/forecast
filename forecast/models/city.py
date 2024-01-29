from __future__ import annotations

import typing
from typing import NamedTuple, Self

from sqlalchemy.orm import Mapped, mapped_column, relationship

from forecast.models.base import Base

if typing.TYPE_CHECKING:
    from forecast.models.location import Location


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


class City(Base):
    __tablename__ = 'city'

    id: Mapped[int] = mapped_column(primary_key=True)
    source_list_id: Mapped[int] = mapped_column(unique=True)

    name: Mapped[str] = mapped_column()
    name_ascii: Mapped[str] = mapped_column()

    latitude: Mapped[float] = mapped_column()
    longitude: Mapped[float] = mapped_column()

    country_name: Mapped[str] = mapped_column()

    iso_code_two: Mapped[str] = mapped_column()
    iso_code_three: Mapped[str] = mapped_column()

    population: Mapped[int] = mapped_column()

    locations: Mapped[list[Location]] = relationship(back_populates='city')

    @classmethod
    def from_city_named_tuple(cls, data: CityTuple) -> Self:
        new_city = cls(
            source_list_id=data.id,
            name=data.city,
            name_ascii=data.city_ascii,
            latitude=data.lat,
            longitude=data.lng,
            country_name=data.country,
            iso_code_two=data.iso2,
            iso_code_three=data.iso3,
            population=data.population,
        )

        return new_city
