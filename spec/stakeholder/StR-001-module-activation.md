---
id: StR-001
title: "ISO-style spec artifact templates"
artifact_type: StR
---
# [StR-001] ISO-style spec artifact templates

## Stakeholder

Filament platform / spec authors / agent CLI generators.

## Need

Spec authors need fast, validated generation of FR/NFR/StR/US/IT/TC/AC/CON documents with consistent structure.

## Acceptance Criteria

| ID | Criteria |
|----|----------|
| StR-001-AC-1 | A Module activation against filament-core registers the contents this module declares. |
| StR-001-AC-2 | Agent CLI generators (quire-cli) can produce valid artifacts using the templates and schemas this module ships. |

## Dependencies

- **Upstream**: filament-core-service FR-035 (Module Manifest Schema)
