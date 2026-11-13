---
id: SR-032
title: "EARS conformance review — FR-009 software safety class field (PLAT-1526, #73)"
type: SpecReview
analysis: ears-conformance
scope: "agent-ix/spec-artifacts-iso; spec/functional/FR-009-software-safety-class-field.md"
review_set: subset
---
# SR-032: EARS conformance review — FR-009 software safety class field (PLAT-1526, #73)

## Summary

Ticket: PLAT-1526, PR agent-ix/spec-artifacts-iso#73. One new requirement statement is in scope, FR-009's
Description. Its only normative keyword is "The module **SHALL NOT** supply a default for `software_safety_class`."
That is a well-formed ubiquitous negative. The positive obligation, adding the optional field to the four
archetypes with the ordered inline enum, is written as narration: "This requirement adds an optional frontmatter
field" and "The permitted values are an ordered list declared once". FR-008, the precedent, states its positive
obligation with **SHALL** ("The four frontmatter schemas **SHALL** declare the enumeration inline").

## Verdict

**Minor non-conformance.** The core positive obligation has no EARS-form statement. The acceptance criteria carry it,
so this is low.

## Findings

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-001 | low | FR-009 has no SHALL statement for its main obligation. The field, its optionality and the ordered inline enum are described ("This requirement adds", "The permitted values are") but never stated as "The `StR`, `US`, `FR` and `NFR` frontmatter schemas **SHALL** declare an optional `software_safety_class` ...", the way FR-008 does. Only the no-default prohibition is normative. | spec/functional/FR-009-software-safety-class-field.md:29,38 |
