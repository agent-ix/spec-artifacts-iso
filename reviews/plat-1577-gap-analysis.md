---
id: SR-036
title: "Gap analysis — software safety class fields (PLAT-1577, #74)"
type: SpecReview
analysis: gap-analysis
scope: "agent-ix/spec-artifacts-iso; spec/functional/FR-009-software-safety-class-field.md, tests/test_software_safety_class.py, spec/tests.md"
review_set: subset
---
# SR-036: Gap analysis — software safety class fields (PLAT-1577, #74)

## Summary

Ticket: PLAT-1577. PR agent-ix/spec-artifacts-iso#74, head 6219196, against
FR-009 AC-1..AC-13 and CON-1/CON-2. AC-14 is out of scope by the PR's own
statement (blocked on quire-rs FR-090). Plan completion: not assessed.

Computed matrix (`quire matrix`, quire 0.44.0 / engine 0.59.1; `quoin matrix
--json`, quoin 0.30.1): every `Test`-method FR-009 criterion is `untagged`
with no binder (ten tested here, plus AC-14, which is out of scope). Each marker draws a
`criterion-tagged-outside-row` warning: "no matrix row cited by that test
references it ... This tag does not provide backing". The repo binds a test
to a criterion only through a `spec/tests.md` TC row whose Traces To cell
lists the criterion plus the same TC id on the test's marker, as every
FR-008 test does (`@pytest.mark.trace("TC-067", "FR-008-AC-2")`). Verified
on a scratch copy: adding a TC row for FR-009-AC-2 and the TC id to that
test's marker turned FR-009-AC-2 to `tagged`; either half alone did not.

Per-criterion, by reading the tests and running them (all pass, none
skipped):

- AC-1, AC-2, AC-3, AC-4, AC-5, AC-6, AC-7, AC-10, AC-13: asserted by their
  tagged tests as written.
- AC-8 (Inspection): asserted by `test_fr009_ac8_no_default_in_any_schema`
  and confirmed by inspection.
- AC-9: the mapped values are asserted; the `lossless: false` half of the
  declaration was confirmed by inspection in all four models.
- AC-11 (Inspection): holds by inspection (no schema, mapping or skeleton
  relates a class key to `criticality`), but the test tagged with it does not
  assert it (FND-002).
- AC-12 (Inspection): asserted by `test_fr009_skeletons_carry_none_of_the_fields`.
- CON-1, CON-2: hold by inspection; enum declared only in the four
  frontmatter schemas and `main.tsp`, projected copy generated
  (`make schemas-check` clean); nothing computes or fills a value.

## Verdict

**Changes requested.** The behaviour is right and the tests that exist
assert it, but the computed matrix counts none of them, so FR-009 reads as
entirely unbacked. Add TC rows to `spec/tests.md` and their ids to the
markers, as FR-008 did.

## Findings

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-001 | medium | All ten tested `Test`-method FR-009 criteria (AC-1..7, AC-9, AC-10, AC-13) are `untagged` in the computed matrix: the markers carry only criterion ids, and `spec/tests.md` has no TC row tracing any FR-009 criterion, so quire reports `criterion-tagged-outside-row` on every marker and binds nothing. Add TC rows (next free id is TC-071) tracing the FR-009 criteria and put the TC id on each marker, as `tests/test_criticality.py` does for FR-008. | tests/test_software_safety_class.py:81-242, spec/tests.md:82-89 |
| FND-002 | low | `test_fr009_skeletons_carry_none_of_the_fields` is tagged `FR-009-AC-11` but asserts only that skeletons omit the keys, which is AC-12. AC-11 (no schema, mapping or skeleton relates a class key to `criticality`) holds by inspection but nothing asserts it. Drop AC-11 from the marker, or add an assertion that no class key's schema or mapping entry mentions `criticality` and vice versa. | tests/test_software_safety_class.py:240-246 |

## New findings (disposition pass 1)

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-003 | low | The new `test_fr009_ac11_class_and_criticality_never_refer_to_each_other` asserts the schema half of FR-009-AC-11 but not the mapping half: `mappings.yaml` is never read. Its skeleton check is vacuous: no skeleton contains `criticality`, so `.partition("criticality")[2]` is always `""`. The skeleton half is already implied by AC-12's test. Add a check that no class mapping entry names `criticality` and the `criticality` entry names no class key, and drop the vacuous skeleton assertion. Inspection confirms AC-11 holds today. | tests/test_software_safety_class.py:249-266 |

## Dispositions

| FND | Outcome | Reason |
| --- | --- | --- |
| FND-001 | fixed | Round 1 (d5fc873): TC-071..TC-077 rows added to `spec/tests.md` and every marker carries its TC id. `quire matrix` (engine 0.59.1): FR-009 AC-1..7, AC-9, AC-10, AC-13 `tagged`; AC-8, AC-11, AC-12 `method-without-symbol` (Inspection, bound), AC-14 `untagged` (out of scope). No `criterion-tagged-outside-row` warning remains. |
| FND-002 | fixed | Round 1 (d5fc873): the skeleton test now carries only `TC-077`, `FR-009-AC-12`; a new test carries `TC-077`, `FR-009-AC-11` (its own gap is FND-003). |
