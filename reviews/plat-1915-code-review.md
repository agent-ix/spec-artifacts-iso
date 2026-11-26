---
id: SR-048
title: "code-review — FR-006 TC-047"
type: SpecReview
analysis: code-review
scope: "agent-ix/spec-artifacts-iso; PLAT-1915; PR #79; tests/test_semantic_manifest.py"
review_set: subset
---

## Summary

Reviewed commit 71d933280901c817b16ed7b96e0868704f911ba4 for PLAT-1915. PASS: TC-047 now asserts the reference-only shape required by FR-006-CON-2, and its trace tag matches both that constraint and the existing FR-006-AC-2 assertion.

## Verdict

**PASS** — the changed assertion rejects extra inline schema fields and verifies the remaining schema reference against the expected file mapping.

## Findings

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-001 | low | No findings (placeholder) | - |

## Reviewed units and bindings

```yaml
scope:
  - id: FR-006-AC-2
    path: spec/functional/FR-006-semantic-manifest-block.md
    role: examined
    excerpt: "For each of the nine exported artifact types, `data_schema.schema` names an existing file under `spec_artifacts_iso/schemas/` per the FR-005 map, and `exports` equals the set of artifact types carrying a reference."
  - id: FR-006-CON-2
    path: spec/functional/FR-006-semantic-manifest-block.md
    role: examined
    excerpt: "The manifest SHALL carry no inline `data_schema` object on any artifact type; the reference form is the only form."
bindings:
  - test_id: test_tc047_every_export_carries_a_reference_to_its_mapped_file
    ac_id: FR-006-AC-2
    trace: correct
  - test_id: test_tc047_every_export_carries_a_reference_to_its_mapped_file
    ac_id: FR-006-CON-2
    trace: correct
```

## Coverage and evidence

Only `tests/test_semantic_manifest.py` changed. The assertion `set(ref) == {"schema"}` fails if an inline field such as `type` is added to any exported artifact's `data_schema`; subsequent assertions check the expected mapped schema path and file existence. The test reads the committed manifest directly, uses no mocks, and the TC-047 assertions are active. No production function changed, so no `implements` tag is applicable. Related manifest implementation inspected: `spec_artifacts_iso/manifest.yaml`.

`CARGO_PROFILE_DEV_DEBUG=0 CARGO_PROFILE_TEST_DEBUG=0 CARGO_INCREMENTAL=0 /home/peter/dev/worktrees/locked-build.sh /home/peter/dev/worktrees/plat1915-iso/target poetry run pytest --no-cov tests/test_semantic_manifest.py -k tc047 -q` passed: 2 passed, 16 deselected. `git diff --check origin/main...HEAD` passed. The installed Quoin CLI is 0.36.8; the installed spec-artifacts-process module is v0.36.0. The PR's reported Quoin 0.37.0 refresh is its own matrix evidence and is not contradicted by this environment's older installed CLI. No applicable AssuranceProfile was found under `spec/`. No specification, production code, or dependency revision changed. No aggregate gate was run.

The exact model ID is not exposed in this session; comment marker uses `model=unknown`.
