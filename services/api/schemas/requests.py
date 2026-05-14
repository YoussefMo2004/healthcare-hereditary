"""FastAPI request body schemas (Pydantic v2).

All patient-facing endpoints receive a UUID-only patient identifier.
No PHI fields (name, DOB, address) are accepted in request bodies —
those are resolved server-side from the patient's stored record.
"""

from __future__ import annotations

import uuid
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class PredictHeredityRiskRequest(BaseModel):
    """Request body for POST /predict/hereditary-risk."""

    model_config = ConfigDict(frozen=True)

    patient_id: uuid.UUID = Field(..., description="Patient UUID")
    feature_date: str | None = Field(
        default=None,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Feature snapshot date (YYYY-MM-DD). Defaults to today.",
    )
    include_shap: bool = Field(
        default=True,
        description="Include SHAP feature contributions in the response.",
    )
    top_n_factors: Annotated[int, Field(ge=1, le=20)] = Field(
        default=5,
        description="Number of top SHAP contributors to return.",
    )


class PredictFromSymptomsRequest(BaseModel):
    """Request body for POST /predict/disease-from-symptoms."""

    model_config = ConfigDict(frozen=True)

    patient_id: uuid.UUID
    symptom_codes: list[str] = Field(
        ...,
        min_length=1,
        max_length=20,
        description="ICD-10 or SNOMED CT symptom codes.",
    )
    include_differential: bool = Field(
        default=True,
        description="Return a ranked differential diagnosis list.",
    )
    top_n: Annotated[int, Field(ge=1, le=10)] = 5


class PredictFromPrescriptionRequest(BaseModel):
    """Request body for POST /predict/disease-from-prescription."""

    model_config = ConfigDict(frozen=True)

    patient_id: uuid.UUID
    medication_codes: list[str] = Field(
        ...,
        min_length=1,
        max_length=20,
        description="RxNorm RXCUI medication codes.",
    )
    include_differential: bool = True
    top_n: Annotated[int, Field(ge=1, le=10)] = 5
