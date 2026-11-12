---
id: SR-027
title: "Code review — trace markers and NFR mitigates edge (PLAT-1474, PLAT-1495, #72)"
type: SpecReview
analysis: code-review
scope: "agent-ix/spec-artifacts-iso; spec_artifacts_iso/manifest.yaml, tests/test_invariants_clause.py, tests/test_manifest_and_validate.py, tests/test_mapping_failures.py, tests/test_markdown_mappings.py, tests/test_packaging.py, tests/test_reproducibility.py, tests/test_semantic_manifest.py, tests/test_semantic_schemas.py"
review_set: subset
---
# SR-027: Code review — trace markers and NFR mitigates edge (PLAT-1474, PLAT-1495, #72)

## Summary

Ticket: PLAT-1474 and PLAT-1495. PR agent-ix/spec-artifacts-iso#72, head
3d8ab31, one commit, 11 files, scoped to `git diff origin/main...HEAD`.

What the diff does:

- PLAT-1495: `mitigates` joins the `NFR` archetype's `allowed_links`
  (`spec_artifacts_iso/manifest.yaml:233`). The verb was already declared in
  `edge_types` (`governance`), so no verb is added.
- PLAT-1495: new test `test_fr004_ac7_nfr_allows_a_mitigates_edge` (TC-070).
- PLAT-1474: 80 docstring criterion tags become `@pytest.mark.trace(...)`
  decorators on 80 test functions across 8 test files. With the new TC-070
  test that makes 81 new markers. `test_criticality.py` already had its 8.
  The PR body says "36 test functions", which is wrong. The real count is 80
  converted plus 1 new.

Measured independently:

- Conversion fidelity, all 80 checked by AST, not a sample. Every marker id
  appears in the function's own docstring. No marker repeats an id. No
  `FR-x-AC-n`, `FR-x-CON-n` or `NFR-x-M-n` id in a docstring was dropped.
  Bare `FR-NNN`, `IT-NNN-AC-n` and prose like "NFR-001 metric 1" were
  dropped, because none of them is a criterion id. Each criterion id was
  checked against the `spec/tests.md` Traces To cell of the TC the test
  claims. No criterion is attached to a test that the TC row does not trace
  it to. Three **TC** ids were copied from passing mentions in a docstring
  (FND-001..003). `quire trace` resolves TC ids as the `test-case` trace
  target, so these three markers are false `verifies` claims.
- No behaviour change. Apart from the new TC-070 test, the diff adds only
  decorators and two `import pytest` lines. `trace` was already a registered
  marker (`pyproject.toml:135`), so `filterwarnings = error` still holds.
- PLAT-1495, by hand with quire 0.43.0 (engine 0.58.0), `--module` pointed at
  each tree, on the NFR skeleton with its one edge's verb swapped:
  - head with `mitigates`: no `disallowed-edge-type`.
  - head with `blocks`: warns `disallowed-edge-type`; `--strict` exits 3.
  - origin/main with `mitigates`: warns.
  - `--okf` bundle mode gives the same output on main and head, and shows no
    `disallowed-edge-type` in either.
- Mutation: with the `- mitigates` line deleted, TC-070 fails. With it
  restored, TC-070 passes.
- Local pytest on a poetry venv from internal PyPI, without npm: 193 passed
  and 22 failed. Every failure is a missing
  `spec_artifacts_iso/semantic/node_modules`: 18 say semantic-core is missing
  and 4 say the TypeSpec compiler `tsp` is missing. Coverage is 100%.
  TC-070 PASSED locally, not skipped. ruff and black are clean. CI run
  43303847526 (workflow_dispatch on head 3d8ab31, quire-cli 0.43.0) is
  green: 215 passed, 100% coverage, ruff, black and schemas-check all pass.

## Verdict

**Changes requested (small).** The manifest change and TC-070 are correct
and mutation-proven. The conversion is faithful to the docstrings. But
copying the docstrings mechanically turned three passing TC mentions into
false `verifies` markers. One of them contradicts its own docstring, which
says "Untagged: TC-051 ...". Each fix is a one-line marker edit.

## Findings

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-001 | medium | `test_a_prose_clause_heading_yields_no_clause_ref` is tagged `TC-051`, but its docstring says "Untagged: TC-051 enumerates a prose `## Invariants` *section*, not a prose clause heading". The script copied a mention that explicitly disclaims the binding. `quire trace --id TC-051` now lists this test as `verifies`. | tests/test_invariants_clause.py:225 |
| FND-002 | medium | `test_tc056_two_schema_runs_reproduce_the_committed_bundle` is tagged `TC-047`. The docstring mentions TC-047 only as a test the restore protects ("without also leaving the checkout drifted for TC-047"). TC-047 is the FR-006 data_schema reference test, and `quire trace --id TC-047` now lists the NFR-001 reproducibility test as verifying it. | tests/test_reproducibility.py:68 |
| FND-003 | medium | `test_tc039_every_locator_output_has_a_property` is tagged `TC-052`. The docstring says the reverse direction "is TC-052's", which means this test does not cover it. `quire trace --id TC-052` now lists it as `verifies`. | tests/test_semantic_schemas.py:316 |
