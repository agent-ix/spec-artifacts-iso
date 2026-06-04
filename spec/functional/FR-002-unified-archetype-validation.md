---
id: FR-002
title: "Archetypes use the unified shape and validate authored markdown"
artifact_type: FR
relationships:
  - target: "ix://agent-ix/filament-core-service/FR-035"
    type: "implements"
  - target: "ix://agent-ix/quire-rs/spec/functional/FR-032"
    type: "consumes"
  - target: "ix://agent-ix/spec-artifacts-iso/FR-001"
    type: "extends"
---
# [FR-002] Archetypes use the unified shape and validate authored markdown

## Description

The system **SHALL** declare every ISO archetype (FR, NFR, StR, US, IT, TC, AC, CON)
in the **unified archetype shape** (filament-core FR-035 CR-002; quire-rs ADR 0003):
`frontmatter_schema_ref` + `body_extraction` with `assert` facets; `template_ref`
optional/legacy; no `required_sections` and no `variants`.

Each archetype's `body_extraction` **SHALL** assert its required structure such that
quire-rs `validate_document` (quire-rs FR-032) accepts a conformant authored
markdown artifact and rejects structural violations — without any render step.

## Specification

### Inputs

- `spec_artifacts_iso/manifest.yaml` (unified archetype declarations)
- An authored markdown artifact for an archetype

### Outputs

- A `ValidationResult` (pass / line-numbered failures) from `validate_document`
- An extracted data record from `extract` over the same `body_extraction`

### Behavior

- Each archetype **SHALL** assert section presence at the declared heading level, required tables (exact `columns`, `min_rows`), required lists (`min_items`), and id patterns where applicable.
- Acceptance-criteria / constraint id asserts **SHALL** use `{id}` interpolation (quire-rs FR-034) so row ids are prefixed with the document's own id and contiguous.
- Archetype structure **SHALL** keep headings unique per level (quire-rs FR-035) and fit the 2-level nesting ceiling (quire-rs ADR 0005 #4).
- Each archetype **SHALL** ship an authoring **skeleton** (the example an author fills), replacing former template placeholder defaults.

## Acceptance Criteria

| ID | Criteria | Verification |
|----|----------|--------------|
| FR-002-AC-1 | All eight archetypes declare `body_extraction` with `assert` facets; none declare `required_sections` or `variants` | Schema Test |
| FR-002-AC-2 | A conformant authored `FR` markdown artifact passes `validate_document`; copies with a missing required section, wrong Acceptance-Criteria columns, or a non-contiguous AC id each fail with a line-numbered diagnostic | Integration Test |
| FR-002-AC-3 | Acceptance-Criteria id asserts use `{id}` so a row prefixed with a different artifact's id fails | Integration Test |
| FR-002-AC-4 | Every archetype's declared headings are unique per level across its skeleton | Schema Test |
| FR-002-AC-5 | Each archetype ships an authoring skeleton that itself passes `validate_document` once filled with substantive content | Integration Test |

## Dependencies

- **Upstream**: filament-core-service FR-035 (CR-002 unified shape), quire-rs FR-031/FR-032/FR-033/FR-034/FR-035
- **Downstream**: the `/specify` authoring workflow; consumers validating ISO artifacts
