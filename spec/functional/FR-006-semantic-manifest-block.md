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

> **Review pass (2026-09-03, SR-003..SR-010):** obligations on quoin and on
> "the module author" are removed; this requirement binds the manifest and the
> module's own suite only. What quoin and quire do with the block is recorded
> as evidence, not as obligations. The quire engine floor (0.46.0, the wheel
> carrying quire-rs FR-069) and the FR-035 schema refresh provenance
> (filament-core-service CR-003, revision a77f31e, as vendored by quoin
> 3e842ce) are named. The known quoin contract gap is stated as certain:
> quoin 3e842ce checks `semantic.exports` and resolves `data_schema` against
> `object_types` only.
>
> **Which record `data_schema` binds.** For this module, `data_schema` binds
> the FR-007 record (frontmatter identity, sections, typed rows, provenance).
> quire's `validate_document` validates a *declaration* record
> (`{fields, clauses, operations}`) against `data_schema`, and only on the
> `object:` axis (quire-rs FR-069-AC-1, `semantic_findings`); it never reaches
> an artifact-type record, so no engine validates this module's records
> today. That validation is engine work owned by agent-ix/quire-rs (see
> spec.md Out of Scope); this module's suite is the record oracle until then.

The module manifest (`spec_artifacts_iso/manifest.yaml`) SHALL carry one
`semantic` block under the quoin FR-070 contract (`contract_version: 1.0.0`).

The manifest SHALL reference, on every artifact type FR-005 gives a model, the
emitted schema by module-relative path and SHA-256 digest (`data_schema: {
schema: schemas/<Model>.json, digest: sha256:<hex> }`), so that quoin at
install time and quire at load time bind the archetype to the exact shipped
bytes.

## Inputs

- `spec_artifacts_iso/manifest.yaml` with its existing `artifact_types[]`,
  `frontmatter_schema_ref` values, and `body_extraction` locators.
- The emitted schemas of [FR-005](./FR-005-semantic-data-schemas.md) and the
  export-name to model map fixed there.
- The FR-035 module-manifest schema bundled at
  `spec_artifacts_iso/module-manifest.schema.json`, refreshed with the
  `semantic` block and the `data_schema` reference form of
  filament-core-service FR-035 CR-003 (agent-ix/filament-core-service#21,
  revision a77f31e, SHA-256 `69cf9738…dcbbc`, as vendored by quoin 3e842ce).
- The quire wheel the suite runs against: `>= 0.33.0`, the published floor of
  the internal package index. Every criterion of this requirement except AC-3's
  digest-refusal half is discharged at that floor, because a consumer that
  ignores the `semantic` block loads the module unchanged (CON-1).
- The digest-refusal half of AC-3 needs quire-rs FR-069, which is on `quire-rs`
  main (engine 0.46.0) and in no published wheel (agent-ix/quire-rs#388). The
  suite SHALL record that assertion as a strict expected failure naming
  agent-ix/quire-rs#388 — never a skip and never a pass. A skip reports green
  for a check that did not run, which is the failure mode this module's IT-002
  history already paid for; a strict expected failure that starts passing fails
  the suite, so the wheel's arrival is reported by the gate itself.

## Outputs

- The `semantic` block: `contract_version: 1.0.0`, `semantic_core: 0.1.0`,
  `package: agent-ix/spec-artifacts-iso`, `exports` naming every artifact type
  that carries a `data_schema` reference (`FR`, `NFR`, `StR`, `US`, `IT`, `TC`,
  `master-requirements`, `index`, `log`, `Glossary`), `imports: {}`,
  `targets: [json-schema, markdown]`, `mappings: [frontmatter, section, table,
  typed-table, ocl-clause, list, token, provenance]`, `compatibility_posture: additive`, and
  `legacy_forms: warning`. `sweep_report` is absent because `legacy_forms` is
  `warning`; nine of the ten admitted keys are present. `legacy_forms` governs
  the legacy `## Properties` forms quoin FR-074 sweeps — a form none of this
  module's own documents author — so `warning` is the value that changes
  nothing, and promoting it to `error` is what would demand a `sweep_report`.
- A legacy-manifest fixture at `tests/fixtures/manifest-legacy.yaml`: this
  manifest with the `semantic` block and every `data_schema` removed, which
  CON-1 and AC-7 use to prove the module still validates and loads for a
  consumer that predates the block.
- One `data_schema` reference per exported artifact type, beside its
  `frontmatter_schema_ref`, using the FR-005 map (`master-requirements` →
  `schemas/MasterRequirements.json`, `index` → `schemas/Index.json`, `log` →
  `schemas/Log.json`).
- `version: 0.2.0` (every emitted `$id` embeds it), bumped as the first step
  of the change so `make schemas` and the digests are computed once.
- On the `FR` archetype, one new optional locator `invariants` (`from:
  code_block`, `language: ocl`, `under_section: Invariants`, `required:
  false`, `multiple: true`) for the FR-007 `ocl-clause` mapping, declared
  together with the `## Invariants` heading the FR skeleton gains, so that the
  FR-002-AC-6 and FR-002-AC-7 skeleton/assert parity checks (TC-009, TC-010)
  keep passing in both directions.
- A digest refresh step, `make schemas` followed by `make manifest-digests`,
  which rewrites every `data_schema.digest` from the shipped bytes; the suite
  never hand-computes a digest.

## Behavior

- The `semantic` block SHALL carry exactly the nine keys listed in Outputs.
- Each `data_schema.digest` SHALL equal the SHA-256 over the raw bytes of the
  file `data_schema.schema` names, with no line-ending normalization.
- Every existing `frontmatter_schema_ref`, `body_extraction` locator, and
  `assert` facet SHALL remain byte-for-byte as before this change; the only
  locator addition is the `FR` `invariants` locator of Outputs.
- The bundled FR-035 schema SHALL carry, verbatim from revision a77f31e, the
  `semantic` property and the `ObjectTypeEntry.data_schema` reference form,
  and the same reference form on `ArtifactTypeEntry.data_schema`.
- The manifest SHALL carry no inline `data_schema` object on any artifact
  type.
- If any `data_schema.digest` differs from the SHA-256 of the shipped file,
  then the module's test suite SHALL fail naming the artifact type, the
  recorded digest, and the computed digest.
- If the manifest carries a `semantic` key outside the admitted ten, a
  `data_schema` mixing `schema`/`digest` with any other key, a `package` that
  is not `<org>/<repo>`, or a `targets` value outside the registry, then the
  bundled FR-035 schema SHALL reject the manifest naming the key or value.
- Evidence, not obligation — quire: with the block and the references in
  place, the quire 0.46.0 loader (`quire.Registry.load_from`) admits
  artifact-type exports because it checks `exports` against every archetype
  (`Manifest::all_archetypes`), resolves each reference-form `data_schema`,
  and refuses the module (`unknown archetype`) on a digest mismatch or an
  undeclared export — probed on 2026-09-03 against a copy of this module with
  one export. quire-rs FR-069's prose says "object types"; the loader's
  behaviour is the evidence this requirement relies on, and the wording gap is
  filed as agent-ix/quire-rs#393 with the record-kind question above.
- Evidence, not obligation — quoin: quoin at 3e842ce (`readSemanticBlock`)
  checks `semantic.exports` against `object_types` names and builds
  `dataSchemas` from `object_types` only, so `quoin module install
  path:<module root>` on this manifest emits, per exported artifact type,
  `semantic.unknown-export` and `semantic.export-without-schema` and refuses
  the install. The gap is filed as agent-ix/quoin#336; the manifest keeps
  `exports` and the references as specified rather than bend to it, because the
  FR-070 amendment is quoin's to make.

## Constraints

| ID | Constraint | Type | Validation |
|----|------------|------|------------|
| FR-006-CON-1 | The manifest SHALL add no new required key at the manifest root or on any `ArtifactTypeEntry`, so that a consumer that ignores the `semantic` block loads the module as before; the suite carries a legacy-manifest fixture (this manifest with the block and the references removed) that validates under the same FR-035 schema and loads under quire. | Compatibility | Test (TC-046) |
| FR-006-CON-2 | The manifest SHALL carry no inline `data_schema` object on any artifact type; the reference form is the only form. | Integrity | Test (TC-047) |

## Acceptance Criteria

| ID | Criteria | Verification |
|----|----------|--------------|
| FR-006-AC-1 | The manifest validates against the bundled FR-035 schema with the `semantic` block present, and the block's key set equals exactly `{contract_version, semantic_core, package, exports, imports, targets, mappings, compatibility_posture, legacy_forms}` with the values of Outputs. | Test (TC-046) |
| FR-006-AC-2 | For each of the ten exported artifact types, `data_schema.schema` names an existing file under `spec_artifacts_iso/schemas/` per the FR-005 map, `data_schema.digest` equals `sha256:` plus the hex SHA-256 of that file's bytes, and `exports` equals the set of artifact types carrying a reference. | Test (TC-047) |
| FR-006-AC-3 | At the published floor (quire ≥ 0.33.0), `quire.Registry.load_from` over the module's parent directory lists all eleven archetypes with the `semantic` block and the ten `data_schema` references present, and `validate_document` passes every skeleton — adding the block breaks no consumer. | Test (TC-048) |
| FR-006-AC-4 | The bundled FR-035 schema rejects `semantic: {…, foo: 1}` naming `foo`, rejects `data_schema: {schema: x.json, digest: sha256:…, type: object}`, rejects `package: ix://agent-ix/x`, and rejects `targets: [go]`; its `semantic` property and `ObjectTypeEntry.data_schema` equal the a77f31e originals byte-for-byte after JSON canonicalization. | Test (TC-049) |
| FR-006-AC-5 | A one-byte edit to any emitted schema without a digest update fails the suite naming the artifact type and both digests. | Test (TC-047) |
| FR-006-AC-6 | `quoin module install path:<module root>` on quoin 0.23.1 (main ≥ 3e842ce) refuses the install with `semantic.unknown-export` and `semantic.export-without-schema` for each of the ten exports and no other diagnostic; the verbatim output is recorded against agent-ix/quoin#336, and the previously installed registry version of this module is restored afterwards. | Demonstration (TC-055) |
| FR-006-AC-7 | The legacy-manifest fixture (no `semantic` block, no `data_schema`) validates under the bundled FR-035 schema and loads under quire with the same eleven archetypes. | Test (TC-046) |
| FR-006-AC-8 | On a wheel carrying quire-rs FR-069, a copy of the module with one `data_schema.digest` altered by one hex digit is refused at load — the digest binding is real, not a no-op. Recorded as a strict expected failure naming agent-ix/quire-rs#388 until such a wheel is published. | Test (TC-063) |

## Dependencies

- **Upstream**: [FR-001](./FR-001-module-manifest-activates.md) (the FR-035 gate), [FR-005](./FR-005-semantic-data-schemas.md) (the referenced files), quoin FR-070 and FR-073 (agent-ix/quoin#293), quire-rs FR-069 (agent-ix/quire-rs#388; wheel 0.46.0), filament-core-service FR-035 CR-003 (agent-ix/filament-core-service#21)
- **Blocked downstream**: quoin FR-075 (derives the package manifest and registry pins from `exports`) cannot consume this module until agent-ix/quoin#336 lands
- **Downstream**: [NFR-001](../non-functional/NFR-001-reproducible-offline-schema-projection.md), agent-ix/filament-core-data#36
