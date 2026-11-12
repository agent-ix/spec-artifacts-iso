---
id: SR-030
title: "EARS conformance review — FR-004 NFR mitigates allowance (PLAT-1495, #72)"
type: SpecReview
analysis: ears-conformance
scope: "agent-ix/spec-artifacts-iso; spec/functional/FR-004-edge-type-vocabulary.md"
review_set: subset
---
# SR-030: EARS conformance review — FR-004 NFR mitigates allowance (PLAT-1495, #72)

## Summary

Ticket: PLAT-1495, PR agent-ix/spec-artifacts-iso#72. One new requirement statement is in scope: "The `NFR`
archetype's `allowed_links` **SHALL** include `mitigates`." It is a ubiquitous EARS statement (`The <system> shall
<response>`) with one subject and one obligation, and it is unconditional. The rationale sentences that follow it are
informative and contain no second SHALL. FR-004-AC-7 restates the obligation as an observable outcome of single-file
`quire validate`.

## Verdict

**Conforms.** No EARS defects.

## Findings

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-001 | low | No findings (placeholder) | - |
