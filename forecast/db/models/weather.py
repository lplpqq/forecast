from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column

from forecast.models.base import Base


class Weather(Base):
    __tablename__ = 'weather'

    id: Mapped[int] = mapped_column(primary_key=True)

    # FIXME: Move to a related table.
    # city = Column(String)
    # country = Column(String)
    # city_id = Column(Integer)
    # country_id = Column(Integer)

    date: Mapped[datetime] = mapped_column(DateTime)
    pressure: Mapped[float] = mapped_column()
    wind_speed: Mapped[float] = mapped_column()
    wind_gust_speed: Mapped[float] = mapped_column()
    wind_dir: Mapped[float] = mapped_column()
    temperature: Mapped[float] = mapped_column()
    feelslike_temp: Mapped[float] = mapped_column()
    humidity: Mapped[float] = mapped_column()
    clouds: Mapped[float] = mapped_column()
    visibility: Mapped[float] = mapped_column()
    precipitation: Mapped[float] = mapped_column()
    snow: Mapped[float] = mapped_column()