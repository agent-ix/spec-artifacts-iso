---
id: SR-004
title: "Failure-domain review of the semantic data schemas and Markdown mappings (US-001, FR-005..007, NFR-001)"
type: SpecReview
analysis: failure-domain
scope: "spec/usecase/US-001-consume-typed-iso-artifact-records.md, spec/functional/FR-005-semantic-data-schemas.md, spec/functional/FR-006-semantic-manifest-block.md, spec/functional/FR-007-markdown-mappings.md, spec/non-functional/NFR-001-reproducible-offline-schema-projection.md"
review_set: all
---
# SR-004: Failure-domain review of the semantic data schemas and Markdown mappings

## Summary

This analysis walked the five documents of agent-ix/spec-artifacts-iso#34
(branch `spec/34-semantic-data-schemas`, commit 1187c51) plus the Test Matrix
rows TC-039..TC-059 against the `spec-failure-domain-analysis` checklist
(extension points, entity identity, evaluation purity, topological robustness)
and against the contracts the spec claims to implement: quoin FR-070..FR-075 with
`src/semantic/manifest.ts` and `data-schema.ts`, quire-rs FR-069..FR-072 with
`src/semantic/contract.rs`, `src/semantic/surface.rs`, and
`src/loader/mod.rs` (`read_module_semantic`), and semantic-core `main.tsp`.
Where a failure mode depends on the corpus, the count below is from a fresh
`grep` over `~/dev/*/spec` on 2026-09-03, counted by document or by line as
stated in the finding.

Much is specified well: digest mismatch (FR-006 Behavior, `semantic.data-schema-digest-mismatch`
in both engines), a `$ref` to a missing sibling (FR-005-AC-2, `semantic.schema-ref-unshipped`),
an export the installed quoin refuses (FR-006 Behavior), a skeleton copied
before this change (FR-007-AC-5 at 3d87196), a wrong-prefix row id, a duplicated
level-2 heading, and a malformed `## Story` (FR-007 Behavior, "no partial
record"). The findings below are the failure modes the five documents leave
unstated or state in a way the contract sources cannot satisfy. Three are
high: the `data_schema` binding names a schema the engine's only
`data_schema` validator would reject on every ISO document; empty verification
cells (41 in the census the spec cites) cannot satisfy both `minLength: 1` and
the compatibility guarantee; and FR-006-AC-6 admits exactly one quoin
diagnostic where the quoin reader emits two.

## Findings

| ID | Severity | Summary | Refs |
|----|----------|---------|------|
| FND-200 | high | `data_schema` has two meanings: quire's only consumer of the bound schema validates the `{fields, clauses, operations}` declaration record (surface.rs `declaration_record`, FR-069-AC-1), while FR-005's sealed record requires `id`, `title`, `type`, `provenance`, sections; any engine-side validation of an ISO document against `FR.json` fails `semantic.record-invalid`, and the spec never says which record the binding governs | FR-005, FR-006-AC-3, US-001 |
| FND-201 | high | Empty verification cells (41 in the cited census; 4 in FR AC tables today) map to `Verification.method = ""`, which `minLength: 1` rejects, contradicting FR-007's "a document that validated before FR-005 maps to a record that validates"; neither requirement says which wins | FR-005, FR-007-AC-5, US-001-EX-2 |
| FND-202 | high | FR-006-AC-6 accepts only `semantic.unknown-export`, but quoin `readSemanticBlock` builds `dataSchemas` from `object_types` alone and so also emits `semantic.export-without-schema` for every one of the ten exports (and `semantic.unknown-semantic-core` if `0.1.0` is not in its `SEMANTIC_CONTRACT`); the demonstration cannot pass as written | FR-006-AC-6, TC-055 |
| FND-203 | medium | `ocl-clause` names two failures (non-`Identifier` heading, other language) and is silent on a fence with no owning `###` heading, a heading with no fence, a heading with two fences, an unterminated fence, and a duplicate `clauseId` (the identity key of `ClauseRef[]` is never stated); quire FR-071 has a code for each | FR-007, FR-005 (`FR.invariants`) |
| FND-204 | medium | 54 corpus FR documents already carry a prose `## Invariants` section with no fence at all; whether they map to `invariants: []`, to an absent field, or to a mapping error is unstated, and FR-007-AC-5 tests skeletons only, so the compatibility claim is unmeasured on the one heading this change claims | FR-007-CON-1, FR-007-AC-5, FR-006 |
| FND-205 | medium | `sourceSpan` is a semantic-core `SourceLocus`, whose `sourceIdentity` is required, but `provenance.sourceIdentity` is optional and FR-007 takes it "from the caller when supplied"; a clause mapped without a caller identity has no specified outcome (fail, omit `sourceSpan`, or default as quire does with `semantic.source-identity-defaulted`) | FR-005, FR-007 |
| FND-206 | medium | Row identity is unstated: two rows with one id in a table (the locator checks the pattern, not uniqueness), a `### <row id>` subsection naming no row, two subsections naming one row, or a subsection under a different H2; the same for `GlossaryTerm.term` and `IndexEntry.href` | FR-005, FR-007 |
| FND-207 | medium | Zero-row tables: 82 corpus FR documents carry `## Constraints` with no table; FR-005 says `constraints` is "present only when the section is" but not whether it is `[]`, absent, or rejected, nor whether the arrays carry `minItems: 1` to mirror the locators' `min_rows: 1` | FR-005, FR-005-CON-1 |
| FND-208 | medium | CRLF documents: `provenance.digest` is over raw bytes and `Section.text` is byte-exact, so a checkout that normalises line endings changes every golden record's digest and text; whether table "cells trimmed" strips `\r`, and how `examples/*.record.json` stay byte-stable across `core.autocrlf` settings, is unstated | FR-007, FR-005, NFR-001 |
| FND-209 | medium | "No partial record" is attached to three mapping conditions only; a record that maps but fails its schema (a `status` outside `^[A-Za-z][A-Za-z_-]*$`, an `href` containing `:`, a `cardinality` spelling outside the census) has no stated owner, and whether the mapping reports the first failure or all failures is unstated | FR-007, FR-005 |
| FND-210 | medium | The verification-cell grammar loses references silently: `Test ([IT-003](../integration/IT-003-…md))`, `agent-behaviour-eval (TC-EV-054)`, and `Test TC-001` all yield `testRefs: []` with no diagnostic; `lossless: false` is defined as formatting loss only | FR-007, FR-005 |
| FND-211 | medium | `Index.entries` and `Log.history` are defined by one line shape each, but 709 of 6,125 corpus index links use `-` bullets, 5,184 carry no ` - summary`, and 4 of 624 log entries have no ` — `; whether a non-matching line is skipped, errors, or is a different row is unstated | FR-005 |
| FND-212 | medium | Export names and model names diverge for three types (`master-requirements`/`MasterRequirements`, `index`/`Index`, `log`/`Log`); quoin FR-075 mints `typeIdentity: ix://agent-ix/spec-artifacts-iso/type/master-requirements` while the `$id` is `MasterRequirements.json`, and no requirement states the mapping | FR-006, FR-005 |
| FND-213 | medium | Every frontmatter schema declares `additionalProperties: true` while every model is sealed; a document with an extra frontmatter key validates today, and whether the mapping drops the key silently, records it, or fails is unstated | FR-005, FR-007 |
| FND-214 | medium | NFR-001 claims reproduction "on any machine", but `@agent-ix/semantic-core` is not on the public npm registry, FR-005-CON-3 forbids a repository `.npmrc`, and nothing says where scope resolution and the lockfile's `resolved` host come from; on a clean clone `npm ci` is the failure, not the projection | NFR-001, FR-005-CON-3 |
| FND-215 | low | The bundle digest in `toolchain.json` is defined by reference ("same shape as" semantic-core); file order, concatenation, and the `normalization` record are not restated, so `make schemas-check` and TC-042 have no local definition of the digest they compare | FR-005-AC-7, TC-042 |
| FND-216 | low | The `status` pattern is justified by a 16-spelling census; the off-pattern values in the corpus (`🚧 In Progress`, `gate-blocking issues identified`) are on non-ISO types, which the requirement should state so the population is auditable | FR-005 |
| FND-217 | low | The FR skeleton gains an example OCL clause; every FR authored from it carries a sample `### <clauseId>` until deleted, and the FR-002 skeleton⇔assert tests (TC-009, TC-010) meet a `code_block` locator kind for the first time with no stated handling | FR-007, FR-006 |
| FND-218 | low | The `Validation` column is typed two ways: `Constraint.validation` is a string while `ValidationCriterion.validation` is a `Verification`, so `Test (TC-039, TC-040)` on a constraint row keeps no `testRefs` | FR-005 |

## Verdict

Not ready for `spec-to-plan` as written. The three high findings are each a
requirement that cannot be satisfied together with another requirement or with
the contract it names: FND-200 (which record `data_schema` governs at the
engine), FND-201 (empty verification cells versus `minLength: 1`), and FND-202
(one accepted quoin diagnostic where the reader emits two). The twelve medium
findings are unstated failure modes on inputs the corpus already contains;
each is a one-line addition to FR-005 or FR-007 Behavior. Nothing here changes
the design: the TypeSpec source, the reference form, the five mapping kinds,
and the round-trip policy stand.

## Recommendations

Concrete edits, one per finding, in the file the finding names. Quoted text is
the proposed replacement or addition.

1. **FND-200 (FR-005 Description, FR-006 Behavior).** State which record the
   binding governs and what the engine may validate. Add to FR-006 Behavior:
   "The schema a `data_schema` reference names is the record schema of FR-007;
   the engine's declaration record (`{fields, clauses, operations}`, quire-rs
   FR-072) is NOT an instance of it. When the quire wheel validates a
   declaration record against the bound schema (quire-rs FR-069-AC-1), that
   path SHALL be reachable only for `object:` artifacts, and this module
   declares no `object:` archetype; the module's suite SHALL assert that
   `validate_document` over each skeleton reports no `semantic.record-invalid`
   finding." Record the divergence against quire-rs FR-069 in FR-006
   Dependencies and file it on agent-ix/quire-rs, since the same key now has
   two instance shapes across two modules.

2. **FND-201 (FR-005 Behavior, `Verification`).** Decide, then say it. Given
   the requirement's own rule ("a schema that closed them would reject the
   corpus it describes"), replace the `Verification` sentence with:
   "`Verification { method, testRefs: ^TC-[0-9]+$[] }` splits the cell
   `Test (TC-035, TC-036)` into the method token and the annotated test-case
   references; `method` is free text: the `ac-verification-method` lint owns
   the vocabulary, and the census counts 41 empty cells, so `method` MAY be
   the empty string and `minLength` is not applied to it." Add the empty cell
   to FR-007-AC-6's negative cases only if the decision goes the other way.

3. **FND-202 (FR-006-AC-6, TC-055).** Replace the accepted set: "…or fails
   only with diagnostics whose codes are within `{semantic.unknown-export,
   semantic.export-without-schema}`, one pair per exported type, recorded
   verbatim in this requirement and in a filed agent-ix/quoin issue; any other
   code fails the demonstration." Note in the Behavior bullet that quoin
   resolves `data_schema` for `object_types` only (manifest.ts) while quire
   resolves it for `artifact_types` too (`Manifest::all_archetypes`).

4. **FND-203 (FR-007 Behavior, `ocl-clause`).** Append: "…a fence under
   `## Invariants` with no owning `###` heading, a heading that owns no fence,
   a heading that owns two fences, an unterminated fence, and a second heading
   whose `clauseId` repeats an earlier one are each a mapping error at that
   line; `clauseId` is the identity of a `ClauseRef` within one document."
   Add the five cases to FR-007-AC-4 or a new AC with a TC.

5. **FND-204 (FR-007 Behavior).** Append: "A `## Invariants` section that
   contains no fenced block maps to an absent `invariants` field with no
   error." Extend FR-007-AC-5 or TC-050 to one corpus FR document with a prose
   `## Invariants` (there are 54).

6. **FND-205 (FR-007 Behavior, provenance bullet).** Append: "When the caller
   supplies no `sourceIdentity`, the mapping SHALL set `sourceSpan.sourceIdentity`
   to `ix://local/<corpus directory name>/spec` and record one advisory per
   document, matching quire-rs FR-071; it SHALL NOT omit `sourceSpan`."

7. **FND-206 (FR-007 Behavior, `typed-table`).** Append: "Row ids SHALL be
   unique within a table; a repeated id, a `### <row id>` subsection that
   names no row of the enclosing section, or two subsections naming one row
   are mapping errors at the line. `GlossaryTerm.term` is unique within
   `## Terms`."

8. **FND-207 (FR-005 Behavior, table bullet).** Append: "A section whose
   locator is `required: false` and which carries no table maps to an absent
   array, never to `[]`; every row array carries `minItems: 1`, mirroring the
   locator's `min_rows: 1`."

9. **FND-208 (FR-007 Behavior, round-trip bullet; NFR-001 Scope).** Append to
   FR-007: "Cell trimming removes ASCII space and tab only; a CR is content."
   Add to NFR-001 Scope: "The repository SHALL declare `* text eol=lf` for
   `spec_artifacts_iso/**` in `.gitattributes`, so golden records and digests
   are checkout-independent."

10. **FND-209 (FR-007 Behavior).** Replace the "If a document carries…" bullet
    with: "If any mapping step fails, or the mapped record fails its schema,
    then the mapping SHALL report every failure with its line (or JSON path)
    and SHALL emit no record." State the ownership in FR-005: schema failures
    after mapping are the mapping's failures on this surface.

11. **FND-210 (FR-007 Behavior, `typed-table`).** Append: "A verification cell
    whose parenthesised text contains a token that is not `TC-[0-9]+` is a
    mapping warning naming the token; text outside the first parenthesised
    group other than the method is carried in `Verification.text`." (Or
    declare the loss explicitly as accepted; either is a decision the spec
    must make.)

12. **FND-211 (FR-005 Behavior, `Index.entries` and `Log.history`).** State
    the population: "one per line under `## Contents` matching
    `^[*-] \[(?<title>[^\]]+)\]\((?<href>[^)]+)\)( - (?<summary>.*))?$`; a
    non-matching line is not an entry and is not an error." Give `Log.history`
    the same treatment and admit `-` and `:` separators or reject them by name.

13. **FND-212 (FR-006 Outputs).** Add: "The export name is the manifest
    `artifact_types[].name`; its model is the `<Model>` of the `data_schema`
    path. The map is `master-requirements → MasterRequirements`,
    `index → Index`, `log → Log`, identity otherwise." Note the FR-075
    `typeIdentity` consequence in Downstream.

14. **FND-213 (FR-007 Behavior, `frontmatter`).** Append: "A frontmatter key
    the mapping does not name is dropped and counted in a per-document
    `dropped` list on the mapping result; it is never a record field."

15. **FND-214 (NFR-001 Scope).** Replace "any machine with the pinned
    toolchain" with "any machine with the pinned toolchain and a user-level
    npm configuration resolving the `@agent-ix` scope", and state in FR-005
    Inputs which registry the lockfile's `resolved` URLs name.

16. **FND-215 (FR-005 Outputs).** Restate the digest: "the SHA-256 over the
    concatenated bytes of the emitted files in `files` order (sorted by name)".

17. **FND-216 (FR-005 Behavior, `status`).** Add "(census over ISO artifact
    types only; every value matched)" after the pattern.

18. **FND-217 (FR-007 Outputs).** Add "The example clause is a comment-marked
    placeholder that TC-009/TC-010 treat as an optional `code_block` locator."

19. **FND-218 (FR-005 Behavior, `FR.constraints`).** Either type
    `Constraint.validation` as `Verification` or add "free text: the
    Validation column of a constraint row names a method, not a test list" to
    the doc comment so FR-005-AC-3 is satisfied deliberately.
