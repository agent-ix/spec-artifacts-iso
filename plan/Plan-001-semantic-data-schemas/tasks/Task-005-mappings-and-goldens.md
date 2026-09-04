---
id: Task-005
title: "FR-007 — mappings.yaml, its schema, and the golden records"
type: Task
status: done
track: A
priority: P0
relationships:
  - target: ix://agent-ix/spec-artifacts-iso/Task-004
    type: depends_on
  - target: ix://agent-ix/spec-artifacts-iso/FR-007
    type: references
  - target: ix://agent-ix/spec-artifacts-iso/TC-044
    type: verifies
  - target: ix://agent-ix/spec-artifacts-iso/TC-050
    type: verifies
  - target: ix://agent-ix/spec-artifacts-iso/TC-052
    type: verifies
  - target: ix://agent-ix/spec-artifacts-iso/TC-053
    type: verifies
---
# Task-005: FR-007 — mappings.yaml, its schema, and the golden records

## Scope

Publish how a document becomes a record, in a form a consumer can read without
reading this module's Python.

## Subtasks

- [ ] **`mappings.schema.json`**: the shape of the mapping file itself, so a
  malformed mapping is a schema error rather than a reader's surprise.
- [ ] **`mappings.yaml`**: per model, `authority: markdown`, `round_trip:
  derived`, the dropped frontmatter key set, and per property the mapping kind
  (one of the eight), its source, its split or parse rule, and `lossless`.
- [ ] **The reference mapping** grown to the full FR-007 surface: the eight
  kinds, the `story` parse, the `Verification` split, `### <row id>` detail
  subsections, and canonical JSON serialization (sorted keys, two-space indent,
  trailing newline).
- [ ] **Ten golden records** at `spec_artifacts_iso/examples/<type>.record.json`.
- [ ] **TC-044**: each golden is reproduced byte-for-byte and validates.
- [ ] **TC-050**: the pre-change skeletons at 3d87196 still map to records that
  validate — read them out of git, do not copy them by hand.
- [ ] **TC-052**: `mappings.yaml` validates, names every property exactly once,
  names none the model does not declare, and its table column lists equal the
  locators' `assert.columns`.
- [ ] **TC-053**: the FR skeleton's AC row splits `Test (TC-001)` into `method:
  Test`, `annotation: TC-001`, `testRefs: [TC-001]`, and its constraint row
  carries `type: Security`.

## Deliverables

- `spec_artifacts_iso/mappings.yaml`, `spec_artifacts_iso/mappings.schema.json`
- `spec_artifacts_iso/examples/*.record.json`
- `tests/support/reference_mapping.py`
- `tests/test_markdown_mappings.py`

## Notes

- The property list `mappings.yaml` must cover comes from the emitted schemas,
  not from a hand-kept list — derive it, so a new model property fails TC-052
  the moment it appears.
- Unblocks: Task-008 and Task-009, which both drive this mapping.
