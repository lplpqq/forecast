from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select

from forecast.api.dependencies import InjectedDBSesssion
from forecast.api.dependencies.closest_city_provider import ClosestCityProvider
from forecast.api.models.weather import WeatherData, WeatherResponse
from forecast.db.models import City, WeatherJournal
from forecast.logging import logger_provider

router = APIRouter(prefix='/weather')


PAGE_SIZE = 500


logger = logger_provider(name)
closest_city_provider = ClosestCityProvider()


@router.get('/')
async def get_weather(
    session: InjectedDBSesssion,
    from_date: datetime = Query(alias='from'),
    to_date: datetime = Query(alias='to'),
    city: City = Depends(closest_city_provider),
    cursor: datetime | None = Query(default=None),
) -> WeatherResponse:
    if from_date > to_date:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail='from should be earlier in time to'
        )

    from_date = from_date.replace(tzinfo=None)
    to_date = to_date.replace(tzinfo=None)

    logger.info(f'Fetching further data for: {city.name}')

    history_query = (
        select(
            WeatherJournal.date,
            func.avg(WeatherJournal.temperature).label('temperature'),
            func.avg(WeatherJournal.pressure).label('pressure'),
            func.avg(WeatherJournal.wind_speed).label('wind_speed'),
            func.avg(WeatherJournal.wind_direction).label('wind_direction'),
            func.avg(WeatherJournal.humidity).label('humidity'),
            func.avg(WeatherJournal.precipitation).label('precipitation'),
            func.avg(WeatherJournal.snow).label('snow'),
        )
        .where(
            WeatherJournal.date >= (cursor or from_date),
            WeatherJournal.date <= to_date,
            WeatherJournal.city_id == city.id,
            WeatherJournal.precipitation.isnot(None),
            WeatherJournal.snow.isnot(None),
        )
        .group_by(WeatherJournal.date)
        .order_by(WeatherJournal.date)
        .limit(PAGE_SIZE + 1)
    )

    history = (await session.execute(history_query)).all()
    data = [WeatherData.model_validate(model._mapping) for model in history]

    next_date = None
    if len(data) > 0:
        last_item = data.pop(-1)
        next_date = last_item.date

    return WeatherResponse(data=data[: PAGE_SIZE + 1], next_date=next_date)