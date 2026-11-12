---
id: FR-008
title: "Requirement archetypes carry an optional enumerated criticality field"
type: FR
relationships:
  - target: "ix://agent-ix/spec-artifacts-iso/StR-001"
    type: "satisfies"
  - target: "ix://agent-ix/spec-artifacts-iso/FR-002"
    type: "extends"
  - target: "ix://agent-ix/quire-rs/spec/functional/FR-082"
    type: "consumes"
---
# FR-008: Requirement archetypes carry an optional enumerated criticality field

## Description

A requirement's criticality is a human judgement about how much its failure matters. A
traceability report can only show it if the requirement can record it. This requirement adds an
optional frontmatter field, `criticality`, to the requirement archetypes `StR`, `US`, `FR` and
`NFR`.

The module **SHALL** declare the permitted values once, as a single enumerated schema
(`Criticality.json`) referenced by each of those archetypes' frontmatter schemas, so the
vocabulary is module data and not engine knowledge. The permitted values are `low`, `medium`
and `high`.

The field is optional. A requirement that omits it is valid and is not given a value by the
module, by a schema `default`, or by any tool; "no criticality assigned" is a real state, reported
as such by consumers ([quire-rs FR-082](ix://agent-ix/quire-rs/spec/functional/FR-082)). The
value is authored by a person; nothing in this module computes or infers it.

## Acceptance Criteria

| ID | Criteria | Verification |
|----|----------|--------------|
| FR-008-AC-1 | The frontmatter schemas for `StR`, `US`, `FR` and `NFR` each declare an optional `criticality` property that references the one shared `Criticality.json` enumeration; `criticality` is not in any of their `required` lists. | Test |
| FR-008-AC-2 | An `FR` whose frontmatter has `criticality: high` (and likewise `low`, `medium`) passes `quire validate`. | Test |
| FR-008-AC-3 | An `FR` that omits `criticality` passes `quire validate` and the validated record carries no `criticality` value. | Test |
| FR-008-AC-4 | An `FR` with `criticality: critical` (a value outside the enumeration) fails `quire validate` with a diagnostic naming the `criticality` field. | Test |
| FR-008-AC-5 | An `FR` with `criticality: High` (wrong case) or `criticality: ""` fails `quire validate`; neither is normalised nor treated as absent. | Test |
| FR-008-AC-6 | `Criticality.json` contains no `default` keyword, and no archetype schema supplies one for `criticality`. | Inspection |

## Constraints

| ID | Constraint | Type | Validation |
|----|-----------|------|------------|
| FR-008-CON-1 | Archetype schemas SHALL reference the single `Criticality.json` enumeration. | Design | Inspection |

## Dependencies

- **Upstream**: [FR-002](./FR-002-unified-archetype-validation.md) (archetype frontmatter validation)
- **Downstream**: quire-rs [FR-082](ix://agent-ix/quire-rs/spec/functional/FR-082) (criticality in the trace model)
