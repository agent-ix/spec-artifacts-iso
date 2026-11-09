---
id: SR-017
title: "Code review — specifies declares inverse specified_by (PLAT-160, #67)"
type: SpecReview
analysis: code-review
scope: "agent-ix/spec-artifacts-iso; spec_artifacts_iso/manifest.yaml (edge_types.specifies), spec/functional/FR-004-edge-type-vocabulary.md, tests/test_manifest_and_validate.py"
review_set: subset
---
# SR-017: Code review — specifies declares inverse specified_by (PLAT-160, #67)

## Summary

Ticket: PLAT-160 (gap 1). PR agent-ix/spec-artifacts-iso#67, head 48b5d0e,
base origin/main 034c240. Three files changed: one manifest line, two FR-004
prose counts, one new test.

- `manifest.yaml:890`: `specifies` gains `inverse: specified_by`. The label is
  new, is not an `edge_types` key, and is not shared with any other verb.
  FR-004-CON-1 ("adds and removes no verb") holds: an inverse label is not a verb.
- FR-004 "28 of which name an inverse": measured 28 on the head (27 on main). Correct.
- FR-004 "26 of the 27 distinct inverse labels": measured 28 distinct labels on
  the head, 27 of them absent from `edge_types` (only `contains` is both). Wrong
  by one (FND-001). Main's "25 of the 26" was already wrong by one (27 distinct,
  26 non-key), and the PR carried the error forward.
- The new test `test_specifies_declares_the_specified_by_inverse` fails on the
  main manifest (`KeyError: 'inverse'`) and passes on the head.
- No copied or vendored files. No new ids (no TC, AC or SR ids), so no
  collision with open PRs #58 (`contains` inverse, same file, different hunk)
  or #32 (TC-039..041, FR-001). PR #58 would change the label set again if it
  landed, so it would make the FR-004 count drift again.
- `test_fr004_ac5_...` fails on both main and the head with quire 0.53.0
  (`QuireSchemaError ... edge_types.contains: missing field category`), and
  passes on both with the locked quire 0.52.0. So the failure was there before
  this PR and depends on the quire version. It is not caused by this PR.

## Verdict

**FAIL, one medium and one low.** The manifest change and the test are correct.
The FR-004 distinct-label count is wrong by one. Fix the count, or replace it
with wording that does not pin a number ("every inverse label but `contains`").
The number has already drifted once on main. The stale shared-label bullet next
to it is why it drifted.

## Findings

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-001 | medium | FR-004 says "26 of the 27 distinct inverse labels" are absent from `edge_types`. The head manifest has 28 distinct inverse labels, 27 absent (only `contains` is a key). Correct to "27 of the 28", or drop the number. | spec/functional/FR-004-edge-type-vocabulary.md:57 |
| FND-002 | low | Stale prose next to the count: "`contains` and `aggregates` both name `part_of`" and "`contains` names `part_of` as its own" are false. `contains` names `contained_in`, and no label is shared. "AC-2 pins the current set" cites an AC that FR-004 no longer has. Pre-existing, but it is why the count above drifted. | spec/functional/FR-004-edge-type-vocabulary.md:64-70 |

## New findings (disposition pass 1)

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-003 | low | One fixed count is left in FR-004. "Adding a verb" step 1 still says "**Check the existing 76.**" The number is true today (76 verbs), but it is the same kind of pinned count that FND-001 removed. The fix commit message says the counts were removed. Use "Check the existing verbs." | spec/functional/FR-004-edge-type-vocabulary.md:93 |

## Dispositions

| FND | Outcome | Reason |
| --- | --- | --- |
| FND-001 | fixed | Round 1 (83803da): the count is replaced by "Most inverse labels (`part_of`, `called_by`, `implemented_by`, …) appear nowhere as `edge_types` keys". The description line also drops "76 edge verbs", "28 of which" and "9 capability roles". |
| FND-002 | fixed | Round 1 (83803da): the bullets now say that no label is shared, that `contains` names `contained_in` and `aggregates` names `part_of`, and that `contains` is a forward verb whose own inverse is `contained_in`. I checked each of these against the manifest at the head. The dangling "AC-2 pins the current set" is removed. |
