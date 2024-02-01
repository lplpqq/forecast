from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select

from forecast.api.dependencies import InjectedDBSesssion
from forecast.api.dependencies.closest_city_provider import ClosestCityProvider
from forecast.api.models.weather import WeatherData, WeatherResponse
from forecast.db.models import City, WeatherJournal
from forecast.logging import logger_provider

router = APIRouter(prefix='/weather')


PAGE_SIZE = 500


logger = logger_provider(__name__)
closest_city_provider = ClosestCityProvider()


@router.get('/')
async def get_weather(
    session: InjectedDBSesssion,
    from_date: datetime = Query(alias='from'),
    to_date: datetime = Query(alias='to'),
    cursor_id: int = Query(default=0),
    city: City = Depends(closest_city_provider),
) -> WeatherResponse:
    if from_date > to_date:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail='from should be eariler in time to'
        )

    logger.info(f'Fetching feather data for: {city.name}')

    # TODO: group by and average. Try to implement media, use average if isn't going to work
    history_request = (
        select(
            WeatherJournal,
        )
        .where(
            WeatherJournal.date >= from_date,
            WeatherJournal.date <= to_date,
            City.latitude == city.latitude,
            City.longitude == city.longitude,
            WeatherJournal.id >= cursor_id,
        )
        .join(City)
        .order_by(WeatherJournal.date)
        .limit(PAGE_SIZE)
    )

    history = (await session.scalars(history_request)).all()
    data = [WeatherData.model_validate(model) for model in history]

    next_cursor_id = data[-1].id + 1 if len(data) > 0 else None
    return WeatherResponse(data=data, next_cursor_id=next_cursor_id)
