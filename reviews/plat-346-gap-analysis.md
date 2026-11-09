---
id: SR-016
title: "Gap analysis — FR skeleton lineage edge satisfies (PLAT-346, #66)"
type: SpecReview
analysis: gap-analysis
scope: "agent-ix/spec-artifacts-iso; spec_artifacts_iso/manifest.yaml (FR allowed_links), spec_artifacts_iso/skeletons/fr.md, spec/functional/FR-004, FR-005-AC-4, FR-007-AC-2, spec/tests.md TC-044, tests/test_markdown_mappings.py, tests/test_manifest_and_validate.py"
review_set: subset
---
# SR-016: Gap analysis — FR skeleton lineage edge satisfies (PLAT-346, #66)

## Summary

Ticket: PLAT-346. PR agent-ix/spec-artifacts-iso#66. Plan completion: not
assessed (planless).

- FR-005-AC-4 / FR-007-AC-2 (golden records): TC-044
  (`test_tc044_every_skeleton_reproduces_its_golden_record`) is tagged to both.
  It rebuilds each golden from its skeleton, compares bytes and validates
  against the schema, and it passes on the PR head. The binding is correct.
- FR-004 (edge vocabulary): the PR changes no `edge_types` entry, so FR-004-CON-1
  ("adds and removes no verb") holds. `satisfies` stays an inverse label only.
- The `allowed_links` addition changes behaviour only through the FR input
  contract (quire-rs FR-040-AC-11). No test in this repo asserts it.
- Contract entries for inverse labels carry no `category` or `description`,
  because quire-rs looks up `edge_types` by forward key. That is a quire-rs
  gap, not this repo's, and it is not a finding here.

## Verdict

**PASS with one low.** The tests cover the changed skeleton and golden. Only
the new `allowed_links` entry has no test.

## Findings

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-001 | low | No test pins `satisfies` in the FR `allowed_links`. Removing it changes the FR authoring contract, which then offers `implements` and not `satisfies`, yet every test still passes, because Tier-1 validation accepts inverse labels anyway. A one-line assertion that `quire.input_contract("FR", PKG_ROOT)` lists `satisfies` would back the entry. | spec_artifacts_iso/manifest.yaml:116 |
