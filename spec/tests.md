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
| FR-002-AC-1 | All eight archetypes declare `body_extraction` with `assert`; none declare `required_sections` or `variants` | Schema | TC-SCHEMA-001 (manifest-shape sweep over 8 archetypes) | 🚧 |
| FR-002-AC-2 | Conformant authored `FR` passes `validate_document`; missing-section / wrong-AC-columns / non-contiguous-AC-id copies each fail with a line-numbered diagnostic | Integration | IT-002 (IT-002-AC-1, IT-002-AC-2) | 🚧 |
| FR-002-AC-3 | Acceptance-Criteria id asserts use `{id}`; a row prefixed with a different artifact's id fails | Integration | IT-002 (IT-002-AC-2, AC-id mutation) | 🚧 |
| FR-002-AC-4 | Every archetype's declared headings are unique per level across its skeleton | Schema | TC-SCHEMA-002 (per-level heading-uniqueness sweep) | 🚧 |
| FR-002-AC-5 | Each archetype's authoring skeleton itself passes `validate_document` once filled with substantive content | Integration | IT-002 (IT-002-AC-1, skeleton over 8 archetypes) | 🚧 |

### Integration Tests

| AC | Criteria | Method | Covering Test | Status |
|----|----------|--------|---------------|--------|
| IT-002-AC-1 | Step 3 passes for all eight archetypes | Integration | IT-002 step 3 (validate skeleton × 8 archetypes) | 🚧 |
| IT-002-AC-2 | Each mutation in steps 4-5 fails with the expected reason and a line number | Integration | IT-002 steps 4-5 (missing-section / assert-column / AC-id mutations) | 🚧 |
| IT-002-AC-3 | Step 6 extraction yields the expected record for each archetype (validate and extract use the same `body_extraction`) | Integration | IT-002 step 6 (extract × 8 archetypes) | 🚧 |

## Coverage Audit

Every AC defined in `spec/functional/` and `spec/integration/` appears above.

- FR-002: AC-1..5 — all covered.
- IT-002: AC-1..3 — all covered.

**Coverage: 8 / 8 in-scope ACs covered (FR-002 + IT-002).** FR-001 / IT-001 are
the pre-existing rows. New tests are 🚧 pending implementation.
