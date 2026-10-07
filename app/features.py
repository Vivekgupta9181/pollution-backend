import numpy as np
import pandas as pd


def calculate_season(month):

    if month in [3, 4, 5]:
        return "summer"

    elif month in [6, 7, 8, 9]:
        return "monsoon"

    elif month in [10, 11]:
        return "post_monsoon"

    else:
        return "winter"


def create_features(df):

    df = df.copy()

    # ==================================================
    # 1. DATETIME
    # ==================================================

    df["DateTime"] = pd.to_datetime(
        df["DateTime"]
    )

    df = (
        df
        .sort_values("DateTime")
        .reset_index(drop=True)
    )

    # ==================================================
    # 2. RENAME DATABASE COLUMNS
    # ==================================================

    df = df.rename(
        columns={

            "station_id": "Station_ID",

            "pm25": "PM2.5",
            "pm10": "PM10",

            "no2": "NO₂",
            "so2": "SO₂",

            "co": "CO",
            "o3": "O₃",

            "temp_c": "Temp_C",
            "humidity": "Humidity_%",

            "wind_speed": "Wind_Speed_mps",
            "wind_direction": "Wind_Direction_deg",

            "pressure": "Pressure_hPa",
            "rain": "Rain_mm"
        }
    )

    # ==================================================
    # 3. TIME FEATURES
    # ==================================================

    df["Date"] = (
        df["DateTime"].dt.date
    )

    df["Time"] = (
        df["DateTime"].dt.time
    )

    df["month"] = (
        df["DateTime"].dt.month
    )

    df["hour"] = (
        df["DateTime"].dt.hour
    )

    df["day_of_week"] = (
        df["DateTime"].dt.dayofweek
    )

    # ==================================================
    # 4. SEASON
    # ==================================================

    df["season"] = (
        df["month"].apply(calculate_season)
    )

    # ==================================================
    # 5. CYCLIC TIME FEATURES
    # ==================================================

    df["hour_sin"] = np.sin(
        2 * np.pi * df["hour"] / 24
    )

    df["hour_cos"] = np.cos(
        2 * np.pi * df["hour"] / 24
    )

    df["dow_sin"] = np.sin(
        2 * np.pi * df["day_of_week"] / 7
    )

    df["dow_cos"] = np.cos(
        2 * np.pi * df["day_of_week"] / 7
    )

    # ==================================================
    # 6. RATE OF CHANGE
    # ==================================================

    roc_columns = [
        "NO₂",
        "SO₂",
        "CO",
        "O₃",
        "Temp_C",
        "Humidity_%"
    ]

    for col in roc_columns:

        for hours in range(1, 6):

            df[f"{col}_ROC_{hours}h"] = (
                df[col] - df[col].shift(hours)
            ) / hours

    # ==================================================
    # 7. WIND DIRECTION CYCLIC ENCODING
    # ==================================================

    df["wind_dir_sin"] = np.sin(
        np.deg2rad(
            df["Wind_Direction_deg"]
        )
    )

    df["wind_dir_cos"] = np.cos(
        np.deg2rad(
            df["Wind_Direction_deg"]
        )
    )

    # ==================================================
    # 8. PM2.5 LAG FEATURES
    # ==================================================

    for hours in range(1, 6):

        df[f"PM2.5_lag_{hours}h"] = (
            df["PM2.5"].shift(hours)
        )

    # ==================================================
    # 9. PM10 LAG FEATURES
    # ==================================================

    for hours in range(1, 6):

        df[f"PM10_lag_{hours}h"] = (
            df["PM10"].shift(hours)
        )

    # ==================================================
    # 10. ROLLING MEAN
    # ==================================================

    rolling_windows = [
        3,
        6,
        12,
        24
    ]

    for window in rolling_windows:

        df[
            f"PM2.5_rolling_mean_{window}h"
        ] = (
            df["PM2.5"]
            .shift(1)
            .rolling(window=window)
            .mean()
        )

        df[
            f"PM10_rolling_mean_{window}h"
        ] = (
            df["PM10"]
            .shift(1)
            .rolling(window=window)
            .mean()
        )

    # ==================================================
    # 11. STATION ONE-HOT ENCODING
    # ==================================================

    station_encoded = pd.get_dummies(
        df["Station_ID"],
        prefix="station"
    )

    required_stations = [
        "station_1",
        "station_2",
        "station_3",
        "station_4",
        "station_5"
    ]

    station_encoded = station_encoded.reindex(
        columns=required_stations,
        fill_value=0
    )

    df = pd.concat(
        [
            df,
            station_encoded
        ],
        axis=1
    )

    # ==================================================
    # 12. SEASON ONE-HOT ENCODING
    # ==================================================

    season_encoded = pd.get_dummies(
        df["season"],
        prefix="season"
    )

    required_seasons = [
        "season_monsoon",
        "season_post_monsoon",
        "season_summer",
        "season_winter"
    ]

    season_encoded = season_encoded.reindex(
        columns=required_seasons,
        fill_value=0
    )

    df = pd.concat(
        [
            df,
            season_encoded
        ],
        axis=1
    )

    return df







# import numpy as np
# import pandas as pd


# def calculate_season(month):

#     if month in [3, 4, 5]:
#         return "summer"

#     elif month in [6, 7, 8, 9]:
#         return "monsoon"

#     elif month in [10, 11]:
#         return "post_monsoon"

#     else:
#         return "winter"


# def create_features(df):

#     df = df.copy()

#     # --------------------------------------------------
#     # Make sure datetime is datetime
#     # --------------------------------------------------

#     df["DateTime"] = pd.to_datetime(df["DateTime"])

#     df = df.sort_values("DateTime").reset_index(drop=True)

#     # --------------------------------------------------
#     # Rename database columns to training names
#     # --------------------------------------------------

#     df = df.rename(
#         columns={
#             "station_id": "Station_ID",
#             "pm25": "PM2.5",
#             "pm10": "PM10",
#             "no2": "NO₂",
#             "so2": "SO₂",
#             "co": "CO",
#             "o3": "O₃",

#             "temp_c": "Temp_C",
#             "humidity": "Humidity_%",

#             "wind_speed": "Wind_Speed_mps",
#             "wind_direction": "Wind_Direction_deg",

#             "pressure": "Pressure_hPa",
#             "rain": "Rain_mm"
#         }
#     )

#     # --------------------------------------------------
#     # Time features
#     # --------------------------------------------------

#     df["Date"] = df["DateTime"].dt.date
#     df["Time"] = df["DateTime"].dt.time

#     df["month"] = df["DateTime"].dt.month
#     df["hour"] = df["DateTime"].dt.hour
#     df["day_of_week"] = df["DateTime"].dt.dayofweek

#     # --------------------------------------------------
#     # Season
#     # --------------------------------------------------

#     df["season"] = df["month"].apply(calculate_season)

#     # --------------------------------------------------
#     # Cyclic time encoding
#     # --------------------------------------------------

#     df["hour_sin"] = np.sin(
#         2 * np.pi * df["hour"] / 24
#     )

#     df["hour_cos"] = np.cos(
#         2 * np.pi * df["hour"] / 24
#     )

#     df["dow_sin"] = np.sin(
#         2 * np.pi * df["day_of_week"] / 7
#     )

#     df["dow_cos"] = np.cos(
#         2 * np.pi * df["day_of_week"] / 7
#     )

#     # --------------------------------------------------
#     # Rate of change
#     # --------------------------------------------------

#     roc_columns = [
#         "NO₂",
#         "SO₂",
#         "CO",
#         "O₃",
#         "Temp_C",
#         "Humidity_%"
#     ]

#     for col in roc_columns:

#         for hours in range(1, 6):

#             df[f"{col}_ROC_{hours}h"] = (
#                 df[col] - df[col].shift(hours)
#             ) / hours

#     # --------------------------------------------------
#     # Wind direction cyclic encoding
#     # --------------------------------------------------

#     df["wind_dir_sin"] = np.sin(
#         np.deg2rad(df["Wind_Direction_deg"])
#     )

#     df["wind_dir_cos"] = np.cos(
#         np.deg2rad(df["Wind_Direction_deg"])
#     )

#     # --------------------------------------------------
#     # PM2.5 lag
#     # --------------------------------------------------

#     for hours in range(1, 6):

#         df[f"PM2.5_lag_{hours}h"] = (
#             df["PM2.5"].shift(hours)
#         )

#     # --------------------------------------------------
#     # PM10 lag
#     # --------------------------------------------------

#     for hours in range(1, 6):

#         df[f"PM10_lag_{hours}h"] = (
#             df["PM10"].shift(hours)
#         )

#     # --------------------------------------------------
#     # Rolling mean
#     # --------------------------------------------------

#     rolling_windows = [3, 6, 12, 24]

#     for window in rolling_windows:

#         df[f"PM2.5_rolling_mean_{window}h"] = (
#             df["PM2.5"]
#             .shift(1)
#             .rolling(window=window)
#             .mean()
#         )

#         df[f"PM10_rolling_mean_{window}h"] = (
#             df["PM10"]
#             .shift(1)
#             .rolling(window=window)
#             .mean()
#         )
#      # --------------------------------------------------
#     # Station one-hot encoding
#     # --------------------------------------------------

#     station_encoded = pd.get_dummies(
#         df["Station_ID"],
#         prefix="station"
#     )

#     required_stations = [
#         "station_1",
#         "station_2",
#         "station_3",
#         "station_4",
#         "station_5"
#     ]

#     station_encoded = station_encoded.reindex(
#         columns=required_stations,
#         fill_value=0
#     )

#     df = pd.concat(
#         [df, station_encoded],
#         axis=1
#     )   
    
#     # --------------------------------------------------
#     # One-hot encoding season
#     # --------------------------------------------------

#     season_encoded = pd.get_dummies(
#         df["season"],
#         prefix="season"
#     )

#     required_seasons = [
#         "season_monsoon",
#         "season_post_monsoon",
#         "season_summer",
#         "season_winter"
#     ]

#     season_encoded = season_encoded.reindex(
#         columns=required_seasons,
#         fill_value=0
#     )

#     df = pd.concat(
#         [df, season_encoded],
#         axis=1
#     )

#     return df