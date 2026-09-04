---
id: Task-002
title: "FR-005 — the schema-projection test suite"
type: Task
status: done
track: A
priority: P0
relationships:
  - target: ix://agent-ix/spec-artifacts-iso/Task-001
    type: depends_on
  - target: ix://agent-ix/spec-artifacts-iso/FR-005
    type: references
  - target: ix://agent-ix/spec-artifacts-iso/TC-041
    type: verifies
  - target: ix://agent-ix/spec-artifacts-iso/TC-042
    type: verifies
  - target: ix://agent-ix/spec-artifacts-iso/TC-043
    type: verifies
  - target: ix://agent-ix/spec-artifacts-iso/TC-060
    type: verifies
  - target: ix://agent-ix/spec-artifacts-iso/TC-061
    type: verifies
---
# Task-002: FR-005 — the schema-projection test suite

## Scope

Assert the properties of the emitted bundle that a consumer relies on, in tests
that fail when the bundle changes rather than in prose.

## Subtasks

- [ ] **TC-041.** The ten exported schemas exist, each with the 2020-12
  `$schema` and `$id`
  `https://schemas.agent-ix.org/agent-ix/spec-artifacts-iso/<manifest version>/<Model>.json`;
  every `$ref` across the bundle resolves to a shipped sibling or to a file of
  the semantic-core 0.1.0 bundle, with no network read; no `$id` under the
  semantic-core base ships; each model's `type` `const` is the archetype name.
- [ ] **TC-060.** Every emitted object schema declares its properties inline —
  no `allOf`/`oneOf`/`anyOf`/`$ref` at an object's top level except a nullable
  scalar's `anyOf` — and the Python `jsonschema` validator accepts every golden
  record and rejects every TC-045 mutation.
- [ ] **TC-061.** The emitted file set equals `toolchain.json`'s `files` and the
  digest recomputed over those bytes equals the recorded digest, computed from
  the committed tree with no toolchain run.
- [ ] **TC-042.** `make schemas-check` exits 0 on the committed tree and
  non-zero naming the file after a one-byte edit to an emitted schema. Restore
  the file in a fixture teardown, not by hand.
- [ ] **TC-043.** No emitted property is named `result`, `outcome`, `passed`,
  `failed`, `run`, `executedAt` or `evidence`, and `TC.json`'s description
  carries the sentence `execution results (pass/fail, run time, evidence) are
  not modelled`.
- [ ] **TC-039 / TC-040 harness.** The constraint-coverage walker every
  criterion-level assertion reuses: follow `$ref`, then decide constrained vs
  free text.

## Deliverables

- `tests/test_semantic_schemas.py`

## Notes

- TC-042 shells out to `make`; it must fail loudly when the TypeSpec package is
  not installed rather than skip. `make semantic-install` is the precondition
  and the failure message should say so.
