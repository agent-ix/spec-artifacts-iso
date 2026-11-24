---
id: SR-044
title: "Gap analysis — SOUP requirement verbs against spec-objects-security FR-030 (PLAT-1855, #77)"
type: SpecReview
analysis: gap-analysis
scope: "agent-ix/spec-artifacts-iso; FR-004-AC-9, TC-080, spec_artifacts_iso/manifest.yaml (FR and NFR allowed_links), tests/test_manifest_and_validate.py; against agent-ix/spec-objects-security FR-030 Dependencies (origin/main d7abe37)"
review_set: subset
---
# SR-044: Gap analysis — SOUP requirement verbs against spec-objects-security FR-030 (PLAT-1855, #77)

## Summary

Ticket: PLAT-1855. PR agent-ix/spec-artifacts-iso#77, head 5a018fd. This is a
planless audit. Plan completion: not assessed.

- **Against FR-030 (merged, spec-objects-security origin/main d7abe37).** The
  Cross-repository Dependency reads: "`spec-artifacts-iso` does not list
  `soup_requirement_for` or `has_soup_requirement` in the `allowed_links` of
  `FR` and `NFR`; until it does, authoring the verb draws the advisory
  `disallowed-edge-type`". The diff adds exactly those two verbs to exactly
  `FR` and `NFR`, and nothing else. FR-030 says the security module "declares
  it in its own `edge_types` … so it relies on no other module for the verb".
  Iso declaring neither verb matches that ownership statement. Merging with
  security #80 (70538ff) raises no `DuplicateEdgeType`.
- **Precedent.** Within iso this is the first allowed verb that iso does not
  declare. The earlier shared verbs (`verifies_implementation`,
  `verifies_effectiveness`, PLAT-1837) were declared in iso because no other
  module declared them, and FR-004-CON-1 makes the owner the module that needs
  the verb. Sibling PR spec-artifacts-process#163 uses the same pattern for
  `segregates_for_requirement`, which spec-objects-architecture owns. The choice
  is consistent with this ticket's other modules.
- **Matrix.** `quire matrix --scope .` lists FR-004-AC-9 as `tagged`, bound to
  `tests/test_manifest_and_validate.py:741`
  (`@pytest.mark.trace("TC-080", "FR-004-AC-9")`). It shows the same
  `requirement-without-design` status as every other FR-004 criterion.
- **Reverse gap.** The four added manifest lines are owned by FR-004-AC-9 and
  asserted by TC-080. No code is left without an owning requirement.
- **Stub and inflation check.** The test runs real `quire validate` and includes
  a `blocks` negative control. Mutations fail it (see SR-043).
- **Id collisions.** FR-004-AC-9 and TC-080 appear nowhere on `origin/main`. The
  other open PRs (#58, #32) add neither id.

## Verdict

Clean against FR-030. The PR delivers exactly the iso side of FR-030's
dependency. FR-030-AC-3 ("no `disallowed-edge-type` warning" for the inverse)
holds with security #80 loaded, both before and after this PR, because the
inverse label is type-allowed (quire-rs FR-041-AC-2).

The PR body says to merge this before security #80 "so its tests see the
allowances". That ordering is not sufficient. Security's tests load iso through
the installed `spec-artifacts-iso` package (`^0.25.0` from internal-pypi,
`tests/conftest.py` `find_spec`). With iso `origin/main` plus security #80, an
FR authoring `soup_requirement_for` still draws `disallowed-edge-type`, so
`test_a_statement_or_the_inverse_covers_the_served_fr`
(`_disallowed(FR-200) == []`) needs an iso release that contains this PR,
together with a matching lock bump in security. This is a release-ordering note
for the lead and not a defect of this PR.

## Findings

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-001 | low | No findings (placeholder) | - |
