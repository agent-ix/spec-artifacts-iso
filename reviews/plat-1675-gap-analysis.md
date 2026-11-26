---
id: SR-047
title: "gap-analysis — tension edge vocabulary"
type: SpecReview
analysis: gap-analysis
scope: "agent-ix/spec-artifacts-iso; PLAT-1675; PR #78; spec_artifacts_iso/manifest.yaml; tests/test_manifest_and_validate.py"
review_set: subset
---

## Summary

Reviewed e368d3c481b2fffeb47bc101697f3a182e4a8ed2: FAIL. The change declares symmetric conflicts_with and forward resolves with inverse resolved_by for downstream authored tensions.

## Verdict

**FAIL**.

## Findings

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-001 | high | The whole-repository matrix contains 44 untagged obligation rows, including FR-003-AC-3. These inherited gaps prevent a repository-wide gap-analysis PASS; they were not introduced by the two added edge declarations and should remain with their owning work. | spec/functional/FR-003-master-requirements-archetype.md:88 |

## Reviewed units and bindings

```yaml
scope:
- id: FR-004-AC-1
  path: spec/functional/FR-004-edge-type-vocabulary.md
  role: examined
  excerpt: Every entry in `edge_types` carries a non-empty `description` and a `category`
    drawn from the seven declared categories.
- id: FR-004:inverses
  path: spec/functional/FR-004-edge-type-vocabulary.md
  role: examined
  excerpt: "A verb with **no** declared inverse is one where the reverse reading has\
    \ no name \u2014 either because the relationship is symmetric (`peer`) or because\
    \ only one direction is meaningful to author (`transitions_to`)."
- id: FR-004:inverse-labels
  path: spec/functional/FR-004-edge-type-vocabulary.md
  role: examined
  excerpt: An inverse label is a **derived name, not a second declaration**.
- id: FR-003-AC-3
  path: spec/functional/FR-003-master-requirements-archetype.md
  role: examined
  excerpt: A conformant master `spec.md` passes `validate_document`
bindings: []
```

## Coverage and evidence

Explicit authoring/matrix tool: `/tmp/regfinish-quoin-v0.37.0/quoin` 0.37.0. Artifact validator and CLI probe: Quire 0.52.0 (engine 0.62.2). Module: spec-artifacts-process@v0.36.0. No applicable AssuranceProfile found. Exact model ID is not exposed; marker uses model=unknown. No spec/plan files changed, so no spec-review method applies. No dependency revision moved. Artifact custody belongs to the dispatching lead; repository files were not modified.

Plan completion: not assessed

Whole-repository reconciliation: Quoin 0.37.0 matrix reports 123 obligation rows: 63 tagged, 16 method-without-symbol and 44 untagged. Repeated criterion IDs occur among generated rows; these counts describe rows, not 44 unique missing criterion IDs. All rows have no run evidence. This is an inherited repository assurance result, separate from the clean PR code-review. No new criterion was introduced by this PR; FR-004-AC-1 remains tagged.

Coverage extraction reports no new untracked symbols for the changed test; the tool warns about existing duplicate nested helper `reasons` symbols elsewhere in the same test file. No artifact or matrix was synthesized by hand.

Reverse inventory: ISO archetype registration/extraction/assert facets are owned by FR-001–003; edge/role vocabulary by FR-004; TypeSpec semantic schemas by FR-005; semantic manifest block by FR-006; mappings by FR-007; criticality and safety-class fields by FR-008–009. Existing generator/staging/build scripts are build glue; module init exports resource paths. The two new verbs are owned by FR-004 and downstream safety FR-402. Surface and pattern inspection found no new unowned runtime behavior or stubs. Marker-like XXX/pass text is documentation or schema prose, not executable placeholders. Optional semantic gap-analysis was not separately invoked; requested intent verification was performed by code-review.

Missing matrix row IDs, retaining duplicate identities: FR-001-AC-2, FR-001-AC-3, FR-001-AC-4, FR-001-AC-1, FR-001-CON-1, FR-001-AC-1, FR-001-AC-1, FR-001-AC-1, FR-001-AC-1, FR-001-AC-2, FR-001-AC-1, FR-001-AC-1, FR-001-AC-1, FR-001-AC-1, FR-001-AC-1, FR-001-AC-1, FR-001-AC-1, FR-001-AC-2, FR-001-AC-1, FR-001-AC-1, FR-001-AC-1, FR-001-AC-1, FR-001-AC-1, FR-001-AC-1, FR-001-AC-1, FR-001-AC-1, FR-001-AC-1, FR-001-AC-1, FR-001-AC-1, FR-001-AC-1, FR-001-AC-1, FR-001-AC-1, FR-003-AC-3, FR-003-AC-4, FR-003-AC-5, FR-003-AC-6, FR-003-AC-7, FR-003-AC-8, FR-003-CON-1, FR-006-AC-6, FR-006-CON-2, NFR-001-M-2, nfr-M-1, nfr-M-2

## Dispositions

| FND | outcome | reason |
| --- | --- | --- |
| FND-001 | deferred | Deferred to PLAT-1915: these inherited repository-wide untagged obligation rows are outside PLAT-1675's two-entry vocabulary feature diff. PLAT-1915 explicitly owns older regulated-support traceability gaps, including spec-artifacts-iso, and requires re-running the matrix, classifying criterion age, and adding meaningful feature-scoped evidence. Generated/duplicate matrix identities remain subject to that classification; this deferral does not claim they are all distinct older requirements. |

## Disposition pass 1

**PR mergeable=yes** at e368d3c481b2fffeb47bc101697f3a182e4a8ed2. Code-review SR-046 remains PASS with no real findings. The sole gap-analysis finding is deferred under the dispatching lead's instruction after checking PLAT-1915's outcome, baseline and acceptance criteria. The repository-wide gap-analysis result remains FAIL as originally recorded; this disposition clears the inherited finding for this bounded PR, not for the repository.

Verified PLAT-1915 names older gaps across spec modules, explicitly includes spec-artifacts-iso, and requires released-tool matrix refresh, age classification and meaningful tests before new tags. Git first-add history for the implicated root FR-001, FR-003, FR-006 and NFR-001 files predates its 2026-11-11 cutoff (May, June and September). Repeated/generated identities in the raw matrix remain provisional and are not silently classified by that history. No source or test delta since the reviewed head, so no further test run was needed. Existing focused seven-test result remains applicable.
