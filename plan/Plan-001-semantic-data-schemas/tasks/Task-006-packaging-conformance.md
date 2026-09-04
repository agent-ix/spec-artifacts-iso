---
id: Task-006
title: "FR-005 — packaging and toolchain conformance"
type: Task
status: done
track: B
priority: P1
relationships:
  - target: ix://agent-ix/spec-artifacts-iso/FR-005
    type: references
  - target: ix://agent-ix/spec-artifacts-iso/TC-054
    type: verifies
  - target: ix://agent-ix/spec-artifacts-iso/TC-062
    type: verifies
---
# Task-006: FR-005 — packaging and toolchain conformance

## Scope

Two payloads leave this repository — a Python sdist/wheel and an npm tarball —
and they must carry the same module. Assert that, and assert the pinning rules
the reproducibility claim rests on.

## Subtasks

- [ ] **TC-054.** `spec_artifacts_iso/semantic/package.json` pins
  `@typespec/compiler` 1.15.0, `@typespec/json-schema` 1.15.0 and
  `@agent-ix/semantic-core` 0.1.0 exactly, `package-lock.json` is committed, no
  dependency uses a `file:` or `link:` reference, and no `.npmrc` exists
  anywhere in the repository.
- [ ] **TC-062.** The `pyproject.toml` `include` list and the `package.json`
  `files` list name every shipped payload entry of FR-005 Outputs and no
  TypeSpec toolchain file; a built sdist and a packed npm tarball carry the
  same payload entry set.
- [ ] **Check `poetry.lock` carries no local-registry source.** The published
  internal index is the only source a committed lockfile may name.

## Deliverables

- `tests/test_packaging.py`

## Notes

- TC-062 builds real artifacts. Build into a temporary directory and compare
  entry sets, not bytes — the sdist carries a `PKG-INFO` the tarball does not,
  and comparing bytes would assert something neither requirement claims.
- This track touches only packaging files and `tests/`, so it merges whenever
  it is green.
