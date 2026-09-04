---
id: FR-007
title: "Markdown mappings and round-trip policy for the semantic records"
type: FR
relationships:
  - target: "ix://agent-ix/spec-artifacts-iso/US-001"
    type: "implements"
  - target: "ix://agent-ix/spec-artifacts-iso/FR-005"
    type: "depends_on"
  - target: "ix://agent-ix/spec-artifacts-iso/FR-002"
    type: "depends_on"
  - target: "ix://agent-ix/quoin/FR-071"
    type: "uses"
  - target: "ix://agent-ix/quoin/FR-072"
    type: "uses"
---
# FR-007: Markdown mappings and round-trip policy for the semantic records

## Description

The module SHALL publish, for every FR-005 model, a machine-readable mapping
from the authored Markdown to each field of the record, using exactly the five
mapping kinds the manifest declares — `frontmatter`, `section`, `table`,
`typed-table`, and `ocl-clause` — together with the round-trip policy that
Markdown is the sole authority and the record is a derived projection, so that
every consumer builds the same record from the same document.

The Markdown forms are the ones the corpus already uses. This requirement adds
no new table header, renames no heading, and reorders no column: a document that
validated before FR-005 maps to a record that validates against its model.

## Inputs

- `spec_artifacts_iso/mappings.yaml`: per model, the authority and round-trip
  policy, and per field the mapping kind and its source (a frontmatter path, a
  heading, a table with its columns, or a fenced language).
- The ten authoring skeletons under `spec_artifacts_iso/skeletons/`.
- The quoin mapping conventions for typed tables and clauses (quoin FR-071,
  FR-072) and the quire-rs extraction semantics for section content (quire-rs
  FR-008: byte-exact slices).

## Outputs

- `spec_artifacts_iso/mappings.yaml`, shipped with the module.
- One golden record per skeleton at `spec_artifacts_iso/examples/<type>.record.json`,
  built by the reference mapping and validated against the type's schema.
- A reference mapping implementation in the module's test support (Python),
  used by the suite to build records from Markdown; it is a test oracle, not
  module code, and the module ships data only.
- The FR skeleton extended with an optional `## Invariants` section showing the
  `ocl-clause` form (`### <clauseId>` followed by one ```` ```ocl ```` fence).

## Behavior

- `frontmatter` mappings SHALL name a frontmatter key path and the record field
  it fills (`id`, `title`, `type`, `status`, `object`, `relationships`,
  `quality_attribute`, and the master-requirements identity keys).
- `section` mappings SHALL name a level-2 heading and fill a `Section` field
  with the heading's byte-exact content and its 1-based start and end lines;
  the `Story` field additionally parses `asA`, `iWant`, and `soThat` from the
  section text using the regex the `story` locator asserts.
- `table` mappings SHALL name a section and a column list equal to the
  `assert.columns` of the corresponding locator, and fill an array with one
  object per data row in authored order, cells trimmed, with the row's line.
- `typed-table` mappings SHALL be `table` mappings whose cells are parsed
  further: an id cell into the row `id`, a verification cell into `Verification
  { method, testRefs }` where `method` is the text before the first `(` trimmed
  and `testRefs` are the `TC-[0-9]+` tokens inside the parentheses, and a
  supplementary `### <row id>` subsection into the row's `detail`.
- `ocl-clause` mappings SHALL map each `### <clauseId>` heading under
  `## Invariants` that owns one fenced block tagged `ocl` to a semantic-core
  `ClauseRef { language: ocl, clauseId, sourceSpan }`, where `sourceSpan` is a
  `SourceLocus` over the fence (`startLine` the opening fence line,
  `endLine` the closing fence line, columns per quire-rs FR-071), the clause
  text is carried verbatim beside the record and never parsed, and a heading
  whose text is not an `Identifier` or a fence with another language is a
  mapping error at that line.
- The mapping SHALL derive `provenance.path` from the document's corpus-relative
  path, `provenance.digest` from the document bytes, and `provenance.sourceIdentity`
  from the caller when supplied.
- Round-trip policy: the mapping SHALL record `authority: markdown` and
  `round_trip: derived` per model, with `lossless: true` on `section` fields
  (the text is the byte-exact slice) and `lossless: false` on `table`,
  `typed-table`, and `frontmatter` fields (cell whitespace, column alignment,
  YAML formatting, and the order of frontmatter keys are not preserved); no
  consumer SHALL regenerate the Markdown from the record as an authority.
- Every property of every emitted model SHALL have exactly one mapping entry,
  and every mapping entry SHALL name a property the model declares; a `table`
  or `typed-table` mapping's columns SHALL equal the locator's `assert.columns`.
- If a document carries a typed-table row whose id does not match the locator's
  `id_pattern`, a heading the mapping names twice, or a `Story` section that
  does not match the story regex, then the mapping SHALL fail naming the line;
  it SHALL NOT emit a partial record.
- The reference mapping SHALL produce, for each skeleton, the record committed
  under `examples/`, byte-for-byte after canonical JSON serialization (sorted
  keys, two-space indent, trailing newline).

## Constraints

| ID | Constraint | Type | Validation |
|----|------------|------|------------|
| FR-007-CON-1 | The mapping SHALL keep every existing table header, heading, and column order the corpus uses; the only Markdown form it adds is the optional `## Invariants` section on FR. | Compatibility | Test (TC-050) |
| FR-007-CON-2 | The mapping SHALL carry clause text under `## Invariants` as opaque bytes; no code in this module tokenizes, typechecks, or evaluates it. | Boundary | Test (TC-051) |
| FR-007-CON-3 | The record SHALL be a projection: the mapping reads Markdown and writes nothing back; no file in the module derives Markdown from a record. | Boundary | Inspection |

## Acceptance Criteria

| ID | Criteria | Verification |
|----|----------|--------------|
| FR-007-AC-1 | `mappings.yaml` declares every property of every exported model exactly once, names no undeclared property, uses only the five mapping kinds the manifest lists, and each `table`/`typed-table` column list equals the locator's `assert.columns`. | Test (TC-052) |
| FR-007-AC-2 | For each of the ten skeletons the reference mapping produces a record equal to `examples/<type>.record.json` and that record validates against `schemas/<Model>.json`. | Test (TC-044) |
| FR-007-AC-3 | The FR skeleton's `## Acceptance Criteria` rows map to `AcceptanceCriterion` objects whose `verification` splits `Test (TC-001)` into `method: Test` and `testRefs: [TC-001]`, and the `## Constraints` row maps to a `Constraint` with `type: Security`. | Test (TC-053) |
| FR-007-AC-4 | The FR skeleton's `## Invariants` clause maps to a `ClauseRef` with `language: ocl`, `clauseId` equal to the `###` heading, and a `sourceSpan` whose `startLine`/`endLine` are the fence lines; the clause text equals the fence body byte-for-byte; a `### not-an-identifier` heading and a ```` ```tla ```` fence each fail naming the line. | Test (TC-051) |
| FR-007-AC-5 | A document copied from each of the ten skeletons before this change (the committed pre-change skeletons at 3d87196) maps to a record that validates against the new schema, so existing conforming Markdown is semantically equivalent. | Test (TC-050) |
| FR-007-AC-6 | A row id with the wrong prefix, a duplicated level-2 heading, and a `## Story` without the As-a/I-want/So-that shape each fail the mapping naming the line and yield no record. | Test (TC-045) |
| FR-007-AC-7 | `section` fields carry `lossless: true` and `table`, `typed-table`, and `frontmatter` fields `lossless: false` in `mappings.yaml`, and every model records `authority: markdown` and `round_trip: derived`. | Test (TC-052) |

## Dependencies

- **Upstream**: [FR-005](./FR-005-semantic-data-schemas.md), [FR-002](./FR-002-unified-archetype-validation.md) (the locators and skeletons), quoin FR-071/FR-072 (typed-table and clause conventions), quire-rs FR-008 (byte-exact section slicing), quire-rs FR-071 (span convention)
- **Downstream**: agent-ix/quire-contract-ir#52 (ISO frontend consumes the mapping and the golden records), agent-ix/filament-core-data#36 (generated-language fixtures)
