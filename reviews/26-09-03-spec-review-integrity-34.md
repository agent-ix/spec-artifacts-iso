---
id: SR-005
title: "Integrity review of the semantic data schema set (US-001, FR-005..FR-007, NFR-001, TM-001)"
type: SpecReview
analysis: integrity
scope: "spec/usecase/US-001-consume-typed-iso-artifact-records.md, spec/functional/FR-005-semantic-data-schemas.md, spec/functional/FR-006-semantic-manifest-block.md, spec/functional/FR-007-markdown-mappings.md, spec/non-functional/NFR-001-reproducible-offline-schema-projection.md, spec/tests.md"
review_set: all
---
# SR-005: Integrity review of the semantic data schema set

## Summary

Completeness, consistency and atomicity pass over the #34 set (US-001, FR-005,
FR-006, FR-007, NFR-001, matrix rows TC-039..TC-059) against the existing
FR-001..FR-004, StR-001, IT-001..IT-003, the shipped manifest, skeletons and
frontmatter schemas, semantic-core `main.tsp`, and the upstream contracts quoin
FR-070..FR-075 and quire-rs FR-069..FR-072. Traceability is intact: every AC
and CON of FR-005..FR-007 and every NFR-001 metric has a matrix row, and every
TC-039..TC-059 row names an existing criterion. Two findings are high: the
`exports`/`data_schema`-on-`artifact_types` form that FR-006-AC-3 requires
quire to load is a form quire-rs FR-069 refuses (`semantic.export-undeclared`),
and the `MasterRequirements` model is unspecified beyond three identity keys
while its sealed `Relationship` contradicts what FR-003 admits. Twelve medium
findings are internal inconsistencies (a Validation cell naming the wrong TC,
one cell name typed two ways, an AC no `$ref` property can satisfy, mapping
kinds that do not cover three models, a `typed-table` term collision with the
quoin contract) and unstated decisions (export-name to file map, dropped
frontmatter keys, engine version). Verdict: revise before planning.

## Traceability

| Chain | Result |
|-------|--------|
| US-001 -> FR | FR-005, FR-006, FR-007 (`implements`); each FR names US-001 upstream |
| FR -> StR | Transitive only: FR-005..007 -> US-001 -> StR-001 (`traces_to`); no FR names StR-001 and no StR-001 VC covers typed records (FND-234) |
| FR/NFR -> verification | FR-005: 7 AC + 4 CON, all in TM-001; FR-006: 6 AC + 2 CON, all in TM-001; FR-007: 7 AC + 3 CON, all in TM-001; NFR-001: 3 metrics -> TC-056..058 |
| TC-039..TC-059 -> criterion | 21 rows, every `Traces To` value names an existing FR-00x-AC/CON id or NFR-001 metric |
| Verification cell = matrix row | Mismatch on FR-005-CON-3 (cell TC-042, matrix TC-054); FR-006-AC-6 and FR-007-CON-3 cells carry no TC ref (FND-222) |
| NFR -> affected FR | NFR-001 `constrains` FR-005 and FR-006; neither FR references NFR-001 (FND-234) |

## Findings

| ID | Severity | Summary | Refs |
|----|----------|---------|------|
| FND-220 | high | FR-006-AC-3 requires `quire.Registry` to load the module with `exports` naming `artifact_types` and `data_schema` on `ArtifactTypeEntry`, but quire-rs FR-069 admits `exports` only over declared object types (`semantic.export-undeclared`) and the reference-form `data_schema` only on object types; this module declares `object_types: []`. Only the quoin half of the gap is hedged (FR-006-AC-6); the quire half makes AC-3 and TC-048 unachievable against the upstream contract as written. | FR-006-AC-3, FR-006-AC-6, TC-048, TC-055, quire-rs FR-069, quoin FR-070 |
| FND-221 | high | `MasterRequirements` is specified as `name`, `org`, `componentType` only. Unstated: `type` const, `title` (the H1 `heading` locator), `dependsOn`, `implementationLanguage` (string or null), `tags`, `standardsAlignment`, `securityCritical`, `relationships`, and what the three `from: heading` locators (`scope`, `system_overview`, `requirements_architecture`) yield. FR-003 Behavior explicitly admits annotation keys (`note`, `models`, `endpoints`) on relationship items, while FR-005 seals `Relationship { target, type, cardinality? }`, so a master spec FR-003 accepts fails the sealed model; TC-050 tests skeletons only and would not catch it. | FR-005 Behavior, FR-005-CON-1, FR-003 Behavior, FR-007 Behavior, TC-039, TC-050 |
| FND-222 | medium | Validation cells disagree with the matrix: FR-005-CON-3 says `Test (TC-042)` (the `schemas-check` test) while TM-001 backs it with TC-054 (the pin check); FR-006-AC-6 (`Demonstration`) and FR-007-CON-3 (`Inspection`) carry no TC reference although TM-001 rows TC-055 and TC-059 exist for them. | FR-005-CON-3, FR-006-AC-6, FR-007-CON-3, TC-042, TC-054, TC-055, TC-059 |
| FND-223 | medium | The `validation` cell is typed two ways inside FR-005: `Constraint.validation` is a plain `minLength: 1` string, `ValidationCriterion.validation` is a `Verification { method, testRefs }`. FR-005's own Constraints table writes `Test (TC-039, TC-040)` in that cell, so the test references of every CON row are lost as unparsed text. Naming the StR validation object `Verification` also blurs the 29148 validation/verification split the manifest comment on `validation_criteria_table` insists on. | FR-005 Behavior, FR-005-CON-1, FR-007 Behavior (typed-table), TC-039, TC-052 |
| FND-224 | medium | FR-005-AC-3 cannot be satisfied by any object-valued property: a `$ref` property in the emitted schema carries no `type` keyword, and the criterion admits `$ref` only "to a constrained scalar". `provenance`, `verification`, `story`, every `Section` field and the `relationships` items therefore fail AC-3 as written, so TC-040 either fails on every model or tests a weaker rule than the text. | FR-005-AC-3, TC-040 |
| FND-225 | medium | Field-name drift between FR-005 and FR-007: FR-007 maps the frontmatter key `object` but no FR-005 model declares it; `provenance.digest` is named only in FR-007; FR-007 writes `quality_attribute` where FR-005 writes `qualityAttribute` and no casing convention is stated; the types of `AcceptanceCriterion.detail`, `Story.text`, `SuccessCriterion.text` and `LogEntry.text` are not given. | FR-005 Behavior, FR-007 Behavior (frontmatter, typed-table), FR-007-AC-1 |
| FND-226 | medium | The five mapping kinds do not cover three models: `IT.successCriteria` (a token scan over Test Procedure), `Index.entries` and `Log.history` (list-item parses) and the `Story` regex parse are none of `frontmatter`, `section`, `table`, `typed-table`, `ocl-clause`, yet FR-007-AC-1 requires every property to carry exactly one of the five. Extents are also unspecified: `spec/log.md` already holds multi-paragraph entries with indented continuation lines, the story regex has no capture groups and greedy `.+`, and where `soThat` ends is undefined. | FR-005 Behavior, FR-007 Behavior, FR-007-AC-1, FR-007-AC-6, TC-052 |
| FND-227 | medium | `typed-table` collides with the quoin contract the manifest block is read under: quoin FR-070 defines `semantic.mappings` as the named representation mappings of FR-071..FR-073, where `typed-table` is the `Field \| Type \| Multiplicity \| Constraints` Properties table that quire-rs FR-070 lowers to `FieldDecl[]`. This module declares `typed-table` to mean AC/CON/VC row parsing, so a consumer honouring FR-070 reads a mapping the module does not ship. `mappings.yaml` also has no schema, yet TC-052 asserts its structure. | FR-006 Outputs, FR-007 Description, FR-007-AC-1, quoin FR-070, quoin FR-071 |
| FND-228 | medium | `ocl-clause` narrows the convention it declares it `uses` without saying so: quoin FR-072 and quire-rs FR-071 accept `sysml`, `fretish` and namespaced fences with an advisory, FR-007 makes every non-`ocl` fence a mapping error. Semantic-core `SourceLocus.sourceIdentity` is required while `Provenance.sourceIdentity` is optional, so a record built with no caller identity cannot carry a valid `ClauseRef.sourceSpan`. The clause text is "carried verbatim beside the record" with no named location, so FR-007-AC-4 compares bytes against nothing specified. | FR-007 Behavior (ocl-clause), FR-007-AC-4, FR-005 Behavior (`FR.invariants`), semantic-core `SourceLocus`, quire-rs FR-071 |
| FND-229 | medium | The export-name to schema-file rule is unstated (`master-requirements` to `MasterRequirements.json`, `index` to `Index.json`, `log` to `Log.json`); quoin FR-075 derives `typeIdentity` from the export name, so the two spellings diverge. `spec_artifacts_iso/schemas/` already holds ten `*-frontmatter.schema.json` files the projection does not produce, so `make schemas-check` ("a committed file the projection no longer produces") and FR-005-AC-7 need an exclusion rule. The `Glossary` `id` pattern is missing from FR-005's list (manifest default `GLO-{next:03d}`, frontmatter `minLength: 1`). | FR-005 Behavior, FR-005-AC-5, FR-005-AC-7, FR-006-AC-2, TC-042, TC-047 |
| FND-230 | medium | Sealed models silently drop frontmatter the shipped schemas declare: Index `title`, `description`, `okf_version`; Log `title`, `description`; Glossary `scope`, `description`; and corpus keys the `additionalProperties: true` schemas admit (`verification_method`, `evidence` on quire-rs FRs). FR-007's `lossless: false` clause names formatting only, not key loss, and FR-005-AC-6 forbids a property named `evidence`, so that key can never be modelled. The decision is not recorded. | FR-005 Behavior, FR-005-AC-6, FR-007 Behavior (round-trip), FR-005-CON-1 |
| FND-231 | medium | The `## Invariants` change is split across three FRs with a cycle: FR-005 declares `FR.invariants` and `depends_on` FR-002 only, the `invariants` locator (`from: code_block`) is added by FR-006, which `depends_on` FR-005, and FR-007-CON-1 claims the section as its only Markdown addition. FR-002-AC-6/AC-7 parity (TC-009, TC-010: skeleton headings and asserts match in both directions) is not addressed for the new H2 and the `### <clauseId>` H3, and a `code_block` locator carries no `assert.level`. The FR-006 bullet also states two obligations (byte-for-byte, except the locator). | FR-005 Behavior, FR-006 Behavior, FR-007-CON-1, FR-007 Outputs, FR-002-AC-6, FR-002-AC-7 |
| FND-232 | medium | FR-006-AC-6 passes on both outcomes ("either succeeds, or fails with `semantic.unknown-export`"), so it decides nothing; the code `semantic.unknown-export` exists in neither quoin FR-070 (no code named) nor quire-rs FR-069 (`semantic.export-undeclared`); and the matching Behavior bullet obliges "the module author" to record a diagnostic and file an issue, a process step rather than an observable system behavior. | FR-006 Behavior, FR-006-AC-6, TC-055 |
| FND-233 | medium | The engine version FR-006-AC-3 and FR-005-AC-2 run against is unstated: `pyproject.toml` pins `quire ^0.33.0`, quire-rs FR-069 (#388) is unreleased, and the suite's stale-wheel skip pattern (log 2026-08-18: 21 silent skips) would report TC-048 green. TC-041 resolves `$ref`s against "the semantic-core 0.1.0 bundle vendored by the installed quire wheel", a surface neither FR-069 nor FR-072 exposes to Python, while the `@agent-ix/semantic-core` npm package already in the devDependencies ships the same files. | FR-005-AC-2, FR-006-AC-3, FR-006 Behavior, NFR-001 Scope, TC-041, TC-048 |
| FND-234 | low | FR-005..FR-007 reach StR-001 only through US-001; StR-001's need and VC-1/VC-2 speak of activation and validated authoring, not typed records or the consumers US-001 names, and no FR references NFR-001 in its Dependencies although NFR-001 `constrains` FR-005 and FR-006. | US-001, StR-001, NFR-001, FR-005 Dependencies, FR-006 Dependencies |
| FND-235 | low | The census (7,119 documents, 266 bundles, 5,427 identified, 973 status documents, 16 spellings, 896/142 story forms, 156/182 IT, 30 constraint categories) is cited with no artifact, command or path; the figures are internally consistent (448+147+118+77+20 = 810, 16 = 5+11) but unreproducible, and NFR-001's "reference machine" for TC-058 is undefined. | FR-005 Inputs, FR-005 Behavior, NFR-001 Measurement, TC-058 |
| FND-236 | low | Inherited count drift: FR-002-AC-1, FR-003 Description and IT-002 (SC-01, AC-1) say "eight" archetypes and list AC/CON, which the manifest removed; the manifest declares ten `artifact_types`, and FR-005/FR-006 say ten. FR-003-AC-2 names an `artifact_type` const while the shipped schema and FR-005 use `type`. | FR-002-AC-1, FR-003 Description, FR-003-AC-2, IT-002, FR-005 Description, FR-006 Outputs |
| FND-237 | low | Two-obligation statements: NFR-001 Statement (reproduce byte-for-byte AND resolve offline), FR-006 Description (carry the block AND reference each schema), the FR-005 `provenance`/`relationships` bullet, and the FR-006 byte-for-byte/except bullet. Each is verifiable but not atomic. | NFR-001 Statement, FR-006 Description, FR-005 Behavior, FR-006 Behavior |
| FND-238 | low | Packaging assumptions left implicit: `@agent-ix/semantic-core` is not on the public npm registry (FR-005 says "from the npm registry"), CON-3 bans `.npmrc` so the registry is environmental and the lockfile `resolved` URLs pin it; `spec_artifacts_iso/semantic/` sits inside package data and will ship `package.json`/lockfile in the wheel unless excluded; whether a schema change forces a manifest `version` bump (the `$id` embeds it) is unstated; `href` pattern `^\.{0,2}/?[^:]*$` admits the empty string; the `\|` cell-escape rule for `table` mappings is unstated. | FR-005 Inputs, FR-005-CON-3, FR-005 Behavior (`IndexEntry`), FR-006 Outputs, FR-007 Behavior (table) |
| FND-239 | low | FR-006 Inputs cite quoin revision 3e842ce as the FR-035 schema provenance; the schema is filament-core-service's (quire-rs FR-069 vendors it at a77f31e) and the source revision is what a provenance record needs. "Before any engine sees the manifest" is a test-ordering claim no test can observe. The bundled schema constrains `targets` but the spec says nothing about `mappings` values, a hidden assumption that they are free strings. | FR-006 Inputs, FR-006 Behavior, FR-006-AC-4 |

## Verdict

Revise before `spec-to-plan`. The set is complete on traceability (every
criterion has a row, every row has a criterion) but not consistent: FND-220
makes FR-006-AC-3 unachievable against quire-rs FR-069 as written, and FND-221
leaves one of the ten exported models unspecified and in contradiction with
FR-003. The medium findings are each a one-paragraph edit; none changes the
design.

## Recommendations

1. **FND-220 / FND-232** — Decide the `artifact_types` question once, in
   FR-006, and make AC-3 and AC-6 single-outcome. Either file the quire-rs
   change (extend FR-069 `exports`/`data_schema` to `ArtifactTypeEntry`) and
   name it as an upstream dependency, or export nothing until it lands. Replace
   FR-006-AC-6 with:
   > `quoin module install path:<module root>` on quoin main at or after the
   > revision that admits `artifact_types` exports (agent-ix/quoin#NNN) exits 0
   > and records ten schema digests in `registry.json`.
   And add to FR-006 Dependencies: "quire-rs FR-069 CR-x (agent-ix/quire-rs#NNN):
   `exports` and reference-form `data_schema` admitted on `artifact_types`".
   Drop the "module author SHALL record ... file an issue" bullet; it is a
   ticket, not a behavior.
2. **FND-221** — Add a `MasterRequirements` bullet to FR-005 Behavior:
   > The `MasterRequirements` model SHALL carry `type` (`const:
   > master-requirements`), `name`, `org`, `componentType`
   > (`^[a-z][a-z0-9-]*$`), `title: Section` (the H1 `heading` locator),
   > `purpose: Section`, `references: Section`, and the optional frontmatter
   > fields the schema types — `implementationLanguage: string | null`,
   > `tags: string[]`, `dependsOn: string[]`, `standardsAlignment: string[]`,
   > `securityCritical: boolean`, `relationships: AnnotatedRelationship[]` —
   > where `AnnotatedRelationship` extends `Relationship` with
   > `unevaluatedProperties: true`, because FR-003 admits annotation keys on
   > master-spec relationship items.
   State what a `from: heading` locator yields (recommend: a `Section` over the
   heading's content, or nothing if it is a presence check, and say which).
3. **FND-222** — Change FR-005-CON-3's Validation cell to `Test (TC-054)`;
   change FR-006-AC-6 to `Demonstration (TC-055)` and FR-007-CON-3 to
   `Inspection (TC-059)`.
4. **FND-223** — Type the cell once. In FR-005 replace `Constraint { id, constraint,
   type, validation, line }` with `Constraint { id, constraint, type,
   validation: Verification, line }`, remove `validation` from the
   `minLength: 1` string list, and rename the object `VerificationCell`
   (or `MethodRef`) so it reads correctly under both the `Verification` and
   `Validation` columns.
5. **FND-224** — Replace FR-005-AC-3 with:
   > Every property of every emitted object schema either (a) carries a `type`
   > and at least one of `pattern`, `minLength`, `minimum`, `enum`, `const`,
   > `format`, or `items` satisfying (a) or (b); or (b) is a `$ref` to a
   > shipped sibling or semantic-core schema; or (c) carries a `description`
   > containing `free text:` followed by the reason.
6. **FND-225** — Add one sentence to FR-005 Description: "Record field names
   are camelCase projections of the snake_case frontmatter keys and locator
   names (`quality_attribute` -> `qualityAttribute`, `component_type` ->
   `componentType`)." Add `object?: string` to the seven `id`-bearing models,
   name `Provenance.digest` in FR-005, and type `detail?: Section`,
   `Story.text: string (free text)`, `SuccessCriterion.text`, `LogEntry.text`.
7. **FND-226** — Either add two kinds to the manifest `mappings` list and to
   FR-006 Outputs and FR-007 Description (`list` for `Index.entries` and
   `Log.history`; `token` for `IT.successCriteria`) or define them as
   `section` mappings with a `parse:` sub-key and say so in FR-007-AC-1.
   Specify extents: a `LogEntry.text` runs from the entry's first character
   after the em dash to the byte before the next `* **` item or the section
   end; a `SuccessCriterion.text` is the remainder of the token's line; the
   story regex gains named groups
   `(?is)\bas an?\b\s*(?P<asA>.+?)\s*\bi want\b\s*(?P<iWant>.+?)\s*\bso that\b\s*(?P<soThat>.+?)(?:\n\s*\n|\z)`.
8. **FND-227** — Rename the module's kinds so they do not shadow quoin's:
   `criteria-table` (or `id-table`) for the parsed row kind, and state in
   FR-006 that `semantic.mappings` lists this module's kinds and that none of
   quoin FR-071..FR-073's mappings apply (no `## Properties` on any ISO type).
   Ship `spec_artifacts_iso/mappings.schema.json` and add it to FR-007 Outputs.
9. **FND-228** — In FR-007's `ocl-clause` bullet either replace "a fence with
   another language is a mapping error" with the quoin FR-072 rule (accept
   `ClauseLanguage`, advisory for non-`ocl`) or add "narrower than quoin
   FR-072 on purpose: this module names one checker". Make
   `Provenance.sourceIdentity` required, or state that `sourceSpan` is omitted
   when no identity is supplied. Name where clause text lives, for example
   `examples/<type>.clauses.json` keyed by `clauseId`, and point FR-007-AC-4
   at it.
10. **FND-229** — Add to FR-006 Behavior: "`data_schema.schema` for an export
    `<name>` is `schemas/<Model>.json` where `<Model>` is the PascalCase of
    `<name>` (`master-requirements` -> `MasterRequirements`, `index` ->
    `Index`, `log` -> `Log`)." Add to FR-005 Outputs: "`make schemas-check`
    compares only the files `toolchain.json` lists; the
    `*-frontmatter.schema.json` files beside them are FR-002 data and out of
    scope." Add `^GLO-[0-9]+$` to the FR-005 id-pattern list.
11. **FND-230** — Extend the FR-007 round-trip bullet: "frontmatter keys with no
    mapping entry are dropped from the record; this is the only key loss and
    it is listed per model in `mappings.yaml` under `dropped:`." Give Index,
    Log and Glossary their declared optional fields (`title`, `description`,
    `okfVersion`, `scope`) or list them as dropped.
12. **FND-231** — Move the `invariants` locator into FR-007 (Outputs and
    Behavior), which already owns the section and the skeleton change, and
    make FR-006's bullet a single obligation: "Every existing
    `frontmatter_schema_ref`, `body_extraction` locator, and `assert` facet
    SHALL remain byte-for-byte as before this change." Add to FR-007-AC-5 or a
    new AC: "TC-009 and TC-010 pass with the extended FR skeleton: the
    `Invariants` locator asserts `level: 2` on the heading and the `###
    <clauseId>` H3 is admitted by the parity check." Add FR-007 to FR-005's
    `depends_on`-free wording ("the locator FR-007 adds").
13. **FND-233** — State the engine: "FR-006-AC-3 and TC-048 run against quire
    >= <first release carrying FR-069>; the test FAILS, not skips, on an older
    wheel." Resolve `$ref`s in TC-041 from the `@agent-ix/semantic-core`
    package's `generated/json-schema/` (already a pinned devDependency) and
    say so in FR-005-AC-2 and NFR-001 Scope.
14. **FND-234..FND-239** — Add a VC to StR-001 (or a StR-002) for typed
    consumption; reference NFR-001 from FR-005 and FR-006 Dependencies; record
    the census as `spec/reviews/census-2026-09-03.md` or a script path; fix
    "eight" to "ten" in FR-002-AC-1, FR-003 Description and IT-002 and
    `artifact_type` to `type` in FR-003-AC-2; split NFR-001 into a
    reproducibility statement and an offline statement (or two NFRs); write
    "from GitHub Packages (`@agent-ix` scope)" in FR-005 Inputs and add an
    exclusion of `semantic/node_modules` to the wheel; name the
    filament-core-service revision in FR-006 Inputs.
