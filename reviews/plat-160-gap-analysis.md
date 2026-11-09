---
id: SR-018
title: "Gap analysis — specifies declares inverse specified_by (PLAT-160, #67)"
type: SpecReview
analysis: gap-analysis
scope: "agent-ix/spec-artifacts-iso; spec_artifacts_iso/manifest.yaml (edge_types.specifies), spec/functional/FR-004-edge-type-vocabulary.md (AC-1, AC-4, AC-5, CON-1), spec/tests.md, tests/test_manifest_and_validate.py"
review_set: subset
---
# SR-018: Gap analysis — specifies declares inverse specified_by (PLAT-160, #67)

## Summary

Ticket: PLAT-160 (gap 1). PR agent-ix/spec-artifacts-iso#67. Plan completion:
not assessed (planless).

- FR-004-AC-1 (every verb has a description and category): TC-017 still passes.
  The changed entry keeps both.
- FR-004-AC-4 (roles): not touched. TC-020 passes.
- FR-004-AC-5: TC-021 passes on the head with the locked quire 0.52.0. With
  quire 0.53.0 it fails on main and on the head alike: the engine now raises
  `QuireSchemaError` for the category-less entry where 0.52.0 returned an empty
  registry. This is a quire behaviour change that the test does not tolerate.
  It was there before this PR and is outside its scope.
- FR-004-CON-1: holds. No verb is added or removed.
- `quoin matrix` shows every FR-004 criterion as `untagged` repo-wide, both
  before and after the PR. The matrix does not bind docstring tags in this
  repo, so this is not specific to this PR.
- The new test has no owning criterion (FND-001).

## Verdict

**PASS with one low.** The behaviour change has a test, and that test fails
without the change. It is not traced to any criterion.

## Findings

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-001 | low | `test_specifies_declares_the_specified_by_inverse` cites only "PLAT-160", with no FR-004 criterion or TC id, and `spec/tests.md` has no row for it. No FR-004 AC states that `specifies` has an inverse. The FR-004 description sentence "SHALL declare ... where the relationship is directional and both readings are authorable — an inverse" is the obligation it backs. Tag it to FR-004 and add a TC row, or fold it into TC-017. | tests/test_manifest_and_validate.py:714-716 |

## New findings (disposition pass 1)

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-002 | medium | The TC-065 catalog row is in the wrong table. It sits at spec/tests.md:69 inside "Functional Requirement Coverage", a 4-column table, between the FR-006-AC-9 and FR-006-AC-7 rows, and it has 6 cells. "Test Case Summary" (line 93 onward, which holds TC-017/020/021) has no TC-065 row. Move the row into the Test Case Summary table. `quire validate` does not catch this. | spec/tests.md:69 |

## Dispositions

| FND | Outcome | Reason |
| --- | --- | --- |
| FND-001 | fixed | Round 1 (83803da): FR-004-AC-6 is added. The test is renamed `test_fr004_ac6_specifies_declares_the_specified_by_inverse`, its docstring cites "TC-065: (FR-004-AC-6, PLAT-160)", and the coverage row `FR-004 \| FR-004-AC-6 \| TC-065` is added at spec/tests.md:50. The test passes at the head. The misplaced catalog row is FND-002. |
| FND-002 | fixed | Round 2 (f9c0d4b): the TC-065 row is gone from the Functional Requirement Coverage table and is now in the Test Case Summary table (spec/tests.md:127). The coverage row `FR-004 \| FR-004-AC-6 \| TC-065` stays at spec/tests.md:50. |
