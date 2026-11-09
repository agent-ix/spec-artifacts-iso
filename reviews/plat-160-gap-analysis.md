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
