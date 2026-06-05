# Specification: spec-artifacts-iso

## Purpose

Spec authors need fast, structurally validated **authoring** of FR/NFR/StR/US/IT/TC/AC/CON documents with consistent structure (authored as markdown from the per-archetype skeletons; templates removed — see FR-002 CR).

## Module Summary

Module contributes the `spec` archetype, `iso-spec-core` grammar, and 8 artifact_types (FR, NFR, StR, US, IT, TC, AC, CON) as **unified-shape archetypes** — per-archetype authoring **skeletons** (the source of truth), `body_extraction` asserts, and JSON Schema frontmatter validation. **Templates (`.md.j2`) and `template_ref` are removed** (render removal, 2026-06-04; parity with quire-rs commit 500a3d3 and filament-core FR-035 CR-002); structural completeness is checked by quire-rs `validate_document`.

## Structure

- `stakeholder/` — StR-XXX stakeholder requirements
- `functional/` — FR-XXX functional requirements
- `integration/` — IT-XXX integration tests
- `tests.md` — test matrix
