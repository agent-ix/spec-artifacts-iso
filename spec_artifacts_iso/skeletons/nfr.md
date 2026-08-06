---
id: NFR-001
title: "Import throughput under sustained load"
type: NFR
quality_attribute: performance_efficiency
relationships:
  - target: "ix://agent-ix/example/FR-001"
    type: "constrains"
---
<!-- NFR authoring skeleton (spec-artifacts-iso). Fill every section with
     substantive content. Contract (manifest body_extraction asserts):
     - REQUIRED (level 2): Statement, Measurement and Evaluation (with
       table), Verification.
     - OPTIONAL (level 2): Scope, Rationale, Acceptance Criteria,
       Dependencies.
     - `quality_attribute` lives in FRONTMATTER as an ISO 25010 enum
       (see schemas/nfr-frontmatter.schema.json); the old
       `## Quality Attribute` body section is retired.
     - Measurement and Evaluation table headers MUST be exactly:
       Metric | Target | Threshold | Method with ≥1 data row. The table
       IS the NFR's acceptance-criteria equivalent; use the optional
       Acceptance Criteria section only for policy NFRs whose
       compliance checks don't reduce to metrics.
     - When the optional Acceptance Criteria section IS present, its table
       headers MUST be exactly ID | Criteria | Verification with >=1 data
       row and ids `NFR-NNN-AC-N` — the same shape as FR, checked by the
       same `ac-verification-method` lint advisory. Either omit the section
       or author the table; unstructured prose is no longer accepted.
     - The Statement SHOULD follow EARS (advisory grammar `iso-spec-core`,
       FR-042): one `shall`, a named subject, a concrete response. NFRs are
       typically ubiquitous or state-driven (`The system shall sustain …
       while under load`); a trigger is not required and its absence is
       never a defect. `quire validate` warns on violations (never blocks).
     - Keep headings unique per level; nest ≤2 levels below the H1 title
       (through H3). -->
# NFR-001: Import throughput under sustained load

## Statement

The system SHALL sustain at least 500 artifact imports per second at p95 latency
under or equal to 200 ms during a 10-minute sustained-load window.

## Scope

- Applies to: the artifact import ingestion path.
- Operational context: steady-state production load with warm caches.

## Rationale

Ingestion is on the critical path for downstream indexing; sustained throughput
bounds the end-to-end freshness SLA committed to consumers.

## Measurement and Evaluation

| Metric | Target | Threshold | Method |
|--------|--------|-----------|--------|
| Import throughput | 600 imports/s | 500 imports/s | Load Benchmark |
| Import p95 latency | 120 ms | 200 ms | Load Benchmark |

## Verification

A repeatable load benchmark drives the ingestion path for 10 minutes and asserts
the measured throughput and p95 latency stay within threshold.

## Acceptance Criteria

<!-- Optional. The Measurement table above IS the acceptance-criteria
     equivalent for a *measurable* NFR — such an NFR omits this section
     entirely. Use it only for a *policy* NFR whose compliance checks don't
     reduce to a number (e.g. "evidence artifacts live under the owning
     packet"). When present it takes the FR table shape below, so the section
     is either absent or well-formed. Delete this section and the table if the
     Measurement table already carries the criteria. -->

| ID | Criteria | Verification |
|----|----------|--------------|
| NFR-001-AC-1 | Every benchmark evidence artifact is stored under the packet directory that owns the measurement it supports. | Inspection |

## Dependencies

- **Upstream**: [FR-001](../functional/FR-001-verify-checksums.md) checksum verification on import
- **Downstream**: capacity-planning runbook
