---
id: SR-010
title: "ears-conformance review of FR-005, FR-006, FR-007, NFR-001 (semantic data schemas, #34)"
type: SpecReview
analysis: ears-conformance
scope: "spec/functional/FR-005-semantic-data-schemas.md; spec/functional/FR-006-semantic-manifest-block.md; spec/functional/FR-007-markdown-mappings.md; spec/non-functional/NFR-001-reproducible-offline-schema-projection.md"
review_set: all
---

## Summary

EARS requirement-grammar review of the four requirement-bearing files on
`spec/34-semantic-data-schemas` (ticket agent-ix/spec-artifacts-iso#34): 51
`SHALL`-bearing statements across FR-005 (25 Behavior/Description/Constraint
statements), FR-006 (11), FR-007 (14) and NFR-001 (1). The engine
(`quire 0.31.0`, engine 0.46.0, `iso-spec-core` grammar, quire-rs FR-042)
flags one statement (FR-006 line 71: `unclassifiable` + `missing-subject`); the
hand pass finds 19 further defects the tokenizer does not see. The dominant
defect is **non-singular** statements — nine bullets, one Description and the
NFR Statement pack two or three `SHALL` into one sentence — followed by
**field-typing copulas** (`X SHALL be Y`) whose subject is a schema field rather
than a component. One statement (FR-006 quoin install, lines 72-78) is rated
high: it mixes `When ... If ... then`, places an obligation on an external
system (`quoin SHALL accept`) and on a person (`the module author SHALL record`),
and contradicts its own acceptance criterion. No vague-verb
(support/handle/manage/process/provide/enable) hits and no `etc` /
`appropriate` / `as needed` ambiguity terms were found; 29 of 51 statements are
clean.

## Verdict

**Revise before plan.** One high and twelve medium findings. None changes the
intended design; every rewrite below is a split or a re-subjecting that keeps
the authored obligation. The high finding (FND-321) must be resolved because
the Behavior bullet and FR-006-AC-6 currently disagree on what "done" means when
the installed quoin refuses the `exports` list. The mediums degrade traceability
(one Behavior bullet maps to two or three AC rows) and should be split before
the Test Matrix is built so each `SHALL` binds to one AC.

## Engine Findings

Command run from the repository root:

```
quire validate --scope /home/peter/dev/spec-artifacts-iso "spec/functional/FR-005*.md" "spec/functional/FR-006*.md" "spec/functional/FR-007*.md" "spec/non-functional/*.md"
```

Verbatim `[ears:...]` / `[quality:...]` warning lines (the preceding
`DuplicateModuleName` / `DuplicateArchetype` / `DuplicateInverseEdge` lines are
registry-load diagnostics from two copies of the module on the search path,
not grammar findings):

```
warning: /home/peter/dev/spec-artifacts-iso/spec/functional/FR-006-semantic-manifest-block.md: line 71: [ears:unclassifiable] statement does not match any EARS pattern (ubiquitous / event / state / unwanted / optional / complex) [grammar]
warning: /home/peter/dev/spec-artifacts-iso/spec/functional/FR-006-semantic-manifest-block.md: line 71: [ears:missing-subject] statement names no system/actor subject before `shall` [grammar]
```

No `[quality:...]` warnings were emitted. FR-005, FR-007 and NFR-001 produced
no engine warnings; the engine treats each multi-line bullet as one statement
and does not count `SHALL` occurrences inside it, so the non-singular findings
below are all validator-missed.

## Findings

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-320 | medium | FR-006 Behavior lines 68-71 (engine: `unclassifiable`, `missing-subject`): `When the module is loaded ..., the load SHALL succeed ... and validate_document ... SHALL still report is_valid` — two `SHALL`, subject "the load" is an event not a component; split into two `When` statements with `quire.Registry` as subject. | FR-006 |
| FND-321 | high | FR-006 Behavior lines 72-78: `When the module is installed by quoin, quoin SHALL accept the block. If the installed quoin refuses ... then the module author SHALL record ..., file ..., and keep ...` — `When ... If ... then` is unclassifiable; obligations fall on an external system (quoin) and a person (the module author), not on the module; the `SHALL accept` contradicts FR-006-AC-6, which accepts a refusal. Changes what "done" means. | FR-006 |
| FND-322 | medium | FR-006 Description lines 21-26 packs two `SHALL` (`SHALL carry one semantic block ... and SHALL reference ... the emitted schema`); split into a block statement and a reference statement. | FR-006 |
| FND-323 | medium | FR-006 Behavior lines 63-67 packs two `SHALL` on the bundled FR-035 schema (`SHALL accept ... and SHALL reject ...` four cases); split into one accept statement and one `If ... then` reject statement. | FR-006 |
| FND-324 | medium | FR-005 Behavior lines 85-93 packs two `SHALL` with different subjects (`Every model SHALL carry provenance ... and every requirement, test, and glossary model SHALL carry relationships ...`); split. | FR-005 |
| FND-325 | medium | FR-005 Behavior lines 145-148 packs two `SHALL` over two models (`NFR.qualityAttribute SHALL be ... and MasterRequirements.componentType SHALL match ...`) plus a trailing rule without `SHALL` (`the models restate no constraint more loosely`); split into three statements. | FR-005 |
| FND-326 | medium | FR-005 Behavior field-typing copulas at lines 129, 132, 136, 140, 142 (`US.story SHALL be a Story ...`, `IT.successCriteria SHALL be ...`, `Index.entries SHALL be ...`, `Log.history SHALL be ...`, `FR.invariants SHALL be ...`): subject is a schema field, response is `be`; re-subject each on the model (`The US model SHALL declare story as ...`). | FR-005 |
| FND-327 | medium | FR-005 Behavior lines 106-128: the enumerated `Every table ... SHALL map to ...` statement carries a second `SHALL` inside its own sub-list (line 120-121, `cells SHALL be strings with minLength: 1`) followed by five lines of census rationale; lift the cell rule to its own bullet and move the rationale to Description. | FR-005 |
| FND-328 | low | FR-005 Behavior lines 81-84: `The id pattern of each model SHALL be the artifact type's own prefix ..., which is the population the census measured` — `SHALL be` copula with a property subject and rationale appended; re-subject on the model and drop the relative clause. | FR-005 |
| FND-329 | low | FR-005 Behavior lines 94-99: the obligation (`Every model SHALL carry an optional status ...`) is followed in the same bullet by four lines of non-normative census rationale (`The value set is NOT closed ... needs a sweep-and-report decision`); move the rationale to Description. | FR-005 |
| FND-330 | low | FR-005 Behavior lines 149-151: `If make schemas-check finds ..., then it SHALL exit non-zero` — pronoun subject `it`; name `make schemas-check` in the response clause. | FR-005 |
| FND-331 | medium | FR-005-CON-4 (line 163): `Requirement definitions and execution results SHALL stay distinct: no model carries ...` — subject is a concept, response `stay distinct` is unverifiable on its own; the verifiable rule is the colon clause. Restate with the models as subject. | FR-005 |
| FND-332 | low | FR-005-CON-1 (line 160): `The models SHALL neither add ... nor drop ...: the record is the typed form ...` — two prohibitions under one `SHALL` plus rationale after the colon; acceptable as a complex constraint but tighter as two rows or one row without the rationale. | FR-005 |
| FND-333 | medium | FR-007 Behavior lines 70-77: one `SHALL` (`ocl-clause mappings SHALL map ...`) followed by two further obligations stated declaratively (`the clause text is carried verbatim ... and never parsed`, `a heading whose text is not an Identifier ... is a mapping error`); the second is an unwanted condition and needs an `If ... then ... SHALL` form. | FR-007 |
| FND-334 | medium | FR-007 Behavior lines 81-86: `the mapping SHALL record authority: markdown ...; no consumer SHALL regenerate the Markdown ...` — two `SHALL`, the second on `consumer`, an actor outside the module; split, and restate the second as a module constraint (already FR-007-CON-3). | FR-007 |
| FND-335 | medium | FR-007 Behavior lines 87-89 packs three `SHALL` (`Every property ... SHALL have exactly one mapping entry, and every mapping entry SHALL name ...; ... columns SHALL equal ...`); split into three bullets. | FR-007 |
| FND-336 | low | FR-007 Behavior lines 58-61: `section mappings SHALL name ... and fill ...; the Story field additionally parses asA, iWant, and soThat` — the `Story` parsing is an obligation with no `SHALL`; give it its own statement. | FR-007 |
| FND-337 | low | FR-006 Behavior lines 79-81: `... the module's own test suite SHALL fail ..., before any engine sees the manifest` — the temporal qualifier `before any engine sees` names no observable event; drop it or restate as the test suite running in `make test`. | FR-006 |
| FND-338 | medium | FR-007-CON-3 (line 104): `The record SHALL be a projection: the mapping reads Markdown and writes nothing back; no file in the module derives Markdown from a record` — the `SHALL` is on a description (`be a projection`); the obligations follow the colon without `SHALL`. Restate with the module as subject. | FR-007 |
| FND-339 | medium | NFR-001 Statement lines 16-18 packs two `SHALL` (`SHALL reproduce ... byte-for-byte ... and SHALL validate and resolve the bundle with no network read`) and quantifies over `any machine with the pinned toolchain`; split into a reproducibility statement and an offline statement, and bind "any machine" to the Scope's operational context. | NFR-001 |

## Recommendations

Each rewrite keeps the authored obligation and only splits, re-subjects, or
moves rationale. Line numbers refer to the files at the head of
`spec/34-semantic-data-schemas`.

### FND-321 (high) — FR-006 lines 72-78

Replace the bullet with two statements on the module and move the process
obligation out of Behavior:

- `When the module is installed by quoin (quoin module install path:<module root>) built from main at 3e842ce or later, the manifest SHALL pass the install with no diagnostic other than semantic.unknown-export.`
- `If the installed quoin emits semantic.unknown-export for an artifact_types name in semantic.exports, then the manifest SHALL keep the exports list and the data_schema references as specified in Outputs.`

Move "record the exact diagnostic in this requirement's change log and file an
issue on agent-ix/quoin" to the `Verification` text of FR-006-AC-6 (it is a
verification procedure, not a module behaviour), and keep FR-006-AC-6 as the
acceptance criterion — the rewritten statements now agree with it.

### FND-320 (medium) — FR-006 lines 68-71

- `When quire.Registry loads the module root, the registry SHALL resolve every exported type's schema and record its digest.`
- `When validate_document runs over each skeleton after the module is loaded by quire.Registry, the registry SHALL report is_valid for every skeleton.`

### FND-322 (medium) — FR-006 lines 21-26

- `The module manifest (spec_artifacts_iso/manifest.yaml) SHALL carry one semantic block under the quoin FR-070 contract (contract_version: 1.0.0).`
- `The module manifest SHALL reference, on every artifact type FR-005 gives a model, the emitted schema by module-relative path and SHA-256 digest (data_schema: { schema: schemas/<Model>.json, digest: sha256:<hex> }).`

The `so that quoin at install time and quire at load time bind ...` clause is
rationale; keep it as a separate sentence without `SHALL`.

### FND-323 (medium) — FR-006 lines 63-67

- `The bundled FR-035 schema SHALL accept the semantic block and the reference form of data_schema.`
- `If a manifest carries a semantic block with a key outside the admitted ten, a data_schema mixing schema/digest with any other key, a package that is not <org>/<repo>, or a targets value outside the registry, then the bundled FR-035 schema SHALL reject the manifest naming the offending key.`

### FND-324 (medium) — FR-005 lines 85-93

- `Every model SHALL carry provenance: Provenance — the document's corpus-relative path, its optional sourceIdentity (a semantic-core SemanticId), and a sha256:<64 hex> digest over the document bytes.`
- `Every requirement, test, and glossary model SHALL carry relationships: Relationship[] with target (^ix://), type (^[a-z][a-z0-9_]*$), and an optional cardinality matching <pattern>.`

Move the census population list (`1:1`, `1:N`, ...) to Inputs beside the
census entry.

### FND-325 (medium) — FR-005 lines 145-148

- `The NFR model SHALL declare qualityAttribute as the twelve-value enum the NFR frontmatter schema declares.`
- `The MasterRequirements model SHALL constrain componentType with ^[a-z][a-z0-9-]*$.`
- `The models SHALL restate no frontmatter constraint more loosely than the frontmatter schema beside them.`

### FND-326 (medium) — FR-005 lines 129, 132, 136, 140, 142

- `The US model SHALL declare story as Story { asA, iWant, soThat, text }, parsed from the matches regex the story locator asserts, with the skeleton's bold markers stripped.`
- `The IT model SHALL declare successCriteria as SuccessCriterion { id: ^IT-[0-9]+-SC-[0-9]+$, text, line }[], one per IT-XXX-SC-NN token in ## Test Procedure; the array MAY be empty.`
- `The Index model SHALL declare entries as IndexEntry { title, href, summary?, line }[], one per * [title](href) - summary line under ## Contents, with href a relative path (^\.{0,2}/?[^:]*$).`
- `The Log model SHALL declare history as LogEntry { date: ^[0-9]{4}-[0-9]{2}-[0-9]{2}$, text, line }[], one per * **YYYY-MM-DD** — text entry under ## History.`
- `The FR model SHALL declare invariants as an optional ClauseRef[] mapped from an optional ## Invariants section by the FR-007 ocl-clause mapping.`

The parenthetical census counts and the "because index links are local
navigation" reason belong in Description.

### FND-327 (medium) — FR-005 lines 106-128

Keep the enumerated statement for the five row shapes and lift the cell rule
out of the sub-list:

- `The row models SHALL declare the criteria, constraint, type, validation, metric, target, threshold, method, term, and definition cells as strings with minLength: 1.`

Move the "free text because their vocabularies are owned by advisory lint
rules" paragraph to Description, where the free-text policy already lives
(lines 29-30).

### FND-331 (medium) — FR-005-CON-4

- `The models SHALL carry no field that records a pass/fail outcome, a run, or evidence of executing a test case.`

### FND-333 (medium) — FR-007 lines 70-77

- `ocl-clause mappings SHALL map each ### <clauseId> heading under ## Invariants that owns one fenced block tagged ocl to a semantic-core ClauseRef { language: ocl, clauseId, sourceSpan }, where sourceSpan is a SourceLocus over the fence (startLine the opening fence line, endLine the closing fence line, columns per quire-rs FR-071).`
- `The ocl-clause mapping SHALL carry the clause text verbatim beside the record and SHALL NOT parse it.` (a `SHALL`/`SHALL NOT` pair on one subject; split further if the matrix needs one AC each)
- `If a ### heading under ## Invariants is not an Identifier, or its fence carries a language other than ocl, then the mapping SHALL fail naming the line.`

### FND-334 (medium) — FR-007 lines 81-86

- `The mapping SHALL record authority: markdown and round_trip: derived per model, lossless: true on section fields, and lossless: false on table, typed-table, and frontmatter fields.`

Delete `no consumer SHALL regenerate the Markdown from the record as an
authority` from Behavior; FR-007-CON-3 (as rewritten in FND-338) already
carries the module-side prohibition, and an obligation on consumers is outside
this module's boundary.

### FND-335 (medium) — FR-007 lines 87-89

- `The mapping SHALL carry exactly one entry for every property of every emitted model.`
- `Every mapping entry SHALL name a property the model declares.`
- `Every table or typed-table mapping SHALL carry a column list equal to the locator's assert.columns.`

### FND-338 (medium) — FR-007-CON-3

- `The module SHALL ship no code that derives Markdown from a record; the mapping reads Markdown and writes no file.`

### FND-339 (medium) — NFR-001 Statement

- `The module SHALL reproduce its emitted schema bundle byte-for-byte from the committed TypeSpec source and lockfile on a clean clone with the pinned toolchain installed (Scope: operational context).`
- `The module SHALL validate and resolve the emitted bundle with no network read.`

### Low findings (FND-328, FND-329, FND-330, FND-332, FND-336, FND-337)

- FND-328: `Each model SHALL constrain id with the artifact type's own prefix pattern (^FR-[0-9]+$, ^NFR-[0-9]+$, ^StR-[0-9]+$, ^US-[0-9]+$, ^IT-[0-9]+$, ^TC-[0-9]+$).`
- FND-329: keep line 94-95 as the statement; move `The value set is NOT closed ...` to Description.
- FND-330: `..., then make schemas-check SHALL exit non-zero naming each file.`
- FND-332: `The models SHALL declare no field that no locator, frontmatter schema, or FR-007 mapping produces.` and `The models SHALL declare a field for every locator output.`
- FND-336: `The section mapping for US.story SHALL additionally parse asA, iWant, and soThat from the section text using the regex the story locator asserts.`
- FND-337: `If any data_schema.digest differs from the SHA-256 of the shipped file, then make test SHALL fail naming the type, the recorded digest, and the computed digest.`
