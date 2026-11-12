---
id: FR-008
title: "Requirement archetypes carry an optional enumerated criticality field"
type: FR
relationships:
  - target: "ix://agent-ix/spec-artifacts-iso/StR-001"
    type: "satisfies"
  - target: "ix://agent-ix/spec-artifacts-iso/FR-002"
    type: "extends"
  - target: "ix://agent-ix/spec-artifacts-iso/FR-005"
    type: "extends"
  - target: "ix://agent-ix/quire-rs/spec/functional/FR-082"
    type: "references"
---
# FR-008: Requirement archetypes carry an optional enumerated criticality field

## Description

A requirement's criticality is a human judgement about how much its failure matters. A
traceability report can only show it if the requirement can record it. This requirement adds an
optional frontmatter field, `criticality`, to the requirement archetypes `StR`, `US`, `FR` and
`NFR`.

The permitted values are `low`, `medium` and `high`, ordered `low` < `medium` < `high`. The four
frontmatter schemas **SHALL** declare the enumeration inline, as `quality_attribute` does on the
NFR schema. The matching TypeSpec models in `main.tsp` **SHALL** declare `criticality?`, so the
projected record schemas carry it (FR-005). Any shared enumeration file is generated from
`main.tsp`, never hand-written.

Criticality is its own axis. It is a requirement-level importance rating, and it is not a software
safety class; a later mapping from criticality onto a safety class is a separate decision and is
not made here.

The field is optional. A requirement that omits it is valid, and "no criticality assigned" is a
real state that consumers report as such ([quire-rs FR-082](ix://agent-ix/quire-rs/spec/functional/FR-082)).
The module **SHALL NOT** supply a default for `criticality`. A person authors the value, and no
tool computes it.

## Acceptance Criteria

| ID | Criteria | Verification |
|----|----------|--------------|
| FR-008-AC-1 | The frontmatter schemas for `StR`, `US`, `FR` and `NFR` each declare an optional `criticality` property with the inline enumeration `low`, `medium`, `high`; `criticality` is in none of their `required` lists; no hand-written shared enumeration file exists. | Test |
| FR-008-AC-2 | For each of `StR`, `US`, `FR` and `NFR`, a document with `criticality: low`, `medium` or `high` passes `quire validate`. | Test |
| FR-008-AC-3 | The TypeSpec `FR`, `NFR`, `StR` and `US` models each declare `criticality?` as the three-value enum, the projected `FR.json`, `NFR.json`, `StR.json` and `US.json` carry it as optional, and `make schemas-check` passes. | Test |
| FR-008-AC-4 | For each of `StR`, `US`, `FR` and `NFR`, a document that omits `criticality` passes `quire validate` and its mapped record carries no `criticality` value. | Test |
| FR-008-AC-5 | A document with `criticality: critical` (outside the enumeration) fails `quire validate` with a diagnostic naming the `criticality` field. | Test |
| FR-008-AC-6 | A document with `criticality: High` (wrong case) or `criticality: ""` fails `quire validate`; neither is normalised nor treated as absent. | Test |
| FR-008-AC-7 | No frontmatter or record schema carries a `default` for `criticality`. | Inspection |

## Constraints

| ID | Constraint | Type | Validation |
|----|-----------|------|------------|
| FR-008-CON-1 | The module declares the enumeration inline in each frontmatter schema and in `main.tsp`, and generates any shared enumeration file from `main.tsp`. | Design | Inspection |

## Dependencies

- **Upstream**: [FR-002](./FR-002-unified-archetype-validation.md) (archetype frontmatter validation), [FR-005](./FR-005-semantic-data-schemas.md) (typed data models), [FR-007](./FR-007-markdown-mappings.md) (frontmatter mapping)
