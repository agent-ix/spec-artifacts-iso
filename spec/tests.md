---
type: TestMatrix
id: TM-001
title: "Test Matrix"
---
# Test Matrix

## Overview

Maps every acceptance criterion to the test that backs it.

This document was **non-canonical until 2026-08-19**, and that had a measurable
cost. It carried no `## Test Case Summary`, so the module minted **zero
`test-case` targets** and every `TC-…` id written in a test bound to nothing —
the defect agent-ix/quire-rs#72 counts across the ecosystem. The ids were also
spelled `TC-SCHEMA-nnn`, a second shape nothing else in the ecosystem uses; they
are **renumbered rather than admitted**, because a rule accepting every spelling
enforces nothing.

**[RAN]** `quire coverage --scope .` in this repository, before and after:
**17 written trace tags bound to nothing → 0**.

The 10 criteria still pending are the ones whose verification is an
**activation or authoring integration test** against a running filament-core, or
a document-mutation test — none of which this package's suite runs. They are
listed as pending rather than quietly dropped.

Two rows depend on a release outside this repository and cannot be green
here until it lands. TC-055 and TC-064 are manual because the
published quoin carries no semantic-block reader: the refusal
agent-ix/quoin#336 tracks can be read out of quoin main's source, not run. TC-057 is the manual offline gate that
no CI job claims. TC-063 needed a `quire` wheel carrying quire-rs FR-069's
digest-binding half; that shipped in quire-rs v0.47.0/0.47.1
(agent-ix/quire-rs#390), so TC-063 is now an ordinary passing test, not an
expected failure. Every other row is dischargeable at the module's committed
floor (`quire ^0.47.1`).

An NFR has no `-AC-` ids — its criteria are its `Metric | Target | Threshold |
Method` rows — so NFR rows trace to `NFR-001 (metric n)` (SR-003 FND-006).

## Requirements Traceability

### Functional Requirement Coverage

| Functional Req | Acceptance Criteria | Test Cases | Status |
|----------------|---------------------|------------|-----------------|
| FR-001 | FR-001-AC-2 | — | 🚧 Pending |
| FR-001 | FR-001-AC-3 | — | 🚧 Pending |
| FR-001 | FR-001-AC-4 | — | 🚧 Pending |
| FR-002 | FR-002-AC-1 | TC-005, TC-006, TC-014, TC-015, TC-016 | ✅ Complete |
| FR-002 | FR-002-AC-2 | TC-013 | ✅ Complete |
| FR-002 | FR-002-AC-3 | — | 🚧 Pending |
| FR-002 | FR-002-AC-4 | TC-007 | ✅ Complete |
| FR-002 | FR-002-AC-5 | TC-008, TC-012 | ✅ Complete |
| FR-002 | FR-002-AC-6 | TC-009 | ✅ Complete |
| FR-002 | FR-002-AC-7 | TC-010 | ✅ Complete |
| FR-002 | FR-002-AC-8 | TC-011 | ✅ Complete |
| FR-003 | FR-003-AC-1 | TC-003 | ✅ Complete |
| FR-003 | FR-003-AC-2 | TC-004 | ✅ Complete |
| FR-003 | FR-003-AC-3 | — | 🚧 Pending |
| FR-003 | FR-003-AC-4 | — | 🚧 Pending |
| FR-003 | FR-003-AC-5 | — | 🚧 Pending |
| FR-003 | FR-003-AC-6 | — | 🚧 Pending |
| FR-003 | FR-003-AC-7 | — | 🚧 Pending |
| FR-003 | FR-003-AC-8 | — | 🚧 Pending |
| FR-004 | FR-004-AC-1 | TC-017 | ✅ Complete |
| FR-004 | FR-004-AC-2 | TC-018 | ✅ Complete |
| FR-004 | FR-004-AC-3 | TC-019 | ✅ Complete |
| FR-004 | FR-004-AC-4 | TC-020 | ✅ Complete |
| FR-004 | FR-004-AC-5 | TC-021 | ✅ Complete |
| FR-005 | FR-005-AC-1 | TC-041 | ✅ Complete |
| FR-005 | FR-005-AC-2 | TC-041 | ✅ Complete |
| FR-005 | FR-005-AC-3 | TC-040 | ✅ Complete |
| FR-005 | FR-005-AC-4 | TC-044, TC-045 | ✅ Complete |
| FR-005 | FR-005-AC-5 | TC-042 | ✅ Complete |
| FR-005 | FR-005-AC-6 | TC-043 | ✅ Complete |
| FR-005 | FR-005-AC-7 | TC-061 | ✅ Complete |
| FR-005 | FR-005-AC-8 | TC-060 | ✅ Complete |
| FR-005 | FR-005-AC-9 | TC-062 | ✅ Complete |
| FR-005 | FR-005-CON-1 | TC-039, TC-040 | ✅ Complete |
| FR-005 | FR-005-CON-2 | TC-041 | ✅ Complete |
| FR-005 | FR-005-CON-3 | TC-054 | ✅ Complete |
| FR-005 | FR-005-CON-4 | TC-043 | ✅ Complete |
| FR-006 | FR-006-AC-1 | TC-046 | ✅ Complete |
| FR-006 | FR-006-AC-2 | TC-047 | ✅ Complete |
| FR-006 | FR-006-AC-3 | TC-048 | ✅ Complete |
| FR-006 | FR-006-AC-5 | TC-047 | ✅ Complete |
| FR-006 | FR-006-AC-6 | TC-055 | ✅ Complete |
| FR-006 | FR-006-AC-9 | TC-064 | ✅ Complete |
| FR-006 | FR-006-AC-7 | TC-046 | ✅ Complete |
| FR-006 | FR-006-AC-8 | TC-063 | ✅ Complete |
| FR-006 | FR-006-CON-1 | TC-046 | ✅ Complete |
| FR-006 | FR-006-CON-2 | TC-047 | ✅ Complete |
| FR-007 | FR-007-AC-1 | TC-052 | ✅ Complete |
| FR-007 | FR-007-AC-2 | TC-044 | ✅ Complete |
| FR-007 | FR-007-AC-3 | TC-053 | ✅ Complete |
| FR-007 | FR-007-AC-4 | TC-051 | ✅ Complete |
| FR-007 | FR-007-AC-5 | TC-050 | ✅ Complete |
| FR-007 | FR-007-AC-6 | TC-045 | ✅ Complete |
| FR-007 | FR-007-AC-7 | TC-052 | ✅ Complete |
| FR-007 | FR-007-CON-1 | TC-050 | ✅ Complete |
| FR-007 | FR-007-CON-2 | TC-051 | ✅ Complete |
| FR-007 | FR-007-CON-3 | TC-059 | ✅ Complete |

### Non-Functional Requirement Coverage

| Non-Functional Req | Verification Method | Evidence/Test Cases | Status |
|--------------------|---------------------|---------------------|--------|
| NFR-001 | Test (metric 1: byte differences between two `make schemas` runs) | TC-056 | ✅ Complete |
| NFR-001 | Demonstration (metric 2: network reads during `make schemas-check` and `make test`) | TC-057 | ✅ Complete |
| NFR-001 | Benchmark (metric 3: wall time of `make schemas-check`) | TC-058 | ✅ Complete |

## Test Case Summary

| Test ID | Title | Type | Priority | Traces To | Status |
|---------|-------|------|----------|-----------|--------|
| TC-003 | a ``master-requirements`` artifact_type is declared with a frontmatter_schema_ref and a body_extraction carrying assert facets (`test_fr003_ac1_master_requirements_archetype_registered`) | Unit | P0 | FR-003-AC-1 | ✅ |
| TC-004 | TC-004): the master-requirements frontmatter schema requires type/name/org/component_type, does NOT require id/title, and constrains component_type to kebab-case ``^[a-z][a-z0-9-]*$`` (`test_fr003_ac2_master_requirements_frontmatter_schema_shape`) | Unit | P0 | FR-003-AC-2 | ✅ |
| TC-005 | every archetype declares ``body_extraction`` with asserts and declares none of ``template_ref`` / ``required_sections`` / ``variants`` (`test_fr002_ac1_unified_shape_no_retired_fields`) | Unit | P0 | FR-002-AC-1 | ✅ |
| TC-006 | templates/ is removed and no archetype references one (`test_fr002_ac1_no_template_dir_or_refs`) | Unit | P0 | FR-002-AC-1 | ✅ |
| TC-007 | declared section headings are unique per level (`test_fr002_ac4_headings_unique_per_level`) | Unit | P0 | FR-002-AC-4 | ✅ |
| TC-008 | Each archetype ships an authoring skeleton carrying its required headings (`test_fr002_skeleton_exists_and_has_required_headings`) | Unit | P0 | FR-002-AC-5 | ✅ |
| TC-009 | I1): the manifest asserts are consistent with / derived from the skeleton — every asserted heading exists in the skeleton at the asserted level, every asserted table's header row is present in the skeleton, and every asserted id_p (`test_fr002_ac6_asserts_derived_from_skeleton`) | Unit | P0 | FR-002-AC-6 | ✅ |
| TC-010 | I2): the skeleton's heading set and literal table header rows match the archetype's asserts exactly — a diff in either direction fails. Forward: skeleton ⊇ asserts (covered by AC-6). Reverse: every *asserted-level* skeleton headin (`test_fr002_ac7_literal_consistency_both_directions`) | Unit | P0 | FR-002-AC-7 | ✅ |
| TC-011 | I3): heading-presence locators are distinguished from ``section_body`` locators; the skeleton supplies substantive (non-empty, non-placeholder) body for every ``section_body``-asserted section (`test_fr002_ac8_locator_kinds_and_substantive_bodies`) | Unit | P0 | FR-002-AC-8 | ✅ |
| TC-012 | a filled skeleton passes validate_document. Skips when the installed quire wheel predates the markdown-default validator (FR-032); build/install a local quire-rs >=0.3.6 wheel to exercise it (`test_it002_ac1_skeleton_validates`) | Unit | P0 | FR-002-AC-5 | ✅ |
| TC-013 | deleting a section, breaking AC columns, breaking an AC id, and duplicating a heading each fail validation with the expected reason (`test_it002_ac2_fr_mutations_fail`) | Unit | P0 | FR-002-AC-2 | ✅ |
| TC-014 | StR binding criteria are addressable rows under `## Validation Criteria`. The heading and the `Validation` column are deliberately NOT renamed to the FR spelling: ISO/IEC/IEEE 29148 validates a stakeholder requirement against the  (`test_str_validation_criteria_table_is_binding`) | Unit | P0 | FR-002-AC-1 | ✅ |
| TC-015 | NFR's AC section stays optional but takes the FR table shape when present. A *measurable* NFR's criteria are its `Metric \| Target \| Threshold \| Method` rows and it omits the section; a *policy* NFR authors the table. What is no (`test_nfr_acceptance_criteria_is_absent_or_well_formed`) | Unit | P0 | FR-002-AC-1 | ✅ |
| TC-016 | extract over the conformant skeleton yields a record whose fields match the archetype's body_extraction (validate + extract share one declaration) (`test_it002_ac3_extract_yields_record`) | Unit | P0 | FR-002-AC-1 | ✅ |
| TC-017 | . A verb with no description is a verb nobody can use correctly, and a category outside the declared seven is a typo that would silently create an eighth (`test_fr004_ac1_every_edge_type_has_a_description_and_known_category`) | Unit | P0 | FR-004-AC-1 | ✅ |
| TC-018 | . An inverse label declared by two forward verbs resolves first-wins with a diagnostic (quire-rs FR-041-AC-3), so which verb it normalizes onto depends on declaration order. That is designed. What is *not* designed is a new collis (`test_fr004_ac2_shared_inverse_labels_are_the_recorded_set`) | Unit | P0 | FR-004-AC-2 | ✅ |
| TC-019 | . Deliberately the opposite of the invariant it is tempting to assert. quire-rs FR-041-AC-2 type-allows an edge whose verb is a declared inverse label "even when the label is absent from ``edge_types``" — so requiring every invers (`test_fr004_ac3_inverse_labels_need_not_be_declared_verbs`) | Unit | P0 | FR-004-AC-3 | ✅ |
| TC-020 |  (`test_fr004_ac4_every_role_has_a_description`) | Unit | P0 | FR-004-AC-4 | ✅ |
| TC-021 | the manifest declares both vocabulary registries, and an `edge_types` entry that loses its `category` costs the module every archetype under `Registry.load_from`, with an unmutated control proving the load is real (`test_fr004_ac5_the_vocabulary_is_declared_and_a_broken_entry_is_refused`) | Unit | P0 | FR-004-AC-5 | ✅ |
| TC-039 | Every locator output of every artifact type is a property of its model, and every model property traces to a locator, a frontmatter key, or a `mappings.yaml` entry (FR-005-CON-1) | Unit | P0 | FR-005-CON-1 | ✅ |
| TC-040 | Every property of every emitted object schema is typed and constrained, or its description carries `free text:` and a reason (FR-005-AC-3) | Unit | P0 | FR-005-AC-3, FR-005-CON-1 | ✅ |
| TC-041 | The ten exported schemas exist with the 2020-12 `$schema` and the versioned `$id`; every `$ref` in the bundle resolves to a shipped sibling or to the semantic-core 0.3.0 bundle vendored by the quire wheel, offline (FR-005-AC-1, AC-2) | Unit | P0 | FR-005-AC-1, FR-005-AC-2, FR-005-CON-2 | ✅ |
| TC-042 | `make schemas-check` exits 0 on the committed tree and non-zero naming the file after a one-byte edit to an emitted schema (FR-005-AC-5) | Integration | P0 | FR-005-AC-5 | ✅ |
| TC-043 | No emitted property is an execution-result field and the `TC` model's description says results are not modelled (FR-005-AC-6) | Static | P1 | FR-005-AC-6, FR-005-CON-4 | ✅ |
| TC-044 | For each of the ten skeletons the reference mapping yields the committed `examples/<type>.record.json` and the record validates against `schemas/<Model>.json` (FR-005-AC-4, FR-007-AC-2) | Snapshot | P0 | FR-005-AC-4, FR-007-AC-2 | ✅ |
| TC-045 | An extra property, a wrong-prefix row id, a removed required section, a duplicated H2, a malformed `## Story`, a typed table with a header and zero rows (`minItems` boundary), a `line: 0` (`minimum` boundary), a CRLF document, an empty `Verification` cell, and a `status` outside its pattern, and a row id repeated within one table each fail — the schema naming the path, the mapping naming the line, every failure in a document reported together, and no partial record (FR-005-AC-4, FR-007-AC-6; SR-003 FND-002/003) | Unit | P0 | FR-005-AC-4, FR-007-AC-6 | ✅ |
| TC-046 | The manifest's `semantic` block key set is exactly the nine declared keys with the declared values; the block and the `data_schema` references add no required key at the manifest root or on an `ArtifactTypeEntry`; and the legacy-manifest fixture (block and references removed) is this manifest with exactly those removals and loads under quire with the same eleven archetypes (FR-006-AC-1, AC-7) | Unit | P0 | FR-006-AC-1, FR-006-AC-7, FR-006-CON-1 | ✅ |
| TC-047 | Every exported artifact type carries a `{schema, digest}` reference to an existing file whose SHA-256 equals the digest; `exports` equals the referencing set; no inline `data_schema` remains; a one-byte schema edit fails naming the type and both digests (FR-006-AC-2, AC-5) | Unit | P0 | FR-006-AC-2, FR-006-AC-5, FR-006-CON-2 | ✅ |
| TC-048 | On `quire ^0.47.1`, `Registry.load_from` lists all eleven archetypes with the `semantic` block and the ten `data_schema` references present, and `validate_document` passes every skeleton — the block breaks no consumer (FR-006-AC-3) | Integration | P0 | FR-006-AC-3 | ✅ |
| TC-050 | Each pre-change skeleton committed at 3d87196 maps to a record that validates against the new schema; no table header, heading, or column order changed (FR-007-AC-5) | Snapshot | P0 | FR-007-AC-5, FR-007-CON-1 | ✅ |
| TC-051 | The FR skeleton's `## Invariants` clause maps to a `ClauseRef` with `language: ocl` and the heading as `clauseId`; `sourceSpan` is present with a caller `sourceIdentity` and absent without one; the `invariantsText` entry equals the fence body byte-for-byte; a non-identifier heading, a `tla` fence, a second fence under one heading, a repeated `clauseId`, and an unowned fence each fail naming the line; a prose `## Invariants` leaves `invariants` absent without failing; no module code parses the clause (FR-007-AC-4) | Unit | P0 | FR-007-AC-4, FR-007-CON-2 | ✅ |
| TC-052 | `mappings.yaml` validates against `mappings.schema.json`, names every model property exactly once with one of the eight mapping kinds, names no undeclared property, matches locator `assert.columns` on tables, and records `authority`, `round_trip`, per-property `lossless`, and the dropped frontmatter keys (FR-007-AC-1, AC-7) | Unit | P0 | FR-007-AC-1, FR-007-AC-7 | ✅ |
| TC-053 | The FR skeleton's AC rows split `Test (TC-001)` into `method` and `testRefs`, and its constraint row carries `type: Security` (FR-007-AC-3) | Unit | P0 | FR-007-AC-3 | ✅ |
| TC-054 | The TypeSpec package pins `@typespec/compiler` 1.15.0, `@typespec/json-schema` 1.15.0, and `@agent-ix/semantic-core` 0.3.0 with a committed lockfile, no `file:`/`link:` reference, and no `.npmrc` in the repository (FR-005-CON-3) | Static | P1 | FR-005-CON-3 | ✅ |
| TC-055 | `quoin module install path:<module root>` on the published quoin (0.23.1) installs the module with no diagnostic, so the block is inert to every quoin a user can install today; output recorded verbatim and the previous registry version restored (FR-006-AC-6) | Manual | P1 | FR-006-AC-6 | ✅ |
| TC-064 | quoin main at 3e842ce resolves `semantic.exports` and `data_schema` against `object_types` only (`src/semantic/manifest.ts:175-186,258`), so an artifact-type export yields `semantic.unknown-export` and `semantic.export-without-schema`; a source reading, because no quoin carrying it is published (agent-ix/quoin#336) (FR-006-AC-9) | Manual | P2 | FR-006-AC-9 | ✅ |
| TC-056 | Two consecutive `make schemas` runs on one tree produce byte-identical bundles for every emitted file (NFR-001 metric 1) | Property | P1 | NFR-001 (metric 1) | ✅ |
| TC-057 | `make schemas-check` and `make test` exit 0 with the network namespace disabled after `npm ci` and `poetry install` (NFR-001 metric 2) | Manual | P2 | NFR-001 (metric 2) | ✅ |
| TC-058 | `make schemas-check` completes within 30 s on the reference machine (NFR-001 metric 3) | Benchmark | P3 | NFR-001 (metric 3) | ✅ |
| TC-059 | No file in the module or its test support writes a Markdown document, and the reference mapping opens every document read-only — enumerated over the tree, not sampled (FR-007-CON-3) | Static | P2 | FR-007-CON-3 | ✅ |
| TC-060 | Every emitted object schema declares its properties inline (no `allOf`/`oneOf`/`anyOf`/`$ref` at the object's top level except a nullable scalar's `anyOf`), and the Python `jsonschema` validator accepts every golden record and rejects every TC-045 mutation (FR-005-AC-8) | Unit | P0 | FR-005-AC-8 | ✅ |
| TC-061 | The emitted schema file set equals `toolchain.json`'s `files`, and the digest recomputed over those bytes equals the recorded digest, with no toolchain run (FR-005-AC-7) | Unit | P0 | FR-005-AC-7 | ✅ |
| TC-062 | The sdist/wheel `include` list and the npm `files` list name every shipped payload entry and no TypeSpec toolchain file; a built sdist and a packed npm tarball carry the same payload entry set (FR-005-AC-9) | Integration | P1 | FR-005-AC-9 | ✅ |
| TC-063 | A copy of the module with one `data_schema.digest` altered by one hex digit loads with that archetype absent from `Registry.archetype_names()` — the digest binding shipped in quire-rs v0.47.0/0.47.1 (agent-ix/quire-rs#390) and drops the archetype rather than raising; a control proves the unmodified copy still loads it (FR-006-AC-8) | Integration | P0 | FR-006-AC-8 | ✅ |
