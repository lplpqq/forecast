from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from forecast.db.models import City


class CitiesProvider:
    def __init__(self):
        self._cities: list[City] | None = []

    async def fetch_cities_and_cache(self, session: AsyncSession) -> None:
        self._cities = list((await session.scalars(select(City))).all())

    async def __call__(self, *args, **kwargs):
        if self._cities is None:
            await self.fetch_cities_and_cache()

        return self._cities


cities_provider = CitiesProvider()
InjectedCities = Annotated[list[City], Depends(cities_provider)]
