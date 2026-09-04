---
id: Task-001
title: "FR-005 — TypeSpec models realigned with the reviewed requirement"
type: Task
status: done
track: A
priority: P0
relationships:
  - target: ix://agent-ix/spec-artifacts-iso/FR-005
    type: references
  - target: ix://agent-ix/spec-artifacts-iso/TC-039
    type: verifies
  - target: ix://agent-ix/spec-artifacts-iso/TC-040
    type: verifies
---
# Task-001: FR-005 — TypeSpec models realigned with the reviewed requirement

## Scope

`spec_artifacts_iso/semantic/main.tsp` predates the review pass and disagrees
with FR-005 in three places. Bring the source into line and regenerate, so that
everything downstream binds to the right bytes.

## Subtasks

- [ ] **`Verification` gains `annotation?`.** FR-005 Behavior: for a cell
  `<method> (<annotation>)`, `annotation` is the text between the first `(` and
  the last `)` verbatim, and `testRefs` are the `TC-[0-9]+` tokens found inside
  it. No byte of the cell is dropped.
- [ ] **`Constraint.validation` becomes a `Verification`.** It is currently a
  plain `NonEmptyText`, which contradicts FR-005 and `ValidationCriterion`
  beside it.
- [ ] **`Relationship` is sealed to `target`, `type`, `cardinality?`.** Record in
  the doc comment that the annotation keys FR-003 admits (`note`, `models`,
  `endpoints`) are dropped under the FR-007 frontmatter drop policy, so the
  loss is declared where a reader of the model will see it.
- [ ] **`MasterRequirements` carries `relationships`** like every other model,
  matching the amended FR-005 bullet.
- [ ] **`toolchain.json` records the semantic-core package digest.** Hash the
  resolved `@agent-ix/semantic-core` package's own `generated/toolchain.json`
  so the copy compiled against is identified by bytes, not by a version string
  two registries could disagree on.
- [ ] **Regenerate and verify determinism.** `make schemas` twice; the tree must
  be unchanged the second time.

## Deliverables

- `spec_artifacts_iso/semantic/main.tsp`
- `spec_artifacts_iso/semantic/scripts/generate.mjs` (semantic-core digest)
- The regenerated `spec_artifacts_iso/schemas/*.json` and
  `spec_artifacts_iso/semantic/generated/toolchain.json`

## Notes

- Emission is the official `@typespec/json-schema` emitter through
  `tsp compile`. Do not write a custom emitter and never hand-edit an emitted
  file — `make schemas-check` exists to catch exactly that.
- Unblocks: every other track. The digests Task-003 records and the properties
  Task-005 maps are both fixed here.
