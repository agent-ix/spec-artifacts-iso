---
id: SR-037
title: "Code review — software safety class carried on the coverage report (PLAT-1578, #75)"
type: SpecReview
analysis: code-review
scope: "agent-ix/spec-artifacts-iso; spec_artifacts_iso/manifest.yaml (traceability.carried_fields), spec/tests.md, tests/test_software_safety_class.py, tests/test_semantic_manifest.py, tests/test_manifest_and_validate.py, pyproject.toml, poetry.lock"
review_set: subset
---
# SR-037: Code review — software safety class carried on the coverage report (PLAT-1578, #75)

## Summary

Ticket: PLAT-1578. PR agent-ix/spec-artifacts-iso#75, head 2ca7582. Language
lane: Python. Scope is `git diff origin/main...HEAD` (7 files).

Checks run on the PR head with the quire 0.60.0 Linux wheel (CI run
43454484186) and quire-cli 0.45.0 (engine 0.60.0) in a scratch prefix:

- `tests/test_software_safety_class.py`, `tests/test_semantic_manifest.py` and
  `test_fr004_ac5_*`: 101 passed.
- `make schemas-check`: "schema projection is up to date (45 files)".
- `quire validate` on `spec/tests.md`: fails on the PR head
  (`line 101: [TestMatrix] 'functional_coverage': table row has 6 cell(s) but
  the header declares 4 [row-width]`). It passes on `origin/main`.

Engine drift, measured on unmodified `origin/main` with the 0.60 wheel: exactly
`test_tc046_legacy_fixture_loads_under_quire`,
`test_tc048_registry_lists_ten_archetypes_with_the_block_present` and
`test_fr004_ac5_the_vocabulary_is_declared_and_a_broken_entry_is_refused` fail
(3 failed, 174 passed over the three files). The cause is real engine change:
quire-rs PLAT-277 no longer registers an `archetypes:` row with no validation
part, so the `Spec` container row drops out, and a manifest whose `edge_types`
entry lacks `category` now raises `QuireSchemaError` (`edge_types.contains:
missing field category`) instead of loading empty. The drift edits keep exact
set equality for the archetype list and keep the unmutated control in AC-5.

`carried_fields` entry: `quire coverage` returns `carried_vocabulary =
{software_safety_class: [class-1, class-2, class-3]}`, which equals the enum in
the four frontmatter schemas. The manifest test asserts the exact entry, so no
`criticality` entry can be added unnoticed.

Dependency bump: the `poetry.lock` diff changes only the generator header line,
the quire package version and its five wheel hashes, and the content hash. All
five hashes equal the sha256 of the CI run's wheels.

No standard is named or quoted in the diff. Nothing is vendored. No ceremony was
added.

## Verdict

**FAIL, fix required.** The test-matrix row for TC-078 is in the wrong table and
breaks structural validation of `spec/tests.md`. The drift edits are genuine but
leave the FR-006 criteria stating ten archetypes. The AC-5 rewrite keeps a dead
branch for the old engine.

## Findings

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-001 | high | The TC-078 test-case row is inserted into the Functional Requirement Coverage table (between the FR-009-AC-11 and AC-12 rows), not into the Test Case Summary. The row has 6 cells against a 4-column header, so `quire validate spec/tests.md` fails on the PR head (row-width) and passes on main. The Test Case Summary has no TC-078 row. Move the row to the Test Case Summary after TC-077. | spec/tests.md:101 |
| FND-002 | medium | The drift edits change the asserted archetype set from ten to nine, but FR-006-AC-3 and FR-006-AC-7 still state "all ten archetypes" / "the same ten archetypes". The spec and its tests now disagree. The same stale count is in the TC-046 and TC-048 rows of spec/tests.md, the FR-004 note, the test name `test_tc048_registry_lists_ten_archetypes_with_the_block_present` and the docstrings in tests/test_semantic_manifest.py:8,15,211,250 and tests/test_manifest_and_validate.py (AC-5 docstring). Update the criteria to the nine artifact types. | spec/functional/FR-006-semantic-manifest-block.md:146 |
| FND-003 | low | `test_fr004_ac5_*` now accepts two outcomes: a `QuireSchemaError` or an empty registry. The PR pins quire `^0.60.0`, where only the exception occurs, so the `assert not loaded` path is a branch kept for the old engine. The `except` also accepts any schema error without checking that it names `category`. Use `pytest.raises(quire.QuireSchemaError, match="category")` and drop the old branch. | tests/test_manifest_and_validate.py:761-767 |

## Dispositions

| FND | Outcome | Reason |
| --- | --- | --- |
| FND-001 | fixed | Round 1 (head 09532d5): the TC-078 row moved from the Functional Requirement Coverage table to the Test Case Summary after TC-077 (spec/tests.md:163). `quire validate` (quire-cli 0.45.0) passes on spec/tests.md, FR-004 and FR-006. |
| FND-002 | fixed | Round 1: FR-006-AC-3, FR-006-AC-7, the TC-046 and TC-048 rows, the FR-004 note, the AC-5 docstring and the tests/test_semantic_manifest.py docstrings now say nine archetypes; the test is renamed `test_tc048_registry_lists_nine_archetypes_with_the_block_present`. |
| FND-003 | fixed | Round 1: `with pytest.raises(quire.QuireSchemaError, match="category"):` replaces the try/except, and the old-engine `assert not loaded` branch is gone (tests/test_manifest_and_validate.py:761-764). Passes with the 0.60.0 wheel. |
