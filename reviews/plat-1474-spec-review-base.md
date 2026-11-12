---
id: SR-029
title: "Base spec review — FR-004 NFR mitigates allowance (PLAT-1495, #72)"
type: SpecReview
analysis: base
scope: "agent-ix/spec-artifacts-iso; spec/functional/FR-004-edge-type-vocabulary.md, spec/tests.md"
review_set: subset
---
# SR-029: Base spec review — FR-004 NFR mitigates allowance (PLAT-1495, #72)

## Summary

Ticket: PLAT-1495, which shares PR agent-ix/spec-artifacts-iso#72 with PLAT-1474. The spec changes are a new FR-004
subsection "Archetype `allowed_links` and the NFR `mitigates` edge", the criterion FR-004-AC-7, and TC-070 rows in
both `spec/tests.md` tables.

What was checked:

- **Intent.** The subsection says an NFR may author `mitigates`. Security and safety NFRs are required to mitigate a
  threat, hazard or failure mode, so the edge is legitimate. The citations are correct on the upstream mains:
  `spec-objects-security` FR-008 is `security-nfr-needs-mitigation-target` and `spec-objects-safety` FR-009 is
  `safety-nfr-needs-mitigation-target`.
- **Consistency with the vocabulary FR.** FR-004-CON-1 says the requirement "adds and removes no verb". The new text
  says "this adds it to the NFR's allowance and adds no verb", and the manifest already declares `mitigates`
  (`governance`). FR-004's "What a category means" says a category does not constrain which archetypes may use a
  verb. The new text puts that constraint in `allowed_links`, not in the category, so there is no contradiction.
- **AC-7.** It is atomic and testable, and it can fail: a negative case (no warning for `mitigates`) is paired with a
  control (an outside verb still warns). TC-070 implements exactly that, and removing the verb makes it fail.
- **tests.md.** The TC-070 row and the FR-004-AC-7 coverage row agree with the test name and the criterion.

## Verdict

**Approve.** The spec change states the intent correctly, sits in the owning vocabulary FR as the ticket asks, and
does not contradict FR-004's other statements or constraints.

## Findings

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-001 | low | No findings (placeholder) | - |
