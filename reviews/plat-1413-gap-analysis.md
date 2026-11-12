---
id: SR-026
title: "Gap analysis — optional criticality field on StR/US/FR/NFR (PLAT-1413, #71)"
type: SpecReview
analysis: gap-analysis
scope: "agent-ix/spec-artifacts-iso; spec/functional/FR-008 (AC-1..8, CON-1), FR-005 (criticality bullet), FR-007-AC-8, tests/test_criticality.py, spec_artifacts_iso/schemas, spec_artifacts_iso/semantic/main.tsp, spec_artifacts_iso/mappings.yaml"
review_set: subset
---
# SR-026: Gap analysis — optional criticality field on StR/US/FR/NFR (PLAT-1413, #71)

## Summary

Ticket: PLAT-1413. PR agent-ix/spec-artifacts-iso#71. Plan completion: not
assessed (planless).

Each criterion below was checked against the PR code and the tests:

- FR-008-AC-1: inline enum in all four frontmatter schemas, not required, no
  shared file. `test_fr008_ac1_*` asserts all three. Covered.
- FR-008-AC-2: `test_fr008_ac2_*` runs `quire validate` for 4 archetypes x 3
  values. Covered.
- FR-008-AC-3: the TypeSpec `criticality?` lines are present. The record schemas
  carry the property as optional (`test_fr008_ac3_*`), and `make schemas-check`
  passes (measured). Covered.
- FR-008-AC-4: omitted field validates and maps to no value
  (`test_fr008_ac4_*`). Covered.
- FR-008-AC-5/6/7: `critical`, `High` and `""` fail, naming the field
  (`test_fr008_invalid_values_fail_naming_the_field`). Covered.
- FR-008-AC-8 and FR-008-CON-1: no `default` in either schema family
  (`test_fr008_ac8_*`). The enumeration is inline in the frontmatter schemas
  and in `main.tsp`. Covered by inspection and test.
- FR-005 (criticality bullet): all four models gain `criticality?` with no
  default. The record constraint is not looser than the frontmatter enum: the
  same three values. FR-005-CON-1 holds because the field has a mapping source.
- FR-007-AC-8: the mapping entries match `qualityAttribute`'s shape. Presence is
  tested (`test_fr007_ac8_*`). Omission is tested only inside the AC-4 test
  (FND-002).

Computed matrix (`quire matrix --format tsv` on the PR head): every FR-008 AC and
FR-007-AC-8 reads `untagged`, and AC-8 and CON-1 read `method-without-symbol`.
This is repo-wide: 62 rows untagged, 0 bound. Every existing test in the repo
tags criteria in docstrings, and the module's trace grammar does not read
docstrings (FND-001).

## Verdict

**PASS with two lows.** Every FR-008 criterion and FR-007-AC-8 has a passing
test that would fail if the behaviour broke. The gaps are in trace binding
(repo-wide, inherited) and in one half-criterion's placement.

## Findings

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-001 | low | The new tests tag FR-008-AC-1..8 and FR-007-AC-8 in docstrings, and the parametrize ids carry AC-5..7. The module's trace grammar binds `@pytest.mark.trace("...")` only, so `quire matrix` reports every one of these criteria `untagged` (warnings `trace-id-outside-marker` and "not read by the declared trace grammar"). The PR follows the repo's existing convention, under which all 62 criteria are unbound. The fix is a repo-wide marker migration, not a change to this PR alone. | tests/test_criticality.py:58-136 |
| FND-002 | low | FR-007-AC-8 has two halves. Its tagged test checks only the first: a present key maps as written. The second half, "a document without the key yields a record without criticality", is asserted only inside `test_fr008_ac4_*`. That test is `@needs_quire`, so this pure-mapping assertion, which needs no quire, is skipped whenever the CLI is absent. | tests/test_criticality.py:88-112 |
