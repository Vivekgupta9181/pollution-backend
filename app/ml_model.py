from pathlib import Path

import joblib


MODEL_PATH = (
    Path(__file__).resolve().parent.parent
    / "model"
    / "pollution_model.pkl"
)


model = None


def load_model():

    global model

    if not MODEL_PATH.exists():

        raise FileNotFoundError(
            f"Model not found: {MODEL_PATH}"
        )

    model = joblib.load(MODEL_PATH)

    return model


def get_model():

    global model

    if model is None:
        load_model()

    return model