---
type: TestMatrix
id: TM-001
title: "Test Matrix"
---
# Test Matrix

| FR | IT | Status |
|----|----|--------|
| FR-001 | IT-001 | Specified |
| FR-002 | IT-002 | Specified |
| FR-003 | IT-003 | Specified |

## AC → Test Coverage

This section maps every Acceptance Criterion to the test(s) that verify it.
Integration coverage runs through the `IT-002` markdown validate/extract
roundtrip and the `IT-003` master-requirements validate; schema-shape criteria
are verified by a schema test over the shipped archetype manifests (the eight ISO
artifact archetypes plus `master-requirements`). Tests are 🚧 pending implementation.

### Functional Requirements

| AC | Criteria | Method | Covering Test | Status |
|----|----------|--------|---------------|--------|
| FR-002-AC-1 | Every registered artifact_type (the eight ISO + `master-requirements`) declares `body_extraction` with `assert`; none declare `template_ref`, `required_sections`, or `variants` | Schema | TC-SCHEMA-001 (manifest-shape sweep over all archetypes; template_ref absent) | 🚧 |
| FR-002-AC-2 | Conformant authored `FR` passes `validate_document`; missing-section / wrong-AC-columns / non-contiguous-AC-id copies each fail with a line-numbered diagnostic | Integration | IT-002 (IT-002-AC-1, IT-002-AC-2) | 🚧 |
| FR-002-AC-3 | Acceptance-Criteria id asserts use `{id}`; a row prefixed with a different artifact's id fails | Integration | IT-002 (IT-002-AC-2, AC-id mutation) | 🚧 |
| FR-002-AC-4 | Every archetype's declared headings are unique per level across its skeleton | Schema | TC-SCHEMA-002 (per-level heading-uniqueness sweep) | 🚧 |
| FR-002-AC-5 | Each archetype's authoring skeleton itself passes `validate_document` once filled with substantive content | Integration | IT-002 (IT-002-AC-1, skeleton over 8 archetypes) | 🚧 |
| FR-002-AC-6 | **(I1)** Manifest `body_extraction` asserts (headings+levels, table `columns`, `id_pattern`s) are consistent with / derived from each archetype's skeleton — a parity requirement | Schema | TC-SCHEMA-003 (assert↔skeleton parity sweep over 8 archetypes) | 🚧 |
| FR-002-AC-7 | **(I2)** Each skeleton's heading set + literal table header rows match its archetype's asserts exactly (text, order, level) | Schema | TC-SCHEMA-004 (literal-consistency sweep) | 🚧 |
| FR-002-AC-8 | **(I3)** Asserts distinguish heading-presence locators from `section_body` (non-empty/non-placeholder) locators; the skeleton supplies substantive body for every `section_body`-asserted section | Schema + Integration | TC-SCHEMA-005 (locator-kind classification) + IT-002 (IT-002-AC-1 substantive skeleton) | 🚧 |
| FR-003-AC-1 | The manifest declares a `master-requirements` artifact_type with a `frontmatter_schema_ref` and a `body_extraction` carrying `assert` facets | Schema | TC-SCHEMA-001 (manifest-shape sweep, master-requirements row) | 🚧 |
| FR-003-AC-2 | The frontmatter schema requires `artifact_type`/`name`/`org`/`component_type`, does not require `id`/`title`, and constrains `component_type` to `^[a-z][a-z0-9-]*$` | Schema | TC-SCHEMA-006 (master-requirements frontmatter-schema shape) | 🚧 |
| FR-003-AC-3 | A conformant master `spec.md` passes `validate_document` | Integration | IT-003 (IT-003-AC-1); TC-SCHEMA-007 (skeleton validates, master-requirements row) | 🚧 |
| FR-003-AC-4 | A master spec missing `component_type` (or empty) fails frontmatter validation naming the field | Integration | IT-003 (IT-003-AC-2) | 🚧 |
| FR-003-AC-5 | A master spec whose `component_type` carries a space/inline comment fails the kebab pattern | Integration | IT-003 (IT-003-AC-2) | 🚧 |
| FR-003-AC-6 | A master spec missing the H1 title or any required canonical section fails with a line-numbered diagnostic | Integration | IT-003 (IT-003-AC-3) | 🚧 |
| FR-003-AC-7 | A master spec carrying optional sections (Domain Model, Security Model) and extra H2s still passes | Integration | IT-003 (IT-003-AC-4) | 🚧 |
| FR-003-AC-8 | The `master-requirements` skeleton itself passes `validate_document` and satisfies the assert↔skeleton parity (FR-002-AC-6/7/8) | Schema + Integration | TC-SCHEMA-003/004/005 (parity sweeps, master-requirements row) + IT-003 (IT-003-AC-1) | 🚧 |

### Integration Tests

| AC | Criteria | Method | Covering Test | Status |
|----|----------|--------|---------------|--------|
| IT-002-AC-1 | Step 3 passes for all eight archetypes | Integration | IT-002 step 3 (validate skeleton × 8 archetypes) | 🚧 |
| IT-002-AC-2 | Each mutation in steps 4-5 fails with the expected reason and a line number | Integration | IT-002 steps 4-5 (missing-section / assert-column / AC-id mutations) | 🚧 |
| IT-002-AC-3 | Step 6 extraction yields the expected record for each archetype (validate and extract use the same `body_extraction`) | Integration | IT-002 step 6 (extract × 8 archetypes) | 🚧 |
| IT-003-AC-1 | Step 3 passes: the conformant master spec validates | Integration | IT-003 step 3 (validate master-requirements skeleton) | 🚧 |
| IT-003-AC-2 | Both frontmatter mutations in step 4 fail (missing field; kebab-pattern violation) | Integration | IT-003 step 4 (component_type mutations) | 🚧 |
| IT-003-AC-3 | Each body mutation in step 5 fails with the expected reason and a line number | Integration | IT-003 step 5 (missing section / blank Purpose / missing H1) | 🚧 |
| IT-003-AC-4 | Step 6 passes: optional/extra sections do not break validation | Integration | IT-003 step 6 (Domain Model + Security Model added) | 🚧 |

## Coverage Audit

Every AC defined in `spec/functional/` and `spec/integration/` appears above.

- FR-002: AC-1..8 — all covered (AC-6/7/8 are the render-removal assert↔skeleton parity ACs, I1/I2/I3).
- FR-003: AC-1..8 — all covered (master-requirements archetype: AC-1/AC-8 via the parametrized manifest+parity sweeps now including the `master-requirements` row; AC-2 via the frontmatter-schema-shape test; AC-3..7 via IT-003).
- IT-002: AC-1..3 — all covered.
- IT-003: AC-1..4 — all covered.

**Coverage: 23 / 23 in-scope ACs covered (FR-002 AC-1..8 + FR-003 AC-1..8 + IT-002 AC-1..3 + IT-003 AC-1..4).**
FR-001 / IT-001 are the pre-existing rows. New tests are 🚧 pending implementation.

> **Render removal (2026-06-04):** templates removed; **skeletons are the
> authoring source of truth** (FR-002 CR; parity with quire-rs commit 500a3d3 +
> filament-core FR-035 CR-002). `template_ref` is removed/rejected. New schema
> TCs TC-SCHEMA-003..005 enforce assert↔skeleton parity (I1), literal consistency
> (I2), and the heading-presence vs `section_body` locator distinction (I3). The
> deletion of `templates/` and the `template_ref:` manifest lines is an
> implementation task.
