---
id: StR-001
title: "ISO-style spec artifact archetypes"
artifact_type: StR
---
# [StR-001] ISO-style spec artifact archetypes

> **CR (render removal — 2026-06-04):** templates are removed; the per-archetype
> **skeletons** are the authoring source of truth. The need is reframed from
> "generation" to fast, validated **authoring + structural validation**. AC-2 is
> revised off templates.

## Stakeholder

Filament platform / spec authors / agent CLI authors + validators.

## Need

Spec authors need fast, structurally **validated authoring** of FR/NFR/StR/US/IT/TC/AC/CON documents with consistent structure (authored as markdown from the per-archetype skeletons, checked by `validate_document`).

## Acceptance Criteria

| ID | Criteria |
|----|----------|
| StR-001-AC-1 | A Module activation against filament-core registers the contents this module declares. |
| StR-001-AC-2 | Agent CLI authors (quire-cli) can author and validate artifacts using the skeletons, `body_extraction` asserts, and frontmatter schemas this module ships (no template render). |

## Dependencies

- **Upstream**: filament-core-service FR-035 (Module Manifest Schema)
