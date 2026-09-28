---
id: SR-013
title: "Code review — drop ac-verification-method (PLAT-1085, #46)"
type: SpecReview
analysis: code-review
scope: "agent-ix/spec-artifacts-iso@608cd5314c8eb756bf96a71303f90cc39378b6df; README.md, scripts/corpus_census.py, spec/functional/FR-005-semantic-data-schemas.md, spec/log.md, spec_artifacts_iso/examples/{FR,NFR,StR}.record.json, spec_artifacts_iso/manifest.yaml, spec_artifacts_iso/schemas/Verification.json, spec_artifacts_iso/semantic/generated/toolchain.json, spec_artifacts_iso/semantic/main.tsp, spec_artifacts_iso/skeletons/{fr,nfr,str}.md, tests/fixtures/manifest-legacy.yaml, tests/test_markdown_mappings.py"
review_set: subset
---
# SR-013: Code review — drop ac-verification-method (PLAT-1085, #46)

## Summary

Ticket: PLAT-1085. PR agent-ix/spec-artifacts-iso#46, one commit (608cd53),
16 files. Removes the FR/NFR `ac-verification-method` lint rule (ownership
moves to spec-artifacts-process FR-004 CR-066), drops `annotation_pattern`
from the StR `vc-validation-method` rule, and updates skeletons, goldens,
schema doc comment, legacy fixture, README, FR-005 prose and TC-053.

Independently measured:

- Golden records: rebuilt all ten from the skeletons with
  `tests/support/reference_mapping.py` and the `golden_records` caller inputs;
  all ten are byte-identical to the committed `examples/*.record.json`, so the
  FR/NFR/StR goldens are tool output, not hand edits.
- `scripts/manifest_digests.py --check`: every `data_schema.digest` matches.
- `derive_legacy(manifest.yaml)` equals `tests/fixtures/manifest-legacy.yaml`.
- `toolchain.json` digest recomputed over `schemas/` equals the recorded value;
  `Verification.json` description equals the `main.tsp` doc comment.
- CI run 36367387432 at head 608cd53: success (pytest, ruff, black,
  schemas-check all green).
- Branch carries exactly one commit; its file set matches the commit message
  and `spec/log.md` entry, with nothing stray (the `corpus_census.py` comment
  edit is the ticket's own listed item).
- Rewritten `test_tc053_acceptance_rows_split_the_verification_cell` fails on
  the old skeleton (old cell `Test (TC-001)` yields `annotation`/`testRefs`).
  The split mechanism itself is still exercised by
  `test_tc053_verification_split_keeps_every_byte` (unchanged), which drives
  `split_verification` over annotated, nested-paren and bare cells.

## Verdict

**PASS with findings** — no high. One medium: FR-007-AC-3 and the TC-053 matrix
row still state the old behavior that the rewritten test now contradicts.
Lows are informational.

## Findings

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-001 | medium | FR-007-AC-3 still says the FR skeleton's AC rows split `Test (TC-001)` into `method: Test`, `annotation: TC-001`, `testRefs: [TC-001]`, and spec/tests.md TC-053 repeats it; the rewritten TC-053 now asserts the skeleton yields `method` only with `testRefs: []`. The requirement and its only test disagree, so the matrix row marked Complete backs a criterion the test no longer checks. | spec/functional/FR-007-markdown-mappings.md:216, spec/tests.md:149, tests/test_markdown_mappings.py:473-491 |
| FND-002 | low | No test asserts the rule change itself: nothing fails if `ac-verification-method` is re-added or `annotation_pattern` restored on `vc-validation-method` (the legacy fixture is derived from the manifest, so it tracks either state). | spec_artifacts_iso/manifest.yaml:795-823 |
| FND-003 | low | Shipped schema text still uses `Test (TC-035)` / `Test (TC-035, TC-036)` as the canonical example of a verification cell, while the skeletons and README now say tests bind by criterion id. The split still parses legacy cells, so this is description drift, not a defect. | spec_artifacts_iso/schemas/TestCaseRef.json:6, spec_artifacts_iso/schemas/Verification.json:28, spec_artifacts_iso/semantic/main.tsp:75,193 |
| FND-004 | low | Ticket item "Release; bump the iso pin in quoin default-modules.yaml" is not in this PR; it must happen with the PLAT-1079 release so the two contracts never coexist in a released default module set. | PLAT-1085 Change list |
