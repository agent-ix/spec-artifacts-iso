---
id: SR-046
title: "code-review — tension edge vocabulary"
type: SpecReview
analysis: code-review
scope: "agent-ix/spec-artifacts-iso; PLAT-1675; PR #78; spec_artifacts_iso/manifest.yaml; tests/test_manifest_and_validate.py"
review_set: subset
---

## Summary

Reviewed e368d3c481b2fffeb47bc101697f3a182e4a8ed2: PASS. The change declares symmetric conflicts_with and forward resolves with inverse resolved_by for downstream authored tensions.

## Verdict

**PASS**.

## Findings

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-001 | low | No findings (placeholder) | - |

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
bindings:
- test_id: test_fr004_ac1_every_edge_type_has_a_description_and_known_category
  ac_id: FR-004-AC-1
  trace: correct
```

## Coverage and evidence

Explicit authoring/matrix tool: `/tmp/regfinish-quoin-v0.37.0/quoin` 0.37.0. Artifact validator and CLI probe: Quire 0.52.0 (engine 0.62.2). Module: spec-artifacts-process@v0.36.0. No applicable AssuranceProfile found. Exact model ID is not exposed; marker uses model=unknown. No spec/plan files changed, so no spec-review method applies. No dependency revision moved. Artifact custody belongs to the dispatching lead; repository files were not modified.

Independent focused run with project-lock-matching Quire wheel 0.60.0 in `/home/peter/.cache/pypoetry/virtualenvs/spec-artifacts-iso-Dlv00LQf-py3.13`: `python -m pytest -o addopts='' tests/test_manifest_and_validate.py -k fr004 -q` → 7 passed, 74 deselected. Ruff and Black passed for the changed test; diff whitespace check passed.

A real CLI consumer probe loads this ISO module plus a temporary tension archetype whose allowed_links contain conflicts_with and resolved_by. A document authoring both validates with exit 0 and no diagnostics for those verbs. A misspelled inverse control emits UnknownEdgeType. Existing soup_requirement_for diagnostics arise because that unrelated vocabulary provider is not included in the focused probe; they are not new findings.

The new registry declarations satisfy the symmetric/forward-inverse intent without introducing a second resolved_by declaration. No inverse label collision was introduced. The changed assertions observe real manifest data, are unguarded, and retain the existing FR-004-AC-1 trace tag. Removing conflicts_with, changing its category, or breaking the inverse causes the asserted contract to fail. No production functions were added, so no implements function tags are required.

An initial run in a cached Quire wheel 0.52.0 environment failed unchanged AC-5's unmutated-load control (6 passed, 1 failed). That wheel is below project-lock Quire 0.60.0 and the failure is not attributed to this PR; the correctly versioned independent rerun above passed.
