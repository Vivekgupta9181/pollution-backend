from datetime import datetime

from pydantic import BaseModel, Field


class PollutionDataCreate(BaseModel):

    datetime: datetime
    station_id: int= Field(..., ge=0)

    pm25: float = Field(..., ge=0)
    pm10: float = Field(..., ge=0)

    no2: float = Field(..., ge=0)
    so2: float = Field(..., ge=0)

    co: float = Field(..., ge=0)
    o3: float = Field(..., ge=0)

    temp_c: float
    humidity: float = Field(..., ge=0, le=100)

    wind_speed: float = Field(..., ge=0)
    wind_direction: float = Field(..., ge=0, le=360)

    pressure: float = Field(..., ge=0)
    rain: float = Field(..., ge=0)


class PollutionDataResponse(PollutionDataCreate):

    id: int

    model_config = {
        "from_attributes": True
    }