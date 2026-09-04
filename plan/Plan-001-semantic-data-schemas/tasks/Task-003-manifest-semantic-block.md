---
id: Task-003
title: "FR-006 — the manifest semantic block and digest references"
type: Task
status: done
track: A
priority: P0
relationships:
  - target: ix://agent-ix/spec-artifacts-iso/Task-001
    type: depends_on
  - target: ix://agent-ix/spec-artifacts-iso/FR-006
    type: references
  - target: ix://agent-ix/spec-artifacts-iso/TC-046
    type: verifies
  - target: ix://agent-ix/spec-artifacts-iso/TC-047
    type: verifies
  - target: ix://agent-ix/spec-artifacts-iso/TC-048
    type: verifies
  - target: ix://agent-ix/spec-artifacts-iso/TC-049
    type: verifies
---
# Task-003: FR-006 — the manifest semantic block and digest references

## Scope

Bind each archetype to the exact shipped schema bytes, without adding a
required key that would break a consumer predating the block.

## Subtasks

- [ ] **The `semantic` block**: `contract_version: 1.0.0`, `semantic_core:
  0.1.0`, `package: agent-ix/spec-artifacts-iso`, the ten `exports`,
  `imports: {}`, `targets: [json-schema, markdown]`, the eight `mappings`,
  `compatibility_posture: additive`, `legacy_forms: warning`. Exactly nine
  keys; `sweep_report` stays absent.
- [ ] **Ten `data_schema` references** beside the existing
  `frontmatter_schema_ref` values, using the FR-005 export-name to file map.
- [ ] **The `invariants` locator** on the `FR` archetype (`from: code_block`,
  `language: ocl`, `under_section: Invariants`, `required: false`,
  `multiple: true`), declared together with the `## Invariants` heading the FR
  skeleton gains, so TC-009 and TC-010 keep passing in both directions.
- [ ] **`make manifest-digests`**: rewrites every `data_schema.digest` from the
  shipped bytes. The suite never hand-computes a digest.
- [ ] **The legacy fixture** `tests/fixtures/manifest-legacy.yaml`: this manifest
  with the block and every `data_schema` removed.
- [ ] **TC-046, TC-047, TC-048, TC-049** as the matrix states them.

## Deliverables

- `spec_artifacts_iso/manifest.yaml`
- `spec_artifacts_iso/skeletons/fr.md` (the `## Invariants` section)
- `scripts/manifest_digests.py` and the `manifest-digests` make target
- `tests/fixtures/manifest-legacy.yaml`
- `tests/test_semantic_manifest.py`

## Notes

- The bundled FR-035 schema already carries the `semantic` property and the
  `data_schema` reference form (working tree). TC-049 asserts it rejects the
  four malformed forms and matches the a77f31e original after canonicalization.
- Probed on 2026-09-03 at the published floor (`quire 0.33.0`): a manifest
  carrying the block and a reference-form `data_schema` loads and lists all
  eleven archetypes. That is FR-006-CON-1's evidence and TC-048's baseline.
