from datetime import datetime
from typing import Literal

from requests import Session
from pydantic_extra_types.coordinate import Latitude, Longitude, Coordinate

from .base import Requestor


class WeatherBit(Requestor):
    def __init__(self, api_key: str, session: Session):
        super(WeatherBit, self).__init__(api_key, 'https://api.weatherbit.io/v2.0', session)

    def _get_forecast_url(self, granularity):
        return self.base_endpoint_url + "/forecast/" + granularity + "?key=" + self.api_key + "&client=wbitpython"

    def get_forecast_url(self, **kwargs):
        granularity = kwargs['granularity']

        if granularity not in ['hourly','daily']:
            raise Exception('Unsupported granularity')

        base_url = self._get_forecast_url(granularity)

        # Build root geo-lookup.
        if 'lat' in kwargs and 'lon' in kwargs:
            arg_url_str = "&lat=%(lat)s&lon=%(lon)s"
        elif 'city' in kwargs:
            arg_url_str = "&city=%(city)s"
        elif 'city_id' in kwargs:
            arg_url_str = "&city_id=%(city_id)s"
        elif 'station' in kwargs:
            arg_url_str = "&station=%(station)s"
        elif 'postal_code' in kwargs:
            arg_url_str = "&postal_code=%(postal_code)s"

        # Add on additional parameters.
        if 'state' in kwargs:
            arg_url_str = arg_url_str + "&state=%(state)s"
        if 'country' in kwargs:
            arg_url_str = arg_url_str + "&country=%(country)s"
        if 'days' in kwargs:
            arg_url_str = arg_url_str + "&days=%(days)s"
        if 'units' in kwargs:
            arg_url_str = arg_url_str + "&units=%(units)s"
        if 'hours' in kwargs:
            arg_url_str = arg_url_str + "&hours=%(hours)s"

        return base_url + (arg_url_str % kwargs)

    def get_historical_weather(self, granularity: Literal['hourly', 'daily'],
                               coordinate: Coordinate,
                               start_date: datetime, end_date: datetime):
        return self._get(
            f'/history/{granularity}',
            params={
                'lat': coordinate.latitude,
                'lon': coordinate.longitude,
                'start_date': start_date.strftime("%Y-%m-%d"),
                'end_date': end_date.strftime("%Y-%m-%d"),
                'key': self.api_key,
            }
        )

