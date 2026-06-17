---
id: IT-002
title: "Direct-markdown validate + extract roundtrip"
type: IT
relationships:
  - target: "ix://agent-ix/spec-artifacts-iso/FR-002"
    type: "verifies"
  - target: "ix://agent-ix/quire-rs/spec/functional/FR-032"
    type: "verifies"
---
# [IT-002] Direct-markdown validate + extract roundtrip

## Objective

Verify that, for each ISO archetype, an authored markdown artifact (no render
step) validates structurally via quire-rs `validate_document` and extracts to the
expected data record via the same `body_extraction` — proving validate and
extract share one declaration, and that the documented mutations each fail with
the expected line-numbered diagnostic.

## Target Integration

The system under test is the quire-rs validation engine consuming this Module.
The integration exercised is `Registry::load_module` against `spec_artifacts_iso/`
followed by `validate_document(archetype, doc_text)` and `extract` over the same
artifact, so that the Module's `body_extraction` asserts drive both validation and
extraction.

## Preconditions

A build of quire-rs exposing `Registry::load_module`, `validate_document`, and
extraction is available, and this Module's `spec_artifacts_iso/` source tree
(manifest, schemas, skeletons) is present so the eight archetypes can be loaded.

## Inputs

For each archetype, its authoring skeleton filled with substantive content (a
conformant artifact), plus three deliberately mutated copies (a deleted required
section, a changed Acceptance-Criteria column header, and a renumbered AC id) and
one copy carrying a duplicate heading at the same level.

## Test Procedure

Each step performs one discrete action and has its own success criterion.

1. Load this Module via quire-rs `Registry::load_module` against `spec_artifacts_iso/`.
   - IT-002-SC-01: the Module loads with its eight archetypes registered.
2. For each archetype, take its authoring skeleton filled with substantive
   content and run `validate_document(archetype, doc_text)`.
   - IT-002-SC-02: `is_valid == true` with no errors for every archetype.
3. Mutate the artifact three ways and re-validate, asserting a line-numbered
   failure each time: (a) delete a required section (reason `missing`); (b) change
   an Acceptance-Criteria table column header (reason `assert`); (c) renumber an AC
   id to a non-matching prefix/gap (reason `assert`, via `{id}` interpolation).
   - IT-002-SC-03: each mutation fails with the stated reason and a line number.
4. Introduce a duplicate heading at the same level and re-validate.
   - IT-002-SC-04: validation fails with reason `duplicate-heading`.
5. Run `extract` over the conformant artifact for each archetype.
   - IT-002-SC-05: the yielded record matches the archetype's `body_extraction` fields.

## Expected Results

Every conformant skeleton validates with no errors; each documented mutation
fails with its expected reason and a line number; and extraction over the
conformant artifact yields the record the archetype's `body_extraction` declares —
demonstrating that validate and extract share one declaration.

## Acceptance Criteria

| ID | Criteria |
|----|----------|
| IT-002-AC-1 | Step 2 passes for all eight archetypes |
| IT-002-AC-2 | Each mutation in steps 3-4 fails with the expected reason and a line number |
| IT-002-AC-3 | Step 5 extraction yields the expected record for each archetype (validate and extract use the same `body_extraction`) |
