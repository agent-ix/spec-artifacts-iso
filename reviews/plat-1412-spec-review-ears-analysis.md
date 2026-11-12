---
id: SR-022
title: "EARS conformance review — FR-008 criticality field (PLAT-1412, #70)"
type: SpecReview
analysis: ears-conformance
scope: "agent-ix/spec-artifacts-iso; spec/functional/FR-008-criticality-field.md"
review_set: subset
---
# SR-022: EARS conformance review — FR-008 criticality field (PLAT-1412, #70)

## Summary

Ticket: PLAT-1412. Checked the FR-008 statement clauses and AC-1..AC-6 for
EARS and atomicity. The core clause ("The module SHALL declare the permitted
values once ...") is a well-formed ubiquitous requirement. AC-1, AC-2, AC-3,
AC-4 and AC-6 are each one observable outcome.

## Verdict

**Minor findings.** Two low wording defects. Neither blocks implementation.

## Findings

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-001 | low | The no-default rule, the requirement's main safety property, is stated in descriptive voice ("is not given a value by the module, by a schema `default`, or by any tool") and not as a SHALL NOT clause. Only the enumeration clause carries SHALL. | spec/functional/FR-008-criticality-field.md:27-30 |
| FND-002 | low | AC-5 is compound: it has two inputs (`High` and `""`) and two outcomes (rejection, and not treated as absent). A failure does not say which part broke. Split it into two ACs. | spec/functional/FR-008-criticality-field.md:40 |

## Dispositions

| FND | outcome | reason |
| --- | --- | --- |
| FND-001 | fixed | Round 1 (42fc231): "The module **SHALL NOT** supply a default for `criticality`." |
| FND-002 | still-open | Round 1 (42fc231): the criterion was renumbered AC-5 -> AC-6 but not split; it still combines `High` and `""` and two outcomes in one row. |
