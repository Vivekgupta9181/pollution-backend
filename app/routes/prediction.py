import pandas as pd

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import PollutionData
from ..features import create_features
from ..ml_model import get_model


router = APIRouter(
    prefix="/predict",
    tags=["Prediction"]
)


@router.get("/")
def predict(
    station_id: int = Query(..., ge=1),
    db: Session = Depends(get_db)
):

    # ==================================================
    # 1. GET LATEST 50 RECORDS FOR SELECTED STATION
    # ==================================================

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

    # ==================================================
    # 2. CHECK HISTORICAL DATA
    # ==================================================

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

    # ==================================================
    # 3. DATABASE -> DATAFRAME
    # ==================================================

    data = []

    for row in records:

        data.append({

            "DateTime": row.datetime,
            "station_id": row.station_id,

            "pm25": row.pm25,
            "pm10": row.pm10,

            "no2": row.no2,
            "so2": row.so2,

            "co": row.co,
            "o3": row.o3,

            "temp_c": row.temp_c,
            "humidity": row.humidity,

            "wind_speed": row.wind_speed,
            "wind_direction": row.wind_direction,

            "pressure": row.pressure,
            "rain": row.rain
        })

    df = pd.DataFrame(data)

    # ==================================================
    # 4. SORT CHRONOLOGICALLY
    # ==================================================

    df = (
        df
        .sort_values("DateTime")
        .reset_index(drop=True)
    )

    # ==================================================
    # 5. CREATE FEATURES
    # ==================================================

    df = create_features(df)

    # ==================================================
    # 6. GET LATEST ROW
    # ==================================================

    latest = df.iloc[-1:].copy()

    # ==================================================
    # 7. LOAD MODEL
    # ==================================================

    model = get_model()

    # ==================================================
    # 8. GET FEATURES FROM TRAINED MODEL
    # ==================================================

    if not hasattr(model, "feature_names_in_"):

        raise HTTPException(
            status_code=500,
            detail={
                "message":
                    "Loaded model does not contain "
                    "feature_names_in_."
            }
        )

    model_features = list(
        model.feature_names_in_
    )

    # ==================================================
    # 9. CHECK MISSING FEATURES
    # ==================================================

    missing_features = [
        feature
        for feature in model_features
        if feature not in latest.columns
    ]

    if missing_features:

        raise HTTPException(
            status_code=500,
            detail={
                "message":
                    "Prediction dataframe is missing "
                    "model features.",

                "missing_features":
                    missing_features
            }
        )

    # ==================================================
    # 10. CREATE EXACT MODEL INPUT
    # ==================================================

    X = latest.loc[
        :,
        model_features
    ].copy()

    # ==================================================
    # 11. CHECK FEATURE ORDER
    # ==================================================

    print()
    print("========================================")
    print("MODEL FEATURE COUNT:", len(model_features))
    print("PREDICTION FEATURE COUNT:", len(X.columns))
    print(
        "FEATURE ORDER MATCH:",
        list(X.columns) == model_features
    )
    print("========================================")

    # ==================================================
    # 12. CHECK NaN
    # ==================================================

    if X.isnull().any().any():

        nan_features = (
            X.columns[
                X.isnull().any()
            ].tolist()
        )

        raise HTTPException(
            status_code=400,
            detail={
                "message":
                    "Some features could not be calculated.",

                "features_with_nan":
                    nan_features
            }
        )

    # ==================================================
    # 13. CONVERT TO NUMPY
    # ==================================================

    X_array = X.to_numpy(dtype=float)

    # ==================================================
    # 14. PREDICTION
    # ==================================================

    try:

        prediction = model.predict(X_array)

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail={
                "message":
                    "Model prediction failed.",

                "error":
                    str(e)
            }
        )

    # ==================================================
    # 15. RETURN RESPONSE
    # ==================================================

    return {

        "status": "success",

        "station_id": station_id,

        "prediction":
            prediction.tolist(),

        "datetime":
            str(
                latest["DateTime"].iloc[0]
            )
    }