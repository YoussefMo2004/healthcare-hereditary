"""CRUD request/response schemas for Patient, Condition, Family, Medication.

All schemas use Pydantic v2 with strict validation.  PHI fields are present
in create/update requests (server-side encryption is handled by the service
layer) but are never exposed in list responses for researcher roles.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ── Pagination ────────────────────────────────────────────────────────────────

class PaginationParams(BaseModel):
    """Query parameters for paginated list endpoints."""

    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper."""

    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int


# ── Patient ───────────────────────────────────────────────────────────────────

class PatientCreate(BaseModel):
    """Request body for POST /patients."""

    model_config = ConfigDict(str_strip_whitespace=True)

    given_name: str = Field(..., min_length=1, max_length=255)
    family_name: str = Field(..., min_length=1, max_length=255)
    middle_name: Optional[str] = Field(default=None, max_length=255)
    date_of_birth: date
    gender: str = Field(..., pattern=r"^(male|female|other|unknown)$")
    ethnicity: Optional[str] = Field(default=None, max_length=100)
    race: Optional[str] = Field(default=None, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=50)
    email: Optional[str] = Field(default=None, max_length=255)
    address_line: Optional[str] = Field(default=None, max_length=500)
    city: Optional[str] = Field(default=None, max_length=255)
    state: Optional[str] = Field(default=None, max_length=100)
    postal_code: Optional[str] = Field(default=None, max_length=20)
    country: str = Field(default="US", max_length=100)
    language: str = Field(default="en", max_length=10)
    external_id: Optional[str] = Field(default=None, max_length=255)
    identifier_system: Optional[str] = Field(default=None, max_length=255)


class PatientUpdate(BaseModel):
    """Request body for PUT /patients/{id}.  All fields optional."""

    model_config = ConfigDict(str_strip_whitespace=True)

    given_name: Optional[str] = Field(default=None, max_length=255)
    family_name: Optional[str] = Field(default=None, max_length=255)
    middle_name: Optional[str] = Field(default=None, max_length=255)
    date_of_birth: Optional[date] = None
    gender: Optional[str] = Field(default=None, pattern=r"^(male|female|other|unknown)$")
    ethnicity: Optional[str] = Field(default=None, max_length=100)
    race: Optional[str] = Field(default=None, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=50)
    email: Optional[str] = Field(default=None, max_length=255)
    address_line: Optional[str] = Field(default=None, max_length=500)
    city: Optional[str] = Field(default=None, max_length=255)
    state: Optional[str] = Field(default=None, max_length=100)
    postal_code: Optional[str] = Field(default=None, max_length=20)
    country: Optional[str] = Field(default=None, max_length=100)
    language: Optional[str] = Field(default=None, max_length=10)
    deceased: Optional[bool] = None
    deceased_date: Optional[date] = None
    research_consent: Optional[bool] = None


class PatientResponse(BaseModel):
    """Patient record returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    external_id: Optional[str] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    middle_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    ethnicity: Optional[str] = None
    race: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address_line: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    language: Optional[str] = None
    deceased: bool = False
    research_consent: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class PatientSummaryResponse(BaseModel):
    """Full clinical summary for a patient."""

    patient: PatientResponse
    conditions: list["ConditionResponse"] = []
    medications: list["MedicationResponse"] = []
    family_members: list["FamilyMemberResponse"] = []
    condition_count: int = 0
    active_medication_count: int = 0
    family_member_count: int = 0


# ── Condition ─────────────────────────────────────────────────────────────────

class ConditionCreate(BaseModel):
    """Request body for POST /patients/{id}/conditions."""

    model_config = ConfigDict(str_strip_whitespace=True)

    code: str = Field(..., min_length=1, max_length=50, description="ICD-10 or SNOMED code")
    code_system: str = Field(
        default="http://hl7.org/fhir/sid/icd-10",
        max_length=255,
        description="Coding system URI",
    )
    code_display: Optional[str] = Field(default=None, max_length=500)
    code_text: Optional[str] = Field(default=None, max_length=500)
    clinical_status: str = Field(
        default="active",
        pattern=r"^(active|confirmed|recurrence|relapse|inactive|remission|resolved)$",
    )
    verification_status: Optional[str] = Field(
        default="confirmed",
        pattern=r"^(unconfirmed|provisional|differential|confirmed|refuted|entered-in-error)$",
    )
    severity: Optional[str] = Field(
        default=None,
        pattern=r"^(severe|moderate|mild)$",
    )
    is_hereditary: bool = Field(default=False, description="Is this a hereditary condition?")
    onset_datetime: Optional[datetime] = None
    onset_age_years: Optional[int] = Field(default=None, ge=0, le=150)


class ConditionUpdate(BaseModel):
    """Request body for PUT /conditions/{id}."""

    clinical_status: Optional[str] = Field(
        default=None,
        pattern=r"^(active|confirmed|recurrence|relapse|inactive|remission|resolved)$",
    )
    verification_status: Optional[str] = Field(
        default=None,
        pattern=r"^(unconfirmed|provisional|differential|confirmed|refuted|entered-in-error)$",
    )
    severity: Optional[str] = Field(
        default=None,
        pattern=r"^(severe|moderate|mild)$",
    )
    is_hereditary: Optional[bool] = None
    abatement_datetime: Optional[datetime] = None


class ConditionResponse(BaseModel):
    """Condition record returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    patient_id: uuid.UUID
    code: str
    code_system: str
    code_display: Optional[str] = None
    code_text: Optional[str] = None
    clinical_status: str
    verification_status: Optional[str] = None
    severity: Optional[str] = None
    is_hereditary: bool = False
    family_history_flag: bool = False
    onset_datetime: Optional[datetime] = None
    onset_age_years: Optional[int] = None
    abatement_datetime: Optional[datetime] = None
    created_at: Optional[datetime] = None


# ── Family Member ─────────────────────────────────────────────────────────────

class FamilyMemberCreate(BaseModel):
    """Request body for POST /patients/{id}/family."""

    model_config = ConfigDict(str_strip_whitespace=True)

    relationship_code: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="HL7 v3 code: MTH, FTH, SIB, GRPRN, etc.",
    )
    relationship_display: Optional[str] = Field(default=None, max_length=100)
    degree_of_relatedness: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Wright coefficient: 0.5=1st degree, 0.25=2nd, 0.125=3rd",
    )
    related_patient_id: Optional[uuid.UUID] = Field(
        default=None,
        description="Link to existing patient in system (if applicable)",
    )
    sex: Optional[str] = Field(default=None, max_length=20)
    born_date: Optional[date] = None
    deceased: Optional[bool] = None
    deceased_age_years: Optional[int] = Field(default=None, ge=0, le=150)
    conditions: Optional[list[dict]] = Field(
        default=None,
        description="FHIR-shaped condition objects: [{code, outcome, onset}]",
    )
    status: str = Field(default="completed", pattern=r"^(partial|completed|entered-in-error|health-unknown)$")


class FamilyMemberUpdate(BaseModel):
    """Request body for PUT /family/{id}."""

    relationship_code: Optional[str] = Field(default=None, max_length=50)
    relationship_display: Optional[str] = Field(default=None, max_length=100)
    degree_of_relatedness: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    related_patient_id: Optional[uuid.UUID] = None
    deceased: Optional[bool] = None
    deceased_age_years: Optional[int] = Field(default=None, ge=0, le=150)
    conditions: Optional[list[dict]] = None
    status: Optional[str] = Field(
        default=None,
        pattern=r"^(partial|completed|entered-in-error|health-unknown)$",
    )


class FamilyMemberResponse(BaseModel):
    """Family member record returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    patient_id: uuid.UUID
    related_patient_id: Optional[uuid.UUID] = None
    relationship_code: str
    relationship_display: Optional[str] = None
    degree_of_relatedness: Optional[float] = None
    sex: Optional[str] = None
    born_date: Optional[date] = None
    deceased: Optional[bool] = None
    deceased_age_years: Optional[int] = None
    conditions: Optional[list[dict]] = None
    status: str
    neo4j_synced: bool = False
    created_at: Optional[datetime] = None


# ── Medication ────────────────────────────────────────────────────────────────

class MedicationCreate(BaseModel):
    """Request body for POST /patients/{id}/medications."""

    model_config = ConfigDict(str_strip_whitespace=True)

    medication_code: str = Field(..., min_length=1, max_length=50, description="RxNorm RXCUI")
    medication_code_system: str = Field(
        default="http://www.nlm.nih.gov/research/umls/rxnorm",
        max_length=255,
    )
    medication_display: Optional[str] = Field(default=None, max_length=500)
    status: str = Field(
        default="active",
        pattern=r"^(active|on-hold|cancelled|completed|entered-in-error|stopped|draft|unknown)$",
    )
    intent: str = Field(
        default="order",
        pattern=r"^(proposal|plan|order|original-order|reflex-order|filler-order|instance-order|option)$",
    )
    dosage_text: Optional[str] = Field(default=None, max_length=500)
    dosage_timing: Optional[str] = Field(default=None, max_length=255)
    dosage_route: Optional[str] = Field(default=None, max_length=100)
    dose_quantity: Optional[float] = None
    dose_unit: Optional[str] = Field(default=None, max_length=50)
    authored_on: datetime = Field(default_factory=datetime.utcnow)


class MedicationUpdate(BaseModel):
    """Request body for PUT /medications/{id}."""

    status: Optional[str] = Field(
        default=None,
        pattern=r"^(active|on-hold|cancelled|completed|entered-in-error|stopped|draft|unknown)$",
    )
    dosage_text: Optional[str] = Field(default=None, max_length=500)
    dosage_timing: Optional[str] = Field(default=None, max_length=255)
    dose_quantity: Optional[float] = None
    dose_unit: Optional[str] = Field(default=None, max_length=50)


class MedicationResponse(BaseModel):
    """Medication record returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    patient_id: uuid.UUID
    medication_code: str
    medication_code_system: Optional[str] = None
    medication_display: Optional[str] = None
    status: str
    intent: str
    dosage_text: Optional[str] = None
    dosage_timing: Optional[str] = None
    dosage_route: Optional[str] = None
    dose_quantity: Optional[float] = None
    dose_unit: Optional[str] = None
    authored_on: Optional[datetime] = None
    created_at: Optional[datetime] = None


# ── Encounter ─────────────────────────────────────────────────────────────────

class EncounterCreate(BaseModel):
    """Request body for POST /patients/{id}/encounters."""

    model_config = ConfigDict(str_strip_whitespace=True)

    encounter_class: str = Field(
        default="AMB",
        pattern=r"^(AMB|IMP|EMER|HH|VR|SS)$",
        description="HL7 v3 ActCode: AMB=ambulatory, IMP=inpatient, EMER=emergency, HH=home health",
    )
    type_code: Optional[str] = Field(default=None, max_length=100)
    type_display: Optional[str] = Field(default=None, max_length=255)
    service_type: Optional[str] = Field(default=None, max_length=255)
    facility_name: Optional[str] = Field(default=None, max_length=255)
    facility_id: Optional[str] = Field(default=None, max_length=255)


class EncounterUpdate(BaseModel):
    """Request body for PUT /encounters/{id}."""

    status: Optional[str] = Field(
        default=None,
        pattern=r"^(planned|arrived|triaged|in-progress|onleave|finished|cancelled|entered-in-error|unknown)$",
    )
    encounter_class: Optional[str] = Field(
        default=None,
        pattern=r"^(AMB|IMP|EMER|HH|VR|SS)$",
    )
    type_code: Optional[str] = Field(default=None, max_length=100)
    type_display: Optional[str] = Field(default=None, max_length=255)
    facility_name: Optional[str] = Field(default=None, max_length=255)


class EncounterResponse(BaseModel):
    """Encounter record returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    patient_id: uuid.UUID
    status: str
    encounter_class: Optional[str] = None
    type_code: Optional[str] = None
    type_display: Optional[str] = None
    service_type: Optional[str] = None
    facility_name: Optional[str] = None
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    created_at: Optional[datetime] = None


class EncounterDetailResponse(BaseModel):
    """Encounter with linked clinical data."""

    encounter: EncounterResponse
    conditions: list[ConditionResponse] = []
    observations: list["ObservationResponse"] = []
    medications: list[MedicationResponse] = []


# ── Observation ───────────────────────────────────────────────────────────────

class ObservationCreate(BaseModel):
    """Request body for POST /patients/{id}/observations."""

    model_config = ConfigDict(str_strip_whitespace=True)

    encounter_id: Optional[uuid.UUID] = None
    code: str = Field(..., min_length=1, max_length=50, description="LOINC or SNOMED code")
    code_system: str = Field(
        default="http://loinc.org",
        max_length=255,
    )
    code_display: Optional[str] = Field(default=None, max_length=500)
    category: Optional[str] = Field(
        default="vital-signs",
        pattern=r"^(vital-signs|laboratory|imaging|exam|survey|social-history|activity)$",
    )
    status: str = Field(
        default="final",
        pattern=r"^(registered|preliminary|final|amended|corrected|cancelled|entered-in-error|unknown)$",
    )
    effective_datetime: datetime = Field(default_factory=datetime.utcnow)
    value_quantity: Optional[float] = None
    value_unit: Optional[str] = Field(default=None, max_length=50)
    value_string: Optional[str] = Field(default=None, max_length=500)
    value_boolean: Optional[bool] = None
    interpretation: Optional[str] = Field(
        default=None,
        max_length=10,
        description="HL7 v3: H=high, L=low, N=normal, A=abnormal",
    )
    ref_range_low: Optional[float] = None
    ref_range_high: Optional[float] = None


class VitalsCreate(BaseModel):
    """Convenience schema for recording common vitals in one call."""

    model_config = ConfigDict(str_strip_whitespace=True)

    encounter_id: Optional[uuid.UUID] = None
    effective_datetime: datetime = Field(default_factory=datetime.utcnow)
    systolic_bp: Optional[float] = Field(default=None, ge=50, le=300, description="mmHg")
    diastolic_bp: Optional[float] = Field(default=None, ge=20, le=200, description="mmHg")
    heart_rate: Optional[float] = Field(default=None, ge=20, le=300, description="bpm")
    temperature: Optional[float] = Field(default=None, ge=30, le=45, description="°C")
    spo2: Optional[float] = Field(default=None, ge=50, le=100, description="%")
    weight: Optional[float] = Field(default=None, ge=0.5, le=500, description="kg")
    height: Optional[float] = Field(default=None, ge=20, le=300, description="cm")


class ObservationUpdate(BaseModel):
    """Request body for PUT /observations/{id}."""

    status: Optional[str] = Field(
        default=None,
        pattern=r"^(registered|preliminary|final|amended|corrected|cancelled|entered-in-error|unknown)$",
    )
    value_quantity: Optional[float] = None
    value_unit: Optional[str] = Field(default=None, max_length=50)
    value_string: Optional[str] = Field(default=None, max_length=500)
    interpretation: Optional[str] = Field(default=None, max_length=10)


class ObservationResponse(BaseModel):
    """Observation record returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    patient_id: uuid.UUID
    encounter_id: Optional[uuid.UUID] = None
    status: str
    category: Optional[str] = None
    code: str
    code_system: str
    code_display: Optional[str] = None
    effective_datetime: Optional[datetime] = None
    value_quantity: Optional[float] = None
    value_unit: Optional[str] = None
    value_string: Optional[str] = None
    value_boolean: Optional[bool] = None
    interpretation: Optional[str] = None
    ref_range_low: Optional[float] = None
    ref_range_high: Optional[float] = None
    created_at: Optional[datetime] = None


# ── Batch Screening ───────────────────────────────────────────────────────────

class BatchScreenRequest(BaseModel):
    """Request body for POST /predict/batch-screen."""

    patient_ids: Optional[list[uuid.UUID]] = Field(
        default=None, max_length=500, description="Explicit patient UUIDs (max 500)"
    )
    filter_gender: Optional[str] = Field(
        default=None, pattern=r"^(male|female|other|unknown)$"
    )
    filter_min_age: Optional[int] = Field(default=None, ge=0, le=150)
    filter_max_age: Optional[int] = Field(default=None, ge=0, le=150)
    include_shap: bool = Field(default=False)
    top_n_factors: int = Field(default=3, ge=1, le=10)


class BatchScreenJobResponse(BaseModel):
    """Response for POST /predict/batch-screen (HTTP 202)."""

    job_id: str
    status: str  # pending | running | completed | failed
    total_patients: int
    progress: int = 0
    message: str = ""


class BatchScreenPatientResult(BaseModel):
    """Single patient result within a batch screening job."""

    patient_id: uuid.UUID
    risk_score: float
    risk_tier: str
    shap_factors: Optional[list[dict]] = None


class BatchScreenResultResponse(BaseModel):
    """Response for GET /predict/batch-screen/{job_id}."""

    job_id: str
    status: str
    total_patients: int
    progress: int
    results: list[BatchScreenPatientResult] = []
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    message: str = ""


# ── Risk History ──────────────────────────────────────────────────────────────

class RiskHistoryEntry(BaseModel):
    """Single prediction log entry."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    patient_id: uuid.UUID
    risk_score: float
    risk_tier: str
    model_name: str
    model_version: str
    feature_date: str
    shap_top_factors: Optional[dict] = None
    source: str
    predicted_at: Optional[datetime] = None


class RiskTrendResponse(BaseModel):
    """Risk trend analysis for a patient."""

    patient_id: uuid.UUID
    current_score: Optional[float] = None
    previous_score: Optional[float] = None
    trend: str  # improving | worsening | stable | insufficient_data
    change_pct: Optional[float] = None
    total_predictions: int
    history: list[RiskHistoryEntry] = []


# Forward reference resolution
PatientSummaryResponse.model_rebuild()
EncounterDetailResponse.model_rebuild()
