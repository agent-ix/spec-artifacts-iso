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

The module SHALL declare one semantic data model per ISO artifact type — `FR`,
`NFR`, `StR`, `US`, `IT`, `TC`, `MasterRequirements`, `Index`, `Log`, and
`Glossary` — as TypeSpec source importing `@agent-ix/semantic-core` 0.1.0.

The module SHALL ship the JSON Schema 2020-12 projection of each model at
`spec_artifacts_iso/schemas/<Model>.json`.

Each model describes the record the archetype's existing `body_extraction`
locators already extract — every section body, every asserted table row, and
the frontmatter identity, relationships, status, and provenance — as typed
fields with constraints. A field is free text only where the requirement below
says so and the TypeSpec doc comment records why.

The models describe requirement *definitions*. A `TC` record describes a test
case; the outcome of executing it is not a field of any model.

## Inputs

- `spec_artifacts_iso/semantic/main.tsp`: the TypeSpec source (namespace
  `AgentIx.SpecArtifactsIso`, `@jsonSchema` base
  `https://schemas.agent-ix.org/agent-ix/spec-artifacts-iso/<manifest version>/`).
- `@agent-ix/semantic-core` 0.1.0 from the npm registry, pinned exactly, for
  `SemanticId`, `Identifier`, `ClauseRef`, and `SourceLocus`.
- `@typespec/compiler` 1.15.0 and `@typespec/json-schema` 1.15.0 as
  devDependencies of the TypeSpec package, with a lockfile.
- The existing `body_extraction` locators of `spec_artifacts_iso/manifest.yaml`
  (unchanged by this requirement).
- The corpus census of 2026-09-03 (7,119 documents in 266 `~/dev/*/spec`
  bundles, counted by document) that fixes the id, status, cardinality,
  verification-cell, and constraint-type populations the constraints below
  admit.

## Outputs

- `spec_artifacts_iso/schemas/<Model>.json` for the ten exported models and for
  every shared model they reference (`Section`, `Provenance`, `Relationship`,
  `AcceptanceCriterion`, `Constraint`, `ValidationCriterion`, `MeasurementRow`,
  `SuccessCriterion`, `Story`, `GlossaryTerm`, `IndexEntry`, `LogEntry`,
  `Verification`, and the scalar and enum schemas they use).
- `spec_artifacts_iso/semantic/generated/toolchain.json` recording the compiler
  and emitter versions and a SHA-256 digest over the emitted files, in the
  same shape as `packages/semantic-core/generated/toolchain.json` in
  filament-core-data.
- `make schemas` (regenerate) and `make schemas-check` (fail on any byte
  difference between the committed schemas and a fresh projection).

## Behavior

- Every emitted schema SHALL declare `$schema:
  https://json-schema.org/draft/2020-12/schema` and `$id:
  https://schemas.agent-ix.org/agent-ix/spec-artifacts-iso/<manifest version>/<Model>.json`,
  where `<manifest version>` equals `version` in `manifest.yaml`.
- Every `$ref` in an emitted schema SHALL name either a sibling under the same
  base or a schema under `https://schemas.agent-ix.org/semantic-core/0.1.0/`.
- The generator SHALL exclude from the shipped bundle any file the emitter
  produces for an imported semantic-core model.
- The generator SHALL seal every object schema (`unevaluatedProperties: { not: {} }`),
  so a record carrying a field no model declares fails validation.
- The `FR`, `NFR`, `StR`, `US`, `IT`, `TC`, and `Glossary` models SHALL carry
  `id`, `title`, and `type` (a `const`).
- The `MasterRequirements` model SHALL carry `name`, `org`, and `componentType`.
- The `Index` and `Log` models SHALL carry `type`.
- The `id` pattern of each model SHALL be the artifact type's own prefix (`^FR-[0-9]+$`, `^NFR-[0-9]+$`, `^StR-[0-9]+$`,
  `^US-[0-9]+$`, `^IT-[0-9]+$`, `^TC-[0-9]+$`), which is the population the
  census measured (every one of the 5,427 identified requirement and test
  documents).
- Every model SHALL carry `provenance: Provenance` — the document's
  corpus-relative `path`, its `sourceIdentity` (a semantic-core `SemanticId`,
  optional because the `validate_document` surface has none), and a
  `sha256:<64 hex>` digest over the document bytes — and every requirement,
  test, and glossary model SHALL carry `relationships: Relationship[]` with
  `target` (`^ix://`), `type` (an edge verb, `^[a-z][a-z0-9_]*$`), and an
  optional `cardinality` matching `^[0-9A-Za-z*]+(\.\.[0-9A-Za-z*]+)?(:[0-9A-Za-z*]+(\.\.[0-9A-Za-z*]+)?)?$`
  (the census population: `1:1`, `1:N`, `N:1`, `n:1`, `1`, `0:1`, `many:1`,
  `1..1`, `0..1`).
- Every model SHALL carry an optional `status: ArtifactStatus`, a string
  matching `^[A-Za-z][A-Za-z_-]*$`. The value set is NOT closed by this
  requirement: the census counts 16 spellings across 973 documents
  (`APPROVED` 448, `IMPLEMENTED` 147, `DRAFT` 118, `PROPOSED` 77, `SUPERSEDED`
  20 and 11 minor forms), and closing it is a vocabulary change that needs a
  sweep-and-report decision of its own, not a side effect of this schema.
- Every section a `section_body` locator extracts SHALL map to a `Section`
  field — `text` (the byte-exact section content, quire-rs FR-008),
  `startLine`, and `endLine` (1-based document lines) — required where the
  locator is `required: true` and optional otherwise. The `text` is free text
  because the section is authored prose whose sentence grammar is checked by the
  `iso-spec-core` EARS grammar as an advisory, not by a schema.
- Every table a `table_row` locator asserts SHALL map to an array of typed row
  objects, one per data row in authored order, with `line` on each row:
  - `FR.constraints`: `Constraint { id: ^FR-[0-9]+-CON-[0-9]+$, constraint,
    type, validation, line }`, present only when the section is.
  - `FR.acceptanceCriteria` and `NFR.acceptanceCriteria`: `AcceptanceCriterion
    { id: ^(FR|NFR)-[0-9]+-AC-[0-9]+$, criteria, verification: Verification,
    detail?, line }`, where `Verification { method, testRefs: ^TC-[0-9]+$[] }`
    splits the cell `Test (TC-035, TC-036)` into the method token and the
    annotated test-case references, and `detail` carries the body of a
    supplementary `### <criterion id>` subsection when one exists.
  - `StR.validationCriteria`: `ValidationCriterion { id: ^StR-[0-9]+-VC-[0-9]+$,
    criteria, validation: Verification, line }`.
  - `NFR.measurement`: `MeasurementRow { metric, target, threshold, method, line }`.
  - `Glossary.terms`: `GlossaryTerm { term, definition, line }`.
  - The `criteria`, `constraint`, `type`, `validation`, `metric`, `target`,
    `threshold`, `method`, `term`, and `definition` cells SHALL be strings with
    `minLength: 1`; `type` (census: 30 distinct constraint categories),
    `Verification.method` (census: more than 30 spellings, of which the lint
    rule `ac-verification-method` admits four as an advisory), and `target`
    and `threshold` (census: prose quantities such as `600 imports/s`) are free
    text because their vocabularies are owned by advisory lint rules or by no
    rule at all, and a schema that closed them would reject the corpus it
    describes.
- `US.story` SHALL be a `Story { asA, iWant, soThat, text }` parsed from the
  `matches` regex the `story` locator already asserts, with the bold markers
  the skeleton uses stripped (census: 896 bold, 142 plain).
- `IT.successCriteria` SHALL be `SuccessCriterion { id: ^IT-[0-9]+-SC-[0-9]+$,
  text, line }[]`, one per `IT-XXX-SC-NN` token in `## Test Procedure`, and MAY
  be empty (the `it-success-criteria` lint rule is advisory; census: 156 of 182
  IT documents carry tokens).
- `Index.entries` SHALL be `IndexEntry { title, href, summary?, line }[]`, one
  per `* [title](href) - summary` line under `## Contents`, where `href` is a
  relative path (`^\.{0,2}/?[^:]*$`, never a scheme), because index links are
  local navigation and not knowledge-graph edges.
- `Log.history` SHALL be `LogEntry { date: ^[0-9]{4}-[0-9]{2}-[0-9]{2}$, text,
  line }[]`, one per `* **YYYY-MM-DD** — text` entry under `## History`.
- `FR.invariants` SHALL be an optional `ClauseRef[]` (semantic-core) mapped from
  an optional `## Invariants` section by the `ocl-clause` mapping of FR-007;
  the clause text is never parsed.
- `NFR.qualityAttribute` SHALL be the twelve-value enum the NFR frontmatter
  schema already declares, and `MasterRequirements.componentType` SHALL match
  `^[a-z][a-z0-9-]*$` as the frontmatter schema does; the models restate no
  constraint more loosely than the frontmatter schema beside them.
- If `make schemas-check` finds a committed schema whose bytes differ from the
  fresh projection, a committed file the projection no longer produces, or a
  `toolchain.json` that differs, then it SHALL exit non-zero naming each file.
- If the TypeSpec package's `@jsonSchema` base does not embed the manifest
  `version`, then `make schemas` SHALL fail naming both values before writing
  any file.

## Constraints

| ID | Constraint | Type | Validation |
|----|------------|------|------------|
| FR-005-CON-1 | The models SHALL neither add a field that no locator, frontmatter schema, or FR-007 mapping produces nor drop a locator output: the record is the typed form of what `body_extraction` already extracts. | Integrity | Test (TC-039, TC-040) |
| FR-005-CON-2 | The emitted bundle SHALL carry no `$ref` outside the module bundle and the semantic-core 0.1.0 bundle, so that a consumer resolves every reference without a network read. | Boundary | Test (TC-041) |
| FR-005-CON-3 | The TypeSpec package SHALL pin `@typespec/compiler` and `@typespec/json-schema` at 1.15.0 and `@agent-ix/semantic-core` at 0.1.0 with a committed lockfile, no `file:` or `link:` reference, and no `.npmrc` in the repository. | Reproducibility | Test (TC-042) |
| FR-005-CON-4 | Requirement definitions and execution results SHALL stay distinct: no model carries a pass/fail, run, or evidence field. | Scope | Test (TC-043) |

## Acceptance Criteria

| ID | Criteria | Verification |
|----|----------|--------------|
| FR-005-AC-1 | `spec_artifacts_iso/schemas/` carries `FR.json`, `NFR.json`, `StR.json`, `US.json`, `IT.json`, `TC.json`, `MasterRequirements.json`, `Index.json`, `Log.json`, and `Glossary.json`, each a JSON Schema 2020-12 document whose `$id` is `https://schemas.agent-ix.org/agent-ix/spec-artifacts-iso/<manifest version>/<Model>.json`. | Test (TC-041) |
| FR-005-AC-2 | Every `$ref` across the emitted bundle resolves to a shipped sibling or to a file of the semantic-core 0.1.0 bundle vendored by the installed quire wheel; no `$ref` names another semantic-core version or an unshipped file. | Test (TC-041) |
| FR-005-AC-3 | Every property of every emitted object schema carries a type and at least one constraint keyword (`pattern`, `minLength`, `minimum`, `enum`, `const`, `format`, `$ref` to a constrained scalar, or `items` of such), or its TypeSpec doc comment contains the token `free text:` followed by the reason. | Test (TC-040) |
| FR-005-AC-4 | For each of the ten skeletons, the record built by the FR-007 reference mapping validates against the type's schema, and a record with one extra property, one row whose id has the wrong prefix, or one required section removed fails validation naming the path. | Test (TC-044, TC-045) |
| FR-005-AC-5 | `make schemas-check` exits 0 on the committed tree, and exits non-zero naming the file after any one emitted schema is edited by a single byte. | Test (TC-042) |
| FR-005-AC-6 | No emitted schema property is named `result`, `outcome`, `passed`, `status_of_run`, `executed_at`, or `evidence`, and the `TC` model's doc comment states that execution results are not modelled. | Test (TC-043) |
| FR-005-AC-7 | The set of emitted schema files equals the set `toolchain.json` records, and the bundle digest recomputed over those files equals the recorded digest. | Test (TC-042) |

## Dependencies

- **Upstream**: [FR-002](./FR-002-unified-archetype-validation.md) (the locators the models type), [US-001](../usecase/US-001-consume-typed-iso-artifact-records.md), filament-core-data FR-031..FR-033 (`@agent-ix/semantic-core` 0.1.0, agent-ix/filament-core-data#35), filament-core-data ADR-0005 (TypeSpec as the structural source)
- **Downstream**: [FR-006](./FR-006-semantic-manifest-block.md) (references the emitted files by digest), [FR-007](./FR-007-markdown-mappings.md) (maps Markdown onto these models), agent-ix/filament-core-data#36 and agent-ix/quire-contract-ir#52 (consume the schemas as fixtures)
