---
id: IT-003
title: "Master requirements spec validates end-to-end"
artifact_type: IT
relationships:
  - target: "ix://agent-ix/spec-artifacts-iso/FR-003"
    type: "verifies"
  - target: "ix://agent-ix/quire-rs/spec/functional/FR-032"
    type: "verifies"
---
# [IT-003] Master requirements spec validates end-to-end

## Scenario

A `master-requirements` `spec.md` validates structurally via quire-rs
`validate_document` (and the `quire validate` CLI) against the module's
`master-requirements` archetype — frontmatter schema plus the canonical body —
with no render step.

## Steps

1. Load this module via quire-rs `Registry::load_module` against `spec_artifacts_iso/`.
2. Take the `master-requirements` skeleton (`skeletons/spec.md`) filled with substantive content (a conformant master spec).
3. Run `validate_document("master-requirements", doc_text)`; assert `is_valid == true`, no errors.
4. Mutate the frontmatter and re-validate, asserting a failure each time:
   a. remove `component_type` (frontmatter diagnostic naming the field);
   b. set `component_type` to a non-kebab value (`"Fast API Service"`, `React_Lib`, or `""`) — pattern failure.
5. Mutate the body and re-validate, asserting a line-numbered failure each time:
   a. delete the `## References` section (reason `missing`);
   b. blank the `## Purpose` body (reason `placeholder`/`empty`);
   c. remove the `# Master Requirements Specification` H1 title (reason `missing`).
6. Add optional `## Domain Model` and `## Security Model` sections to the conformant spec; assert it still validates.

## Acceptance Criteria

| ID | Criteria |
|----|----------|
| IT-003-AC-1 | Step 3 passes: the conformant master spec validates |
| IT-003-AC-2 | Both frontmatter mutations in step 4 fail with a frontmatter diagnostic (missing field; kebab-pattern violation) |
| IT-003-AC-3 | Each body mutation in step 5 fails with the expected reason and a line number |
| IT-003-AC-4 | Step 6 passes: optional/extra sections do not break validation |
