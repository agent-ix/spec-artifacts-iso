---
id: SR-003
title: "Base checklist review of the #34 semantic-schema requirement set"
type: SpecReview
analysis: base
scope: "spec/usecase/US-001, spec/functional/FR-005, FR-006, FR-007, spec/non-functional/NFR-001, spec/tests.md (TC-039..TC-059)"
review_set: all
---
# SR-003: Base checklist review of the #34 semantic-schema requirement set

## Summary

Checklist pass (ID formats, US/FR quality, the six coverage rules, cross
references) over the five artifacts authored for agent-ix/spec-artifacts-iso#34
and their 21 matrix rows. IDs continue the existing sequences with no gap
(FR-004 → FR-005..007; TC-038 → TC-039..059; first US and first NFR in the
bundle). Every AC and CON of FR-005..007 has at least one matrix row and every
row traces to an existing criterion. `quire validate` reports zero errors over
`spec/**/*.md`; the remaining warnings are EARS advisories handled by SR-010.
The checklist gaps found are boundary rows the matrix does not yet call out
explicitly, one criterion that names an external tool's future behaviour, and
the master spec's scope sections, which still describe the pre-#34 module.

## Verdict

**CONDITIONAL** — no high findings; three mediums to apply before planning
(FND-002, FND-003, FND-004), the rest low.

## Findings

| ID      | Severity | Summary | Refs |
| ------- | -------- | ------- | ---- |
| FND-001 | low      | ID formats conform (`US-001`, `FR-005..007`, `NFR-001`, `TC-039..059`, `FR-00N-AC-N`, `FR-00N-CON-N`); no duplicates, sequences continue the highest id found on any remote branch (FR-004, TC-038). | spec/tests.md |
| FND-002 | medium   | Constraint-boundary rule: the matrix has no explicit row for the `minItems: 1` boundary (a typed table with a header and zero data rows) nor for the `line`/`startLine` lower bound (`minimum: 1`); TC-045 lists mutations but not the empty-table case. Add the zero-row case to TC-045 and a `line: 0` case to the negative schema test. | FR-005-AC-4, spec/tests.md TC-045 |
| FND-003 | medium   | Edge-case rule: no row exercises a CRLF document, an empty `Verification` cell (41 in the census), or a `status` outside the pattern — the three corpus-attested edge cases FR-005 itself cites. Add them to TC-045 (mapping/schema negative) or a new row. | FR-005 Behavior, spec/tests.md |
| FND-004 | medium   | `spec/spec.md` Scope / Out of Scope / System Overview still describe the pre-#34 module (no semantic block, no schemas, no TypeSpec); the ticket's dropped deliverable (generated-language fixtures → agent-ix/filament-core-data#11/#36) is named nowhere in the bundle. Update the master spec before planning. | spec/spec.md, agent-ix/spec-artifacts-iso#34 |
| FND-005 | low      | US-001 carries illustrative examples rather than Given/When/Then acceptance criteria; that is the module's own US contract (`us-acceptance-criteria-drift` lint), so the checklist item "≥ 2 acceptance criteria" is satisfied by the two `US-001-EX` examples plus the FR criteria it exercises. No change. | US-001 |
| FND-006 | low      | NFR-001 has no `-AC-` ids (its criteria are the Measurement rows), so TC-056..058 trace to `NFR-001 (metric n)`; `quire validate` accepts the form. Record the convention in the matrix Overview so a later reader does not "fix" it. | spec/tests.md |
| FND-007 | low      | FR-006-AC-6 accepts two outcomes ("succeeds, or fails with exactly `semantic.unknown-export`"). Acceptable as a Demonstration criterion because the second outcome is the documented contract gap with a filing obligation, but the matrix row (TC-055) must record which outcome occurred. | FR-006-AC-6, TC-055 |
| FND-008 | low      | Cross-references resolve: FR-005/006/007 → US-001 (`implements`), US-001 → FR-005..007 (`exercises`), NFR-001 → FR-005/006 (`constrains`); external `ix://` targets name existing quoin, quire-rs and filament-core-data requirements. | all |

## Checklist

| Gate | Result |
| ---- | ------ |
| ID format and uniqueness | pass |
| User story quality (INVEST, no solution prescribing) | pass — mechanism left to FR-005..007 |
| FR quality (inputs, outputs, behavior, constraints with rationale/validation, error conditions) | pass — error conditions stated as `If … then` bullets in each FR |
| Six coverage rules | coverage pass; option permutation n/a; boundary and edge partial (FND-002, FND-003); error path pass (TC-045, TC-047, TC-049, TC-051); state transition n/a |
| Cross-referencing | pass (FND-008) |

## Dispositions

| Finding | Disposition |
| ------- | ----------- |
| FND-002 | applied — TC-045 gains the zero-row and `line: 0` cases |
| FND-003 | applied — TC-045 gains CRLF, empty `Verification` cell, and out-of-pattern `status` cases |
| FND-004 | applied — spec/spec.md Scope, Out of Scope, System Overview and Requirements Architecture updated for #34 |
| FND-005..008 | noted, no change |
