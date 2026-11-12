---
id: SR-024
title: "Integrity review — FR-008 criticality field (PLAT-1412, #70)"
type: SpecReview
analysis: integrity
scope: "agent-ix/spec-artifacts-iso; spec/functional/FR-008-criticality-field.md, spec/functional/index.md"
review_set: subset
---
# SR-024: Integrity review — FR-008 criticality field (PLAT-1412, #70)

## Summary

Ticket: PLAT-1412. Checked completeness, consistency and atomicity. The index
entry matches the FR title. The ID is the next free one. The AC and CON ids are
sequential. Every AC's Verification cell names a method only. Valid values,
omission, an out-of-range value, wrong case and the empty string all have a
criterion.

## Verdict

**Minor finding.** Coverage is complete for `FR`, but not across the four
archetypes the requirement names.

## Findings

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-001 | low | The FR names four archetypes (`StR`, `US`, `FR`, `NFR`). AC-2 to AC-5 exercise only `FR`. For `StR`, `US` and `NFR`, accept/reject behaviour is backed only by AC-1's schema-shape check, so a typo in one archetype's reference passes AC-1 and nothing tests it. Parametrise AC-2 and AC-4 over the four archetypes. | spec/functional/FR-008-criticality-field.md:36-40 |
