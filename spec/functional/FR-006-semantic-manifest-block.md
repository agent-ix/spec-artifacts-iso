---
id: FR-006
title: "The manifest declares the semantic block and references each data schema by digest"
type: FR
relationships:
  - target: "ix://agent-ix/spec-artifacts-iso/US-001"
    type: "implements"
  - target: "ix://agent-ix/spec-artifacts-iso/FR-001"
    type: "depends_on"
  - target: "ix://agent-ix/spec-artifacts-iso/FR-005"
    type: "depends_on"
  - target: "ix://agent-ix/quoin/FR-070"
    type: "implements"
  - target: "ix://agent-ix/quoin/FR-073"
    type: "implements"
---
# FR-006: The manifest declares the semantic block and references each data schema by digest

## Description

The module manifest (`spec_artifacts_iso/manifest.yaml`) SHALL carry one
`semantic` block under the quoin FR-070 contract (`contract_version: 1.0.0`)
and SHALL reference, on every artifact type FR-005 gives a model, the emitted
schema by module-relative path and SHA-256 digest (`data_schema: { schema:
schemas/<Model>.json, digest: sha256:<hex> }`), so that quoin at install time
and quire at load time bind the archetype to the exact shipped bytes.

## Inputs

- `spec_artifacts_iso/manifest.yaml` with its existing `artifact_types[]`,
  `frontmatter_schema_ref` values, and `body_extraction` locators.
- The emitted schemas of [FR-005](./FR-005-semantic-data-schemas.md).
- The FR-035 module-manifest schema as bundled at
  `spec_artifacts_iso/module-manifest.schema.json`, refreshed with the
  `semantic` block and the `data_schema` reference form of filament-core-service
  FR-035 CR-003 (agent-ix/filament-core-service#21, the revision quoin vendors
  at 3e842ce).

## Outputs

- The `semantic` block: `contract_version: 1.0.0`, `semantic_core: 0.1.0`,
  `package: agent-ix/spec-artifacts-iso`, `exports` naming every artifact type
  that carries a `data_schema` reference (`FR`, `NFR`, `StR`, `US`, `IT`, `TC`,
  `master-requirements`, `index`, `log`, `Glossary`), `imports: {}`,
  `targets: [json-schema, markdown]`, `mappings: [frontmatter, section, table,
  typed-table, ocl-clause]`, `compatibility_posture: additive`, and
  `legacy_forms: warning`.
- One `data_schema` reference per exported artifact type, beside its
  `frontmatter_schema_ref`.
- `version` bumped to `0.2.0`, because every emitted `$id` embeds it.

## Behavior

- The `semantic` block SHALL carry exactly the keys listed in Outputs and no
  other; `sweep_report` is absent because `legacy_forms` is `warning`.
- Each `data_schema.digest` SHALL equal the SHA-256 over the raw bytes of the
  file `data_schema.schema` names, with no line-ending normalization.
- Every existing `frontmatter_schema_ref`, `body_extraction` locator, and
  `assert` facet SHALL remain byte-for-byte as before this change, except that
  the `FR` archetype gains one optional `invariants` locator (`from:
  code_block`, `language: ocl`, `under_section: Invariants`, `required: false`)
  for the FR-007 `ocl-clause` mapping.
- The bundled FR-035 schema SHALL accept the `semantic` block and the reference
  form of `data_schema`, and SHALL reject a `semantic` block carrying a key
  outside the admitted ten, a `data_schema` mixing `schema`/`digest` with any
  other key, a `package` that is not `<org>/<repo>`, and a `targets` value
  outside the registry.
- When the module is loaded by the quire wheel this module tests against
  (`quire.Registry`), the load SHALL succeed with every exported type's schema
  resolved and its digest recorded, and `validate_document` over each skeleton
  SHALL still report `is_valid`.
- When the module is installed by quoin (`quoin module install
  path:<module root>`), quoin SHALL accept the block. If the installed quoin
  refuses an export because its `semantic.exports` check admits only
  `object_types` names while this module exports `artifact_types`, then the
  module author SHALL record the exact diagnostic in this requirement's change
  log, file an issue on agent-ix/quoin, and keep the `exports` and
  `data_schema` references as specified rather than bend to the gap.
- If any `data_schema.digest` differs from the shipped file, then the module's
  own test suite SHALL fail naming the type, the recorded digest, and the
  computed digest, before any engine sees the manifest.

## Constraints

| ID | Constraint | Type | Validation |
|----|------------|------|------------|
| FR-006-CON-1 | The manifest SHALL add no new required key at the manifest root or on any `ArtifactTypeEntry`, so that a consumer that ignores the `semantic` block loads the module as before. | Compatibility | Test (TC-046) |
| FR-006-CON-2 | The manifest SHALL carry no inline `data_schema` object on any artifact type; the reference form is the only form. | Integrity | Test (TC-047) |

## Acceptance Criteria

| ID | Criteria | Verification |
|----|----------|--------------|
| FR-006-AC-1 | The manifest validates against the bundled FR-035 schema with the `semantic` block present, and the block's keys equal exactly `{contract_version, semantic_core, package, exports, imports, targets, mappings, compatibility_posture, legacy_forms}`. | Test (TC-046) |
| FR-006-AC-2 | For each of the ten exported artifact types, `data_schema.schema` names an existing file under `spec_artifacts_iso/schemas/`, `data_schema.digest` equals `sha256:` plus the hex SHA-256 of that file's bytes, and `exports` equals the set of artifact types carrying a reference. | Test (TC-047) |
| FR-006-AC-3 | `quire.Registry` loads the module root with no error, and for every exported type the loaded archetype reports the schema digest the manifest records; each skeleton still passes `validate_document`. | Test (TC-048) |
| FR-006-AC-4 | The bundled FR-035 schema rejects `semantic: {…, foo: 1}` naming `foo`, rejects `data_schema: {schema: x.json, digest: sha256:…, type: object}`, and rejects `package: ix://agent-ix/x`. | Test (TC-049) |
| FR-006-AC-5 | A one-byte edit to any emitted schema without a digest update fails the suite naming the artifact type and both digests. | Test (TC-047) |
| FR-006-AC-6 | `quoin module install path:<module root>` on the quoin built from main at 3e842ce or later either succeeds, or fails with a `semantic.unknown-export` diagnostic that is recorded verbatim in this requirement and in a filed agent-ix/quoin issue; no other diagnostic is accepted. | Demonstration |

## Dependencies

- **Upstream**: [FR-001](./FR-001-module-manifest-activates.md) (the FR-035 gate), [FR-005](./FR-005-semantic-data-schemas.md) (the referenced files), quoin FR-070 and FR-073 (agent-ix/quoin#293), quire-rs FR-069 (agent-ix/quire-rs#388)
- **Downstream**: quoin FR-075 (derives the package manifest and registry pins from `exports`), agent-ix/filament-core-data#36
