---
id: NFR-001
title: "Import throughput under sustained load"
artifact_type: NFR
relationships:
  - target: "ix://agent-ix/example/FR-001"
    type: "constrains"
---
<!-- NFR authoring skeleton (spec-artifacts-iso). Fill every section with
     substantive content. Contract (manifest body_extraction asserts):
     - All H2 sections below are required (heading level 2).
     - Measurement and Evaluation table headers MUST be exactly:
       Metric | Target | Threshold | Method with ≥1 data row.
     - Keep headings unique per level; ≤2 levels of nesting. -->
# [NFR-001] Import throughput under sustained load

## Quality Attribute

Performance (ISO/IEC 25010 — Performance Efficiency).

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

## Dependencies

- **Upstream**: FR-001 checksum verification on import
- **Downstream**: capacity-planning runbook
