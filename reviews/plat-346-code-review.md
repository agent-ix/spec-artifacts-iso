---
id: SR-015
title: "Code review — FR skeleton lineage edge satisfies (PLAT-346, #66)"
type: SpecReview
analysis: code-review
scope: "agent-ix/spec-artifacts-iso; spec_artifacts_iso/skeletons/fr.md, spec_artifacts_iso/examples/FR.record.json, spec_artifacts_iso/manifest.yaml, spec/functional/FR-001..FR-007, tests/fixtures/mutations/**"
review_set: subset
---
# SR-015: Code review — FR skeleton lineage edge satisfies (PLAT-346, #66)

## Summary

Ticket: PLAT-346. PR agent-ix/spec-artifacts-iso#66, one commit, three files.
The FR skeleton's US-001 edge changes from `implements` to `satisfies`, the FR
golden record is regenerated, and `satisfies` joins the FR `allowed_links`.
The vocabulary rule comes from this repo's FR-004 ("Decided: `satisfied_by`
owns stakeholder-requirement lineage").

Measured independently:

- Golden is tool output, not a hand edit. Rebuilding the FR record from the PR
  skeleton with `tests/support/reference_mapping.py` and the `golden_records`
  caller inputs gives bytes identical to the PR's `examples/FR.record.json`,
  and different from the `origin/main` golden. `provenance.digest` equals
  `sha256sum skeletons/fr.md`.
- TC-044 is a real oracle. It compares `canonical_json(record)` byte-for-byte
  against the committed golden and validates the record against
  `schemas/FR.json`. A stale golden fails it.
- Focused suites `test_markdown_mappings.py`, `test_manifest_and_validate.py`
  and `test_semantic_schemas.py` pass: 97 passed, after `make semantic-install`.
- `satisfies` in FR `allowed_links` does real work. quire-rs `validate_document`
  (Tier-1) treats an inverse label as type-allowed no matter what
  `allowed_links` says. Corpus Tier-2 normalizes the edge to `satisfied_by` and
  checks it against the US/StR vocabulary. So validation never reads this
  entry: the skeleton validates with no edge warning with or without it. The
  reader is the authoring input contract (`quire.input_contract("FR", ...)`,
  quire-rs FR-040-AC-11). With the entry, the contract lists `satisfies`.
  Without it, the contract offers only `implements`. That is the vocabulary an
  author sees, so the entry passes the value test and stays.
- The other skeletons already use the right verbs: StR uses `satisfied_by`,
  US uses `traces_to`, NFR uses `constrains`, and TC/IT use `verifies`.

## Verdict

**Changes requested.** The diff is correct and the regeneration is
legitimate. But this repo's own FRs still use `implements` to trace to
US-001, which FR-004 rules out. The repo that owns the decision still
breaks it in its own spec (FND-001). Lows concern test fixtures.

## Findings

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-001 | medium | This repo's own FR-005, FR-006 and FR-007 declare `implements` to `ix://agent-ix/spec-artifacts-iso/US-001` (a `US`). Under FR-004 that is requirement lineage and must be `satisfies`. quire-rs FR-058 will count all three as orphan FRs. They are this repo's share of the PLAT-346 migration and belong in this PR. | spec/functional/FR-005-semantic-data-schemas.md:7, spec/functional/FR-006-semantic-manifest-block.md:7, spec/functional/FR-007-markdown-mappings.md:7 |
| FND-002 | low | 27 FR mutation fixtures are cut-down copies of the FR skeleton and still author `type: "implements"` to `ix://agent-ix/example/US-001`. The skeleton now teaches `satisfies`. The fixtures diverge from it and keep showing the forbidden spelling. | tests/fixtures/mutations/fr-crlf-source.md:7, tests/fixtures/mutations/invariants/one-clause.md:7 (and 25 siblings, line 7/8) |
