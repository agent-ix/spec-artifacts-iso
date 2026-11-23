---
id: SR-042
title: "Spec review (EARS) — FR-004 control verification verbs (PLAT-1837, #76)"
type: SpecReview
analysis: ears-conformance
scope: "agent-ix/spec-artifacts-iso; statements added or changed in spec/functional/FR-004-edge-type-vocabulary.md (Control verification verbs section, FR-004-AC-8, FR-004-CON-1)"
review_set: subset
relationships:
  - { target: "ix://agent-ix/spec-artifacts-iso/FR-004", type: references }
---
# SR-042: Spec review (EARS) — FR-004 control verification verbs (PLAT-1837, #76)

## Summary

Ticket: PLAT-1837. I checked the new "Control verification verbs" section, AC-8
and CON-1 against EARS. AC-8 is a testable acceptance criterion with an
observable response (no `disallowed-edge-type`, and a negative control). CON-1
is a process constraint and needs no EARS form.

## Verdict

Conformant except that the new section is not normative.

## Findings

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-001 | low | The new section uses no SHALL. It describes the state ("the vocabulary declares two further `traceability` verbs … The `NFR`, `IT` and `TC` archetypes … may author both"). The sibling section for the NFR `mitigates` allowance states its obligation as "The `NFR` archetype's `allowed_links` **SHALL** include `mitigates`". Add the matching ubiquitous statements, for example "The module SHALL declare `verifies_implementation` and `verifies_effectiveness` as `traceability` verbs, and the `NFR`, `IT` and `TC` archetypes' `allowed_links` SHALL include both." | spec/functional/FR-004-edge-type-vocabulary.md:91-98 |

## Dispositions

| FND | outcome | reason |
| --- | --- | --- |
| FND-001 | fixed | Round 1, head 3084a3d. FR-004 line 100 adds: "The vocabulary SHALL declare `verifies_implementation` and `verifies_effectiveness` as `traceability` verbs, and the `NFR`, `IT` and `TC` archetypes SHALL allow both in `allowed_links`." This matches the form of the sibling `mitigates` statement. |
