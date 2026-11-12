---
id: SR-028
title: "Gap analysis — criterion binding in quire matrix and NFR mitigates (PLAT-1474, PLAT-1495, #72)"
type: SpecReview
analysis: gap-analysis
scope: "agent-ix/spec-artifacts-iso; spec/functional/FR-002..FR-008, spec/non-functional/NFR-001, spec/tests.md, tests/**, spec_artifacts_iso/manifest.yaml"
review_set: subset
---
# SR-028: Gap analysis — criterion binding in quire matrix and NFR mitigates (PLAT-1474, PLAT-1495, #72)

## Summary

Ticket: PLAT-1474 and PLAT-1495. PR agent-ix/spec-artifacts-iso#72, head 3d8ab31. Planless; plan completion was not
assessed. The ticket text was read as data, not as instructions.

The computed matrix was measured with `quire matrix --format tsv`, quire 0.43.0 (engine 0.58.0), ambient module
discovery: spec-artifacts-process v0.31.0 plus the other installed defaults.

| Status | origin/main (bd02249) | head (3d8ab31) |
| --- | --- | --- |
| tagged | 8 | 44 |
| untagged | 54 | 19 |
| method-without-symbol | 6 | 6 |
| total criteria | 68 | 69 (adds FR-004-AC-7) |
| `criterion-tagged-outside-row` warnings | 0 | 0 |

The coder's figures (8 to 44 tagged, 0 outside-row warnings) reproduce exactly. `trace-id-outside-marker` goes from 274
to 276. The docstrings keep their ids beside the new markers; that is harmless.

**Trace targets.** `--module spec_artifacts_iso` alone yields an empty matrix: `model-mints-nothing` ("the declared
traceability model has no trace_targets"). spec-artifacts-process declares the `test-case`, `acceptance-criterion` and
`nfr-acceptance-criterion` trace targets and the pytest marker form. It binds iso's `FR`/`NFR` archetypes across the
module boundary, and that manifest documents this cross-module binding as deliberate. Neither CI nor the Makefile runs
`quire matrix`. CI is `semantic-module-ci.yml`, which runs pytest, ruff, black and schemas-check. The dependency is
therefore legitimate: the process module owns the traceability grammar, and redeclaring it in iso would duplicate it.
This is not a gap for this PR.

**PLAT-1495.** FR-004-AC-7 is bound to TC-070. The test passes on head and fails when `mitigates` is removed from
`allowed_links`. Single-file and `--okf` behaviour was checked by hand (SR-027). The ticket's "release the next iso
version" step is outside this PR.

**PLAT-1474.** The coder says the 19 untagged criteria and the method-without-symbol rows "have no test". That is
false for at least five of them. Each has a test that asserts it, and the script missed it because the docstring used
a stale id (`IT-002-AC-2`), prose ("NFR-001 metric 1"), or no id at all. I added the markers in a scratch copy:
FR-002-AC-2, NFR-001-M-1 and NFR-001-M-3 then bind, and the counts become 47 tagged and 16 untagged. The scratch copy
was then reverted. The rest of the untagged list is FR-001-AC-2..4, FR-002-AC-3, FR-003-AC-3..8, FR-003-CON-1,
FR-006-AC-6, FR-006-CON-2 and NFR-001-M-2. Each is Pending in tests.md, is a Manual/Demonstration TC, or has no
asserting test that I could find.

## Verdict

**Changes requested (small).** The ticket's goal is mostly met: 36 more criteria are bound and none is bound outside
its row. Five criteria that have real tests are still left unbound, and the PR claims they have no test. The
hand-maintained coverage table in `spec/tests.md` asserts coverage that the computed matrix contradicts (FND-006,
pre-existing).

## Findings

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-001 | medium | FR-002-AC-2 computes `untagged`, but `test_it002_ac2_fr_mutations_fail` (TC-013) asserts exactly this criterion: a missing section, broken AC columns and a broken AC id each fail. Its docstring cites the retired `IT-002-AC-2`, so the script tagged only `TC-013`. Adding `FR-002-AC-2` to its marker binds it; this was verified in a scratch copy. | tests/test_manifest_and_validate.py:487 |
| FND-002 | medium | NFR-001-M-1 computes `untagged`, but `test_tc056_two_schema_runs_reproduce_the_committed_bundle` measures metric 1. Its docstring says "NFR-001 metric 1", which is prose, not an id. Adding `NFR-001-M-1` to the marker binds it; this was verified in a scratch copy. | tests/test_reproducibility.py:68 |
| FND-003 | medium | NFR-001-M-3 computes `untagged`, but `test_tc058_schemas_check_completes_within_the_threshold` measures metric 3, the 30 s threshold. Adding `NFR-001-M-3` to the marker binds it; this was verified in a scratch copy. | tests/test_reproducibility.py:132 |
| FND-004 | low | FR-003-CON-2 (`component_type` SHALL match `^[a-z][a-z0-9-]*$`, validated by Schema Test) computes `untagged`. `test_fr003_ac2_master_requirements_frontmatter_schema_shape` asserts that exact pattern on the schema. | tests/test_manifest_and_validate.py:80 |
| FND-005 | low | FR-006-CON-1 ("the suite carries a legacy-manifest fixture ... that loads under quire") computes `untagged`. `test_tc046_legacy_fixture_loads_under_quire` asserts that half, and tests.md traces TC-046 to FR-006-CON-1. | tests/test_semantic_manifest.py:208 |
| FND-006 | medium | `spec/tests.md` Functional Requirement Coverage, which is pre-existing and extended by this PR, marks rows ✅ Complete that the computed matrix reports untagged (FR-002-AC-2, FR-006-CON-1, FR-006-CON-2, and the three NFR-001 rows). It also lists FR-006-AC-5, FR-006-AC-8 and TC-063, none of which exist in FR-006 or the Test Case Summary. A hand-kept coverage table duplicates `quire matrix` and has drifted from it. The table's presence is required by the spec-artifacts-process `TestMatrix` archetype (`functional_coverage`, `required: true`). | spec/tests.md:23 |
