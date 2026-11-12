---
id: SR-025
title: "Code review — optional criticality field on StR/US/FR/NFR (PLAT-1413, #71)"
type: SpecReview
analysis: code-review
scope: "agent-ix/spec-artifacts-iso; spec_artifacts_iso/schemas/{fr,nfr,str,us}-frontmatter.schema.json, spec_artifacts_iso/schemas/{FR,NFR,StR,US}.json, spec_artifacts_iso/semantic/main.tsp, spec_artifacts_iso/mappings.yaml, tests/test_criticality.py"
review_set: subset
---
# SR-025: Code review — optional criticality field on StR/US/FR/NFR (PLAT-1413, #71)

## Summary

Ticket: PLAT-1413. PR agent-ix/spec-artifacts-iso#71, head ef717e5, 11 files,
+263 lines. Scope is `git diff origin/main...HEAD` only.

Measured independently:

- `make semantic-install` then `make schemas-check` on the PR head: "schema
  projection is up to date (45 files)". The four record schemas are generator
  output from `main.tsp`, not hand edits. The generator's private dependency
  installed with the machine's existing credentials; no auth workaround.
- No shared `Criticality.json` exists, hand-written or generated. Each of the
  four frontmatter schemas declares `enum: [low, medium, high]` inline, not in
  `required`, with no `default`. The four TypeSpec models declare
  `criticality?: "low" | "medium" | "high"`, which projects to an `anyOf` of
  three `const` strings with no `default`.
- `mappings.yaml` adds `criticality` with `kind: frontmatter`,
  `source: {key: criticality}`, `lossless: false` under the FR, NFR, StR and US
  models, the same shape as `qualityAttribute`.
- `pytest tests/test_criticality.py`: 44 passed, 0 skipped, quire 0.40.0 on
  PATH. All four archetypes are parametrised in every test. The `quire
  validate` tests carry `skipif(shutil.which("quire") is None)` and nothing
  else, so they skip only when the CLI is absent.
- The invalid-value tests (AC-5..7) are real oracles. quire prints
  `"High" is not one of "low", "medium" or "high" (at criticality)`. The field
  name comes from the `(at criticality)` locator, not from echoed input or the
  tmp path.
- Neighbouring suites `test_semantic_schemas.py` and `test_markdown_mappings.py`
  pass (21). ruff and black are clean on the new test.

## Verdict

**PASS with one low.** The implementation matches FR-008, FR-005 and FR-007-AC-8
with no default and no hand-written shared file. The only finding is
discoverability in the README.

## Findings

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-001 | low | The README archetype table and the field notes name `quality_attribute` as a frontmatter enum, but nowhere mention the new optional `criticality` field on FR/NFR/StR/US. An author reading the README cannot find the field, and the skeletons do not show it either. | README.md:43-46, README.md:86-88 |
