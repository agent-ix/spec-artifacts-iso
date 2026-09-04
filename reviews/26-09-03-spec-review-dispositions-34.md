---
id: SR-011
title: "Dispositions for the #34 composite spec review (SR-003..SR-010)"
type: SpecReview
analysis: base
scope: "reviews/26-09-03-spec-review-*.md (SR-003..SR-010), spec/spec.md, spec/usecase/US-001-consume-typed-iso-artifact-records.md, spec/functional/FR-005-semantic-data-schemas.md, spec/functional/FR-006-semantic-manifest-block.md, spec/functional/FR-007-markdown-mappings.md, spec/non-functional/NFR-001-reproducible-offline-schema-projection.md, spec/tests.md"
review_set: all
---
# SR-011: Dispositions for the #34 composite spec review

## Summary

The composite review of ticket agent-ix/spec-artifacts-iso#34 ran eight
analyses (SR-003 base, SR-004 failure-domain, SR-005 integrity, SR-006
dependency, SR-007 evidence, SR-008 risk-complexity, SR-009 scope-boundary,
SR-010 ears-conformance) and raised 9 high and 47 medium findings across the
five authored documents and the Test Matrix. Every high and every medium was
re-read against the working tree after the fix pass. This document records the
findings that were deliberately **not** acted on, one line each, so that a
later reader does not re-raise them as gaps.

Two upstream gaps the review demanded numbers for were filed during this pass:
agent-ix/quoin#336 (`semantic.exports` resolves against `object_types` only, so
this module's artifact-type exports are refused at install) and
agent-ix/quire-rs#393 (FR-069's prose says "object type" while the loader
resolves against every archetype). Both numbers are now carried in FR-006.

## Verdict

**PASS** — every high and every medium is applied or dispositioned below.
`quire validate --scope . "spec/**/*.md"` reports zero errors; the three
remaining warnings are pre-existing advisories in FR-002, FR-003 and StR-001,
outside this ticket's documents.

## Findings

| ID | Severity | Summary | Refs |
|----|----------|---------|------|
| FND-401 | low | SR-008 FND-281 token-superset rule declined: `Verification.testRefs` still reads `TC-` tokens from inside the parentheses only. The new `annotation` property carries every byte of the cell verbatim, so nothing is lost; scanning the whole cell would make `method` and `annotation` ambiguous for cells whose prose mentions a test id. | spec/functional/FR-005-semantic-data-schemas.md |
| FND-402 | low | SR-008 FND-281 empty-cell recommendation declined: an empty `Verification` cell stays a `minLength: 1` rejection rather than becoming `method: ""`. Admitting the empty cell would make the schema describe a defect as a form; the corpus occurrences (7 cells of 20,881, re-measured 2026-09-04) are a census finding and TC-045 pins the rejection. | spec/functional/FR-005-semantic-data-schemas.md |
| FND-403 | low | SR-008 FND-287 conformance kit declined for this ticket: the negative cases stay TC-045 fixtures inside the suite rather than a shipped `examples/invalid/` kit. A shipped kit is a consumer-conformance deliverable and there is no consumer yet — the engine-side extractor is agent-ix/quire-rs#393. | spec/functional/FR-007-markdown-mappings.md |
| FND-404 | low | SR-008 FND-288 scope split declined: `## Invariants` stays inside FR-007 rather than moving to its own FR. It is one coherent slice of the `ocl-clause` mapping and a separate requirement would restate FR-007's mapping rules to say the same thing twice. | spec/functional/FR-007-markdown-mappings.md |
| FND-405 | low | SR-005 FND-223 rename declined: the model stays `Verification` rather than `VerificationCell`/`MethodRef`. The name matches the authored column heading the mapping reads, which is what a reader of the record needs to find it. | spec_artifacts_iso/semantic/main.tsp |
| FND-406 | low | SR-005 FND-227 rename declined: the mapping kind stays `typed-table`. It is quoin FR-071's own mapping-kind name; renaming it here would diverge from the contract this module implements. The other half of the finding — that `mappings.yaml` had no schema — was applied (`mappings.schema.json`, FR-007-AC-1). | spec/functional/FR-007-markdown-mappings.md |
| FND-407 | low | SR-005 FND-231 / SR-006 FND-245 relocation declined: the `invariants` locator and the `version: 0.2.0` bump stay in FR-006 Outputs, because FR-006 owns every manifest change. The parity obligation the finding was really about (FR-002-AC-6/AC-7, TC-009/TC-010) is now stated in both FR-006 and FR-007. | spec/functional/FR-006-semantic-manifest-block.md |
| FND-408 | low | SR-007 FND-260 method-token change declined: FR-005-CON-3's verification stays `Test (TC-054)` rather than `Analysis`. Checking the lockfile pins and the absence of an `.npmrc` is executable, so a test is the correct evidence class. | spec/functional/FR-005-semantic-data-schemas.md |
| FND-409 | low | SR-010 FND-327 relocation declined: the free-text rationale (why `type`, `method`, `target`, `threshold` are unconstrained) stays in Behavior beside the rule it justifies rather than moving to Description, where a reader deciding whether a cell may be free text would not find it. | spec/functional/FR-005-semantic-data-schemas.md |
| FND-410 | medium | SR-006 FND-248 CI job **blocked, not declined**: `make schemas-check` cannot run in CI because `@agent-ix/semantic-core` 0.1.0 resolves only from a scope-routed registry (npm.ix) that CI does not reach, and this repository ships no `.npmrc` by FR-005-CON-3. Stated consequence, so nobody is surprised by it: `make test` now contains checks that shell out to `make schemas`/`make schemas-check` (TC-042, TC-056, TC-058), so a dispatched CI run fails until the TypeSpec package is installed. Those tests fail with the command to run rather than skipping, which is the intended behaviour — a skip would report green for a gate that never executed. The gate stays local until agent-ix/filament-core-data#11 publishes the package; NFR-001 Verification records that no CI job is claimed here, and `.github/workflows/ci.yml` is deliberately unchanged by this ticket. | .github/workflows/ci.yml, spec/non-functional/NFR-001-reproducible-offline-schema-projection.md |
| FND-411 | medium | SR-006 FND-240 resolved against the review's own recommendation on one point: the dependency floor is `quire >= 0.33.0` from the internal index, not `>= 0.46.0`, because no 0.46.0 wheel is published and pinning a locally built wheel would make the lockfile unreproducible on any other machine. The half of FR-006-AC-3 that needs FR-069 was split into FR-006-AC-8/TC-063 and is recorded as a **strict expected failure** naming agent-ix/quire-rs#388 — never a skip. | pyproject.toml, spec/functional/FR-006-semantic-manifest-block.md |

## Recommendations

- Re-run this disposition pass when agent-ix/quire-rs#388 publishes a wheel:
  TC-063 will flip from expected-failure to failing-because-it-passes, which is
  the signal to delete the marker and let the assertion stand on its own.
- FND-410 unblocks the moment agent-ix/filament-core-data#11 lands; at that
  point `make semantic-install && make schemas-check` becomes a CI job and
  NFR-001 metric 2 stops being a manual gate.
