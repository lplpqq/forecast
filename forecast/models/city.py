from __future__ import annotations

import typing
from typing import NamedTuple, Self

from geoalchemy2.types import Geography
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

    name: Mapped[str] = mapped_column()
    name_ascii: Mapped[str] = mapped_column()
    center_location: Mapped[Geography] = mapped_column(
        Geography(geometry_type='POINT', srid=4326)
    )
    country_name: Mapped[str] = mapped_column()

    iso_code_two: Mapped[str] = mapped_column()
    iso_code_three: Mapped[str] = mapped_column()

    population: Mapped[int] = mapped_column()

    locations: Mapped[list[Location]] = relationship(back_populates='city')

    @classmethod
    def from_city_named_tuple(cls, data: CityTuple) -> Self:
        new_city = cls(
            name=data.city,
            name_ascii=data.city_ascii,
            center_location=f'POINT({data.lat} {data.lng})',
            country_name=data.country,
            iso_code_two=data.iso2,
            iso_code_three=data.iso3,
            population=data.population,
        )

        return new_city
