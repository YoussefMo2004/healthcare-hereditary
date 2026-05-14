"""Create initial schema for healthcare platform.

Revision ID: 0001
Revises:
Create Date: 2026-05-14 00:00:00.000000

"""
from __future__ import annotations

import uuid
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Apply migration: create initial tables."""
    # ── Patient ───────────────────────────────────────────────────────────────
    op.create_table(
        "patients",
        sa.Column("id", sa.UUID(), nullable=False, default=lambda: uuid.uuid4()),
        sa.Column("external_id", sa.String(255), nullable=False, unique=True),
        sa.Column("first_name_encrypted", sa.LargeBinary(), nullable=True),
        sa.Column("last_name_encrypted", sa.LargeBinary(), nullable=True),
        sa.Column("dob_encrypted", sa.LargeBinary(), nullable=True),
        sa.Column("gender", sa.String(50), nullable=True),
        sa.Column("contact_encrypted", sa.LargeBinary(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("external_id", name="uq_patient_external_id"),
    )
    op.create_index("ix_patients_created_at", "patients", ["created_at"])

    # ── Diagnosis ─────────────────────────────────────────────────────────────
    op.create_table(
        "diagnoses",
        sa.Column("id", sa.UUID(), nullable=False, default=lambda: uuid.uuid4()),
        sa.Column("patient_id", sa.UUID(), nullable=False),
        sa.Column("icd10_code", sa.String(10), nullable=False),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("category", sa.String(50), nullable=True),
        sa.Column("onset_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(50), nullable=True, server_default="active"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_diagnoses_patient_id", "diagnoses", ["patient_id"])
    op.create_index("ix_diagnoses_icd10_code", "diagnoses", ["icd10_code"])
    op.create_index("ix_diagnoses_category", "diagnoses", ["category"])

    # ── Medication ────────────────────────────────────────────────────────────
    op.create_table(
        "medications",
        sa.Column("id", sa.UUID(), nullable=False, default=lambda: uuid.uuid4()),
        sa.Column("patient_id", sa.UUID(), nullable=False),
        sa.Column("rxnorm_code", sa.String(50), nullable=True),
        sa.Column("drug_name", sa.String(255), nullable=False),
        sa.Column("dosage", sa.String(100), nullable=True),
        sa.Column("frequency", sa.String(100), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(50), nullable=True, server_default="active"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_medications_patient_id", "medications", ["patient_id"])
    op.create_index("ix_medications_status", "medications", ["status"])

    # ── Relative Relationship ─────────────────────────────────────────────────
    op.create_table(
        "relative_relationships",
        sa.Column("id", sa.UUID(), nullable=False, default=lambda: uuid.uuid4()),
        sa.Column("patient_id", sa.UUID(), nullable=False),
        sa.Column("relative_id", sa.UUID(), nullable=False),
        sa.Column("relationship_type", sa.String(50), nullable=False),  # parent, sibling, child
        sa.Column("degree_of_relatedness", sa.Float(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["relative_id"], ["patients.id"], ondelete="CASCADE"),
        sa.UniqueConstraint(
            "patient_id",
            "relative_id",
            "relationship_type",
            name="uq_relationship",
        ),
    )
    op.create_index("ix_relatives_patient_id", "relative_relationships", ["patient_id"])
    op.create_index("ix_relatives_relationship_type", "relative_relationships", ["relationship_type"])

    # ── Prediction ────────────────────────────────────────────────────────────
    op.create_table(
        "predictions",
        sa.Column("id", sa.UUID(), nullable=False, default=lambda: uuid.uuid4()),
        sa.Column("patient_id", sa.UUID(), nullable=False),
        sa.Column("risk_score", sa.Float(), nullable=False),
        sa.Column("risk_category", sa.String(50), nullable=False),  # low, moderate, high
        sa.Column("model_version", sa.String(50), nullable=False),
        sa.Column("explanation", sa.JSON(), nullable=True),
        sa.Column("computed_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_predictions_patient_id", "predictions", ["patient_id"])
    op.create_index("ix_predictions_computed_at", "predictions", ["computed_at"])


def downgrade() -> None:
    """Rollback migration."""
    op.drop_index("ix_predictions_computed_at", table_name="predictions")
    op.drop_index("ix_predictions_patient_id", table_name="predictions")
    op.drop_table("predictions")

    op.drop_index("ix_relatives_relationship_type", table_name="relative_relationships")
    op.drop_index("ix_relatives_patient_id", table_name="relative_relationships")
    op.drop_table("relative_relationships")

    op.drop_index("ix_medications_status", table_name="medications")
    op.drop_index("ix_medications_patient_id", table_name="medications")
    op.drop_table("medications")

    op.drop_index("ix_diagnoses_category", table_name="diagnoses")
    op.drop_index("ix_diagnoses_icd10_code", table_name="diagnoses")
    op.drop_index("ix_diagnoses_patient_id", table_name="diagnoses")
    op.drop_table("diagnoses")

    op.drop_index("ix_patients_created_at", table_name="patients")
    op.drop_table("patients")
