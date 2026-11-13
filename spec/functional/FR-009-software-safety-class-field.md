---
id: FR-009
title: "Requirement archetypes carry an optional human-assigned software safety class with assigner and rationale, over a module-declared ordered vocabulary"
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
  - target: "ix://agent-ix/quire-rs/FR-090"
    type: "depends_on"
---
# FR-009: Requirement archetypes carry an optional human-assigned software safety class with assigner and rationale, over a module-declared ordered vocabulary

Tracked by Linear PLAT-1526 (implemented by PLAT-1577).

## Description

A software safety class is a person's judgement of how much rigour the software that realises a
requirement must be built and verified with. It is its own axis. It is not [criticality](./FR-008-criticality-field.md):
criticality rates how much a requirement's failure matters to its stakeholders, the class rates the
rigour demanded of the software item the requirement is allocated to. Neither value implies, bounds
or is computed from the other, and this module declares no mapping between them.

The four frontmatter schemas for the requirement archetypes `StR`, `US`, `FR` and `NFR` **SHALL** each
declare three optional properties:

- `software_safety_class`, one value of the ordered vocabulary below;
- `software_safety_class_assigned_by`, the name of the person who assigned the class, a string of at least one character;
- `software_safety_class_rationale`, that person's reason, a string of at least one character.

The three are required together: a document that carries any one of them **SHALL** carry all three. The
value that sets the rigour a requirement is verified at therefore always has a named person and a reason.
That the named person is who they say is the concern of the signed git history of the file, not of this module.
The same three fields, with the same vocabulary, are declared for software systems and software items by the
architecture module ([spec-objects-architecture FR-012](ix://agent-ix/spec-objects-architecture/FR-012)); a requirement
that states a class states the class it expects its item to carry, and a check reports where the two disagree
([quire-rs FR-091](ix://agent-ix/quire-rs/FR-091)).

### The vocabulary is module data

The permitted values are an **ordered** list declared as the `enum` of `software_safety_class` in the four
frontmatter schemas and as the string-literal union `"class-1" | "class-2" | "class-3"` on `software_safety_class?` in the
`StR`, `US`, `FR` and `NFR` models of `semantic/main.tsp`, which is the form `criticality` uses and which projects
inline into the record schemas. The four `enum`s are identical, in the same order. The list runs from the lowest to
the highest rigour; the position is the order and no value carries a numeric weight. The shipped tokens are neutral
labels. They name no standard and quote no text of one. Another rigour scheme is supported by replacing the list in
the module data, with no change to any engine, because every consumer reads the order from the `enum` and holds no
copy of it. This module is the one place the list is declared; the architecture module repeats it only as a test
fixture of its own conformance ([spec-objects-architecture FR-012](ix://agent-ix/spec-objects-architecture/FR-012)-AC-9).

The frontmatter keys are snake_case and the mapped record keys are camelCase (`softwareSafetyClass`,
`softwareSafetyClassAssignedBy`, `softwareSafetyClassRationale`), as `quality_attribute` maps to `qualityAttribute`.

### Nothing assigns, derives or defaults a class

The fields are optional. A requirement that omits them is valid, and "no class stated" is a real state that
consumers report as `unassigned`. The module **SHALL NOT** supply a default for any of the three. No tool
computes the class from `criticality`, from a relationship, from the class of an item or from the highest value
among related requirements; a person authors it.

## Acceptance Criteria

| ID | Criteria | Verification |
|----|----------|--------------|
| FR-009-AC-1 | The frontmatter schemas for `StR`, `US`, `FR` and `NFR` each declare optional `software_safety_class` (inline ordered enumeration `class-1`, `class-2`, `class-3`), `software_safety_class_assigned_by` and `software_safety_class_rationale` (non-empty strings); none is in a `required` list; no hand-written shared enumeration file exists. | Test |
| FR-009-AC-2 | For each of `StR`, `US`, `FR` and `NFR`, a document with each enumerated class plus a non-empty assigner and rationale passes `quire validate`. | Test |
| FR-009-AC-3 | The `StR`, `US`, `FR` and `NFR` models in `semantic/main.tsp` each declare `software_safety_class?` as the string-literal union `"class-1" \| "class-2" \| "class-3"` (the form of `criticality`) and the two companion properties as optional strings; the projected `FR.json`, `NFR.json`, `StR.json` and `US.json` carry all three as optional under their camelCase record keys, and the enumeration order of the projected schemas equals that of the frontmatter schemas. | Test |
| FR-009-AC-4 | For each of `StR`, `US`, `FR` and `NFR`, a document that omits all three passes `quire validate` and its mapped record carries none of `softwareSafetyClass`, `softwareSafetyClassAssignedBy`, `softwareSafetyClassRationale`. | Test |
| FR-009-AC-5 | A document with `software_safety_class: class-9` (outside the enumeration) fails `quire validate` with a diagnostic naming the `software_safety_class` field. | Test |
| FR-009-AC-6 | A document with `software_safety_class: Class-1` (wrong case) fails `quire validate` with a diagnostic naming the field; the value is not normalised. | Test |
| FR-009-AC-7 | A document with `software_safety_class: ""` fails `quire validate` with a diagnostic naming the field; it is not treated as absent. | Test |
| FR-009-AC-8 | No frontmatter or record schema carries a `default` for any of the three fields. | Inspection |
| FR-009-AC-9 | `mappings.yaml` maps `softwareSafetyClass`, `softwareSafetyClassAssignedBy` and `softwareSafetyClassRationale` for `FR`, `NFR`, `StR` and `US` with `kind: frontmatter`, `source: {key: <snake_case key>}`, `lossless: false`, as FR-007 maps `criticality`; a document without the keys yields a record without them. | Test |
| FR-009-AC-10 | A document carrying `criticality: high` and `software_safety_class: class-1` with assigner and rationale, and one carrying `criticality: low` and `software_safety_class: class-3`, both pass `quire validate`. | Test |
| FR-009-AC-11 | No schema, mapping or skeleton in the module refers to `criticality` from a class property or to a class property from `criticality`. | Inspection |
| FR-009-AC-12 | No skeleton under `skeletons/` carries any of the three fields. | Inspection |
| FR-009-AC-13 | A document with `software_safety_class` and no `software_safety_class_rationale`, one with no `software_safety_class_assigned_by`, and one with an empty-string assigner or rationale each fail `quire validate` naming the missing or empty field; a document with an assigner or rationale and no `software_safety_class` fails naming `software_safety_class`. | Test |
| FR-009-AC-14 | The manifest declares a `traceability.carried_fields` entry ([quire-rs FR-090](ix://agent-ix/quire-rs/FR-090)) with `name` and `key` `software_safety_class` and `from` `StR`, `US`, `FR`, `NFR`, and none for `criticality`. This module owns the entry. It lands after the engine accepts `carried_fields` (quire-rs FR-090), because an engine that does not know the key rejects the manifest. | Test |

## Constraints

| ID | Constraint | Type | Validation |
|----|-----------|------|------------|
| FR-009-CON-1 | The module declares the ordered enumeration in exactly the frontmatter schemas and `semantic/main.tsp`, generates any projected copy from `main.tsp`, and names no standard or its text in any value, description or example. | Design | Inspection |
| FR-009-CON-2 | No file in the module computes, fills in or rewrites a class, assigner or rationale value. | Design | Inspection |

## Dependencies

- **Upstream**: [FR-002](./FR-002-unified-archetype-validation.md), [FR-005](./FR-005-semantic-data-schemas.md), [FR-007](./FR-007-markdown-mappings.md), [FR-008](./FR-008-criticality-field.md) (the separate axis), [quire-rs FR-090](ix://agent-ix/quire-rs/FR-090) (the engine must accept `carried_fields` before AC-14 lands)
- **Downstream**: [spec-objects-architecture FR-012](ix://agent-ix/spec-objects-architecture/FR-012) (item assignment), [quire-rs FR-091](ix://agent-ix/quire-rs/FR-091) (reports inconsistency), [quoin FR-160](ix://agent-ix/quoin/FR-160) (per-class evidence floors)
