from sqlalchemy import Column, Integer, Float, DateTime

from .database import Base


class PollutionData(Base):

    __tablename__ = "pollution_data"

    id = Column(Integer, primary_key=True, index=True)

    datetime = Column(DateTime, nullable=False, index=True)
    station_id= Column(Integer, nullable=False, index=True)

    pm25 = Column(Float, nullable=False)
    pm10 = Column(Float, nullable=False)

    no2 = Column(Float, nullable=False)
    so2 = Column(Float, nullable=False)

    co = Column(Float, nullable=False)
    o3 = Column(Float, nullable=False)

    temp_c = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)

    wind_speed = Column(Float, nullable=False)
    wind_direction = Column(Float, nullable=False)

    pressure = Column(Float, nullable=False)
    rain = Column(Float, nullable=False)