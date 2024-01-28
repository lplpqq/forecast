from datetime import datetime

import aiohttp
from pydantic_extra_types.coordinate import Coordinate

from forecast.enums import Granularity
from forecast.providers.base import Provider
from forecast.providers.schema.visual_crossing import VisualCrossingSchema


class VisualCrossing(Provider):
    def __init__(self, conn: aiohttp.TCPConnector, api_key: str | None) -> None:
        super(Provider, self).__init__(
            'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/weatherdata',
            conn,
            api_key,
        )

    async def get_historical_weather(
        self,
        granularity: Granularity,
        coordinate: Coordinate,
        start_date: datetime,
        end_date: datetime,
    ) -> VisualCrossingSchema:
        aggregate_hours = granularity.value

        raw = await self._get(
            '/history',
            params={
                'aggregateHours': aggregate_hours,
                'location': f'{coordinate.latitude},{coordinate.longitude}',
                'startDateTime': start_date.isoformat(),
                'endDateTime': end_date.isoformat(),
                'contentType': 'json',
                'key': self.api_key,
            },
        )

        return VisualCrossingSchema.model_validate(raw)
