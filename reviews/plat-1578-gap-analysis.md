---
id: SR-038
title: "Gap analysis — software safety class carried on the coverage report (PLAT-1578, #75)"
type: SpecReview
analysis: gap-analysis
scope: "agent-ix/spec-artifacts-iso; spec/functional/FR-009-software-safety-class-field.md (FR-009-AC-14), spec/tests.md, spec_artifacts_iso/manifest.yaml, tests/test_software_safety_class.py"
review_set: subset
---
# SR-038: Gap analysis — software safety class carried on the coverage report (PLAT-1578, #75)

## Summary

Ticket: PLAT-1578. PR agent-ix/spec-artifacts-iso#75, head 2ca7582. Plan
completion: not assessed (planless).

FR-009-AC-14 is the only criterion this PR adds backing for. Two tests are tagged
`TC-078`, `FR-009-AC-14`:

- `test_fr009_ac14_manifest_carries_the_class_and_never_criticality` asserts the
  exact `carried_fields` list. Removing the entry, changing `from`, or adding a
  `criticality` entry fails it.
- `test_fr009_ac14_coverage_carries_the_class_as_written_with_its_vocabulary`
  runs `quire coverage` with this module and the installed
  spec-artifacts-process. Measured output: `carried_vocabulary` is the three
  classes in schema order, `spec/FR-001.md` carries `{software_safety_class:
  class-2}`, and `spec/FR-002.md` is a row with no `carried`. Removing the
  manifest entry fails it (no `carried_vocabulary` key).

Both tests pass on the PR head with quire 0.60.0 / quire-cli 0.45.0.

The computed matrix does not credit them. `quire matrix` (quire-cli 0.45.0, this
module plus spec-artifacts-process) lists `FR-009-AC-14 | (none) | untagged`
and warns `criterion-tagged-outside-row` for both tests, because no TC-078 row
exists in the Test Case Summary (see SR-037 FND-001).

## Verdict

**FAIL, fix required.** The tests back FR-009-AC-14, but the matrix reports the
criterion untagged until the TC-078 row is in the Test Case Summary. One low
test-intent gap.

## Findings

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-001 | high | FR-009-AC-14 is `untagged` in the computed matrix on the PR head, and both tagged tests draw `criterion-tagged-outside-row` ("This tag does not provide backing"). The TC-078 row sits in the Functional Requirement Coverage table, not the Test Case Summary, so no matrix row cites the criterion. spec/tests.md also marks it `✅ Complete`, which the matrix contradicts. | spec/tests.md:101-104 |
| FND-002 | low | The "carries none for a document stating none" half asserts `"spec/FR-002.md" not in carried or carried[...] is None`. The first disjunct passes when the row is missing, so the assertion holds even if the engine drops the document. The row is present today (measured). Assert that the row exists and has no `carried` key. | tests/test_software_safety_class.py:326 |
