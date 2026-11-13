---
id: SR-035
title: "Code review — software safety class fields (PLAT-1577, #74)"
type: SpecReview
analysis: code-review
scope: "agent-ix/spec-artifacts-iso; spec_artifacts_iso/mappings.yaml, spec_artifacts_iso/schemas/{FR,NFR,StR,US}.json, spec_artifacts_iso/schemas/{fr,nfr,str,us}-frontmatter.schema.json, spec_artifacts_iso/semantic/main.tsp, tests/test_semantic_schemas.py, tests/test_software_safety_class.py"
review_set: subset
---
# SR-035: Code review — software safety class fields (PLAT-1577, #74)

## Summary

Ticket: PLAT-1577. PR agent-ix/spec-artifacts-iso#74, head 6219196, one
commit, 12 files, scoped to `git diff origin/main...HEAD`. Implements FR-009
except AC-14 (the `traceability.carried_fields` manifest entry), which the PR
body says is blocked on quire-rs FR-090; that omission is not a finding.

Measured independently, quire 0.44.0 (engine 0.59.1):

- `make schemas-check`: "schema projection is up to date (45 files)".
- `pytest tests/test_software_safety_class.py tests/test_semantic_schemas.py`:
  84 passed, 0 skipped (the quire-backed cases ran).
- Hand probes with `quire validate --module spec_artifacts_iso` on the FR
  skeleton: `class-9` and `""` fail `(at software_safety_class)`; assigner and
  rationale without a class, or the assigner alone, fail
  `"software_safety_class" is a required property`.
- No `default` on any of the three keys in any of the eight schemas.
- `dependentRequired` is present and identical in all four frontmatter
  schemas: class requires assigner and rationale; each companion requires
  the class.
- `mappings.yaml`: all three keys mapped under `FR`, `NFR`, `StR` and `US`
  with `kind: frontmatter`, the snake_case source key and `lossless: false`.
- No skeleton carries any of the keys; no hand-written shared enum file
  exists anywhere under `spec_artifacts_iso/`; no description or value names
  a standard or quotes one.
- No ceremony tests: no digests, pins or counts.

## Verdict

**Changes requested (small).** The frontmatter schemas, mappings and tests
are correct. One real defect: the record-schema projection types the
assigner and rationale as bare `string` and widens the FR-005-AC-3 closed
free-text list to pass the constraint test, although the module already has
the `NonEmptyText` scalar for exactly this ("every prose cell and every
name"). The widening is not justified.

## Findings

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-001 | medium | `softwareSafetyClassAssignedBy` and `softwareSafetyClassRationale` are declared as bare `string` in the four `main.tsp` models, so the record schemas accept `""` while the frontmatter schemas require `minLength: 1`. To get past the FR-005-AC-3 constraint test the PR adds both names to `FREE_TEXT_PROPERTIES`, but FR-005-AC-3 enumerates the closed list in the spec and the test's own comment says widening it "is a spec change, not a test change"; no spec change was made. Use the existing `NonEmptyText` scalar (`@minLength(1)`, "the base of every prose cell and every name") for both properties, regenerate, and revert the two allow-list lines. | spec_artifacts_iso/semantic/main.tsp:299-302, tests/test_semantic_schemas.py:75-76 |
| FND-002 | low | The PR adds `quire matrix` `trace-id-outside-marker` warnings: the `# FR-009: ...` comments on the two allow-list lines and the `FR-009-AC-14` mention in the test module docstring. The comment pair goes away with the FND-001 fix; reword the docstring line to name the gap without the criterion id, or accept the one warning. | tests/test_semantic_schemas.py:75-76, tests/test_software_safety_class.py:5 |

## Dispositions

| FND | Outcome | Reason |
| --- | --- | --- |
| FND-001 | fixed | Round 1 (d5fc873): all four `main.tsp` models declare `softwareSafetyClassAssignedBy?: NonEmptyText` and `softwareSafetyClassRationale?: NonEmptyText`; the regenerated record schemas `$ref` `NonEmptyText.json`; the two `FREE_TEXT_PROPERTIES` lines are reverted. `make schemas-check` up to date (45 files); focused tests 88 passed. |
| FND-002 | fixed | Round 1 (d5fc873): the `# FR-009:` comments went with the allow-list revert, and the docstring no longer names `FR-009-AC-14`. The docstring still names quire-rs `FR-090`, which draws one `trace-id-outside-marker` warning of the same kind several pre-existing FR-008 docstrings draw; it names no criterion of this repo, so it is accepted as is. |
