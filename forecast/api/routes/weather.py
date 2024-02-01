from datetime import datetime

import sqlalchemy
from fastapi import APIRouter, Depends, HTTPException, Query, status

from forecast.api.dependencies import InjectedDBSesssion
from forecast.api.dependencies.closest_city_provider import ClosestCityProvider
from forecast.api.models.weather import WeatherData, WeatherResponse
from forecast.db.models import City
from forecast.logging import logger_provider

router = APIRouter(prefix='/weather')


PAGE_SIZE = 500


logger = logger_provider(__name__)
closest_city_provider = ClosestCityProvider()


HISTORY_REQUEST = sqlalchemy.text(
    f"""
select
    wj.date,
    count(wj.id) as merge_rows_count,
    avg(wj.temperature) as temperature,
    avg(wj.pressure) as pressure,
    avg(wj.wind_speed) as wind_speed,
    avg(wj.wind_direction) as wind_direction,
    avg(wj.humidity) as humidity,
    avg(wj.precipitation) as precipitation,
    avg(wj.snow) as snow
from weather_journal wj
join city c on wj.city_id = c.id
where
    wj.precipitation <> 'NaN'::numeric and
    wj.date >= :from_date and
    wj.date <= :to_date and
    c.latitude = :city_latitude and
    c.longitude = :city_longitude
group by wj.date
order by wj.date
limit {PAGE_SIZE + 1};
"""
)


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
            status.HTTP_400_BAD_REQUEST, detail='from should be eariler in time to'
        )

    logger.info(f'Fetching feather data for: {city.name}')

    history = (
        await session.execute(
            HISTORY_REQUEST,
            {
                'from_date': cursor or from_date,
                'to_date': to_date,
                'city_latitude': city.latitude,
                'city_longitude': city.longitude,
            },
        )
    ).all()
    data = [WeatherData.model_validate(model._mapping) for model in history]

    next_date = None
    if len(data) > 0:
        last_item = data.pop(-1)
        next_date = last_item.date

    return WeatherResponse(data=data[: PAGE_SIZE + 1], next_date=next_date)
