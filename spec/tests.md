# Test Matrix

| FR | IT | Status |
|----|----|--------|
| FR-001 | IT-001 | Specified |
| FR-002 | IT-002 | Specified |

## AC → Test Coverage

This section maps every Acceptance Criterion to the test(s) that verify it.
Integration coverage runs through the `IT-002` markdown validate/extract
roundtrip; schema-shape criteria are verified by a schema test over the eight
shipped archetype manifests. Tests are 🚧 pending implementation.

### Functional Requirements

| AC | Criteria | Method | Covering Test | Status |
|----|----------|--------|---------------|--------|
| FR-002-AC-1 | All eight archetypes declare `body_extraction` with `assert`; none declare `template_ref`, `required_sections`, or `variants` | Schema | TC-SCHEMA-001 (manifest-shape sweep over 8 archetypes; template_ref absent) | 🚧 |
| FR-002-AC-2 | Conformant authored `FR` passes `validate_document`; missing-section / wrong-AC-columns / non-contiguous-AC-id copies each fail with a line-numbered diagnostic | Integration | IT-002 (IT-002-AC-1, IT-002-AC-2) | 🚧 |
| FR-002-AC-3 | Acceptance-Criteria id asserts use `{id}`; a row prefixed with a different artifact's id fails | Integration | IT-002 (IT-002-AC-2, AC-id mutation) | 🚧 |
| FR-002-AC-4 | Every archetype's declared headings are unique per level across its skeleton | Schema | TC-SCHEMA-002 (per-level heading-uniqueness sweep) | 🚧 |
| FR-002-AC-5 | Each archetype's authoring skeleton itself passes `validate_document` once filled with substantive content | Integration | IT-002 (IT-002-AC-1, skeleton over 8 archetypes) | 🚧 |
| FR-002-AC-6 | **(I1)** Manifest `body_extraction` asserts (headings+levels, table `columns`, `id_pattern`s) are consistent with / derived from each archetype's skeleton — a parity requirement | Schema | TC-SCHEMA-003 (assert↔skeleton parity sweep over 8 archetypes) | 🚧 |
| FR-002-AC-7 | **(I2)** Each skeleton's heading set + literal table header rows match its archetype's asserts exactly (text, order, level) | Schema | TC-SCHEMA-004 (literal-consistency sweep) | 🚧 |
| FR-002-AC-8 | **(I3)** Asserts distinguish heading-presence locators from `section_body` (non-empty/non-placeholder) locators; the skeleton supplies substantive body for every `section_body`-asserted section | Schema + Integration | TC-SCHEMA-005 (locator-kind classification) + IT-002 (IT-002-AC-1 substantive skeleton) | 🚧 |

### Integration Tests

| AC | Criteria | Method | Covering Test | Status |
|----|----------|--------|---------------|--------|
| IT-002-AC-1 | Step 3 passes for all eight archetypes | Integration | IT-002 step 3 (validate skeleton × 8 archetypes) | 🚧 |
| IT-002-AC-2 | Each mutation in steps 4-5 fails with the expected reason and a line number | Integration | IT-002 steps 4-5 (missing-section / assert-column / AC-id mutations) | 🚧 |
| IT-002-AC-3 | Step 6 extraction yields the expected record for each archetype (validate and extract use the same `body_extraction`) | Integration | IT-002 step 6 (extract × 8 archetypes) | 🚧 |

## Coverage Audit

Every AC defined in `spec/functional/` and `spec/integration/` appears above.

- FR-002: AC-1..8 — all covered (AC-6/7/8 are the render-removal assert↔skeleton parity ACs, I1/I2/I3).
- IT-002: AC-1..3 — all covered.

**Coverage: 11 / 11 in-scope ACs covered (FR-002 AC-1..8 + IT-002 AC-1..3).**
FR-001 / IT-001 are the pre-existing rows. New tests are 🚧 pending implementation.

> **Render removal (2026-06-04):** templates removed; **skeletons are the
> authoring source of truth** (FR-002 CR; parity with quire-rs commit 500a3d3 +
> filament-core FR-035 CR-002). `template_ref` is removed/rejected. New schema
> TCs TC-SCHEMA-003..005 enforce assert↔skeleton parity (I1), literal consistency
> (I2), and the heading-presence vs `section_body` locator distinction (I3). The
> deletion of `templates/` and the `template_ref:` manifest lines is an
> implementation task.
