---
id: SR-039
title: "Code review — control verification verbs in the iso edge vocabulary (PLAT-1837, #76)"
type: SpecReview
analysis: code-review
scope: "agent-ix/spec-artifacts-iso; spec_artifacts_iso/manifest.yaml, spec/functional/FR-004-edge-type-vocabulary.md, spec/tests.md, tests/test_manifest_and_validate.py"
review_set: subset
---
# SR-039: Code review — control verification verbs in the iso edge vocabulary (PLAT-1837, #76)

## Summary

Ticket: PLAT-1837. PR agent-ix/spec-artifacts-iso#76, head ca3dabe. Language
lane: Python plus manifest YAML. Scope is `git diff origin/main...HEAD` (4 files,
54 insertions, 1 deletion).

Measured with quire-cli 0.52.0 (engine 0.62.2) and the installed quire Python
bindings:

- On `origin/main` (d83c1ce) exactly `NFR`, `IT` and `TC` list `verifies` in
  `allowed_links`. The PR adds both new verbs to exactly those three, beside
  `verifies`, which is unchanged in `allowed_links` and in `edge_types`.
- Both verbs are declared in `edge_types` with `category: traceability` and no
  `inverse`. `verifies` and `traces_to` also declare no inverse, so this is
  consistent with the sibling verbs.
- `-k fr004` on the PR head: 5 passed, 1 failed. The failure is
  `test_fr004_ac5_*` (`QuireSchemaError: unknown field carried_fields`). It fails
  identically on `origin/main` (4 passed, 1 failed), so it is pre-existing
  binding drift and not caused by this PR.
- Mutations of a scratch copy each make `test_fr004_ac8_*` fail: removing
  `verifies_effectiveness` from TC `allowed_links`; removing
  `verifies_implementation` from NFR `allowed_links`; changing
  `verifies_effectiveness` to `category: governance`; deleting the
  `verifies_implementation` entry from `edge_types`.
- Single-file `quire validate` of an IT carrying `verifies_implementation`
  produces `[disallowed-edge-type]` with the `origin/main` module and produces
  nothing with the PR head module.
- `ruff check` and `black --check` pass on the test file.

No issue-id, SHA or count pins were added. There is no compatibility layer, no
vendored content and no quoted standard text.

## Verdict

**Mergeable after a small fix.** The manifest change is correct and complete for
this module, and the test can fail. The TC-079 row is in the wrong table in
`spec/tests.md`. This is the same defect SR-037 FND-001 found for TC-078.

## Findings

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-001 | medium | The TC-079 test-case row (6 cells: Test ID, Title, Type, Priority, Traces To, Status) is appended to the end of the 4-column Functional Requirement Coverage table, after the FR-009-AC-14 row. It should be in the Test Case Summary after TC-078. The Test Case Summary has no TC-079 row, and the coverage table now has a row whose requirement column is `TC-079`. quire-cli 0.52.0 no longer reports row-width for this, but SR-037 FND-001 saw the same misplacement fail `quire validate` under engine 0.60. | spec/tests.md:105 |
| FND-002 | low | The new test declares a nested helper named `warnings`. The AC-7 test above it also declares one, and `quire matrix` now reports `symbol-id-collision: 2 declarations of function warnings` (tests/test_manifest_and_validate.py:686 and :714). The name also shadows the stdlib module. Rename the new helper, for example `validate_warnings`. | tests/test_manifest_and_validate.py:714 |
