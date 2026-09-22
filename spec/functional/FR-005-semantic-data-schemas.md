---
id: FR-005
title: "Semantic data schemas for ISO artifact types are emitted from TypeSpec"
type: FR
relationships:
  - target: "ix://agent-ix/spec-artifacts-iso/US-001"
    type: "implements"
  - target: "ix://agent-ix/spec-artifacts-iso/FR-002"
    type: "depends_on"
  - target: "ix://agent-ix/filament-core-data/spec/functional/FR-031"
    type: "uses"
  - target: "ix://agent-ix/quoin/FR-073"
    type: "implements"
---
# FR-005: Semantic data schemas for ISO artifact types are emitted from TypeSpec

## Description

> **Review pass (2026-09-03, SR-003..SR-010):** rewritten after the composite
> review. Field-typing statements are re-subjected on the generator and the
> models; the `Verification` split keeps every byte of the cell
> (`annotation`); `Constraint.validation` takes the same `Verification` type
> as the criterion cells; the export-name to model map, the CRLF rule, the
> empty-table rule, and the engine floor are stated; the frontmatter
> projection rule (sealed models drop undeclared keys, by policy) moves to
> FR-007.
>
> **Census re-measured 2026-09-04** with `scripts/corpus_census.py --json`,
> which is now a committed, tested script rather than a scratch file. Six
> figures changed materially and are corrected below. The constraint-category
> count was a display limit (the old scratch script printed `most_common(30)`),
> not a measurement: the true distinct count is 335. Verification-method
> spellings are 1,144, not "more than thirty". Empty verification cells are 7,
> not 41. `status` is declared on 863 documents, not 973. `US` stories matching
> neither form are 0, not 8. `log` undated entries are 104 across 9
> repositories, not ~30 across 4. No constraint changes as a result — every
> correction makes the free-text argument stronger.

The module SHALL declare one semantic data model per ISO artifact type — `FR`,
`NFR`, `StR`, `US`, `IT`, `TC`, `MasterRequirements`, `Index`, `Log`, and
`Glossary` — as TypeSpec source importing `@agent-ix/semantic-core` 0.3.0.

The module SHALL ship the JSON Schema 2020-12 projection of each model at
`spec_artifacts_iso/schemas/<Model>.json`.

Each model is the typed form of the record the archetype's existing
`body_extraction` locators extract — every section body, every asserted table
row, and the frontmatter identity, relationships, status, and provenance. The
models describe requirement *definitions*: a `TC` record describes a test case,
and the outcome of executing it is not a field of any model.

## Inputs

- `spec_artifacts_iso/semantic/main.tsp`: the TypeSpec source (namespace
  `AgentIx.SpecArtifactsIso`, `@jsonSchema` base
  `https://schemas.agent-ix.org/agent-ix/spec-artifacts-iso/<manifest version>/`).
- `@agent-ix/semantic-core` 0.3.0, resolved from the registry the developer's
  npm configuration routes the `@agent-ix` scope to (today the local npm.ix
  registry; the public publish is agent-ix/filament-core-data#11), pinned
  exactly, for `SemanticId`, `ClauseRef`, and `SourceLocus`.
- `@typespec/compiler` 1.15.0 and `@typespec/json-schema` 1.15.0 as
  devDependencies of the TypeSpec package, with a committed `package-lock.json`.
- The existing `body_extraction` locators of `spec_artifacts_iso/manifest.yaml`.
- The corpus census of 2026-09-04 (`scripts/corpus_census.py --json` over
  `~/dev/*/spec`: 7,209 ISO artifact documents in 269 bundles, counted by
  document) that fixes the id, status, cardinality, verification-cell, and
  constraint-type populations the constraints below admit. Per type: `FR`
  2,851, `index` 1,168, `US` 1,057, `NFR` 811, `StR` 542, `log` 282,
  `master-requirements` 248, `IT` 183, `TC` 67, `Glossary` 0 — the `Glossary`
  model is authored against its frontmatter schema and skeleton, because the
  corpus carries no instance of it yet.

## Outputs

- `spec_artifacts_iso/schemas/<Model>.json` for the ten exported models and for
  every shared model and scalar they reference (`Section`, `HeadingRef`,
  `Provenance`, `Relationship`, `Verification`, `AcceptanceCriterion`,
  `Constraint`, `ValidationCriterion`, `MeasurementRow`, `SuccessCriterion`,
  `Story`, `GlossaryTerm`, `IndexEntry`, `LogEntry`, `QualityAttribute`, and
  the id, line, digest, and text scalars).
- `spec_artifacts_iso/semantic/generated/toolchain.json` recording the
  compiler, emitter, and semantic-core versions, the SHA-256 digest of the
  resolved `@agent-ix/semantic-core` package's own `generated/toolchain.json`
  (so the copy this module compiled against is identified by bytes and not by
  a version string two registries could disagree on), the emitted file list,
  the imported files excluded, and a SHA-256 digest computed as
  `sha256(concat(name + "\n" + bytes))` over the emitted files in sorted name
  order — the same computation as filament-core-data
  `packages/semantic-core/generated/toolchain.json`.
- `make schemas` (regenerate) and `make schemas-check` (fail on any byte
  difference between the committed projection and a fresh one), each run after
  `make semantic-install` (`npm ci` in the TypeSpec package). The hand-authored
  `*-frontmatter.schema.json` files in the same directory are not projections
  and are outside both targets.
- The shipped payload of the module — identical in the sdist, the wheel, and
  the npm tarball — SHALL carry `schemas/`, `skeletons/`, `manifest.yaml`,
  `mappings.yaml`, `mappings.schema.json`,
  `examples/`, `semantic/main.tsp`, and `semantic/generated/toolchain.json`.
  The TypeSpec toolchain itself (`node_modules`, `package.json`,
  `package-lock.json`, `tspconfig.yaml`, `scripts/`) is a build input and SHALL
  NOT ship.
- The export-name to model map, fixed by this requirement and restated in
  FR-006: `FR` → `FR.json`, `NFR` → `NFR.json`, `StR` → `StR.json`, `US` →
  `US.json`, `IT` → `IT.json`, `TC` → `TC.json`, `master-requirements` →
  `MasterRequirements.json`, `index` → `Index.json`, `log` → `Log.json`,
  `Glossary` → `Glossary.json`. The `type` `const` of each model is the
  archetype name (`master-requirements`, `index`, `log`), never the model name.

## Behavior

Projection:

- The generator SHALL write every emitted schema with `$schema:
  https://json-schema.org/draft/2020-12/schema` and `$id:
  https://schemas.agent-ix.org/agent-ix/spec-artifacts-iso/<manifest version>/<Model>.json`,
  where `<manifest version>` equals `version` in `manifest.yaml`.
- The generator SHALL keep every `$ref` of the shipped bundle inside two bases:
  the module base above and
  `https://schemas.agent-ix.org/semantic-core/0.3.0/`.
- The generator SHALL exclude from the shipped bundle every file whose `$id`
  starts with `https://schemas.agent-ix.org/semantic-core/`, which the
  emitter produces for the imported semantic-core models (they ship in the
  bundles quoin and quire vendor, never here).
- The generator SHALL seal every object schema
  (`unevaluatedProperties: { not: {} }`) and SHALL declare every property
  inline (no `allOf`, `extends`, or spread), so that Python `jsonschema` and
  the Rust `jsonschema` crate agree on every record.
- The generator SHALL render each file as `JSON.stringify(schema, null, 2)`
  plus one trailing newline, with no formatter dependency.
- If `make schemas-check` finds a committed projection whose bytes differ from
  the fresh one, a committed projection the fresh run no longer produces, or a
  `toolchain.json` that differs, then `make schemas-check` SHALL exit non-zero
  naming each file.
- If the `@jsonSchema` base of `main.tsp` does not embed the manifest
  `version`, then `make schemas` SHALL fail naming both values before writing
  any file.

Identity, relationships, status, provenance:

- The `FR`, `NFR`, `StR`, `US`, `IT`, `TC`, and `Glossary` models SHALL carry
  `id`, `title`, and `type` (a `const` equal to the archetype name).
- The `MasterRequirements` model SHALL carry `type` (`master-requirements`),
  `name`, `org`, `componentType` (`^[a-z][a-z0-9-]*$`), and the optional
  `implementationLanguage` (non-empty string or `null`), `tags`, `dependsOn`
  (bare module names; census: 143 non-empty string lists, 67 empty),
  `standardsAlignment`, and `securityCritical` the frontmatter schema declares.
- The `MasterRequirements` model SHALL carry an optional `title` filled from the
  document's H1, not from frontmatter. FR-003 requires a master-requirements
  document to carry neither `id` nor `title` in frontmatter, and its
  frontmatter schema declares no `title` key; the `title` heading locator is
  the only source there is.
- The `Index` model SHALL carry `type` (`index`) and the optional `title`,
  `description`, and `okfVersion`; the `Log` model SHALL carry `type` (`log`)
  and the optional `title` and `description`; the `Glossary` model SHALL carry
  the optional `scope` and `description`.
- The `id` scalar of each model SHALL be the artifact type's own prefix:
  `^FR-[0-9]+$`, `^NFR-[0-9]+$`, `^StR-[0-9]+$`, `^US-[0-9]+$`, `^IT-[0-9]+$`,
  `^TC-[0-9]+$`, and `^[A-Z][A-Za-z]{1,3}-[0-9]+$` for `Glossary` (`GLO-001`).
  The census population is every one of the 5,567 identified requirement and
  test documents (`FR-N` 2,885, `US-N` 1,064, `NFR-N` 825, `StR-N` 543, `IT-N`
  183, `TC-N` 67 — six patterns, no other spelling).
- Every model SHALL carry `provenance: Provenance` — the document's
  corpus-relative `path`, its optional `sourceIdentity` (a semantic-core
  `SemanticId`), and a `sha256:<64 hex>` digest over the document bytes as
  read, with no line-ending normalization.
- Every requirement, test, glossary, and master-requirements model SHALL carry
  `relationships: Relationship[]` with `target` (`^ix://`), `type` (an edge verb,
  `^[a-z][a-z0-9_]*$`), and an optional `cardinality` matching
  `^[0-9A-Za-z*]+(\.\.[0-9A-Za-z*]+)?(:[0-9A-Za-z*]+(\.\.[0-9A-Za-z*]+)?)?$`
  (census: 11 forms over 2,925 relationship entries — `1:1` 1,710, `1:N` 545,
  `N:1` 536, `n:1` 57, `1` 55, `0:1` 9, `1:n` 5, `many:1` 4, `1..1` 2, `0..1`
  1, `1:m` 1).
- The `Relationship` model SHALL declare exactly `target`, `type`, and the
  optional `cardinality`.
- The generator SHALL seal `Relationship` as it seals every other model. FR-003
  admits extra annotation keys on a relationship item (`note`, `models`,
  `endpoints`), so those keys cannot reach the record; they are dropped under
  the FR-007 frontmatter drop policy and listed there as dropped keys, which is
  a declared loss rather than a silent one.
- Every model whose frontmatter schema declares `status` — every model except
  `Index` and `Log`, whose OKF reserved frontmatter has no such key — SHALL
  carry an optional `status: ArtifactStatus`, a string matching
  `^[A-Za-z][A-Za-z_-]*$`. The value set stays open by design: the
  census counts 16 spellings across the 863 documents that declare one
  (`APPROVED` 448, `IMPLEMENTED` 147, `DRAFT` 118, `PROPOSED` 77, `SUPERSEDED`
  20, eleven minor forms), and closing it is a
  vocabulary change owned by a later sweep-and-report (see spec.md Out of
  Scope).
- The `FR`, `NFR`, `StR`, `US`, `IT`, and `TC` models SHALL carry the optional
  `object` (`^[a-z][a-z0-9_]*$`, the frontmatter `object:` key; census: 888
  FR documents).
- Record property names SHALL be the camelCase form of the frontmatter key or
  locator name with a trailing `_table` dropped (`quality_attribute` →
  `qualityAttribute`, `acceptance_criteria_table` → `acceptanceCriteria`).
- Where one section carries both a `section_body` locator and a `table_row`
  locator — `Acceptance Criteria` on `FR` and `NFR`, `Validation Criteria` on
  `StR`, `Measurement and Evaluation` on `NFR`, `Terms` on `Glossary` — the
  models SHALL carry the typed rows under that name.
- The models SHALL NOT also carry the section body of such a section. The rows
  are that section's record form, and carrying both would put the same bytes in
  the record twice.
- The one locator whose property name is not derived from it is `index`
  `contents`, which fills `entries`: the property is the list the section
  carries, not the section. `mappings.yaml` records the pair, and it is the
  only such rename.

Sections and tables:

- Each `section_body` locator SHALL map to a `Section` field — `text` (the
  byte-exact section content per quire-rs FR-008, CR bytes included),
  `startLine`, and `endLine` (1-based document lines) — required where the
  locator is `required: true` and optional otherwise. `text` is free text:
  authored prose whose sentence grammar is the `iso-spec-core` EARS advisory,
  not a schema.
- Each `heading` locator of `MasterRequirements` (`scope`, `systemOverview`,
  `requirementsArchitecture`) SHALL map to a `HeadingRef { heading, line }`.
- Each asserted `table_row` locator SHALL map to an array of typed row objects,
  one per data row in authored order, with `line` on each row and every cell
  trimmed of leading and trailing whitespace (`\r` included):
  - `FR.constraints`: `Constraint { id: ^FR-[0-9]+-CON-[0-9]+$, constraint,
    type, validation: Verification, line }`.
  - `FR.acceptanceCriteria` and `NFR.acceptanceCriteria`: `AcceptanceCriterion
    { id: ^(FR|NFR)-[0-9]+-AC-[0-9]+$, criteria, verification: Verification,
    detail?, line }`, where `detail` carries the body of a supplementary
    `### <criterion id>` subsection when one exists.
  - `StR.validationCriteria`: `ValidationCriterion { id: ^StR-[0-9]+-VC-[0-9]+$,
    criteria, validation: Verification, line }`.
  - `NFR.measurement`: `MeasurementRow { metric, target, threshold, method, line }`.
  - `Glossary.terms`: `GlossaryTerm { term, definition, line }`.
- The `Verification` model SHALL be `{ method, testRefs, annotation? }`: for a
  cell `<method> (<annotation>)`, `method` is the text before the first `(`
  trimmed, `annotation` is the text between the first `(` and the last `)`
  verbatim, and `testRefs` are the `TC-[0-9]+` tokens found in `annotation`,
  in order; a cell without parentheses is `method` alone with `testRefs: []`
  and no `annotation`. No byte of the cell is dropped.
- The models SHALL type the cells `criteria`, `constraint`, `type`, `metric`,
  `target`, `threshold`, `method`, `term`, `definition`, and
  `Verification.method` as strings with `minLength: 1`.
- The models SHALL type the `validation` cell of `Constraint` and of
  `ValidationCriterion` as `Verification`, whose own `method` carries that
  `minLength: 1`, so `validation` is not one of the plain-string cells above.
  `type` (census:
  335 distinct categories over 3,960 constraint rows),
  `Verification.method` (census: 1,144 distinct spellings over 21,181 cells, of
  which the four the advisory lint rule `ac-verification-method` admits are the
  large majority), and `target` and `threshold` (census: prose quantities such as
  `600 imports/s`) are free text because their vocabularies are owned by
  advisory lint rules or by no rule at all, and a schema that closed them would
  reject the corpus it describes. An empty cell (census: 7 of 21,181
  verification cells)
  fails `minLength: 1`; such a document is a census finding, not a form this
  module admits.
- The model SHALL declare `constraints`, `acceptanceCriteria` (on `NFR`),
  `validationCriteria`, `measurement`, `terms`, and `history` with
  `minItems: 1` where the locator asserts `min_rows: 1`; an optional table
  whose section is present but holds no table (census: 74 FR documents with a
  prose `## Constraints`) maps to an absent field, never to `[]`.
- The `US` model SHALL declare `story: Story { asA, iWant, soThat, section }`,
  filled by the FR-007 story grammar (census: 915 bold, 149 plain, 0 neither
  over 1,064 `US` documents — the grammar matches every story in the corpus).
- The `IT` model SHALL declare `successCriteria: SuccessCriterion { id:
  ^IT-[0-9]+-SC-[0-9]+$, text, line }[]`, one per `IT-XXX-SC-NN` token in
  `## Test Procedure` with `text` the trimmed remainder of the token's line
  after an optional `:`; the array MAY be empty (the `it-success-criteria`
  lint rule is advisory; census: 157 of 183 IT documents carry tokens).
- The `Index` model SHALL declare `entries: IndexEntry { title, href, summary?,
  line }[]`, one per `* [title](href) - summary` or `- [title](href)` line
  under `## Contents` (census: 6,286 link lines over 1,169 index documents, 736
  with `-` bullets, 5,163 without a summary), where `href` is a relative path
  (`^(\./|\.\./)*[^:/][^:]*$`, never a scheme), because index links are local
  navigation and not knowledge-graph edges. A line under `## Contents` that
  matches neither form (prose, a nested bullet, a blank line) is not an entry
  and is not an error; `## Contents` is authored prose with links in it, not a
  table.
- The `Log` model SHALL declare `history: LogEntry { date:
  ^[0-9]{4}-[0-9]{2}-[0-9]{2}$, text, line }[]`, one per
  `* **YYYY-MM-DD** — text` entry under `## History`, where the bullet is `*`
  or `-`, the dash separator is optional, and the entry extends to the next
  bullet at the same indentation (census: 782 dated entries, 104 undated across
  9 repositories, which the mapping rejects naming the line).
- The `FR` model SHALL declare `invariants?: ClauseRef[]` (semantic-core,
  `minItems: 1`), filled by the FR-007 `ocl-clause` mapping from an optional
  `## Invariants` section; the clause text is never parsed.
- The `NFR` model SHALL declare `qualityAttribute` as the twelve-value enum the
  NFR frontmatter schema declares.
- No model SHALL restate a constraint more loosely than the frontmatter schema
  beside it.

## Constraints

| ID | Constraint | Type | Validation |
|----|------------|------|------------|
| FR-005-CON-1 | The models SHALL declare exactly the fields the locators, the frontmatter schemas, and the FR-007 grammars produce: no field without a Markdown source, no locator output without a field. | Integrity | Test (TC-039, TC-040) |
| FR-005-CON-2 | The emitted bundle SHALL carry no `$ref` outside the module base and the semantic-core 0.3.0 base, so that a consumer resolves every reference without a network read. | Boundary | Test (TC-041) |
| FR-005-CON-3 | The TypeSpec package SHALL pin `@typespec/compiler` and `@typespec/json-schema` at 1.15.0 and `@agent-ix/semantic-core` at 0.3.0 with a committed lockfile, no `file:` or `link:` reference, and no `.npmrc` in the repository. | Reproducibility | Test (TC-054) |
| FR-005-CON-4 | No model SHALL carry a property named `result`, `outcome`, `passed`, `failed`, `run`, `executedAt`, or `evidence`: requirement definitions and execution results stay distinct. | Scope | Test (TC-043), Inspection |

## Acceptance Criteria

| ID | Criteria | Verification |
|----|----------|--------------|
| FR-005-AC-1 | `spec_artifacts_iso/schemas/` carries `FR.json`, `NFR.json`, `StR.json`, `US.json`, `IT.json`, `TC.json`, `MasterRequirements.json`, `Index.json`, `Log.json`, and `Glossary.json`, each a JSON Schema 2020-12 document whose `$id` is `https://schemas.agent-ix.org/agent-ix/spec-artifacts-iso/<manifest version>/<Model>.json`, and each `type` `const` equals the archetype name of the map in Outputs. | Test (TC-041) |
| FR-005-AC-2 | Every `$ref` across the emitted bundle resolves to a shipped sibling or to a file name of the semantic-core 0.3.0 bundle (the file list of filament-core-data `toolchain.json` at the revision quire vendors), with no network read; no `$ref` names another semantic-core version or an unshipped file; no `$id` under the semantic-core base ships. | Test (TC-041) |
| FR-005-AC-3 | Every property of every emitted object schema is either constrained — its schema, after following `$ref`, carries `pattern`, `minLength`, `minimum`, `enum`, `const`, or `format`, or is an object whose properties are all constrained, or an array of such items, or `boolean`/`null` — or is free text, in which case its description carries `free text:` and a reason and its name is in the closed list the test enumerates (`Section.text`, the prose cells, `detail`, `summary`, `description`, `annotation`). | Test (TC-040) |
| FR-005-AC-4 | For each of the ten skeletons, the record built by the FR-007 reference mapping validates against the type's schema; a record with one extra property, one required section removed, a `line: 0`, an empty typed table, or a `status` outside its pattern fails schema validation naming the JSON path. A row id with the wrong *document* prefix (`FR-002-CON-1` inside `FR-001`) is not one of these: the row-id scalars are anchored to the artifact type, not to the document, so the schema accepts it by design and the FR-007 mapping rejects it against the locator's `id_pattern`, naming the line (FR-007-AC-6). | Test (TC-044, TC-045) |
| FR-005-AC-5 | `make schemas-check` exits 0 on the committed tree, and exits non-zero naming the file after any one emitted schema is edited by a single byte. | Test (TC-042) |
| FR-005-AC-6 | No emitted schema property is named `result`, `outcome`, `passed`, `failed`, `run`, `executedAt`, or `evidence`, and the `TC.json` description carries the sentence `execution results (pass/fail, run time, evidence) are not modelled`. | Test (TC-043) |
| FR-005-AC-7 | The set of emitted schema files equals the `files` list of `toolchain.json`, and the digest recomputed over those files (`sha256(concat(name + "\n" + bytes))`, sorted) equals the recorded digest, with no toolchain run. | Test (TC-061) |
| FR-005-AC-8 | Every emitted object schema declares its properties inline (no `allOf`, `oneOf`, `anyOf`, or `$ref` at the object's top level except the `anyOf` of a nullable scalar), so `unevaluatedProperties` and `additionalProperties` agree; the Python `jsonschema` validator accepts every golden record and rejects every TC-045 mutation that produces a record at all — the mapping-layer cases fail before a record exists, and are FR-007-AC-6's. | Test (TC-060) |
| FR-005-AC-9 | The sdist/wheel `include` list and the npm `files` list both name every shipped payload entry of Outputs and neither names any TypeSpec toolchain file; a fresh `poetry build` sdist and a fresh `npm pack` tarball carry the same payload entry set. | Test (TC-062) |

## Dependencies

- **Upstream**: [FR-002](./FR-002-unified-archetype-validation.md) (the locators the models type), [US-001](../usecase/US-001-consume-typed-iso-artifact-records.md), filament-core-data FR-031..FR-033 (`@agent-ix/semantic-core` 0.3.0, agent-ix/filament-core-data#35; the public npm publish that would make the package resolvable without a scope-routed registry is agent-ix/filament-core-data#11), filament-core-data ADR-0005 (TypeSpec as the structural source)
- **Downstream**: [FR-006](./FR-006-semantic-manifest-block.md) (references the emitted files by digest), [FR-007](./FR-007-markdown-mappings.md) (maps Markdown onto these models), [NFR-001](../non-functional/NFR-001-reproducible-offline-schema-projection.md), agent-ix/filament-core-data#36 and agent-ix/quire-contract-ir#52 (consume the schemas as fixtures)
