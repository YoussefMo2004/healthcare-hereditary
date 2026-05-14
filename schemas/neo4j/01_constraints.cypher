// ============================================================
// Neo4j 5.x — Node Uniqueness Constraints
// Run order: this file first, then 02_indexes.cypher.
// Community edition: uniqueness constraints only.
// Lines marked [ENTERPRISE] require Neo4j Enterprise for
// NODE KEY or property existence constraints.
//
// Apply:
//   cypher-shell -u neo4j -p <pass> -f 01_constraints.cypher
// or via make neo4j-schema
// ============================================================

// ── Patient ──────────────────────────────────────────────────────────────────
// Internal UUID — used as the primary identifier across all services.
CREATE CONSTRAINT patient_id_unique IF NOT EXISTS
FOR (p:Patient) REQUIRE p.id IS UNIQUE;

// External MRN / system ID — must also be unique within a source system.
CREATE CONSTRAINT patient_external_id_unique IF NOT EXISTS
FOR (p:Patient) REQUIRE p.external_id IS UNIQUE;

// ── Relative ──────────────────────────────────────────────────────────────────
// A Relative may also carry the :Patient label (same UUID) if they are an
// active patient in the system.  The id constraint is separate per label
// because Neo4j enforces constraints per label, not across labels.
CREATE CONSTRAINT relative_id_unique IF NOT EXISTS
FOR (r:Relative) REQUIRE r.id IS UNIQUE;

// ── Physician ─────────────────────────────────────────────────────────────────
// NPI (National Provider Identifier) is the authoritative US physician ID.
CREATE CONSTRAINT physician_id_unique IF NOT EXISTS
FOR (ph:Physician) REQUIRE ph.id IS UNIQUE;

CREATE CONSTRAINT physician_npi_unique IF NOT EXISTS
FOR (ph:Physician) REQUIRE ph.npi IS UNIQUE;

// ── Disease ───────────────────────────────────────────────────────────────────
// ICD-10 code is the canonical disease identifier across the platform.
// A disease node is shared — many patients can have DIAGNOSED_WITH edges to it.
CREATE CONSTRAINT disease_id_unique IF NOT EXISTS
FOR (d:Disease) REQUIRE d.id IS UNIQUE;

CREATE CONSTRAINT disease_code_unique IF NOT EXISTS
FOR (d:Disease) REQUIRE d.icd10_code IS UNIQUE;

// ── Symptom ───────────────────────────────────────────────────────────────────
// SNOMED CT concept identifier.
CREATE CONSTRAINT symptom_id_unique IF NOT EXISTS
FOR (s:Symptom) REQUIRE s.id IS UNIQUE;

CREATE CONSTRAINT symptom_snomed_code_unique IF NOT EXISTS
FOR (s:Symptom) REQUIRE s.snomed_code IS UNIQUE;

// ── Medication ────────────────────────────────────────────────────────────────
// RxNorm concept unique identifier (RXCUI).
CREATE CONSTRAINT medication_id_unique IF NOT EXISTS
FOR (m:Medication) REQUIRE m.id IS UNIQUE;

CREATE CONSTRAINT medication_rxcui_unique IF NOT EXISTS
FOR (m:Medication) REQUIRE m.rxcui IS UNIQUE;

// ── Prescription ─────────────────────────────────────────────────────────────
// Each prescription event is a unique node linked to Patient + Medication.
CREATE CONSTRAINT prescription_id_unique IF NOT EXISTS
FOR (rx:Prescription) REQUIRE rx.id IS UNIQUE;

// ── Visit (Encounter) ─────────────────────────────────────────────────────────
CREATE CONSTRAINT visit_id_unique IF NOT EXISTS
FOR (v:Visit) REQUIRE v.id IS UNIQUE;

// ── [ENTERPRISE ONLY] Property existence constraints ──────────────────────────
// Uncomment when using Neo4j Enterprise in staging/production.
//
// CREATE CONSTRAINT patient_id_exists IF NOT EXISTS
// FOR (p:Patient) REQUIRE p.id IS NOT NULL;
//
// CREATE CONSTRAINT patient_created_at_exists IF NOT EXISTS
// FOR (p:Patient) REQUIRE p.created_at IS NOT NULL;
//
// CREATE CONSTRAINT disease_code_exists IF NOT EXISTS
// FOR (d:Disease) REQUIRE d.icd10_code IS NOT NULL;
//
// CREATE CONSTRAINT diagnosed_with_onset_exists IF NOT EXISTS
// FOR ()-[r:DIAGNOSED_WITH]-() REQUIRE r.onset_date IS NOT NULL;
