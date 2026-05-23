# Specification: spec-artifacts-iso

## Purpose

Spec authors need fast, validated generation of FR/NFR/StR/US/IT/TC/AC/CON documents with consistent structure.

## Module Summary

Module contributes the `spec` archetype, `iso-spec-core` grammar, and 8 artifact_types (FR, NFR, StR, US, IT, TC, AC, CON) with Jinja .md.j2 templates and JSON Schema frontmatter validation.

## Structure

- `stakeholder/` — StR-XXX stakeholder requirements
- `functional/` — FR-XXX functional requirements
- `integration/` — IT-XXX integration tests
- `tests.md` — test matrix
