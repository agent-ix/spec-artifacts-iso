---
type: master-requirements
name: spec-artifacts-iso
org: agent-ix
component_type: filament-module
implementation_language: python
tags:
  - spec
  - iso
  - filament-module
standards_alignment:
  - iso-iec-ieee-29148
relationships:
  - target: "ix://agent-ix/filament-core-service/FR-035"
    type: "depends_on"
---
# Master Requirements Specification

## Purpose

This document specifies the requirements for `spec-artifacts-iso`, the Filament
Module that contributes ISO-style spec-artifact archetypes. Spec authors shall be
able to author and structurally validate FR/NFR/StR/US/IT/TC documents — plus a
generic `master-requirements` spec — directly as markdown from the per-archetype
skeletons, with structural completeness checked by quire-rs `validate_document`
and no render step.

## Scope

### In Scope

- The Module manifest the package contributes: the `Spec` archetype, the
  `iso-spec-core` grammar, the per-archetype `body_extraction` asserts, and the
  JSON Schema frontmatter validation it declares.
- The per-archetype authoring skeletons (the source of truth) shipped under
  `skeletons/` and consumed by authors and the `quire validate` CLI.
- The TypeSpec source under `spec_artifacts_iso/semantic/` and the JSON Schema
  2020-12 bundle projected from it at `spec_artifacts_iso/schemas/<Model>.json`,
  together with `spec_artifacts_iso/semantic/generated/toolchain.json` and the
  `make schemas` and `make schemas-check` targets that regenerate and check it.
- The `semantic` block of `spec_artifacts_iso/manifest.yaml` and the
  per-archetype `data_schema: { schema, digest }` references that bind each
  artifact type to the exact shipped schema bytes.
- `spec_artifacts_iso/mappings.yaml`, the golden records at
  `spec_artifacts_iso/examples/<type>.record.json`, and the Python reference
  mapping the test suite uses to build a record from an authored document.

### Out of Scope

- The `quire-rs` validation engine itself (`validate_document`, extraction); this
  Module declares the archetypes, the engine enforces them.
- Render templates and `template_ref`; these were removed (render removal,
  2026-06-04) and are not part of this Module.
- Generated-language fixtures — the Rust, TypeScript, and Python projections of
  these models. They were dropped from agent-ix/spec-artifacts-iso#34
  deliberately; this Module ships JSON Schema only. Owner:
  agent-ix/filament-core-data#36, with the public `@agent-ix/semantic-core`
  publish tracked by agent-ix/filament-core-data#11.
- Validating an artifact-type record against its `data_schema` at load time.
  quire's `validate_document` validates a *declaration* record
  (`{fields, clauses, operations}`) on the `object:` axis only and never reaches
  an artifact-type record. That is engine work owned by agent-ix/quire-rs
  (agent-ix/quire-rs#393); until it lands, this Module's own test suite is the
  record oracle.
- Amending the quoin FR-070 contract so `semantic.exports` admits artifact types
  and not only `object_types` names. Owner: agent-ix/quoin
  (agent-ix/quoin#336); the change is quoin's, not this Module's.
- Closing the `status` frontmatter vocabulary (16 spellings over 973 corpus
  documents). Closing it is a vocabulary sweep-and-report, not a side effect of
  this schema set. Owner: a later sweep in this repository.
- Making the offline, no-network run a CI job. NFR-001 calls this "the corpus
  promotion gate"; it is not owned by agent-ix/spec-artifacts-iso#34. The
  offline run stays a manual gate recorded in the release notes, and no CI job
  is claimed here.

## System Overview

### System Description

The Module contributes the `spec` archetype, the `iso-spec-core` grammar, and the
ISO artifact archetypes (FR, NFR, StR, US, IT, TC) as unified-shape archetypes —
per-archetype authoring skeletons (the source of truth), `body_extraction`
asserts, and JSON Schema frontmatter validation — together with a generic
`master-requirements` archetype. Templates (`.md.j2`) and `template_ref` are
removed (parity with quire-rs commit 500a3d3 and filament-core FR-035 CR-002);
structural completeness is checked by quire-rs `validate_document`.

Beside the archetypes, the Module declares one semantic data model per ISO
artifact type as TypeSpec under `spec_artifacts_iso/semantic/`, ships the JSON
Schema 2020-12 projection of each model at
`spec_artifacts_iso/schemas/<Model>.json` with the `toolchain.json` that records
the projection's provenance, and binds each artifact type to its schema by
module-relative path and SHA-256 digest through the manifest `semantic` block
and per-archetype `data_schema` references. `spec_artifacts_iso/mappings.yaml`
declares how the authored Markdown fills each field of a record, and
`spec_artifacts_iso/examples/<type>.record.json` carries one golden record per
skeleton. Markdown remains the sole authority; the record is a derived
projection. The manifest's `semantic.legacy_forms: warning` governs the legacy
`## Properties` forms quoin FR-074 sweeps, which this Module's own documents
never author; that is why `sweep_report` is absent.

### Intended Users

Filament platform spec authors, agent CLI authors (quire-cli), and validators
who author markdown artifacts from the skeletons and check them with
`validate_document`, together with the semantic consumers of the emitted
schemas and records — the quire-contract-ir frontends, the filament-core-data
code generators, and the Filament extraction API.

## Requirements Architecture

The requirement classes that make up this specification trace to one another as
follows:

- `stakeholder/` — StR-XXX stakeholder requirements (the authoring + validation need).
- `usecase/` — US-XXX user stories stating the consumer-side need the functional
  requirements implement (typed semantic records for the ISO artifact types).
- `functional/` — FR-XXX functional requirements (manifest activation, unified
  archetype validation, the `master-requirements` archetype, the emitted
  semantic data schemas, the manifest `semantic` block and `data_schema`
  references, and the Markdown mappings and round-trip policy).
- `non-functional/` — NFR-XXX quality requirements constraining the functional
  ones (reproducible, offline schema projection).
- `integration/` — IT-XXX integration tests verifying activation against
  filament-core and direct-markdown validate/extract roundtrips.
- `tests.md` — the requirements test matrix mapping every Acceptance Criterion to
  its covering test.

## References

- ISO/IEC/IEEE 29148 — Requirements engineering.
- filament-core-service [FR-035](ix://agent-ix/filament-core-service/FR-035) — Module Manifest Schema (the upstream this Module
  activates against).
- quire-rs `validate_document` — the structural validation engine that enforces
  the archetypes declared here.
