---
id: IT-003
title: "Master requirements spec validates end-to-end"
type: IT
relationships:
  - target: "ix://agent-ix/spec-artifacts-iso/FR-003"
    type: "verifies"
  - target: "ix://agent-ix/quire-rs/spec/functional/FR-032"
    type: "verifies"
---
# [IT-003] Master requirements spec validates end-to-end

## Objective

Verify that a `master-requirements` `spec.md` validates structurally via quire-rs
`validate_document` (and the `quire validate` CLI) against this Module's
`master-requirements` archetype — frontmatter schema plus the canonical body —
with no render step, and that the documented frontmatter and body mutations each
fail as expected while optional sections do not break validation.

## Target Integration

The system under test is the quire-rs validation engine (and the `quire validate`
CLI surface) consuming this Module's `master-requirements` archetype. The
integration exercised is `Registry::load_module` against `spec_artifacts_iso/`
followed by `validate_document("master-requirements", doc_text)`, exercising both
the frontmatter JSON Schema and the canonical-body asserts.

## Preconditions

A build of quire-rs exposing `Registry::load_module` and `validate_document` (and
the `quire validate` CLI) is available, and this Module's `spec_artifacts_iso/`
source tree is present so the `master-requirements` archetype, its frontmatter
schema, and its skeleton (`skeletons/spec.md`) can be loaded.

## Inputs

The `master-requirements` skeleton (`skeletons/spec.md`) filled with substantive
content (a conformant master spec), plus mutated copies: frontmatter with
`component_type` removed and with non-kebab values (`"Fast API Service"`,
`React_Lib`, `""`); body copies with `## References` deleted, the `## Purpose`
body blanked, and the H1 title removed; and a copy carrying optional
`## Domain Model` and `## Security Model` sections.

## Test Procedure

Each step performs one discrete action and has its own success criterion.

1. Load this Module via quire-rs `Registry::load_module` against `spec_artifacts_iso/`.
   - IT-003-SC-01: the `master-requirements` archetype loads with its frontmatter schema.
2. Take the `master-requirements` skeleton filled with substantive content and run
   `validate_document("master-requirements", doc_text)`.
   - IT-003-SC-02: `is_valid == true` with no errors.
3. Mutate the frontmatter and re-validate: (a) remove `component_type`; (b) set
   `component_type` to a non-kebab value (`"Fast API Service"`, `React_Lib`, or `""`).
   - IT-003-SC-03: removal yields a frontmatter diagnostic naming the field; a
     non-kebab value yields a pattern failure.
4. Mutate the body and re-validate: (a) delete `## References` (reason `missing`);
   (b) blank the `## Purpose` body (reason `placeholder`/`empty`); (c) remove the
   `# Master Requirements Specification` H1 title (reason `missing`).
   - IT-003-SC-04: each mutation fails with the expected reason and a line number.
5. Add optional `## Domain Model` and `## Security Model` sections to the
   conformant spec and re-validate.
   - IT-003-SC-05: validation still passes (optional/extra sections do not break it).

## Expected Results

The conformant master spec validates with no errors; both frontmatter mutations
fail with a frontmatter diagnostic (missing field; kebab-pattern violation); each
body mutation fails with its expected reason and a line number; and a spec
carrying optional `Domain Model` and `Security Model` sections still validates.

## Acceptance Criteria

| ID | Criteria |
|----|----------|
| IT-003-AC-1 | Step 2 passes: the conformant master spec validates |
| IT-003-AC-2 | Both frontmatter mutations in step 3 fail with a frontmatter diagnostic (missing field; kebab-pattern violation) |
| IT-003-AC-3 | Each body mutation in step 4 fails with the expected reason and a line number |
| IT-003-AC-4 | Step 5 passes: optional/extra sections do not break validation |
