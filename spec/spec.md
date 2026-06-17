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

### Out of Scope

- The `quire-rs` validation engine itself (`validate_document`, extraction); this
  Module declares the archetypes, the engine enforces them.
- Render templates and `template_ref`; these were removed (render removal,
  2026-06-04) and are not part of this Module.

## System Overview

### System Description

The Module contributes the `spec` archetype, the `iso-spec-core` grammar, and the
ISO artifact archetypes (FR, NFR, StR, US, IT, TC) as unified-shape archetypes —
per-archetype authoring skeletons (the source of truth), `body_extraction`
asserts, and JSON Schema frontmatter validation — together with a generic
`master-requirements` archetype. Templates (`.md.j2`) and `template_ref` are
removed (parity with quire-rs commit 500a3d3 and filament-core FR-035 CR-002);
structural completeness is checked by quire-rs `validate_document`.

### Intended Users

Filament platform spec authors, agent CLI authors (quire-cli), and validators
who author markdown artifacts from the skeletons and check them with
`validate_document`.

## Requirements Architecture

The requirement classes that make up this specification trace to one another as
follows:

- `stakeholder/` — StR-XXX stakeholder requirements (the authoring + validation need).
- `functional/` — FR-XXX functional requirements (manifest activation, unified
  archetype validation, the `master-requirements` archetype).
- `integration/` — IT-XXX integration tests verifying activation against
  filament-core and direct-markdown validate/extract roundtrips.
- `tests.md` — the requirements test matrix mapping every Acceptance Criterion to
  its covering test.

## References

- ISO/IEC/IEEE 29148 — Requirements engineering.
- filament-core-service FR-035 — Module Manifest Schema (the upstream this Module
  activates against).
- quire-rs `validate_document` — the structural validation engine that enforces
  the archetypes declared here.
