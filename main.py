from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


# Load the trained deployment model

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "model.joblib"

try:
    prediction_model = joblib.load(MODEL_PATH)
except Exception as error:
    raise RuntimeError(
        f"Unable to load model.joblib: {error}"
    ) from error


# Create the FastAPI application

app = FastAPI(
    title="Cybersecurity Incident Resolution API",
    description=(
        "Predicts the resolution time of a cybersecurity "
        "incident using the Random Forest deployment model "
        "trained in Part I."
    ),
    version="1.0.0"
)


# Define the request data format

class IncidentInput(BaseModel):
    country: str = Field(min_length=1)
    year: int = Field(ge=2015, le=2024)
    attack_type: str = Field(min_length=1)
    target_industry: str = Field(min_length=1)
    financial_loss_million: float = Field(ge=0)
    affected_users: int = Field(ge=0)
    attack_source: str = Field(min_length=1)
    security_vulnerability_type: str = Field(min_length=1)
    defense_mechanism_used: str = Field(min_length=1)


# API routes

@app.get("/")
def root():
    return {
        "message": "Cybersecurity Incident Resolution API",
        "documentation": "/docs",
        "health_check": "/health"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model_loaded": prediction_model is not None
    }


@app.post("/predict")
def predict(data: IncidentInput):
    try:
        # Column names must match those used during model training
        input_df = pd.DataFrame([
            {
                "Country": data.country,
                "Attack Type": data.attack_type,
                "Target Industry": data.target_industry,
                "Attack Source": data.attack_source,
                "Security Vulnerability Type":
                    data.security_vulnerability_type,
                "Defense Mechanism Used":
                    data.defense_mechanism_used,
                "Year": int(data.year),
                "Financial Loss (in Million $)":
                    float(data.financial_loss_million),
                "Number of Affected Users":
                    int(data.affected_users)
            }
        ])

        predicted_hours = prediction_model.predict(input_df)[0]

        return {
            "predicted_resolution_time_hours": round(
                float(predicted_hours),
                2
            )
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {error}"
        ) from error