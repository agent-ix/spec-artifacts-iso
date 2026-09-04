---
id: Task-008
title: "FR-007 — mapping failure semantics"
type: Task
status: done
track: C
priority: P0
relationships:
  - target: ix://agent-ix/spec-artifacts-iso/Task-005
    type: depends_on
  - target: ix://agent-ix/spec-artifacts-iso/FR-007
    type: references
  - target: ix://agent-ix/spec-artifacts-iso/TC-045
    type: verifies
---
# Task-008: FR-007 — mapping failure semantics

## Scope

A mapping that silently produces a half-record is worse than one that fails.
Pin every failure the requirements name, and pin that they are reported
together.

## Subtasks

- [ ] **Ten negative cases** (TC-045): an extra property, a wrong-prefix row id,
  a removed required section, a duplicated H2, a malformed `## Story`, a typed
  table with a header and zero rows, a `line: 0`, a CRLF document, an empty
  `Verification` cell, and a `status` outside its pattern — plus a row id
  repeated within one table.
- [ ] **Attribute each failure correctly**: the schema names the JSON path, the
  mapping names the document line. A case reported by the wrong layer is a
  finding, not a pass.
- [ ] **One-pass reporting**: a document carrying three defects reports three,
  not the first.
- [ ] **No partial record**: assert the mapping returns nothing, not a record
  with holes.

## Deliverables

- `tests/fixtures/mutations/`
- `tests/test_mapping_failures.py`

## Notes

- The CRLF case exists because the cell trim strips `\r` while `Section.text`
  keeps CR bytes verbatim (FR-005). Both halves need an assertion, or the case
  proves nothing.
- The empty-`Verification`-cell case is deliberately a rejection (SR-011
  FND-402). Do not relax `minLength: 1` to make it pass.
