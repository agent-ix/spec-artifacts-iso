---
id: SR-008
title: "Risk and complexity review of the semantic data schemas review set (#34)"
type: SpecReview
analysis: risk-complexity
scope: "spec/usecase/US-001-consume-typed-iso-artifact-records.md, spec/functional/FR-005-semantic-data-schemas.md, spec/functional/FR-006-semantic-manifest-block.md, spec/functional/FR-007-markdown-mappings.md, spec/non-functional/NFR-001-reproducible-offline-schema-projection.md"
review_set: all
---

# SR-008: Risk and complexity review of the semantic data schemas review set (#34)

## Summary

Risk and volatility scoring of US-001, FR-005, FR-006, FR-007, and NFR-001
(branch `spec/34-semantic-data-schemas`, tests.md rows TC-039..TC-059) against
the code the requirements bind to: `@typespec/json-schema` 1.15.0 as configured
in filament-core-data `packages/semantic-core` (`emitAllModels`, `emitAllRefs`,
`seal-object-schemas`), quoin `src/semantic/data-schema.ts` and `manifest.ts`
at 3e842ce, quire-rs `src/semantic/resolver.rs` and `loader/mod.rs` at 17b80e4
(engine 0.46.0, `jsonschema` crate 0.18.3), the module manifest, the ten
skeletons, and the I1/I2/I3 parity tests. The set is implementable, but two
findings are contradictions the plan cannot route around (a `ClauseRef.sourceSpan`
that cannot be built without a `SemanticId` the spec calls optional, and a
`Verification` cell rule that silently drops test references for the corpus
forms the spec itself counts), and four medium risks are external-contract
volatility (an unpublished quire wheel, a deterministic quoin `unknown-export`
failure, version-embedded `$id` churn, and two validators evaluating
`unevaluatedProperties`). Sixteen findings: 2 high, 8 medium, 6 low.

## Verdict

**Conditionally ready for `spec-to-plan`.** Resolve FND-280 and FND-281 by
spec edit before tasking (both change the golden records and the mapping rules
every downstream consumer copies). The eight medium findings are plan
constraints and small spec edits that can land in the same revision; none
blocks decomposition. No requirement needs to be split into new documents; the
FR model (FND-294) is large but coherent, and the split belongs in the plan's
task graph, not the spec. The `## Invariants` / `ocl-clause` slice (FND-288)
should be the last, dependency-free task of the plan so the consumer story
can ship without it.

## Findings

| ID | Severity | Summary | Refs |
|----|----------|---------|------|
| FND-280 | high | `ClauseRef.sourceSpan` is a semantic-core `SourceLocus` whose `sourceIdentity` (a `SemanticId`) and `startColumn` are REQUIRED in the vendored 0.1.0 schema; FR-007-AC-4 demands a `sourceSpan` on the FR skeleton's golden record while FR-005/FR-007 make `sourceIdentity` optional and caller-supplied, so the golden record either fabricates an identity or fails `ClauseRef.json` | FR-007, FR-005 |
| FND-281 | high | The `typed-table` verification split (`method` = text before the first `(`, `testRefs` = `TC-` tokens inside the parentheses) silently drops references for corpus forms such as `Test: TC-001`, `Test, TC-001`, `Integration Test` (the FR skeleton's own CON row), and yields an empty `method` for the 41 empty cells that `minLength: 1` then rejects; the spec decides neither the superset rule nor the empty-cell outcome | FR-007, FR-005 |
| FND-282 | medium | FR-006-AC-3 / TC-048 need a quire wheel carrying FR-069 (`Registry` reference-form resolution, quire-rs #388 at 17b80e4, 117 commits past v0.45.0, unreleased); `pyproject.toml` pins `quire ^0.33.0` and the spec names only "the quire wheel this module tests against" | FR-006, NFR-001 |
| FND-283 | medium | quoin `manifest.ts` (3e842ce) checks `semantic.exports` against `object_types` only and `data-schema.ts` resolves `data_schema` per object type only, so `quoin module install` fails deterministically with `semantic.unknown-export` for all ten exports and FR-075 derives no pins; FR-006-AC-6 treats this as one of two outcomes and defers the quoin issue to implementation time | FR-006 |
| FND-284 | medium | `$id` embeds the manifest `version`, so every version bump rewrites ten `$id`s, ten `data_schema.digest`s, and `toolchain.json`; no requirement names the target that writes the manifest digests, leaving a hand-edited two-phase change with an inconsistency window that FR-006's own digest test turns red | FR-005, FR-006, NFR-001 |
| FND-285 | medium | Two engines evaluate the sealed schemas: Python `jsonschema` 4.25 (spec suite) and `jsonschema` crate 0.18.3 (quire); `unevaluatedProperties: {not: {}}` behaves identically only when no object schema composes through `allOf`/`$ref` (TypeSpec `extends`/spread), and a Python mapper that emits `null` for an absent optional fails a non-nullable schema in both; no test compares the two verdicts | FR-005, FR-007 |
| FND-286 | medium | `Story` parsing reuses the presence regex `(?is)\bas an?\b.+\bi want\b.+\bso that\b` as a parser: greedy `.+` under DOTALL splits on the last `I want`, `soThat` runs to the end of the section (the skeleton has a trailing paragraph), and the bold-stripping rule is unstated for `**As an**`, `_As a_`, `As a:` (census 896 bold / 142 plain) | FR-007, FR-005 |
| FND-287 | medium | The reference mapper is test-support Python that the module does not ship, while three consumers (quire-contract-ir#52 Rust, filament-core-data#36 generators, the Filament extraction API) must rebuild it from prose; `mappings.yaml` carries kinds and sources but none of the regexes, so the oracle's behaviour is not in the contract | FR-007 |
| FND-288 | medium | `## Invariants` / `ocl-clause` / `FR.invariants` is scope the consumer story never asked for (zero corpus instances); it adds a Markdown form, a `code_block` locator, a mapping kind, and the FND-280 coupling; quire's `eval_code_block` yields only the first fence unless `multiple: true`, so a two-clause FR violates FR-005-CON-1 as the locator is written in FR-006 | FR-005, FR-006, FR-007, US-001 |
| FND-289 | medium | NFR-001 byte reproducibility inherits semantic-core's generator shape, which pipes every file through `biome format` without recording biome in `toolchain.json`; `emitAllRefs: true` also emits the 30 imported semantic-core models into the same directory, and a name-based filter would keep a colliding module model (e.g. a future `Identifier`) | FR-005, NFR-001 |
| FND-290 | low | `LogEntry.date` is required and the entry form pins the em dash `—`; the census counts ~30 undated entries in 4 repos and the spec does not say whether an undated or `-`-separated entry is a mapping error (no partial record) or an optional `date` | FR-005, FR-007 |
| FND-291 | low | `SuccessCriterion.text` is undefined: only 55/182 IT procedures are ordered lists, tokens can sit mid-sentence, and a token repeated in the procedure yields duplicate `id`s | FR-005, FR-007 |
| FND-292 | low | The `type` `const` for `Index`, `Log`, and `MasterRequirements` is unspecified; archetype names are `index`, `log`, `master-requirements`, model names are capitalised, and `exports` must match archetype names case-sensitively in both engines | FR-005, FR-006 |
| FND-293 | low | Census figures (7,119 docs, 16 status spellings, 41 empty cells, 756/~30 log entries, 156/182, 896/142/8) sit in normative Inputs and Behavior; nothing preserves the measurement, so the numbers go stale on the next sweep and a reader cannot re-derive them | FR-005 |
| FND-294 | low | `FR` is the largest record (five `Section` fields, two typed tables with nested `Verification` and `detail`, `ClauseRef[]`, frontmatter, provenance, relationships); the model does not need splitting, but a single "emit the models" task hides the four independent parsers behind one green | FR-005, FR-007 |
| FND-295 | low | Both resolvers refuse `$ref` cycles between files (`semantic.schema-ref-cycle`); a recursive TypeSpec model (or two models referencing each other) is unshippable, and the spec does not forbid it | FR-005 |

## Risk Register

| Risk | Likelihood | Impact | Mitigation | Refs |
|------|------------|--------|------------|------|
| Golden FR record with an `## Invariants` clause cannot validate: `SourceLocus.sourceIdentity` and `startColumn` are required in semantic-core 0.1.0 | high | high | Spec edit (FR-007 Behavior, `ocl-clause`): "`sourceSpan` is emitted only when the caller supplies `provenance.sourceIdentity`; otherwise the `ClauseRef` carries `language` and `clauseId` alone, and the fence lines are carried beside the record as `invariantsText[]`". FR-007-AC-4: the golden record is built with `sourceIdentity: ix://agent-ix/spec-artifacts-iso/skeletons/FR-001` and asserts `startColumn: 1`. | FND-280 |
| `Verification` split drops `TC-` references outside parentheses and rejects 41 empty cells | high | high | Spec edit (FR-007 Behavior, `typed-table`): `testRefs` = every `TC-[0-9]+` token anywhere in the cell, in order, de-duplicated; `method` = the cell with those tokens, their surrounding parentheses/brackets, and separators (`,`, `;`, `:`, `—`, `-`, `/`) stripped, then trimmed. Spec edit (FR-005 Behavior): `Verification.method` is free text with `minLength: 0` and doc comment `free text: 30+ census spellings; the ac-verification-method lint owns the vocabulary`; an empty cell yields `method: ""`, `testRefs: []`. Plan constraint: a table-driven fixture of at least the 30 census spellings with expected `(method, testRefs)` pairs, as one task. | FND-281 |
| TC-048 blocked on an unpublished quire wheel | high | medium | Spec edit (FR-006 Dependencies and NFR-001 Scope): name the wheel as `quire >= <first version published from quire-rs main at or after 17b80e4>`; plan constraint: the quire-rs wheel publish is task 0 of the FR-006 track and TC-048 is not marked skip. | FND-282 |
| `quoin module install` fails with `semantic.unknown-export` for every export | high | medium | File the agent-ix/quoin issue now (the diagnostic is derivable from `manifest.ts:183` without running anything) and rewrite FR-006-AC-6 to the single expected outcome "fails only with `semantic.unknown-export` naming each of the ten exports, quoin issue #<n>" until quoin admits `artifact_types`; plan constraint: FR-075 pin derivation is out of scope for this ticket. | FND-283 |
| Version bump churn: ten `$id`s + ten digests + toolchain in one hand-edited step | medium | medium | Spec edit (FR-006 Outputs): `make schemas` also rewrites every `data_schema.digest` in `manifest.yaml`, and a `make bump-version VERSION=x.y.z` target edits `manifest.yaml`, `semantic/main.tsp` base, regenerates, and rewrites digests in one run; add FR-006 Behavior: "If `manifest.yaml` `version`, the `@jsonSchema` base, and every `$id` disagree, the suite SHALL fail naming all three". | FND-284 |
| Two validators disagree on `unevaluatedProperties` or on `null` vs absent | medium | high | Plan constraint: no `extends`, `is`, or spread in `semantic/main.tsp` (every object schema declares its properties inline); no `\| null` unions, only `?`. Spec edit (FR-007 round-trip bullet): canonical JSON omits absent optional properties and never writes `null`. Recommend TC-060 (dual-engine parity): every negative fixture of TC-045 is validated by `jsonschema.Draft202012Validator` and by `quire.Registry`'s compiled validator with the same verdict. | FND-285 |
| `Story` misparse on real stories | medium | medium | Spec edit (FR-007 Behavior, `section`): `asA`, `iWant`, `soThat` are captured by three anchored, non-greedy, line-start patterns (`^(?:[*_]*)As an?[*_:]*\s+(.+?)$` and likewise for `I want` / `So that`, case-insensitive), taken from the first paragraph of `## Story` only; leading `-`/`*` bullets and `*`/`_` emphasis are stripped from the captured text; the presence regex the locator asserts stays a presence test. `Story.text` remains the byte-exact section. | FND-286 |
| Reference mapper is not the contract | medium | medium | Spec edit (FR-007 Inputs/Outputs): `mappings.yaml` carries, per parsed field, the exact regex or split rule (`story`, `verification`, `log_entry`, `index_entry`, `success_criterion`) and the reference mapper reads them from the file; ship `examples/invalid/<case>.md` with the expected failing line beside the golden records so consumers have a conformance kit. | FND-287 |
| `## Invariants` scope creep and first-fence-only locator | medium | medium | Spec edit (FR-006 Behavior): the `invariants` locator carries `multiple: true`. Plan constraint: `FR.invariants`, the `ocl-clause` mapping, the skeleton section, and the locator are one terminal task with no dependents, so US-001 ships without it if it slips; alternatively move them to an FR-008 that FR-005/FR-007 do not depend on. | FND-288 |
| Byte reproducibility depends on an unrecorded formatter and name-based filtering | medium | medium | Spec edit (FR-005 Outputs): the generator serialises with `JSON.stringify(schema, null, 2) + "\n"` and no external formatter; `toolchain.json` records every program that touched the bytes; the shipped set is every emitted file whose `$id` starts with the module base, and the digest is computed over that filtered set. | FND-289 |
| Undated / differently separated log entries | low | medium | Spec edit (FR-007 Behavior): a `## History` line that does not match `^\* \*\*(\d{4}-\d{2}-\d{2})\*\* [—–-] (.+)$` is a mapping error naming the line (consistent with "no partial record"); the ~30 undated entries are a corpus sweep, not a schema relaxation. | FND-290 |
| `SuccessCriterion.text` and duplicates undefined | low | low | Spec edit (FR-005 Behavior): `text` is the remainder of the line after the token and an optional `:`; a token seen twice is a mapping error naming the second line. | FND-291 |
| `type` const mismatch | low | low | Spec edit (FR-005 Behavior): `type` `const` equals the archetype `name` exactly (`index`, `log`, `master-requirements`, `Glossary`) and the schema file name equals the model name; add the name table to FR-006 Outputs. | FND-292 |
| Census numbers go stale | low | low | Spec edit (FR-005 Inputs): reference the census as a committed artifact (`spec/analysis/census-2026-09-03.md` with the script and per-repo counts) and state that the patterns, not the counts, are normative; re-census is required only when a pattern is tightened. | FND-293 |
| One "emit the models" task hides four parsers | low | medium | Plan constraint: FR-005/FR-007 decompose into shared scalars + `Section`/`Provenance`/`Relationship`; `Verification` + typed tables (FR/NFR/StR); `Story`; `LogEntry`/`IndexEntry`/`SuccessCriterion`; `Glossary`/`TC`/`MasterRequirements`; `Invariants`. | FND-294 |
| Recursive or mutually referencing models refused at load | low | medium | Plan constraint: no model references itself or a model that references it; TC-041 already exercises resolution and will surface `semantic.schema-ref-cycle`. | FND-295 |

### Requirement scoring

| Req | Tech Risk | Volatility | Drivers | Mitigation |
|-----|-----------|------------|---------|------------|
| US-001 | Low | Low | Consumer story; no schema language chosen here | None beyond keeping FND-288 out of its critical path |
| FR-005 | High | Medium | First TypeSpec projection in this module; sealed schemas evaluated by two engines; semantic-core 0.1.0 is published and pinned, typespec 1.15.0 pinned | FND-285 plan constraints; TC-060 parity; FND-289 generator rules |
| FR-006 | Medium | High | quire wheel unreleased; quoin `object_types`-only exports check; `$id` embeds `version` | FND-282/283/284 edits; quire publish as task 0 |
| FR-007 | High | High | Four hand-written parsers over 30+ corpus spellings; `SourceLocus` coupling; oracle lives in tests; quoin FR-071/072 conventions unreleased | FND-280/281/286/287 edits; fixture tables; conformance kit |
| NFR-001 | Medium | Low | Byte-for-byte across machines with an external formatter in the loop; offline gate is manual until CI | FND-289; formatter-free serialisation |

### Top hazards

1. FND-280 — `sourceSpan` cannot be built without a `SemanticId`; decide before the golden records exist.
2. FND-281 — the verification split rule is the one every consumer will copy; fix it before the reference mapper is written.
3. FND-282 / FND-283 — two external engines gate FR-006; sequence the quire publish and file the quoin issue before tasking.
4. FND-285 — dual-engine `unevaluatedProperties` parity; forbid `extends` and `null` now, add TC-060.
5. FND-284 — version-embedded `$id` churn; one `make` target, one commit.

### Failure-domain gaps

Cross-reference: the parallel failure-domain SpecReview of this review set
(same branch, same seven-analyst pass). Open gaps this analysis adds to it:
identity confusion between archetype names and model names (FND-292), and
the partial-extraction topology of a first-fence-only `code_block` locator
(FND-288).

## Recommendations

1. **FR-007 `ocl-clause` (FND-280):** add to the Behavior bullet: "`sourceSpan`
   is present only when `provenance.sourceIdentity` is supplied; it carries
   `sourceIdentity`, `path`, `startLine`, `startColumn: 1`, `endLine`, and
   `endColumn`; without an identity the `ClauseRef` carries `language` and
   `clauseId` only." Amend FR-007-AC-4 to state the identity the golden record
   uses.
2. **FR-007 `typed-table` and FR-005 `Verification` (FND-281):** replace the
   "before the first `(`" rule with the token-superset rule in the register;
   declare `method` free text with `minLength: 0`; add a fixture-table test
   over the census spellings (new TC in tests.md, FR-007-AC-3 refs it).
3. **FR-006 Dependencies / NFR-001 Scope (FND-282):** name the minimum quire
   wheel version; plan orders the publish first.
4. **FR-006-AC-6 (FND-283):** file agent-ix/quoin issue now; make the AC
   expect the `semantic.unknown-export` outcome and reference the issue.
5. **FR-006 Outputs (FND-284):** `make schemas` rewrites manifest digests;
   add `make bump-version`; add the three-way version agreement rule to
   Behavior.
6. **FR-005 / FR-007 (FND-285):** plan constraints "no `extends`/spread, no
   `| null`"; canonical JSON omits absent optionals; add TC-060 dual-engine
   parity to tests.md under FR-005-AC-4.
7. **FR-007 `section` / `Story` (FND-286):** specify the three anchored
   captures and the emphasis-stripping rule; keep the locator regex as a
   presence test.
8. **FR-007 Inputs / Outputs (FND-287):** put every parse regex in
   `mappings.yaml`, make the mapper table-driven, ship `examples/invalid/`.
9. **FR-006 Behavior (FND-288):** `multiple: true` on the `invariants`
   locator; plan makes the Invariants slice terminal (or split to FR-008).
10. **FR-005 Outputs / NFR-001 (FND-289):** formatter-free serialisation,
    `$id`-prefix filtering, digest over the filtered set, every byte-touching
    tool recorded in `toolchain.json`.
11. **FR-005 / FR-007 (FND-290..292):** state the log-line regex and the
    undated-entry outcome; define `SuccessCriterion.text` and the duplicate
    rule; pin `type` consts to archetype names and add the name table.
12. **FR-005 Inputs (FND-293):** commit the census as an analysis artifact and
    make patterns, not counts, normative.
13. **Plan (FND-294, FND-295):** six-task decomposition of FR-005/FR-007 as
    listed in the register; no recursive models.
