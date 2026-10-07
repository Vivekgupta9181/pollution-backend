from fastapi import FastAPI

from .database import Base, engine
from .routes import data
from .routes import prediction


# --------------------------------------------------
# Create database tables
# --------------------------------------------------

Base.metadata.create_all(bind=engine)


# --------------------------------------------------
# Create FastAPI application
# --------------------------------------------------

app = FastAPI(
    title="Pollution Prediction API",
    description="ML Pollution Prediction Backend",
    version="1.0.0"
)


# --------------------------------------------------
# Routes
# --------------------------------------------------

app.include_router(data.router)
app.include_router(prediction.router)


# --------------------------------------------------
# Root endpoint
# --------------------------------------------------

@app.get("/")
def root():

    return {
        "message": "Pollution Prediction API is running"
    }


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }