from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select

from forecast.api.dependencies.db_session import InjectedDBSesssion
from forecast.db.models import City

router = APIRouter(prefix='/cities')

DEFAULT_RESULT_COUNT = 5


class CityEntry(BaseModel):
    name: str
    country: str


class CitiesSearchResponse(BaseModel):
    cities: list[CityEntry]


@router.get('/search')
async def get_cities(
    db_session: InjectedDBSesssion, query: str = Query()
) -> CitiesSearchResponse:
    if len(query) < 3:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail='You may not search, unless the query is longer than 2 characters',
        )

    search_query = (
        select(City.name, City.country_name)
        .where(City.name.ilike(f'{query}%'))
        .order_by(City.population.desc())
        .limit(DEFAULT_RESULT_COUNT)
    )

    query_data = await db_session.execute(search_query)

    return CitiesSearchResponse(
        cities=[CityEntry(name=city[0], country=city[1]) for city in query_data]
    )
