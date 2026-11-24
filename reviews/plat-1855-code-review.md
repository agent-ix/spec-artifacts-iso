---
id: SR-043
title: "Code review — FR and NFR may author the SOUP requirement verbs (PLAT-1855, #77)"
type: SpecReview
analysis: code-review
scope: "agent-ix/spec-artifacts-iso; spec_artifacts_iso/manifest.yaml, tests/test_manifest_and_validate.py, spec/tests.md"
review_set: subset
---
# SR-043: Code review — FR and NFR may author the SOUP requirement verbs (PLAT-1855, #77)

## Summary

Ticket: PLAT-1855. PR agent-ix/spec-artifacts-iso#77, head 5a018fd. Language
lane: Python plus manifest YAML. Scope is `git diff origin/main...HEAD` (4 files,
62 insertions).

Measured with quire-cli 0.52.0 (engine 0.62.2), ruff 0.15.12 and black:

- The manifest adds `soup_requirement_for` and `has_soup_requirement` to the
  `allowed_links` of `FR` and `NFR` only, and to no `edge_types` entry. It is
  the first iso `allowed_links` entry that names a verb iso does not declare
  itself (every other allowed verb is an iso `edge_types` key or a declared
  inverse label).
- Module load: with iso alone, iso plus spec-objects-security `origin/main`, and
  iso plus spec-objects-security PR #80 (70538ff), the module loads and
  `quire validate` exits 0. `--strict` also exits 0, so the engine does not
  reject or reset a module whose `allowed_links` names an unknown verb.
- Single-file validation matrix (FR and NFR, each verb, plus a `blocks`
  control). iso main alone: every SOUP verb gives `disallowed-edge-type`.
  iso PR alone: no `disallowed-edge-type`, but 4 `UnknownEdgeType` lines. iso PR
  plus security #80: no `disallowed-edge-type` and no `UnknownEdgeType`.
  `blocks` warns in every configuration. No `DuplicateEdgeType` appears in any
  configuration.
- `tests/test_manifest_and_validate.py`: 60 passed, 20 skipped, 1 failed. The
  failure is `test_fr004_ac5_*` (`QuireSchemaError: unknown field
  carried_fields`) from the stale system quire Python bindings, the same
  pre-existing drift SR-039 recorded. The new
  `test_fr004_ac9_soup_requirement_verbs_are_authorable` passes.
- Mutations of a scratch copy each make the new test fail: removing
  `soup_requirement_for` from NFR `allowed_links` fails the membership
  assertion, and with the membership assertion disabled the `quire validate`
  assertion still fails. Declaring `soup_requirement_for` in `edge_types` fails
  the not-declared assertion.
- No pin, count or SHA assertions were added. There is no compatibility layer
  and no vendored content.

## Verdict

**Mergeable after small fixes.** The manifest change is what FR-030 asks for and
the test can fail. The new test turns `make lint` red, and it adds a second
nested `validate_warnings` helper. The iso-only load warning is the cost of the
chosen ownership and should be stated exactly (see SR-045).

## Findings

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-001 | medium | The new test's docstring is 90 characters wide. `ruff check` reports E501 at tests/test_manifest_and_validate.py:744:89, so `make lint` (`ruff check .` then `black --check .`) fails on the PR head. It passes on `origin/main`. CI does not run lint, so the PR checks stay green while the repository's lint target turns red. Shorten the docstring. | tests/test_manifest_and_validate.py:744 |
| FND-002 | low | The new test declares a third nested copy of the skeleton-mutation-and-validate helper (AC-7 at :686, AC-8 at :714, AC-9 at :756). Two of them are named `validate_warnings`, and `quire matrix` now reports a new `symbol-id-collision: 2 declarations of function validate_warnings` (:714 and :756), which is absent on `origin/main`. SR-039 FND-002 fixed the same collision for `warnings`. Extract one module-level helper that takes the target, and call it from all three tests. | tests/test_manifest_and_validate.py:756 |
| FND-003 | medium | Listing the two verbs in `allowed_links` without declaring them makes every load of iso without a module that declares them print 4 `UnknownEdgeType` lines at module load (`archetype 'FR'/'NFR' allowed_links uses '<verb>' which is not in any edge_types registry`). This happens on every `quire validate --module <iso>` run, including for an FR skeleton that uses neither verb. Iso-only users and iso plus spec-objects-security up to `origin/main` (d7abe37) and the installed v0.18.0 now get advisory output they did not get before, for content they never wrote. Exit codes are unchanged, including under `--strict`. It disappears once security #80 is loaded. This is the accepted cost of FR-030's single-owner choice, but FR-004 must describe it as a load-time advisory on every run, not as a per-use one (SR-045 FND-002). Also release iso and security together so the default module set never pairs this iso with a security version that does not declare the verbs. | spec_artifacts_iso/manifest.yaml:135 |

## New findings (disposition pass 1)

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-004 | medium | The fix commit (d075202) replaced the 4-cell Functional Requirement Coverage row `\| FR-004 \| FR-004-AC-9 \| TC-080 \| ✅ Complete \|` with an 8-cell row. The TC-080 summary row text (description, `Integration`, `P1`, `FR-004-AC-9`, `✅`) was pasted after `TC-080`, so the coverage table now has a row whose Status column holds the test description. `quire validate spec/tests.md` still exits 0, so nothing catches it. SR-039 FND-001 found the same table misuse. Restore the original 4-cell row. The TC-080 row in the Test Case Summary is correct. | spec/tests.md:54 |

## Dispositions

| FND | outcome | reason |
| --- | --- | --- |
| FND-001 | fixed | Round 1, head d075202. The docstring now reads `"""TC-080: (FR-004-AC-9) FR and NFR allow the SOUP verb; the owner declares it."""`. `ruff check` and `black --check` pass on tests/test_manifest_and_validate.py. |
| FND-002 | fixed | Round 1, head d075202. The AC-8 and AC-9 tests now share one module-level helper, `validate_edge_warnings(tmp_path, kind, verb, target)` (tests/test_manifest_and_validate.py:703). `quire matrix` no longer reports a `validate_warnings` collision; only the pre-existing `reasons` collision from main remains. The AC-7 test keeps its own nested `warnings(verb)` helper with a different signature. That leaves some duplication but causes no collision. |
| FND-003 | accepted-no-change | Lead decision: the load-time advisory is the accepted cost of security owning the verb. FR-004 now states it, and it measures true at head d075202. With iso alone, or with security main d7abe37, every load prints `UnknownEdgeType` for `soup_requirement_for` once per archetype (2 lines, FR and NFR), whatever the document contains. The exit status is unchanged (a plain FR exits 0 under `--strict`). With security #80 (70538ff) the advisory goes away. |
| FND-004 | still-open | New in disposition pass 1. No fix has landed yet: spec/tests.md:54 still holds the 8-cell row. |
| FND-004 | fixed | Round 2, head 0539c06. spec/tests.md:54 is back to the 4-cell row `\| FR-004 \| FR-004-AC-9 \| TC-080 \| ✅ Complete \|`, the same width as the neighbouring FR-004 and FR-005 rows. The TC-080 Test Case Summary row is intact. `git diff origin/main...HEAD -- spec/tests.md` shows only those two added rows. |
