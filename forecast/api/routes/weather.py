from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select

from forecast.api.dependencies import InjectedDBSesssion
from forecast.api.models.weather import WeatherData, WeatherResponse
from forecast.db.models import WeatherJournal

router = APIRouter(prefix='/weather')


PAGE_SIZE = 500


@router.get('/')
async def get_weather(
    session: InjectedDBSesssion,
    from_date: datetime = Query(alias='from'),
    to_date: datetime = Query(alias='to'),
    cursor_id: int = Query(default=0),
) -> WeatherResponse:
    if from_date.timestamp() > to_date.timestamp():
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail='from should be eariler in time to'
        )

    # TODO: group by and average. Try to implement media, use average if isn't going to work
    history_request = (
        select(
            WeatherJournal,
        )
        .where(
            WeatherJournal.date >= from_date,
            WeatherJournal.date <= to_date,
            WeatherJournal.id >= cursor_id,
        )
        .order_by(WeatherJournal.date)
        .limit(PAGE_SIZE)
    )

    history = (await session.scalars(history_request)).all()
    data = [WeatherData.model_validate(model) for model in history]

    next_cursor_id = data[-1].id + 1 if len(data) > 0 else None
    return WeatherResponse(data=data, next_cursor_id=next_cursor_id)
