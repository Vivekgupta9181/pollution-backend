import pandas as pd

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query
)

from sqlalchemy.orm import Session

from ..database import get_db
from ..models import PollutionData
from ..features import create_features
from ..model_feature import MODEL_FEATURES
from ..ml_model import get_model


router = APIRouter(
    prefix="/predict",
    tags=["Prediction"]
)


@router.get("/")
def predict(

    station_id: int = Query(
        ...,
        ge=1,
        le=5
    ),

    db: Session = Depends(get_db)
):

    # --------------------------------------------------
    # 1. Get latest 50 records for selected station
    # --------------------------------------------------

    records = (
        db.query(PollutionData)
        .filter(
            PollutionData.station_id == station_id
        )
        .order_by(
            PollutionData.datetime.desc()
        )
        .limit(50)
        .all()
    )

    # --------------------------------------------------
    # 2. Check number of records
    # --------------------------------------------------

    if len(records) < 25:

        raise HTTPException(
            status_code=400,
            detail={
                "message": "Not enough historical data.",
                "station_id": station_id,
                "required_records": 25,
                "available_records": len(records)
            }
        )

    # --------------------------------------------------
    # 3. Convert database records to DataFrame
    # --------------------------------------------------

    data = []

    for row in records:

        data.append({

            "DateTime": row.datetime,

            # Station
            "station_id": row.station_id,

            # Pollution
            "pm25": row.pm25,
            "pm10": row.pm10,

            "no2": row.no2,
            "so2": row.so2,

            "co": row.co,
            "o3": row.o3,

            # Weather
            "temp_c": row.temp_c,
            "humidity": row.humidity,

            "wind_speed": row.wind_speed,
            "wind_direction": row.wind_direction,

            "pressure": row.pressure,
            "rain": row.rain
        })

    df = pd.DataFrame(data)

    # --------------------------------------------------
    # 4. Sort chronologically
    # --------------------------------------------------

    df = (
        df
        .sort_values("DateTime")
        .reset_index(drop=True)
    )

    # --------------------------------------------------
    # 5. Feature engineering
    # --------------------------------------------------

    df = create_features(df)

    # --------------------------------------------------
    # 6. Get latest record
    # --------------------------------------------------

    latest = df.iloc[-1:].copy()

    # --------------------------------------------------
    # 7. Check required ML features
    # --------------------------------------------------

    missing_features = [
        feature
        for feature in MODEL_FEATURES
        if feature not in latest.columns
    ]

    if missing_features:

        raise HTTPException(
            status_code=500,
            detail={
                "message": "Some model features are missing.",
                "missing_features": missing_features
            }
        )

    # --------------------------------------------------
    # 8. Prepare model input
    # --------------------------------------------------

    X = latest[MODEL_FEATURES]

    # --------------------------------------------------
    # 9. Check NaN
    # --------------------------------------------------

    if X.isnull().any().any():

        missing = (
            X.columns[
                X.isnull().any()
            ]
            .tolist()
        )

        raise HTTPException(
            status_code=400,
            detail={
                "message": "Some features could not be calculated.",
                "features_with_nan": missing
            }
        )

    # --------------------------------------------------
    # 10. Load model
    # --------------------------------------------------

    model = get_model()

    # --------------------------------------------------
    # 11. Debug feature names
    # --------------------------------------------------

    print("\n==============================")
    print("MODEL FEATURES")
    print("==============================")

    print(
        model.feature_names_in_.tolist()
    )

    print("\n==============================")
    print("PREDICTION FEATURES")
    print("==============================")

    print(
        X.columns.tolist()
    )

    # --------------------------------------------------
    # 12. Prediction
    # --------------------------------------------------

    try:

        prediction = model.predict(X)

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail={
                "message": "Model prediction failed.",
                "error": str(e)
            }
        )

    # --------------------------------------------------
    # 13. Return prediction
    # --------------------------------------------------

    return {

        "status": "success",

        "station_id": station_id,

        "prediction": prediction.tolist(),

        "datetime": str(
            latest["DateTime"].iloc[0]
        )
    }




# from typing import List

# from fastapi import APIRouter, Depends, Query
# from sqlalchemy.orm import Session

# from ..database import get_db
# from ..schemas import (
#     PollutionDataCreate,
#     PollutionDataResponse
# )
# from ..crud import (
#     create_pollution_data,
#     get_latest_data,
#     get_history
# )


# router = APIRouter(
#     prefix="/data",
#     tags=["Pollution Data"]
# )


# @router.post(
#     "/",
#     response_model=PollutionDataResponse
# )
# def add_data(
#     data: PollutionDataCreate,
#     db: Session = Depends(get_db)
# ):

#     return create_pollution_data(db, data)


# @router.get(
#     "/latest",
#     response_model=PollutionDataResponse
# )
# def latest_data(
#     db: Session = Depends(get_db)
# ):

#     return get_latest_data(db)


# @router.get(
#     "/history",
#     response_model=List[PollutionDataResponse]
# )
# def history(
#     limit: int = Query(
#         default=30,
#         ge=1,
#         le=500
#     ),

#     db: Session = Depends(get_db)
# ):

#     return get_history(db, limit)