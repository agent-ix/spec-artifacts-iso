---
type: TestMatrix
id: TM-001
title: "Test Matrix"
---
# Test Matrix

## Overview

Maps every acceptance criterion to the test that backs it.

Two rows depend on a release outside this repository and cannot be green
here until it lands. TC-055 and TC-064 are manual because the
published quoin carries no semantic-block reader: the refusal
agent-ix/quoin#336 tracks can be read out of quoin main's source, not run. TC-057 is the manual offline gate that
no CI job claims. Every other row is dischargeable at the module's committed
floor.

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
| FR-002 | FR-002-AC-3 | TC-013 | ✅ Complete |
| FR-002 | FR-002-AC-4 | TC-007 | ✅ Complete |
| FR-002 | FR-002-AC-5 | TC-008, TC-012 | ✅ Complete |
| FR-002 | FR-002-AC-6 | TC-009 | ✅ Complete |
| FR-002 | FR-002-AC-7 | TC-010 | ✅ Complete |
| FR-002 | FR-002-AC-8 | TC-011 | ✅ Complete |
| FR-003 | FR-003-AC-1 | TC-003 | ✅ Complete |
| FR-003 | FR-003-AC-2 | TC-004 | ✅ Complete |
| FR-003 | FR-003-CON-2 | TC-004 | ✅ Complete |
| FR-003 | FR-003-AC-3 | — | 🚧 Pending |
| FR-003 | FR-003-AC-4 | — | 🚧 Pending |
| FR-003 | FR-003-AC-5 | — | 🚧 Pending |
| FR-003 | FR-003-AC-6 | — | 🚧 Pending |
| FR-003 | FR-003-AC-7 | — | 🚧 Pending |
| FR-003 | FR-003-AC-8 | — | 🚧 Pending |
| FR-004 | FR-004-AC-1 | TC-017 | ✅ Complete |
| FR-004 | FR-004-AC-4 | TC-020 | ✅ Complete |
| FR-004 | FR-004-AC-5 | TC-021 | ✅ Complete |
| FR-004 | FR-004-AC-6 | TC-065 | ✅ Complete |
| FR-004 | FR-004-AC-7 | TC-070 | ✅ Complete |
| FR-005 | FR-005-AC-1 | TC-041 | ✅ Complete |
| FR-005 | FR-005-AC-2 | TC-041 | ✅ Complete |
| FR-005 | FR-005-AC-3 | TC-040 | ✅ Complete |
| FR-005 | FR-005-AC-4 | TC-044, TC-045 | ✅ Complete |
| FR-005 | FR-005-AC-5 | TC-042 | ✅ Complete |
| FR-005 | FR-005-AC-6 | TC-043 | ✅ Complete |
| FR-005 | FR-005-AC-8 | TC-060 | ✅ Complete |
| FR-005 | FR-005-AC-9 | TC-062 | ✅ Complete |
| FR-005 | FR-005-CON-1 | TC-039, TC-040 | ✅ Complete |
| FR-005 | FR-005-CON-2 | TC-041 | ✅ Complete |
| FR-005 | FR-005-CON-3 | TC-054 | ✅ Complete |
| FR-005 | FR-005-CON-4 | TC-043 | ✅ Complete |
| FR-006 | FR-006-AC-1 | TC-046 | ✅ Complete |
| FR-006 | FR-006-AC-2 | TC-047 | ✅ Complete |
| FR-006 | FR-006-AC-3 | TC-048 | ✅ Complete |
| FR-006 | FR-006-AC-6 | TC-055 | 🚧 Pending (no tagged test) |
| FR-006 | FR-006-AC-9 | TC-064 | ✅ Complete (manual/inspection, not matrix-bound) |
| FR-006 | FR-006-AC-7 | TC-046 | ✅ Complete |
| FR-006 | FR-006-CON-1 | TC-046 | ✅ Complete |
| FR-006 | FR-006-CON-2 | TC-047 | 🚧 Pending (no tagged test) |
| FR-007 | FR-007-AC-1 | TC-052 | ✅ Complete |
| FR-007 | FR-007-AC-2 | TC-044 | ✅ Complete |
| FR-007 | FR-007-AC-3 | TC-053 | ✅ Complete |
| FR-007 | FR-007-AC-4 | TC-051 | ✅ Complete |
| FR-007 | FR-007-AC-6 | TC-045 | ✅ Complete |
| FR-007 | FR-007-AC-7 | TC-052 | ✅ Complete |
| FR-007 | FR-007-AC-8 | TC-069 | ✅ Complete |
| FR-007 | FR-007-CON-2 | TC-051 | ✅ Complete |
| FR-007 | FR-007-CON-3 | TC-059 | ✅ Complete (manual/inspection, not matrix-bound) |
| FR-008 | FR-008-AC-1 | TC-066 | ✅ Complete |
| FR-008 | FR-008-AC-2 | TC-067 | ✅ Complete |
| FR-008 | FR-008-AC-3 | TC-066 | ✅ Complete |
| FR-008 | FR-008-AC-4 | TC-067 | ✅ Complete |
| FR-008 | FR-008-AC-5 | TC-068 | ✅ Complete |
| FR-008 | FR-008-AC-6 | TC-068 | ✅ Complete |
| FR-008 | FR-008-AC-7 | TC-068 | ✅ Complete |
| FR-008 | FR-008-AC-8 | TC-066 | ✅ Complete (manual/inspection, not matrix-bound) |
| FR-009 | FR-009-AC-1 | TC-071 | ✅ Complete |
| FR-009 | FR-009-AC-2 | TC-072 | ✅ Complete |
| FR-009 | FR-009-AC-3 | TC-071 | ✅ Complete |
| FR-009 | FR-009-AC-4 | TC-072 | ✅ Complete |
| FR-009 | FR-009-AC-5 | TC-073 | ✅ Complete |
| FR-009 | FR-009-AC-6 | TC-073 | ✅ Complete |
| FR-009 | FR-009-AC-7 | TC-073 | ✅ Complete |
| FR-009 | FR-009-AC-8 | TC-071 | ✅ Complete (manual/inspection, not matrix-bound) |
| FR-009 | FR-009-AC-9 | TC-074 | ✅ Complete |
| FR-009 | FR-009-AC-10 | TC-075 | ✅ Complete |
| FR-009 | FR-009-AC-11 | TC-077 | ✅ Complete |
| FR-009 | FR-009-AC-12 | TC-077 | ✅ Complete |
| FR-009 | FR-009-AC-13 | TC-076 | ✅ Complete |
| FR-009 | FR-009-AC-14 | TC-078 | ✅ Complete |

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
| TC-004 | TC-004): the master-requirements frontmatter schema requires type/name/org/component_type, does NOT require id/title, and constrains component_type to kebab-case ``^[a-z][a-z0-9-]*$`` (`test_fr003_ac2_master_requirements_frontmatter_schema_shape`) | Unit | P0 | FR-003-AC-2, FR-003-CON-2 | ✅ |
| TC-005 | every archetype declares ``body_extraction`` with asserts and declares none of ``template_ref`` / ``required_sections`` / ``variants`` (`test_fr002_ac1_unified_shape_no_retired_fields`) | Unit | P0 | FR-002-AC-1 | ✅ |
| TC-006 | templates/ is removed and no archetype references one (`test_fr002_ac1_no_template_dir_or_refs`) | Unit | P0 | FR-002-AC-1 | ✅ |
| TC-007 | declared section headings are unique per level (`test_fr002_ac4_headings_unique_per_level`) | Unit | P0 | FR-002-AC-4 | ✅ |
| TC-008 | Each archetype ships an authoring skeleton carrying its required headings (`test_fr002_skeleton_exists_and_has_required_headings`) | Unit | P0 | FR-002-AC-5 | ✅ |
| TC-009 | I1): the manifest asserts are consistent with / derived from the skeleton — every asserted heading exists in the skeleton at the asserted level, every asserted table's header row is present in the skeleton, and every asserted id_p (`test_fr002_ac6_asserts_derived_from_skeleton`) | Unit | P0 | FR-002-AC-6 | ✅ |
| TC-010 | I2): the skeleton's heading set and literal table header rows match the archetype's asserts exactly — a diff in either direction fails. Forward: skeleton ⊇ asserts (covered by AC-6). Reverse: every *asserted-level* skeleton headin (`test_fr002_ac7_literal_consistency_both_directions`) | Unit | P0 | FR-002-AC-7 | ✅ |
| TC-011 | I3): heading-presence locators are distinguished from ``section_body`` locators; the skeleton supplies substantive (non-empty, non-placeholder) body for every ``section_body``-asserted section (`test_fr002_ac8_locator_kinds_and_substantive_bodies`) | Unit | P0 | FR-002-AC-8 | ✅ |
| TC-012 | a filled skeleton passes validate_document. Skips when the installed quire wheel predates the markdown-default validator (FR-032); build/install a local quire-rs wheel to exercise it (`test_it002_ac1_skeleton_validates`) | Unit | P0 | FR-002-AC-5 | ✅ |
| TC-013 | deleting a section, breaking AC columns, breaking an AC id, and duplicating a heading each fail validation with the expected reason (`test_it002_ac2_fr_mutations_fail`) | Unit | P0 | FR-002-AC-2, FR-002-AC-3 | ✅ |
| TC-014 | StR binding criteria are addressable rows under `## Validation Criteria`. The heading and the `Validation` column are deliberately NOT renamed to the FR spelling: ISO/IEC/IEEE 29148 validates a stakeholder requirement against the  (`test_str_validation_criteria_table_is_binding`) | Unit | P0 | FR-002-AC-1 | ✅ |
| TC-015 | NFR's AC section stays optional but takes the FR table shape when present. A *measurable* NFR's criteria are its `Metric \| Target \| Threshold \| Method` rows and it omits the section; a *policy* NFR authors the table. What is no (`test_nfr_acceptance_criteria_is_absent_or_well_formed`) | Unit | P0 | FR-002-AC-1 | ✅ |
| TC-016 | extract over the conformant skeleton yields a record whose fields match the archetype's body_extraction (validate + extract share one declaration) (`test_it002_ac3_extract_yields_record`) | Unit | P0 | FR-002-AC-1 | ✅ |
| TC-017 | . A verb with no description is a verb nobody can use correctly, and a category outside the declared seven is a typo that would silently create an eighth (`test_fr004_ac1_every_edge_type_has_a_description_and_known_category`) | Unit | P0 | FR-004-AC-1 | ✅ |
| TC-020 |  (`test_fr004_ac4_every_role_has_a_description`) | Unit | P0 | FR-004-AC-4 | ✅ |
| TC-021 | the manifest declares both vocabulary registries, and an `edge_types` entry that loses its `category` costs the module every archetype under `Registry.load_from`, with an unmutated control proving the load is real (`test_fr004_ac5_the_vocabulary_is_declared_and_a_broken_entry_is_refused`) | Unit | P0 | FR-004-AC-5 | ✅ |
| TC-039 | Every locator output of every artifact type is a property of its model, and every model property traces to a locator, a frontmatter key, or a `mappings.yaml` entry (FR-005-CON-1) | Unit | P0 | FR-005-CON-1 | ✅ |
| TC-040 | Every property of every emitted object schema is typed and constrained, or its description carries `free text:` and a reason (FR-005-AC-3) | Unit | P0 | FR-005-AC-3, FR-005-CON-1 | ✅ |
| TC-041 | The nine exported schemas exist with the 2020-12 `$schema` and the `$id`; every `$ref` in the bundle resolves to a shipped sibling or to the semantic-core bundle vendored by the quire wheel, offline (FR-005-AC-1, AC-2) | Unit | P0 | FR-005-AC-1, FR-005-AC-2, FR-005-CON-2 | ✅ |
| TC-042 | `make schemas-check` exits 0 on the committed tree and non-zero naming the file after a one-byte edit to an emitted schema (FR-005-AC-5) | Integration | P0 | FR-005-AC-5 | ✅ |
| TC-043 | No emitted property is an execution-result field and the `TC` model's description says results are not modelled (FR-005-AC-6) | Static | P1 | FR-005-AC-6, FR-005-CON-4 | ✅ |
| TC-044 | For each of the nine skeletons the reference mapping yields the committed `examples/<type>.record.json` and the record validates against `schemas/<Model>.json` (FR-005-AC-4, FR-007-AC-2) | Snapshot | P0 | FR-005-AC-4, FR-007-AC-2 | ✅ |
| TC-045 | An extra property, a wrong-prefix row id, a removed required section, a duplicated H2, a malformed `## Story`, a typed table with a header and zero rows (`minItems` boundary), a `line: 0` (`minimum` boundary), a CRLF document, an empty `Verification` cell, and a `status` outside its pattern, and a row id repeated within one table each fail — the schema naming the path, the mapping naming the line, every failure in a document reported together, and no partial record (FR-005-AC-4, FR-007-AC-6; SR-003 FND-002/003) | Unit | P0 | FR-005-AC-4, FR-007-AC-6 | ✅ |
| TC-046 | The manifest's `semantic` block key set is exactly the eight declared keys with the declared values; the block and the `data_schema` references add no required key at the manifest root or on an `ArtifactTypeEntry`; and the legacy form derived from it (block and references removed) is this manifest with exactly those removals and loads under quire with the same nine archetypes (FR-006-AC-1, AC-7) | Unit | P0 | FR-006-AC-1, FR-006-AC-7, FR-006-CON-1 | ✅ |
| TC-047 | Every exported artifact type carries a `{schema}` reference to an existing file; `exports` equals the referencing set; no inline `data_schema` remains (FR-006-AC-2, AC-5) | Unit | P0 | FR-006-AC-2, FR-006-AC-5, FR-006-CON-2 | ✅ |
| TC-048 | `Registry.load_from` lists all nine archetypes with the `semantic` block and the nine `data_schema` references present, and `validate_document` passes every skeleton — the block breaks no consumer (FR-006-AC-3) | Integration | P0 | FR-006-AC-3 | ✅ |
| TC-051 | The FR skeleton's `## Invariants` clause maps to a `ClauseRef` with `language: ocl` and the heading as `clauseId`; `sourceSpan` is present with a caller `sourceIdentity` and absent without one; the `invariantsText` entry equals the fence body byte-for-byte; a non-identifier heading, a `tla` fence, a second fence under one heading, a repeated `clauseId`, and an unowned fence each fail naming the line; a prose `## Invariants` leaves `invariants` absent without failing; no module code parses the clause (FR-007-AC-4) | Unit | P0 | FR-007-AC-4, FR-007-CON-2 | ✅ |
| TC-052 | `mappings.yaml` validates against `mappings.schema.json`, names every model property exactly once with one of the eight mapping kinds, names no undeclared property, matches locator `assert.columns` on tables, and records `authority`, `round_trip`, per-property `lossless`, and the dropped frontmatter keys (FR-007-AC-1, AC-7) | Unit | P0 | FR-007-AC-1, FR-007-AC-7 | ✅ |
| TC-053 | The FR skeleton's AC rows map to a plain method cell (`method` only, no `annotation`, `testRefs: []`), its constraint row carries `type: Security`, and the split still parses an annotated cell (`Test (TC-035, TC-036)`) for a caller that authors one (FR-007-AC-3) | Unit | P0 | FR-007-AC-3 | ✅ |
| TC-054 | The TypeSpec package carries a committed lockfile, no `file:`/`link:` reference, and no `.npmrc` in the repository (FR-005-CON-3) | Static | P1 | FR-005-CON-3 | ✅ |
| TC-055 | `quoin module install path:<module root>` on the published quoin installs the module with no diagnostic, so the block is inert to every quoin a user can install today; output recorded verbatim and the previous registry version restored (FR-006-AC-6) | Manual | P1 | FR-006-AC-6 | ✅ |
| TC-064 | quoin main resolves `semantic.exports` and `data_schema` against `object_types` only (`src/semantic/manifest.ts:175-186,258`), so an artifact-type export yields `semantic.unknown-export` and `semantic.export-without-schema`; a source reading, because no quoin carrying it is published (agent-ix/quoin#336) (FR-006-AC-9) | Manual | P2 | FR-006-AC-9 | ✅ |
| TC-065 | `specifies` declares inverse `specified_by` (`test_fr004_ac6_specifies_declares_the_specified_by_inverse`) | Unit | P0 | FR-004-AC-6 | ✅ |
| TC-070 | A single NFR file with a `mitigates` relationship validates with no `disallowed-edge-type`; the same file with an unrelated disallowed verb still warns, so the allowance is a membership check and not a disabled one (`test_fr004_ac7_nfr_allows_a_mitigates_edge`) | Integration | P1 | FR-004-AC-7 | ✅ |
| TC-066 | The `FR`, `NFR`, `StR` and `US` frontmatter schemas each declare an optional inline `criticality` enum `low`, `medium`, `high` with no shared enumeration file; the projected record schemas carry it as optional; neither schema family gives it a `default` (`test_criticality::test_fr008_ac1_*`, `test_fr008_ac3_*`, `test_fr008_ac8_*`) | Integration | P1 | FR-008-AC-1, FR-008-AC-3, FR-008-AC-8 | ✅ |
| TC-067 | Each enumerated `criticality` value validates for all four archetypes, and a document omitting it validates (`test_criticality::test_fr008_ac2_*`, `test_fr008_ac4_*`) | Integration | P1 | FR-008-AC-2, FR-008-AC-4 | ✅ |
| TC-068 | `criticality` values `critical`, `High` and `""` fail `quire validate` for all four archetypes with a diagnostic naming the field (`test_criticality::test_fr008_invalid_values_*`) | Integration | P1 | FR-008-AC-5, FR-008-AC-6, FR-008-AC-7 | ✅ |
| TC-069 | `mappings.yaml` maps `criticality` as written for all four archetypes, and a document without the key yields a record without it (`test_criticality::test_fr007_ac8_*`) | Integration | P1 | FR-007-AC-8 | ✅ |
| TC-071 | `FR`, `NFR`, `StR` and `US` frontmatter schemas each declare optional `software_safety_class` (inline enum `class-1`, `class-2`, `class-3`) with non-empty assigner and rationale, none required and none defaulted; the projected record schemas carry the three as optional (`test_software_safety_class::test_fr009_ac1_*`, `test_fr009_ac3_*`, `test_fr009_ac8_*`) | Integration | P1 | FR-009-AC-1, FR-009-AC-3, FR-009-AC-8 | ✅ |
| TC-072 | Each enumerated class with assigner and rationale validates for all four archetypes, and a document omitting all three validates and maps to a record without them (`test_fr009_ac2_*`, `test_fr009_ac4_*`) | Integration | P1 | FR-009-AC-2, FR-009-AC-4 | ✅ |
| TC-073 | `class-9`, `Class-1` and `""` fail `quire validate` for all four archetypes with a diagnostic naming the field (`test_fr009_invalid_class_values_*`) | Integration | P1 | FR-009-AC-5, FR-009-AC-6, FR-009-AC-7 | ✅ |
| TC-074 | `mappings.yaml` maps the three class keys as written for all four archetypes (`test_fr009_ac9_*`) | Integration | P1 | FR-009-AC-9 | ✅ |
| TC-075 | A document carrying `criticality` and a class, in either combination, validates (`test_fr009_ac10_*`) | Integration | P1 | FR-009-AC-10 | ✅ |
| TC-076 | A class without assigner or rationale, an empty assigner or rationale, or an assigner or rationale without a class fails `quire validate` naming the field (`test_fr009_ac13_*`) | Integration | P1 | FR-009-AC-13 | ✅ |
| TC-077 | Schemas, mappings and skeletons keep class and `criticality` separate, and no skeleton carries a class field (`test_fr009_ac11_*`, `test_fr009_skeletons_carry_none_of_the_fields`) | Integration | P1 | FR-009-AC-11, FR-009-AC-12 | ✅ |
| TC-078 | The manifest declares the `software_safety_class` `carried_fields` entry for `StR`, `US`, `FR`, `NFR` and none for `criticality`; the coverage report carries a stated class as written under `carried`, carries none for a document stating none, and exposes the ordered vocabulary as `carried_vocabulary` (`test_fr009_ac14_*`) | Integration | P1 | FR-009-AC-14 | ✅ |
| TC-056 | Two consecutive `make schemas` runs on one tree produce byte-identical bundles for every emitted file (NFR-001 metric 1) | Property | P1 | NFR-001 (metric 1) | ✅ |
| TC-057 | `make schemas-check` and `make test` exit 0 with the network namespace disabled after `npm ci` and `poetry install` (NFR-001 metric 2) | Manual | P2 | NFR-001 (metric 2) | ✅ |
| TC-058 | `make schemas-check` completes within 30 s on the reference machine (NFR-001 metric 3) | Benchmark | P3 | NFR-001 (metric 3) | ✅ |
| TC-059 | No file in the module or its test support writes a Markdown document, and the reference mapping opens every document read-only — enumerated over the tree, not sampled (FR-007-CON-3) | Static | P2 | FR-007-CON-3 | ✅ |
| TC-060 | Every emitted object schema declares its properties inline (no `allOf`/`oneOf`/`anyOf`/`$ref` at the object's top level except a nullable scalar's `anyOf`), and the Python `jsonschema` validator accepts every golden record and rejects every TC-045 mutation (FR-005-AC-8) | Unit | P0 | FR-005-AC-8 | ✅ |
| TC-062 | The sdist/wheel `include` list and the npm `files` list name every shipped payload entry and no TypeSpec toolchain file; a built sdist and a packed npm tarball carry the same payload entry set (FR-005-AC-9) | Integration | P1 | FR-005-AC-9 | ✅ |
