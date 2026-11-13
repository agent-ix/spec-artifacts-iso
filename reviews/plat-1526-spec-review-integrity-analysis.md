---
id: SR-033
title: "Integrity review — FR-009 software safety class field (PLAT-1526, #73)"
type: SpecReview
analysis: integrity
scope: "agent-ix/spec-artifacts-iso; spec/functional/FR-009-software-safety-class-field.md, spec/functional/index.md"
review_set: subset
---
# SR-033: Integrity review — FR-009 software safety class field (PLAT-1526, #73)

## Summary

Ticket: PLAT-1526, PR agent-ix/spec-artifacts-iso#73. Structure checks: the FR-009 id is next after FR-008. The
AC ids FR-009-AC-1..12 and constraint ids FR-009-CON-1..2 run in sequence with no gaps or duplicates. The index line
is added and its title matches the frontmatter `title`. Every AC has a Verification method. `quire validate` passes.
The AC set covers the negative cases FR-008 covers: an out-of-enum value (AC-5), wrong case (AC-6) and an empty
string (AC-7). It adds independence from criticality (AC-10), no skeleton value (AC-11) and the carried-field
declaration (AC-12). The AC-3/AC-9 record-key contradiction is recorded in SR-031 FND-001 and is not repeated here.

## Verdict

**Minor findings.** Two low findings: one AC leaves the TypeSpec form open, and one AC is compound.

## Findings

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-001 | low | AC-3 asks for `software_safety_class?` "as the ordered enum" and for the projected order to equal the frontmatter order, but does not say which TypeSpec form it means. The module's `criticality` is a string-literal union, which projects inline as `anyOf` of `const`. A TypeSpec `enum`, like `QualityAttribute`, projects to a `$ref` to a separate generated schema file. Two implementers would produce different projected shapes, and "the enumeration order in the projected schemas" is checked in a different place in each. | spec/functional/FR-009-software-safety-class-field.md:59 |
| FND-002 | low | AC-10 is compound. A Test half (two documents pass `quire validate`) is joined to an Inspection half ("no schema, mapping or skeleton relates the two fields") under the single Verification `Test`. The second half is the independence claim, and no test of the first half can fail on it. | spec/functional/FR-009-software-safety-class-field.md:66 |

## New findings (disposition pass 1)

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-003 | low | AC-10's second document (`criticality: low`, `software_safety_class: class-3`) is not stated to carry an assigner and rationale; read literally it fails `quire validate` under AC-13 (class without rationale/assigner), so the AC asserts a pass that the spec forbids. Say "each with assigner and rationale". | spec/functional/FR-009-software-safety-class-field.md:81 |

## Dispositions

| FND | outcome | reason |
| --- | --- | --- |
| FND-001 | fixed | Verified at head 833128e (round 1) |
| FND-002 | fixed | Verified at head 833128e (round 1) |
| FND-003 | fixed | Verified at head 0ece6d8 (round 2) |
