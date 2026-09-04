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

> **Review pass (2026-09-03, SR-003..SR-010):** the mapping-kind vocabulary is
> widened from five to eight so that every declared property has exactly one
> kind; the `Verification` split is realigned with FR-005 (`annotation`); the
> `ocl-clause` mapping states what happens to a prose `## Invariants` section,
> an orphan fence, a second fence, an unterminated fence, and a duplicate
> `clauseId`, and states that `sourceSpan` is omitted when the caller supplies
> no `sourceIdentity`, because semantic-core `SourceLocus` requires one; the
> `Story` grammar, the frontmatter drop policy, row-id uniqueness, and the
> failure discipline are stated; obligations on external consumers become
> statements about this module; packaged files are named.

The module SHALL publish, for every FR-005 model, a machine-readable mapping
from the authored Markdown to each field of the record.

The mapping SHALL use exactly the eight mapping kinds the manifest declares —
`frontmatter`, `section`, `table`, `typed-table`, `ocl-clause`, `list`,
`token`, and `provenance`.

The mapping SHALL declare the round-trip policy: Markdown is the sole authority
and the record is a derived projection, so that every consumer builds the same
record from the same document.

The Markdown forms are the ones the corpus already uses. This requirement adds
no new table header, renames no heading, and reorders no column. A document
that validated before FR-005 therefore maps to a record that validates against
its model, with one stated exception: FR-005 gives every prose cell
`minLength: 1`, so a document carrying an empty required cell (census
2026-09-04: 7 `Verification` cells of 20,881) is rejected. That is a census finding
about those documents, not a form this module admits, and TC-045 pins it.

**Who builds the record.** Nothing in production builds an ISO record from
Markdown today. This module ships data — schemas, mappings, and golden records
— and the reference mapping named in Outputs is the test oracle that proves the
data is coherent. `quire.validate_document` validates a *declaration* record on
the `object:` axis and never reaches an artifact-type record (FR-006
Description); an engine-side extractor for these records is quire-rs work, not
this module's (agent-ix/quire-rs#393, and see `spec.md` Out of Scope).

## Inputs

- `spec_artifacts_iso/mappings.yaml`: per model, the authority and round-trip
  policy, and per property the mapping kind, its source (a frontmatter path, a
  heading, a table with its columns, a fenced language, a bullet form, or a
  token pattern), and the cell-level split or parse rule the kind applies.
- `spec_artifacts_iso/mappings.schema.json`: the JSON Schema the mapping file
  itself validates against, so a malformed mapping is a schema error rather
  than a reader's surprise.
- The ten authoring skeletons under `spec_artifacts_iso/skeletons/`.
- The emitted schemas of [FR-005](./FR-005-semantic-data-schemas.md), which fix
  the property set every mapping entry must name.
- The quoin mapping conventions for typed tables and clauses (quoin FR-071,
  FR-072) and the quire-rs extraction semantics for section content (quire-rs
  FR-008: byte-exact slices).

## Outputs

- `spec_artifacts_iso/mappings.yaml` and `spec_artifacts_iso/mappings.schema.json`,
  both shipped with the module in the sdist, the wheel, and the npm payload.
- One golden record per skeleton at `spec_artifacts_iso/examples/<type>.record.json`,
  built by the reference mapping and validated against the type's schema, also
  shipped in all three payloads.
- A reference mapping implementation in the module's test support (Python),
  used by the suite to build records from Markdown. It is a test oracle, not
  module code, and the module ships data only.
- The FR skeleton extended with an optional `## Invariants` section showing the
  `ocl-clause` form (`### <clauseId>` followed by one ```` ```ocl ```` fence),
  and the FR archetype's asserts extended with the matching `invariants`
  locator so that the FR-002-AC-6 and FR-002-AC-7 skeleton/assert parity checks
  (TC-009, TC-010) keep passing in both directions.

## Behavior

Mapping kinds:

- A `frontmatter` mapping SHALL name a frontmatter key path and the record
  property it fills (`id`, `title`, `type`, `status`, `object`,
  `relationships`, `quality_attribute`, and the master-requirements identity
  keys).
- A `frontmatter` mapping SHALL drop every frontmatter key it does not name.
  The frontmatter schemas allow additional keys and the emitted models are
  sealed, so an undeclared key cannot reach the record; dropping it is the
  policy, and `mappings.yaml` records the dropped key set per model so the loss
  is declared rather than silent.
- A `section` mapping SHALL name a level-2 heading and fill a `Section`
  property with the heading's byte-exact content and its 1-based start and end
  lines.
- A `section` mapping MAY carry one named parse; the only parse this module
  declares is `story`, which fills `Story.asA`, `Story.iWant`, and
  `Story.soThat` beside the `Story.section` slice.
- The `story` parse SHALL read the three anchored lines `As a <asA>`, `I want
  <iWant>`, and `So that <soThat>`, each optionally wrapped in `**` or `_`
  emphasis and optionally followed by `:`, matched case-insensitively at the
  start of a line, with the captured text trimmed and its surrounding emphasis
  markers removed (census 2026-09-04: 908 bold, 149 plain, 0 neither over
  1,057 `US` documents — the grammar matches every story in the corpus).
- A `table` mapping SHALL name a section and a column list equal to the
  `assert.columns` of the corresponding locator, and fill an array with one
  object per data row in authored order, cells trimmed, with the row's line.
- A `typed-table` mapping SHALL be a `table` mapping whose cells are parsed
  further: an id cell into the row `id`, a verification cell into `Verification
  { method, testRefs, annotation? }` by the FR-005 split, and a supplementary
  `### <row id>` subsection into the row's `detail`.
- A `list` mapping SHALL name a section and a bullet form and fill an array
  with one object per matching line in authored order; it fills `Index.entries`
  and `Log.history`.
- A `token` mapping SHALL name a section and a token pattern and fill an array
  with one object per token occurrence in authored order; it fills
  `IT.successCriteria`.
- A `provenance` mapping SHALL fill `provenance.path` from the document's
  corpus-relative path and `provenance.digest` from the document bytes as read,
  with no line-ending normalization.
- A `provenance` mapping SHALL fill `provenance.sourceIdentity` from the
  caller, and SHALL leave the property absent when the caller supplies none.
- A `provenance` mapping SHALL NOT synthesize a `sourceIdentity`, because a
  synthesized `ix://` value would be indistinguishable from an authored one.

Clauses:

- An `ocl-clause` mapping SHALL map each `### <clauseId>` heading under
  `## Invariants` that owns exactly one fenced block tagged `ocl` to a
  semantic-core `ClauseRef { language: ocl, clauseId, sourceSpan? }`.
- The mapping SHALL carry the clause text verbatim beside the record, in the
  sidecar array `invariantsText`, one entry per `ClauseRef` in the same order,
  each entry recording the fence's `startLine` and `endLine` and the fence body
  bytes. The record itself never carries the clause text, and no code in this
  module parses it.
- The mapping SHALL emit `sourceSpan` only when the caller supplies a
  `sourceIdentity`, because semantic-core `SourceLocus` requires
  `sourceIdentity`, `path`, `startLine`, and `startColumn`. When present,
  `startLine` is the opening fence line, `endLine` the closing fence line, and
  `startColumn` and `endColumn` are the 1-based columns of the first and last
  characters of those fence lines (quire-rs FR-071).
- If a `## Invariants` section carries no fenced block, then the mapping SHALL
  leave `invariants` absent and SHALL NOT fail. The census counts 54 corpus FR
  documents whose `## Invariants` is prose; those documents keep validating.
- If a `### <clauseId>` heading is not an `Identifier`
  (`^[A-Za-z_][A-Za-z0-9_]*$`), owns a fence tagged with another language, owns
  more than one fence, owns an unterminated fence, or repeats a `clauseId`
  already used in the same document, then the mapping SHALL fail naming the
  line.
- If a fenced `ocl` block under `## Invariants` is not owned by a `###`
  heading, then the mapping SHALL fail naming the fence's opening line, so an
  orphan clause is reported rather than dropped.

Failure discipline:

- If a document carries a typed-table row whose id does not match the
  locator's `id_pattern`, a row id repeated within one table, a heading the
  mapping names twice, a `### <row id>` subsection whose id matches no row or
  matches a row already carrying a `detail`, or a `## Story` section that does
  not match the story grammar, then the mapping SHALL fail naming the line.
- The mapping SHALL report every such failure it finds in one pass, not only
  the first, and SHALL emit no record when any failure is found.
- The mapping SHALL NOT validate the record against the model. A record the
  mapping built and the schema then rejects is a defect in this pair of
  requirements, and the suite reports both the mapping failure and the schema
  failure separately (TC-044, TC-045).

Round-trip policy:

- `mappings.yaml` SHALL record `authority: markdown` and `round_trip: derived`
  per model.
- `mappings.yaml` SHALL record `lossless: true` on `section` and `ocl-clause`
  properties, whose text is the byte-exact slice.
- `mappings.yaml` SHALL record `lossless: false` on `table`, `typed-table`,
  `list`, `token`, and `frontmatter` properties, because cell whitespace,
  column alignment, bullet spelling, YAML formatting, and the order of
  frontmatter keys are not preserved.
- The module SHALL contain no code that derives Markdown from a record, so
  nothing in this module can present a record as the authority.

Golden records:

- The reference mapping SHALL produce, for each skeleton, the record committed
  under `examples/`, byte-for-byte after canonical JSON serialization (sorted
  keys, two-space indent, trailing newline).
- Every property of every emitted model SHALL have exactly one entry in
  `mappings.yaml`, and every entry SHALL name a property the model declares.
- A `table` or `typed-table` mapping's column list SHALL equal the locator's
  `assert.columns`.

## Constraints

| ID | Constraint | Type | Validation |
|----|------------|------|------------|
| FR-007-CON-1 | The mapping SHALL keep every existing table header, heading, and column order the corpus uses; the only Markdown form it adds is the optional `## Invariants` section on FR. | Compatibility | Test (TC-050) |
| FR-007-CON-2 | The mapping SHALL carry clause text under `## Invariants` as opaque bytes; no code in this module tokenizes, typechecks, or evaluates it. | Boundary | Test (TC-051) |
| FR-007-CON-3 | The mapping SHALL read Markdown and write nothing back; no file in the module derives Markdown from a record. | Boundary | Inspection (TC-059) |

## Acceptance Criteria

| ID | Criteria | Verification |
|----|----------|--------------|
| FR-007-AC-1 | `mappings.yaml` validates against `mappings.schema.json`, declares every property of every exported model exactly once, names no undeclared property, uses only the eight mapping kinds the manifest lists, and each `table`/`typed-table` column list equals the locator's `assert.columns`. | Test (TC-052) |
| FR-007-AC-2 | For each of the ten skeletons the reference mapping produces a record equal to `examples/<type>.record.json` and that record validates against `schemas/<Model>.json`. | Test (TC-044) |
| FR-007-AC-3 | The FR skeleton's `## Acceptance Criteria` rows map to `AcceptanceCriterion` objects whose `verification` splits `Test (TC-001)` into `method: Test`, `annotation: TC-001` and `testRefs: [TC-001]`, and the `## Constraints` row maps to a `Constraint` with `type: Security` and a `validation` of the same `Verification` shape. | Test (TC-053) |
| FR-007-AC-4 | The FR skeleton's `## Invariants` clause maps to a `ClauseRef` with `language: ocl` and `clauseId` equal to the `###` heading; with a caller-supplied `sourceIdentity` it also carries a `sourceSpan` whose `startLine`/`endLine` are the fence lines, and without one it carries no `sourceSpan`; the `invariantsText` entry equals the fence body byte-for-byte; a `### not-an-identifier` heading, a ```` ```tla ```` fence, a second fence under one heading, a repeated `clauseId`, and a fence owned by no `###` heading each fail naming the line; a prose `## Invariants` with no fence leaves `invariants` absent and does not fail. | Test (TC-051) |
| FR-007-AC-5 | A document copied from each of the ten skeletons before this change (the committed pre-change skeletons at 3d87196) maps to a record that validates against the new schema, so existing conforming Markdown is semantically equivalent. | Test (TC-050) |
| FR-007-AC-6 | A row id with the wrong prefix, a row id repeated in one table, a duplicated level-2 heading, an empty `Verification` cell, and a `## Story` without the As-a/I-want/So-that grammar each fail the mapping naming the line and yield no record, and all failures present in one document are reported together. | Test (TC-045) |
| FR-007-AC-7 | `section` and `ocl-clause` properties carry `lossless: true` and `table`, `typed-table`, `list`, `token`, and `frontmatter` properties carry `lossless: false` in `mappings.yaml`; every model records `authority: markdown` and `round_trip: derived`; and every model records the frontmatter keys its mapping drops. | Test (TC-052) |

## Dependencies

- **Upstream**: [FR-005](./FR-005-semantic-data-schemas.md), [FR-002](./FR-002-unified-archetype-validation.md) (the locators and skeletons), quoin FR-071/FR-072 (typed-table and clause conventions), quire-rs FR-008 (byte-exact section slicing), quire-rs FR-071 (span convention)
- **Downstream**: agent-ix/quire-contract-ir#52 (ISO frontend consumes the mapping and the golden records), agent-ix/filament-core-data#36 (generated-language fixtures), agent-ix/quire-rs#393 (the engine-side extractor that would build this record in production)
