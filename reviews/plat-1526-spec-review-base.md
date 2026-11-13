---
id: SR-031
title: "Base spec review — FR-009 software safety class field (PLAT-1526, #73)"
type: SpecReview
analysis: base
scope: "agent-ix/spec-artifacts-iso; spec/functional/FR-009-software-safety-class-field.md, spec/functional/index.md"
review_set: subset
---
# SR-031: Base spec review — FR-009 software safety class field (PLAT-1526, #73)

## Summary

Ticket: PLAT-1526, PR agent-ix/spec-artifacts-iso#73 (head a6677fd). The diff adds one requirement, FR-009, and its
index line. Read against FR-008 (criticality), FR-007 (mappings), the module's `main.tsp`, frontmatter and projected
record schemas, `mappings.yaml` and manifest `traceability:` block, and the sibling specs on their PR branches:
quire-rs FR-090/FR-091 (#669), spec-objects-architecture FR-012 (#45) and quoin FR-160 (#855).

What was checked and holds:

- **Separate axes.** FR-009 keeps class and criticality apart and declares no mapping. AC-10 pairs `high`/`class-1`
  and `low`/`class-3`. FR-008 says the same from its side. No contradiction.
- **No assignment, derivation or default.** The text says SHALL NOT default, and no tool computes the value. AC-8
  (no `default`), AC-11 (no skeleton value) and CON-2 back this up.
- **Order as rank.** A JSON Schema `enum` is an ordered array, so ranking by position can be expressed. This is how
  quire-rs FR-090/FR-091 read the rank, from the `from` archetype's frontmatter `enum` (the FR-059 mechanism).
- **Licensing boundary.** The tokens `class-1..3`, "software safety class", "software system" and "software item" are
  generic. No standard is named or quoted. CON-1 forbids that.
- **No compatibility layer** and no pin, digest or tracking record.
- **Manifest entry shape.** AC-12's `carried_fields` entry (`name`, `key`, `from: [StR, US, FR, NFR]`) matches the
  three fields that quire-rs FR-090 as written reads. All four archetypes are declared and the key is in all four
  frontmatter schemas, so FR-090-AC-7 load validation would accept it. The cross-repo problems with AC-12 are in
  SR-034.
- `quire validate --scope . spec/functional/FR-009-software-safety-class-field.md` exits 0 with no diagnostics on
  FR-009.

## Verdict

**Changes requested.** One high and two medium findings. FR-009 contradicts itself on the record key's name. Its
"declared once, no copy" claim is not backed by any criterion. The value that drives quoin's per-class floors is the
requirement-level class, and that value has no named assigner and no rationale.

## Findings

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-001 | high | AC-3 (and the Description) requires the TypeSpec models to declare `software_safety_class?`, but AC-4 and AC-9 require the mapped record key `softwareSafetyClass`. The module convention is a camelCase record key over a snake_case frontmatter key (`qualityAttribute` ← `quality_attribute`). The projected `FR.json` is sealed by `unevaluatedProperties`, so the record that AC-9's mapping produces would fail the schema that AC-3 produces. | spec/functional/FR-009-software-safety-class-field.md:39,59,60,65 |
| FND-002 | medium | The Description says the ordered list is "declared once" and "every consumer reads the order from the `enum` and holds no copy of it". The same sentence lists nine places: four frontmatter schemas, `main.tsp` and four projected schemas. Five of them are hand-written. Only the shipped values are pinned (AC-1). No criterion requires the four frontmatter `enum`s to stay identical when "the list is replaced". quire-rs FR-091 `order_from` reads the rank from a single archetype, so a divergent list silently changes the ranks for the other three. | spec/functional/FR-009-software-safety-class-field.md:38-44 |
| FND-003 | medium | The person and rationale are recorded only for items (spec-objects-architecture FR-012: `Assigned By`, `Rationale`). The requirement-level `software_safety_class` that FR-009 adds has neither. Yet quoin FR-160 keys the evidence floors on the class carried from the requirement, "and only that", and not on the item. The class that sets rigour is therefore the one with no named person or rationale. The ticket scope puts that assignment on the system and its items. Either FR-009 states that the requirement field is only an expectation, to be checked against the item by quire-rs FR-091, and the floors key on the item's assigned class, or the requirement-level statement carries an assigner and a rationale too. | spec/functional/FR-009-software-safety-class-field.md:29-34 |

## New findings (disposition pass 1)

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-004 | medium | FR-009 now says the architecture module repeats the class list "only as a test fixture of its own conformance" and that every consumer "holds no copy". spec-objects-architecture FR-012 (PR #45 head) declares `softwareSafetyClass` in `model Part` (`typespec/main.tsp`) as the same string-literal union, in the record schema it ships, and FR-012-AC-9 pins the two lists identical with a parity test. That is a cross-repo copy plus a pin, not a fixture. It also falsifies "another rigour scheme is supported by replacing the list in the module data": replacing the iso list breaks the architecture module until its copy is edited too. Either the architecture record schema references the iso vocabulary instead of copying it (and AC-9 goes), or FR-009 drops the claim; a copy kept in sync by a parity test is the vendoring/pin antipattern. | spec/functional/FR-009-software-safety-class-field.md:53-56 |

## Dispositions

| FND | outcome | reason |
| --- | --- | --- |
| FND-001 | fixed | Verified at head 833128e (round 1) |
| FND-002 | fixed | Verified at head 833128e (round 1) |
| FND-003 | fixed | Verified at head 833128e (round 1) |
| FND-004 | fixed | Verified at head 0ece6d8 (round 2) |
