# Tier 2 — Clinical Workflow Features

## Goal

Add encounter/visit tracking, clinical observations (vitals & labs), batch risk screening, and risk history trending. These features transform the system from data-entry-only into a **workflow tool** that clinicians can use during actual patient encounters.

## Background

Tier 1 delivered CRUD for patients, conditions, family, and medications. Tier 2 builds **on top of** that by:
- Linking clinical data to encounters (visits)
- Recording structured observations (vitals, labs) during encounters
- Running predictions at scale (batch screening of patient panels)
- Persisting prediction results for longitudinal risk tracking

### Existing Infrastructure to Leverage

| Asset | Status | Used By |
|---|---|---|
| [Encounter model](file:///d:/Healthcare%20-%20Depi/libs/common/models/encounter.py) | ✅ Fully defined (9 statuses, period tracking, physician participants) | Feature 5 |
| [Observation model](file:///d:/Healthcare%20-%20Depi/libs/common/models/observation.py) | ✅ Fully defined (LOINC codes, polymorphic value[x], reference ranges) | Feature 6 |
| [Physician model](file:///d:/Healthcare%20-%20Depi/libs/common/models/physician.py) | ✅ Fully defined (NPI, specialty) | Feature 5 |
| [ModelService](file:///d:/Healthcare%20-%20Depi/services/api/services/model_service.py) | ✅ Has `predict_proba()` + `shap_values()` | Feature 7 |
| [CacheService](file:///d:/Healthcare%20-%20Depi/services/api/services/cache_service.py) | ✅ Redis async cache with domain-specific keys | Feature 7, 8 |
| [DbSession](file:///d:/Healthcare%20-%20Depi/services/api/db.py) | ✅ Async SQLAlchemy (from Tier 1) | All features |
| [AuditLog model](file:///d:/Healthcare%20-%20Depi/libs/common/models/audit_log.py) | ✅ Append-only audit trail | Feature 7, 8 |

---

## Proposed Changes

### Feature 5 — Encounter/Visit Tracking

#### [NEW] [encounters.py](file:///d:/Healthcare%20-%20Depi/services/api/routers/encounters.py)

API router for clinical encounters (visits).

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/patients/{id}/encounters` | Start a new encounter |
| `GET` | `/patients/{id}/encounters` | List encounters (filterable by status, date range) |
| `GET` | `/encounters/{id}` | Get encounter with linked conditions/observations/meds |
| `PUT` | `/encounters/{id}` | Update encounter (status, class, end time) |
| `PUT` | `/encounters/{id}/close` | Close encounter (set `period_end`, status → `finished`) |

**Key design decisions:**
- On `POST`, auto-sets `period_start` to now and status to `in-progress`
- On `close`, auto-sets `period_end` to now
- The `GET` single endpoint returns a **rich object** with all linked conditions, observations, and medications that reference this encounter (using the existing FK relationships on those models)
- Encounter class uses HL7 v3 ActCode: `AMB` (ambulatory), `IMP` (inpatient), `EMER` (emergency), `HH` (home health)

#### [NEW] Encounter schemas in [crud_schemas.py](file:///d:/Healthcare%20-%20Depi/services/api/schemas/crud_schemas.py)

- `EncounterCreate` — required: `encounter_class`; optional: `type_code`, `facility_name`
- `EncounterUpdate` — status, class, type, facility changes
- `EncounterResponse` — basic encounter fields
- `EncounterDetailResponse` — encounter + linked conditions/observations/medications

---

### Feature 6 — Clinical Observations/Vitals

#### [NEW] [observations.py](file:///d:/Healthcare%20-%20Depi/services/api/routers/observations.py)

API router for vital signs, lab results, and clinical assessments.

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/patients/{id}/observations` | Record a vital sign or lab result |
| `GET` | `/patients/{id}/observations` | List observations (filter by category, LOINC code, date range) |
| `GET` | `/observations/{id}` | Get single observation with reference range |
| `PUT` | `/observations/{id}` | Update value or status |
| `DELETE` | `/observations/{id}` | Remove observation |

**Vitals quick-entry:** A convenience endpoint for recording common vitals in bulk:

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/patients/{id}/vitals` | Record BP, HR, temp, SpO2, weight in one call |

This maps to multiple `Observation` rows with pre-configured LOINC codes:

| Vital | LOINC Code | Unit |
|---|---|---|
| Systolic BP | `8480-6` | mmHg |
| Diastolic BP | `8462-4` | mmHg |
| Heart Rate | `8867-4` | /min |
| Temperature | `8310-5` | °C |
| SpO2 | `2708-6` | % |
| Weight | `29463-7` | kg |
| Height | `8302-2` | cm |
| BMI | `39156-5` | kg/m² |

#### [NEW] Observation schemas in [crud_schemas.py](file:///d:/Healthcare%20-%20Depi/services/api/schemas/crud_schemas.py)

- `ObservationCreate` — required: `code`, `code_system`, `effective_datetime`; polymorphic value fields
- `VitalsCreate` — convenience schema: `systolic_bp`, `diastolic_bp`, `heart_rate`, `temperature`, `spo2`, `weight` (all optional)
- `ObservationResponse` — full observation with interpretation and reference range

---

### Feature 7 — Batch Risk Screening

#### [NEW] [batch_screening.py](file:///d:/Healthcare%20-%20Depi/services/api/routers/batch_screening.py)

Async batch prediction for screening entire patient panels.

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/predict/batch-screen` | Submit a batch screening job |
| `GET` | `/predict/batch-screen/{job_id}` | Poll job status and results |

**Design:**
- `POST` accepts a list of patient UUIDs (max 500 per batch) or filter criteria (`gender`, `min_age`, `max_age`)
- Returns a `job_id` immediately (HTTP 202 Accepted)
- Job runs in a background `asyncio.Task` that iterates patients, calls `ModelService.predict_proba()`, and stores results
- Job state stored in Redis: `batch:{job_id}` → `{status, progress, total, results, started_at, completed_at}`
- Results include per-patient `risk_score`, `risk_tier`, and optionally top SHAP factors

#### [NEW] Batch schemas in [crud_schemas.py](file:///d:/Healthcare%20-%20Depi/services/api/schemas/crud_schemas.py)

- `BatchScreenRequest` — `patient_ids: list[UUID]` or filter criteria
- `BatchScreenJobResponse` — `job_id`, `status` (pending/running/completed/failed), `progress`
- `BatchScreenResultResponse` — per-patient results list with risk scores and tiers

---

### Feature 8 — Risk History & Trend Tracking

#### [NEW] [prediction_log.py](file:///d:/Healthcare%20-%20Depi/libs/common/models/prediction_log.py)

New ORM model to persist every prediction for longitudinal tracking:

```python
class PredictionLog(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "prediction_log"
    
    patient_id: UUID (FK → patient.id)
    risk_score: float
    risk_tier: str   # low/moderate/high/very_high
    model_name: str
    model_version: str
    feature_date: str
    shap_top_factors: JSONB  # top-5 SHAP contributions
    source: str  # "api" | "batch" | "scheduled"
    predicted_at: datetime
```

#### [NEW] [risk_history.py](file:///d:/Healthcare%20-%20Depi/services/api/routers/risk_history.py)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/patients/{id}/risk-history` | Risk score time series |
| `GET` | `/patients/{id}/risk-history/latest` | Most recent prediction |
| `GET` | `/patients/{id}/risk-history/trend` | Trend analysis (improving/worsening/stable) |

**Auto-logging:** The existing `/predict/hereditary-risk` endpoint will be updated to write to `prediction_log` after each prediction (in addition to caching in Redis).

---

### Modifications to Existing Files

#### [MODIFY] [main.py](file:///d:/Healthcare%20-%20Depi/services/api/main.py)

- Register 4 new routers: `encounters`, `observations`, `batch_screening`, `risk_history`

#### [MODIFY] [crud_schemas.py](file:///d:/Healthcare%20-%20Depi/services/api/schemas/crud_schemas.py)

- Add Encounter, Observation, Vitals, Batch, and RiskHistory schemas

#### [MODIFY] [predictions.py](file:///d:/Healthcare%20-%20Depi/services/api/routers/predictions.py)

- After computing a prediction, also persist to `prediction_log` table

#### [MODIFY] [rbac.py](file:///d:/Healthcare%20-%20Depi/services/api/auth/rbac.py)

- Add `WRITE_ENCOUNTER` permission (admin, clinician)
- Add `RUN_BATCH_SCREEN` permission (admin, clinician)

#### [MODIFY] [app.py](file:///d:/Healthcare%20-%20Depi/services/streamlit/app.py)

- Add new sidebar entries: "🏥 Encounters" and "📊 Screening"

---

### Streamlit UI

#### [NEW] [encounters_page.py](file:///d:/Healthcare%20-%20Depi/services/streamlit/pages/encounters_page.py)

Encounter management page with:
- **Active Encounters** — list of in-progress visits with patient name, class, start time
- **Start Encounter** — form to begin a new visit (select patient, class, facility)
- **Encounter Detail** — view encounter with linked vitals, conditions, medications
- **Record Vitals** — quick-entry form for common vital signs during an encounter
- **Close Encounter** — one-click close with optional summary notes

#### [NEW] [screening_page.py](file:///d:/Healthcare%20-%20Depi/services/streamlit/pages/screening_page.py)

Batch screening and risk trending page:
- **Run Screening** — select criteria (all patients, gender, age range), start batch job
- **Screening Results** — table of patients with risk scores, color-coded tiers, export button
- **Risk Trends** — select a patient, show risk score over time as a line chart with SHAP waterfall

---

## Summary

| Type | Count | Files |
|---|---|---|
| New files | 7 | `encounters.py`, `observations.py`, `batch_screening.py`, `risk_history.py`, `prediction_log.py`, `encounters_page.py`, `screening_page.py` |
| Modified files | 5 | `main.py`, `crud_schemas.py`, `predictions.py`, `rbac.py`, `app.py` |
| New API endpoints | 17 | 5 encounters + 6 observations + 2 batch + 3 risk history + 1 vitals quick-entry |
| New DB model | 1 | `PredictionLog` |

---

## Open Questions

> [!IMPORTANT]
> **Batch size limit:** The plan caps batch screening at 500 patients per request (processed async in the API process). For larger panels (10k+ patients), should we use Celery workers instead of `asyncio.Task`? This would add `celery` + `flower` as dependencies.

> [!NOTE]
> **Vitals quick-entry:** The convenience `/patients/{id}/vitals` endpoint creates multiple `Observation` rows in one call. An alternative is to only offer individual observation recording. Which approach do you prefer?

---

## Verification Plan

### Automated Tests
- Start Streamlit and verify the two new pages (Encounters, Screening) load without errors
- Create an encounter → record vitals → close encounter → verify data persists
- Run batch screening on demo patients → verify risk scores appear

### Manual Verification
- Navigate through the encounter workflow: start → record vitals → add condition → close
- Run batch screening with different filter criteria
- Verify risk history chart shows prediction trends
