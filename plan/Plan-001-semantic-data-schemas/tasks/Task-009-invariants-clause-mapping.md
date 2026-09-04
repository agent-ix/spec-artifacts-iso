---
id: Task-009
title: "FR-007 — the ## Invariants section and the ocl-clause mapping"
type: Task
status: not_started
track: C
priority: P1
relationships:
  - target: ix://agent-ix/spec-artifacts-iso/Task-005
    type: depends_on
  - target: ix://agent-ix/spec-artifacts-iso/FR-007
    type: references
  - target: ix://agent-ix/spec-artifacts-iso/TC-051
    type: verifies
  - target: ix://agent-ix/spec-artifacts-iso/TC-059
    type: verifies
---
# Task-009: FR-007 — the ## Invariants section and the ocl-clause mapping

## Scope

The one Markdown form this ticket adds, and the only place the module touches
semantic-core's clause types.

## Subtasks

- [ ] **The mapping**: each `### <clauseId>` under `## Invariants` owning
  exactly one ```` ```ocl ```` fence becomes a `ClauseRef { language: ocl,
  clauseId, sourceSpan? }`, with the fence body carried verbatim in the sidecar
  `invariantsText`.
- [ ] **`sourceSpan` only with a caller `sourceIdentity`.** semantic-core's
  `SourceLocus` requires `sourceIdentity`, `path`, `startLine` and
  `startColumn`, so without a caller identity the span cannot be built and the
  property is absent. Never synthesize an `ix://` value.
- [ ] **Five failures**, each naming the line: a non-`Identifier` heading, a
  fence tagged with another language, a second fence under one heading, an
  unterminated fence, and a repeated `clauseId`. Plus an `ocl` fence owned by no
  `###` heading.
- [ ] **Two non-failures**: a prose `## Invariants` with no fence leaves
  `invariants` absent (census: 54 corpus FR documents), and a document with no
  `## Invariants` at all is unaffected.
- [ ] **TC-059**: enumerate the tree and assert that no module file and no test
  support file writes a Markdown document, and that the mapping opens every
  document read-only.
- [ ] **Parity**: TC-009 and TC-010 still pass with the FR skeleton's new
  `## Invariants` H2 and its `###` subheading.

## Deliverables

- `tests/test_invariants_clause.py`
- The `## Invariants` example in `spec_artifacts_iso/skeletons/fr.md`

## Notes

- FR-007-CON-2 is the boundary: the clause text is opaque bytes. Nothing here
  tokenizes, typechecks or evaluates OCL, and TC-059 is what proves it.
