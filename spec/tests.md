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

## Requirements Traceability

### Functional Requirement Coverage

| Functional Req | Acceptance Criteria | Test Cases | Coverage Status |
|----------------|---------------------|------------|-----------------|
| FR-001 | FR-001-AC-1 | TC-001, TC-022, TC-023, TC-024, TC-025, TC-026, TC-027, TC-028, TC-029, TC-030, TC-031, TC-032, TC-033, TC-034 | ✅ Complete |
| FR-001 | FR-001-AC-2 | — | 🚧 Pending |
| FR-001 | FR-001-AC-3 | — | 🚧 Pending |
| FR-001 | FR-001-AC-4 | — | 🚧 Pending |
| FR-002 | FR-002-AC-1 | TC-002, TC-005, TC-006, TC-014, TC-015, TC-016 | ✅ Complete |
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

## Test Case Summary

| Test ID | Title | Type | Priority | Traces To | Status |
|---------|-------|------|----------|-----------|--------|
| TC-001 | the manifest validates against the FR-035 schema. FR-001 CR-002: neither the missing-library nor the missing-schema branch skips any more. A gate that reports "passed" because it could not run is the failure mode this whole ticket (`test_manifest_validates_against_fr035_schema`) | Unit | P0 | FR-001-AC-1 | ✅ |
| TC-002 | the bundled FR-035 schema must REJECT ``template_ref`` on an ArtifactTypeEntry (render is gone; additionalProperties:false → error) (`test_fr002_schema_rejects_template_ref_on_artifact_type`) | Unit | P0 | FR-002-AC-1 | ✅ |
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
| TC-021 | . The FR-035 gate covers the whole manifest; this asserts the vocabulary is *present* when it passes, so a future edit that drops `edge_types` entirely cannot slip through a green schema run (`test_fr004_ac5_vocabulary_validates_under_the_module_manifest_schema`) | Unit | P0 | FR-004-AC-5 | ✅ |
| TC-022 | a well-formed `required_relations` and `acyclic_edges` declaration validates (`test_tc_schema_014_required_relations_is_accepted`) | Unit | P0 | FR-001-AC-1 | ✅ |
| TC-023 | a declaration that cannot be executed is rejected by the schema, not discovered as a corpus-wide false alarm (`test_tc_schema_015_unexecutable_relations_are_rejected`) | Unit | P0 | FR-001-AC-1 | ✅ |
| TC-024 | `to` is the one field where empty carries meaning rather than being a defect (`test_tc_schema_016_empty_to_means_any_target`) | Unit | P0 | FR-001-AC-1 | ✅ |
| TC-025 | a blank verb in `acyclic_edges` is rejected (`test_tc_schema_017_blank_acyclic_verb_is_rejected`) | Unit | P0 | FR-001-AC-1 | ✅ |
| TC-026 | a well-formed declaration validates (`test_tc_schema_018_vocabulary_coverage_is_accepted`) | Unit | P0 | FR-001-AC-1 | ✅ |
| TC-027 | the vocabulary cannot be restated here (`test_tc_schema_019_the_schema_declares_no_values_key`) | Unit | P0 | FR-001-AC-1 | ✅ |
| TC-028 | a declaration that cannot run is rejected (`test_tc_schema_020_malformed_coverage_is_rejected`) | Unit | P0 | FR-001-AC-1 | ✅ |
| TC-029 | a well-formed declaration validates (`test_tc_schema_021_combinatorial_source_is_accepted`) | Unit | P0 | FR-001-AC-1 | ✅ |
| TC-030 | `strength: 0` cannot be declared (`test_tc_schema_022_zero_strength_is_rejected`) | Unit | P0 | FR-001-AC-1 | ✅ |
| TC-031 | a malformed declaration fails at load (`test_tc_schema_023_malformed_combinatorial_is_rejected`) | Unit | P0 | FR-001-AC-1 | ✅ |
| TC-032 | a well-formed declaration validates (`test_tc_schema_024_implements_marker_forms_are_accepted`) | Unit | P0 | FR-001-AC-1 | ✅ |
| TC-033 | scope and evidence cannot be one list (`test_tc_schema_025_implements_is_a_separate_list`) | Unit | P0 | FR-001-AC-1 | ✅ |
| TC-034 | a malformed form fails at load (`test_tc_schema_026_malformed_implements_marker_is_rejected`) | Unit | P0 | FR-001-AC-1 | ✅ |
