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

## Scenario

For each ISO archetype, an authored markdown artifact (no render step) validates
structurally via quire-rs `validate_document` and extracts to the expected data
record via the same `body_extraction` — proving validate and extract share one
declaration.

## Steps

1. Load this module via quire-rs `Registry::load_module` against `spec_artifacts_iso/`.
2. For each archetype, take its authoring skeleton filled with substantive content (a conformant artifact).
3. Run `validate_document(archetype, doc_text)`; assert `is_valid == true`, no errors.
4. Mutate the artifact three ways and re-validate, asserting a line-numbered failure each time:
   a. delete a required section (reason `missing`);
   b. change an Acceptance-Criteria table column header (reason `assert`);
   c. renumber an AC id to a non-matching prefix/gap (reason `assert`, via `{id}` interpolation).
5. Introduce a duplicate heading at the same level; assert reason `duplicate-heading`.
6. Run `extract` over the conformant artifact; assert the yielded record matches the archetype's `body_extraction` fields.

## Acceptance Criteria

| ID | Criteria |
|----|----------|
| IT-002-AC-1 | Step 3 passes for all eight archetypes |
| IT-002-AC-2 | Each mutation in steps 4-5 fails with the expected reason and a line number |
| IT-002-AC-3 | Step 6 extraction yields the expected record for each archetype (validate and extract use the same `body_extraction`) |
