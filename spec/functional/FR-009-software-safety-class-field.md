---
id: FR-009
title: "Requirement archetypes carry an optional software safety class field with a module-declared ordered vocabulary"
type: FR
relationships:
  - target: "ix://agent-ix/spec-artifacts-iso/StR-001"
    type: "satisfies"
  - target: "ix://agent-ix/spec-artifacts-iso/FR-002"
    type: "extends"
  - target: "ix://agent-ix/spec-artifacts-iso/FR-005"
    type: "extends"
  - target: "ix://agent-ix/spec-artifacts-iso/FR-007"
    type: "extends"
  - target: "ix://agent-ix/spec-artifacts-iso/FR-008"
    type: "references"
---
# FR-009: Requirement archetypes carry an optional software safety class field with a module-declared ordered vocabulary

Tracked by Linear PLAT-1526 (implemented by PLAT-1577).

## Description

A software safety class is a person's judgement of how much rigour the software that realises a
requirement must be built and verified with. It is its own axis. It is not [criticality](./FR-008-criticality-field.md):
criticality rates how much a requirement's failure matters to its stakeholders, the class rates the
rigour demanded of the software item the requirement is allocated to. Neither value implies, bounds
or is computed from the other, and this module declares no mapping between them.

This requirement adds an optional frontmatter field, `software_safety_class`, to the requirement
archetypes `StR`, `US`, `FR` and `NFR`. A requirement states the class it is written for. The class
itself is assigned to a software system or software item by a named person with a rationale; that
assignment is owned by the architecture module
([spec-objects-architecture FR-012](ix://agent-ix/spec-objects-architecture/FR-012)), and the field
here only states which class a requirement expects its item to carry.

### The vocabulary is module data

The permitted values are an **ordered** list declared once, as the inline `enum` of the field in the
four frontmatter schemas, in `main.tsp` as an enum on `software_safety_class?`, and in the projected record
schemas. The list is ordered from the lowest to the highest rigour; the position in the `enum` is the
order, and no value carries a numeric weight. The shipped list is `class-1`, `class-2`, `class-3`.
The tokens are neutral labels. They name no standard and quote no text of one; another rigour
scheme is supported by replacing the list in the module data, with no change to any engine, because
every consumer reads the order from the `enum` and holds no copy of it.

### Nothing assigns, derives or defaults a class

The field is optional. A requirement that omits it is valid, and "no class stated" is a real state that
consumers report as `unassigned`. The module **SHALL NOT** supply a default for `software_safety_class`.
No tool computes the value from `criticality`, from a relationship, from the class of an item or from
the highest value among related requirements; a person authors it.

## Acceptance Criteria

| ID | Criteria | Verification |
|----|----------|--------------|
| FR-009-AC-1 | The frontmatter schemas for `StR`, `US`, `FR` and `NFR` each declare an optional `software_safety_class` property with the inline ordered enumeration `class-1`, `class-2`, `class-3`; it is in none of their `required` lists; no hand-written shared enumeration file exists. | Test |
| FR-009-AC-2 | For each of `StR`, `US`, `FR` and `NFR`, a document with `software_safety_class` set to each enumerated value passes `quire validate`. | Test |
| FR-009-AC-3 | The TypeSpec `FR`, `NFR`, `StR` and `US` models each declare `software_safety_class?` as the ordered enum, the projected `FR.json`, `NFR.json`, `StR.json` and `US.json` carry it as optional, and the enumeration order in the projected schemas equals the order in the frontmatter schemas. | Test |
| FR-009-AC-4 | For each of `StR`, `US`, `FR` and `NFR`, a document that omits `software_safety_class` passes `quire validate` and its mapped record carries no `softwareSafetyClass` value. | Test |
| FR-009-AC-5 | A document with `software_safety_class: class-9` (outside the enumeration) fails `quire validate` with a diagnostic naming the `software_safety_class` field. | Test |
| FR-009-AC-6 | A document with `software_safety_class: Class-1` (wrong case) fails `quire validate` with a diagnostic naming the field; the value is not normalised. | Test |
| FR-009-AC-7 | A document with `software_safety_class: ""` fails `quire validate` with a diagnostic naming the field; it is not treated as absent. | Test |
| FR-009-AC-8 | No frontmatter or record schema carries a `default` for `software_safety_class`. | Inspection |
| FR-009-AC-9 | For `FR`, `NFR`, `StR` and `US`, `mappings.yaml` maps `softwareSafetyClass` with `kind: frontmatter` and `source: {key: software_safety_class}`, `lossless: false`, as FR-007 maps `criticality`; a document without the key yields a record without it. | Test |
| FR-009-AC-10 | A document carrying `criticality: high` and `software_safety_class: class-1`, and one carrying `criticality: low` and `software_safety_class: class-3`, both pass `quire validate`; no schema, mapping or skeleton relates the two fields. | Test |
| FR-009-AC-11 | No skeleton under `skeletons/` carries a `software_safety_class` value. | Inspection |
| FR-009-AC-12 | The manifest declares a `traceability.carried_fields` entry ([quire-rs FR-090](ix://agent-ix/quire-rs/spec/functional/FR-090)) with `name` and `key` `software_safety_class` and `from` `StR`, `US`, `FR`, `NFR`, and no `carried_fields` entry for `criticality`; a corpus over the module carries the stated class onto the coverage matrix entry and each obligation of a requirement stating one. | Test |

## Constraints

| ID | Constraint | Type | Validation |
|----|-----------|------|------------|
| FR-009-CON-1 | The module declares the ordered enumeration in exactly the frontmatter schemas and `main.tsp`, generates any projected copy from `main.tsp`, and names no standard or its text in any value, description or example. | Design | Inspection |
| FR-009-CON-2 | No file in the module computes, fills in or rewrites a `software_safety_class` value. | Design | Inspection |

## Dependencies

- **Upstream**: [FR-002](./FR-002-unified-archetype-validation.md), [FR-005](./FR-005-semantic-data-schemas.md), [FR-007](./FR-007-markdown-mappings.md), [FR-008](./FR-008-criticality-field.md) (the separate axis)
- **Downstream**: [spec-objects-architecture FR-012](ix://agent-ix/spec-objects-architecture/FR-012) (item assignment), [quire-rs FR-090](ix://agent-ix/quire-rs/spec/functional/FR-090) (carries the stated class), [quire-rs FR-091](ix://agent-ix/quire-rs/spec/functional/FR-091) (reports inconsistency), [quoin FR-160](ix://agent-ix/quoin/FR-160) (per-class evidence floors)
