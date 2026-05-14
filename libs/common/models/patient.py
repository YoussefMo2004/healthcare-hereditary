"""Patient ORM model — FHIR R4 Patient resource, PHI-aware.

COMPLIANCE NOTE: Fields marked [PHI] must be encrypted at rest using
envelope encryption before this table reaches a non-local environment.
Field-level encryption is implemented in Phase 7.  Do not deploy to staging
or production until Phase 7 encryption is active.

FHIR reference: https://hl7.org/fhir/R4/patient.html
"""

from __future__ import annotations

import enum
from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Date, DateTime, Enum, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from libs.common.models.base import (
    ActorMixin,
    Base,
    SoftDeleteMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)

if TYPE_CHECKING:
    from libs.common.models.condition import Condition
    from libs.common.models.encounter import Encounter
    from libs.common.models.family_member_history import FamilyMemberHistory
    from libs.common.models.medication_request import MedicationRequest
    from libs.common.models.observation import Observation


class AdministrativeGender(str, enum.Enum):
    """FHIR AdministrativeGender value set."""

    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    UNKNOWN = "unknown"


class Patient(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, ActorMixin, Base):
    """Represents a person receiving healthcare services.

    Maps to FHIR R4 ``Patient`` resource.  All PHI columns are annotated;
    Phase 7 will wrap them in transparent column-level encryption via
    ``pgcrypto`` or application-level envelope encryption.
    """

    __tablename__ = "patient"

    # ── External identifiers ──────────────────────────────────────────────────
    # [PHI] Medical Record Number or source-system identifier.
    external_id: Mapped[Optional[str]] = mapped_column(
        String(255), unique=True, index=True
    )
    # Coding system URI for external_id (e.g., "http://hospital.org/mrn").
    identifier_system: Mapped[Optional[str]] = mapped_column(String(255))

    # ── Name [PHI] ────────────────────────────────────────────────────────────
    family_name: Mapped[Optional[str]] = mapped_column(String(255))
    given_name: Mapped[Optional[str]] = mapped_column(String(255))
    middle_name: Mapped[Optional[str]] = mapped_column(String(255))

    # ── Demographics ──────────────────────────────────────────────────────────
    # [PHI] — date of birth is quasi-identifier; needed for age-based ML features.
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date, index=True)

    gender: Mapped[Optional[AdministrativeGender]] = mapped_column(
        Enum(AdministrativeGender, name="administrative_gender"), index=True
    )

    # Ethnicity / race — used for subgroup fairness analysis (Phase 5).
    # Values follow OMB categories; stored as free text to avoid over-constraining.
    ethnicity: Mapped[Optional[str]] = mapped_column(String(100))
    race: Mapped[Optional[str]] = mapped_column(String(100))

    # ── Deceased ──────────────────────────────────────────────────────────────
    deceased: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default=text("false"), nullable=False
    )
    deceased_date: Mapped[Optional[date]] = mapped_column(Date)

    # ── Contact [PHI] ─────────────────────────────────────────────────────────
    phone: Mapped[Optional[str]] = mapped_column(String(50))
    email: Mapped[Optional[str]] = mapped_column(String(255))

    # ── Address [PHI] ─────────────────────────────────────────────────────────
    address_line: Mapped[Optional[str]] = mapped_column(String(500))
    city: Mapped[Optional[str]] = mapped_column(String(255))
    state: Mapped[Optional[str]] = mapped_column(String(100))
    postal_code: Mapped[Optional[str]] = mapped_column(String(20))
    country: Mapped[Optional[str]] = mapped_column(String(100), default="US")

    # ── Communication ─────────────────────────────────────────────────────────
    language: Mapped[Optional[str]] = mapped_column(String(10), default="en")

    # ── Consent ───────────────────────────────────────────────────────────────
    # Research consent must be recorded before including this patient in any
    # de-identified analytics export.
    research_consent: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default=text("false"), nullable=False
    )
    research_consent_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # ── Cross-system references ────────────────────────────────────────────────
    # Neo4j node ID — populated by the ingestion pipeline (Phase 3).
    neo4j_node_id: Mapped[Optional[str]] = mapped_column(String(255), index=True)

    # ── Relationships ─────────────────────────────────────────────────────────
    conditions: Mapped[list["Condition"]] = relationship(back_populates="patient")
    encounters: Mapped[list["Encounter"]] = relationship(back_populates="patient")
    observations: Mapped[list["Observation"]] = relationship(back_populates="patient")
    medication_requests: Mapped[list["MedicationRequest"]] = relationship(
        back_populates="patient"
    )
    family_member_histories: Mapped[list["FamilyMemberHistory"]] = relationship(
        back_populates="patient", foreign_keys="FamilyMemberHistory.patient_id"
    )
