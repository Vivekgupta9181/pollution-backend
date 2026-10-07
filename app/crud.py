from sqlalchemy.orm import Session

from .models import PollutionData
from .schemas import PollutionDataCreate


def create_pollution_data(
    db: Session,
    data: PollutionDataCreate
):

    db_data = PollutionData(
        datetime=data.datetime,
        station_id=data.station_id,

        pm25=data.pm25,
        pm10=data.pm10,

        no2=data.no2,
        so2=data.so2,

        co=data.co,
        o3=data.o3,

        temp_c=data.temp_c,
        humidity=data.humidity,

        wind_speed=data.wind_speed,
        wind_direction=data.wind_direction,

        pressure=data.pressure,
        rain=data.rain
    )

    db.add(db_data)
    db.commit()
    db.refresh(db_data)

    return db_data


def get_latest_data(db: Session):

    return (
        db.query(PollutionData)
        .order_by(PollutionData.datetime.desc())
        .first()
    )


def get_history(db: Session, limit: int = 30):

    return (
        db.query(PollutionData)
        .order_by(PollutionData.datetime.desc())
        .limit(limit)
        .all()
    )