---
id: Task-004
title: "Gate — a record built from a real skeleton validates against its model"
type: Task
status: not_started
track: Gate
priority: P0
relationships:
  - target: ix://agent-ix/spec-artifacts-iso/Task-002
    type: depends_on
  - target: ix://agent-ix/spec-artifacts-iso/Task-003
    type: depends_on
  - target: ix://agent-ix/spec-artifacts-iso/US-001
    type: references
  - target: ix://agent-ix/spec-artifacts-iso/TC-044
    type: verifies
---
# Task-004: Gate — a record built from a real skeleton validates against its model

## Scope

The whole ticket rests on one unproven property: that the models FR-005
declares actually describe what the FR-002 locators extract from a real
document. Measure it on the ten skeletons before building the mapping, the
negative cases and the reproducibility evidence on top of it.

## Subtasks

- [ ] **Minimal reference mapping** for the ten skeletons — enough to build a
  record, not the full FR-007 surface. Task-005 grows it into the deliverable.
- [ ] **Validate each record** against `schemas/<Model>.json` with the Python
  `jsonschema` `Draft202012Validator`.
- [ ] **Report every mismatch** as a model/locator disagreement, naming the
  property and the locator, not as a test to be relaxed.

## Deliverables

- `tests/support/reference_mapping.py` (first cut)
- A recorded gate result in the plan log

## Notes

- **Measures**: whether a record built from each shipped skeleton validates
  against its emitted schema.
- **Pass criteria**: all ten skeletons produce a record their model accepts.
- **If it fails**: the models and the locators disagree. Fix `main.tsp` through
  Task-001 — never by loosening a schema — and do not start Track C.
