---
id: SR-040
title: "Gap analysis — control verification verbs (PLAT-1837, #76)"
type: SpecReview
analysis: gap-analysis
scope: "agent-ix/spec-artifacts-iso; FR-004-AC-8, TC-079, spec_artifacts_iso/manifest.yaml (edge_types, NFR/IT/TC allowed_links), tests/test_manifest_and_validate.py"
review_set: subset
---
# SR-040: Gap analysis — control verification verbs (PLAT-1837, #76)

## Summary

Ticket: PLAT-1837. PR agent-ix/spec-artifacts-iso#76, head ca3dabe. This is a
planless audit. Plan completion: not assessed.

- **Matrix:** `quire matrix --scope .` lists FR-004-AC-8 as `tagged` and bound to
  `tests/test_manifest_and_validate.py:705`
  (`@pytest.mark.trace("TC-079", "FR-004-AC-8")`). The `requirement-without-design`
  status is the same as on every other FR-004 criterion.
- **Reverse gap:** the only production change is the manifest. Each line it adds
  (two `edge_types` entries and two verbs on each of NFR, IT and TC) is owned by
  FR-004-AC-8 and asserted by TC-079. No code is left without an owning
  requirement.
- **Stub and inflation check:** the test runs real `quire validate` against the
  module. It includes a negative control (`blocks` still raises
  `disallowed-edge-type`), which proves the relationship is actually inserted into
  the file. Four manifest mutations each make the test fail (see SR-039). The
  test passes on the PR head.
- **Safety consumer (spec-objects-safety#49, head 240f0b1):** with this branch's
  `spec_artifacts_iso` on `PYTHONPATH`, single-file validation of IT, TC and NFR
  files carrying the new verbs reports no `disallowed-edge-type`. With
  `origin/main` it reports one. This PR therefore delivers what #49 needs from
  iso. The retained-evidence record type belongs to engineering-assurance and is
  outside this PR.

## Verdict

Clean. FR-004-AC-8 is backed by a test that can fail, and the change has no
untested surface.

## Findings

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-001 | low | No findings (placeholder) | - |
