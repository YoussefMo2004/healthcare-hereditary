// ============================================================
// Neo4j 5.x — Performance Indexes and Full-Text Indexes
// Run after 01_constraints.cypher (constraints implicitly
// create a backing index, so don't duplicate them here).
//
// Apply:
//   cypher-shell -u neo4j -p <pass> -f 02_indexes.cypher
// ============================================================

// ── Patient ───────────────────────────────────────────────────────────────────

// Date of birth — used in age-stratified risk queries and ML feature extraction.
CREATE INDEX patient_dob_idx IF NOT EXISTS
FOR (p:Patient) ON (p.date_of_birth);

// Gender — frequently used as a filter in hereditary disease queries.
CREATE INDEX patient_gender_idx IF NOT EXISTS
FOR (p:Patient) ON (p.gender);

// Composite: dob + gender — covers the most common demographic filter combination.
CREATE INDEX patient_dob_gender_idx IF NOT EXISTS
FOR (p:Patient) ON (p.date_of_birth, p.gender);

// Created at — for time-range scans and incremental Spark ingestion.
CREATE INDEX patient_created_at_idx IF NOT EXISTS
FOR (p:Patient) ON (p.created_at);

// ── Relative ──────────────────────────────────────────────────────────────────

CREATE INDEX relative_dob_idx IF NOT EXISTS
FOR (r:Relative) ON (r.date_of_birth);

CREATE INDEX relative_deceased_idx IF NOT EXISTS
FOR (r:Relative) ON (r.deceased);

// ── Disease ───────────────────────────────────────────────────────────────────

// ICD-10 chapter prefix (first 3 chars) — used for disease family grouping in GNN.
CREATE INDEX disease_icd10_prefix_idx IF NOT EXISTS
FOR (d:Disease) ON (d.icd10_code);

CREATE INDEX disease_is_hereditary_idx IF NOT EXISTS
FOR (d:Disease) ON (d.is_hereditary);

// ── Symptom ───────────────────────────────────────────────────────────────────

CREATE INDEX symptom_snomed_idx IF NOT EXISTS
FOR (s:Symptom) ON (s.snomed_code);

// ── Medication ────────────────────────────────────────────────────────────────

CREATE INDEX medication_drug_class_idx IF NOT EXISTS
FOR (m:Medication) ON (m.drug_class);

// ── Visit ─────────────────────────────────────────────────────────────────────

CREATE INDEX visit_date_idx IF NOT EXISTS
FOR (v:Visit) ON (v.visit_date);

// ── Relationship property indexes ─────────────────────────────────────────────
// Available in Neo4j 5.x Community edition.

// DIAGNOSED_WITH.onset_date — core for time-based family disease spread queries.
CREATE INDEX diagnosed_with_onset_idx IF NOT EXISTS
FOR ()-[r:DIAGNOSED_WITH]-() ON (r.onset_date);

// DIAGNOSED_WITH.severity — used in weighted family prevalence feature.
CREATE INDEX diagnosed_with_severity_idx IF NOT EXISTS
FOR ()-[r:DIAGNOSED_WITH]-() ON (r.severity);

// DIAGNOSED_WITH.confidence — filters uncertain historical diagnoses.
CREATE INDEX diagnosed_with_confidence_idx IF NOT EXISTS
FOR ()-[r:DIAGNOSED_WITH]-() ON (r.confidence);

// Family relationship degree — core ML feature: weight by genetic proximity.
CREATE INDEX parent_of_degree_idx IF NOT EXISTS
FOR ()-[r:PARENT_OF]-() ON (r.degree_of_relatedness);

CREATE INDEX child_of_degree_idx IF NOT EXISTS
FOR ()-[r:CHILD_OF]-() ON (r.degree_of_relatedness);

CREATE INDEX sibling_of_degree_idx IF NOT EXISTS
FOR ()-[r:SIBLING_OF]-() ON (r.degree_of_relatedness);

// PRESCRIBED.issued_date — for prescription history time-series features.
CREATE INDEX prescribed_issued_date_idx IF NOT EXISTS
FOR ()-[r:PRESCRIBED]-() ON (r.issued_date);

// ── Full-text indexes ─────────────────────────────────────────────────────────
// Used by symptom-based and disease-based search in the API (Phase 6).

CREATE FULLTEXT INDEX disease_name_fulltext IF NOT EXISTS
FOR (d:Disease) ON EACH [d.name, d.description];

CREATE FULLTEXT INDEX symptom_name_fulltext IF NOT EXISTS
FOR (s:Symptom) ON EACH [s.name, s.description];

CREATE FULLTEXT INDEX medication_name_fulltext IF NOT EXISTS
FOR (m:Medication) ON EACH [m.name, m.generic_name];

// ── Lookup query reference ────────────────────────────────────────────────────
// These are the Cypher patterns that rely on the indexes above.
// Included as comments to document intent; not executable.
//
// Weighted family disease prevalence (N-degree relatives):
//   MATCH (p:Patient {id: $patient_id})-[rel:PARENT_OF|CHILD_OF|SIBLING_OF*1..3]-(relative)
//   -[:DIAGNOSED_WITH {confidence: 'confirmed'}]->(d:Disease {icd10_code: $icd10})
//   RETURN relative.id, rel.degree_of_relatedness, d.icd10_code
//
// Shortest path to nearest affected relative:
//   MATCH path = shortestPath(
//     (p:Patient {id: $patient_id})-[:PARENT_OF|CHILD_OF|SIBLING_OF*]-(r)
//   )
//   WHERE (r)-[:DIAGNOSED_WITH]->(:Disease {icd10_code: $icd10})
//   RETURN path
//
// Full-text disease search:
//   CALL db.index.fulltext.queryNodes('disease_name_fulltext', $query)
//   YIELD node, score
//   RETURN node.icd10_code, node.name, score ORDER BY score DESC LIMIT 10
