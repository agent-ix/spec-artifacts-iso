---
id: SR-020
title: "Gap analysis — master-requirements owned and exported once (PLAT-214, #68)"
type: SpecReview
analysis: gap-analysis
scope: "agent-ix/spec-artifacts-iso; spec/functional/FR-006-semantic-manifest-block.md (AC-9, AC-10), spec/tests.md (Functional Requirement Coverage, Test Case Summary), tests/test_semantic_manifest.py, spec_artifacts_iso/manifest.yaml (artifact_types master-requirements, semantic.exports)"
review_set: subset
---
# SR-020: Gap analysis — master-requirements owned and exported once (PLAT-214, #68)

## Summary

Ticket: PLAT-214. PR agent-ix/spec-artifacts-iso#68. Plan completion: not
assessed (planless).

- The `spec/tests.md` edit is malformed. The original audit row
  `| FR-006 | FR-006-AC-9 | TC-064 | ✅ Complete |` was split in two. The
  TC-066 Test Case Summary row (9 cells) was spliced into the 4-column
  Functional Requirement Coverage table as an `FR-006-AC-9 → TC-066` row, and a
  stray `| TC-064 | ✅ Complete |` row is left after it. The correct
  `FR-006-AC-10 → TC-066` row follows. TC-066 has no row in `## Test Case
  Summary`, and the AC-9 → TC-064 trace is gone. `quire validate` (0.36.2,
  engine 0.50.2) exits 0 on both touched spec files, so tooling does not catch
  this.
- `quoin matrix` (0.29.1) reports FR-006-AC-10 as `untagged`. It reports all 55
  Test-method criteria in this repo the same way, because the repo traces through
  TC ids in docstrings. This is not caused by the PR.
- Id collisions: neither `FR-006-AC-10` nor `TC-066` exists on `origin/main`,
  and neither open PR #58 nor #32 adds them (#32 uses TC-039..041). No collision.
- Value test on AC-10: the type already exists, is declared once and is
  exported once on main, and TC-047 and TC-048 already fail on every
  export-side regression that TC-066 catches (SR-019). AC-10 only restates the
  current state. The real PLAT-214 defect is that `spec-artifacts-app` also
  declares `MasterRequirements`, and that the registry resolves duplicates
  first-wins. Neither is in this repo, and AC-10 cannot test either one here.
- No vendoring, pins or SHAs.

## Verdict

**FAIL, one high and two medium.** The traceability table is broken: AC-9 now
traces to the wrong TC, and TC-066 is missing from the catalog. AC-10 fails the
value test as written. Recommend dropping AC-10, TC-066 and the test. Record iso's
ownership of `master-requirements` in FR-006 prose or in the PLAT-214 ADR, and
put the enforcement where the defect is (spec-artifacts-app drops its
declaration; the quire/quoin registry refuses duplicate exports). If AC-10 is
kept, it needs only its first clause, and its test must count declarations
over the raw `artifact_types` list.

## Findings

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-001 | high | spec/tests.md corrupts the AC-to-TC audit table. The `FR-006-AC-9 → TC-064` row is replaced by a 9-cell TC-066 catalog row (`FR-006-AC-9 → TC-066`) plus a stray `\| TC-064 \| ✅ Complete \|` row. TC-066 has no `## Test Case Summary` row. quire validate passes it. Fix: restore line 68 to main's row, delete line 69, and add the TC-066 row after TC-065 in Test Case Summary. | spec/tests.md:68-69 |
| FND-002 | medium | AC-10 fails the value test. It restates state that main already has and that TC-047/TC-048 already guard. No regression would fail TC-066 alone. The duplicate it is meant to address is in spec-artifacts-app and in the registry's first-wins rule, both outside this repo. | spec/functional/FR-006-semantic-manifest-block.md:150 |
| FND-003 | medium | AC-10 is compound and partly untestable here. "so a module that references it imports it from agent-ix/spec-artifacts-iso and declares no artifact type of its own for it" is a claim about other modules. TC-066 covers only the first clause. | spec/functional/FR-006-semantic-manifest-block.md:150 |
