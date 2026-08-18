---
id: FR-001
title: "Module manifest activates against filament-core"
type: FR
relationships:
  - target: "ix://agent-ix/filament-core-service/FR-035"
    type: "implements"
---
# FR-001: Module manifest activates against filament-core

## Description

> **CR-005 (required relations — 2026-08-18):** the fixture gains
> `traceability.required_relations[]`, `traceability.acyclic_edges[]` and a
> `RequiredRelation` definition (quire-rs FR-058). agent-ix/spec-objects-security#5.
>
> This is the **upward** half of traceability. Downward coverage answers *is what we
> wrote verified*; nothing answered *is anything missing*, and nothing operating over
> the existing spec text can, because a requirement nobody wrote leaves no trace to
> follow. Reading the edge set in the other direction does: a hazard with no mitigating
> requirement is a risk nobody addressed.
>
> **This definition is deliberately stricter than its neighbours,** which is a departure
> from the CR-004 split (schema gates the shape, engine gates the coherence) and worth
> the words. A required relation's failure modes are *quiet*: `edges: []` accepts no
> verb, so nothing satisfies the relation and **every** `from` document is reported —
> on a real repository, hundreds of findings against correctly-linked documents, which
> reads as a corpus-wide defect rather than as the empty declaration it is. So the
> schema carries `minItems: 1` on `edges`, an `enum` on `direction`, and
> `^[^\s:]+$` on `check` (a colon makes the `trace:<check>` severity key ambiguous;
> whitespace breaks the `--severity <grammar>:<check>=<level>` entry, either way leaving
> a relation whose severity nothing can name). quire-rs enforces the same rules again at
> load (FR-058-AC-10, CR-074) — the manifest is not the only way a model is built, so
> both gates are needed rather than one.
>
> `to: []` is the one field where empty carries meaning rather than being a defect: it
> reads as "any document in the bundle", the honest position of a module constraining
> the verb but not the target.
>
> Found the same way CR-003 and CR-004 were — by a module trying to declare the key and
> failing: `Additional properties are not allowed ('required_relations' was unexpected)`.
> Four pre-existing `\u2014` escapes were normalised to literal em-dashes to match the
> other 24 in the file.

> **CR-004 (obligation sources — 2026-08-17):** the fixture gains
> `traceability.obligations[]` and its `ObligationSource` definition (quire-rs
> FR-053). agent-ix/quoin#79.
>
> One shape decision is worth recording, because the schema deliberately says
> *less* than the engine enforces. An obligation source resolves its minting
> documents **exactly one of two ways** — `target:` inherits from a declared
> trace target, or `archetype:` + `section:` + `id_format:` covers rows that
> mint no id of their own — and declaring both, or neither, is a load-time
> error. JSON Schema cannot express that exclusivity without `oneOf` branches
> that would report a confusing union of failures on any malformed source, so
> the definition permits both keys and quire-rs rejects the combination at
> manifest parse, naming the offending source. The schema gates the *shape*; the
> engine gates the *coherence*, which is the split FR-050's `validate` already
> uses.
>
> Caught the same way CR-003 was: `spec-artifacts-process` declared the sources
> and its suite failed on `Additional properties are not allowed ('obligations'
> was unexpected)`.

> **CR-003 (quire-rs v0.29.0 manifest keys — 2026-08-17):** the fixture gains
> **`verification_catalog`** (quire-rs FR-054) and **`ambiguity_terms`**
> (FR-056), with a `VerificationMethodEntry` definition beside the existing
> ones. agent-ix/spec-artifacts-process#35.
>
> **CR-002 caught this, which is the point.** `spec-artifacts-process` declared
> the catalog and its own suite (`make test`) failed on
> `Additional properties are not allowed ('verification_catalog' was
> unexpected)` — a module key that the engine accepts and the FR-035 contract
> had never heard of. Before CR-002 that check skipped in silence and the key
> would have shipped ungated, exactly as `traceability` did.
>
> Two shape decisions are carried from the engine rather than invented here.
> `class` is a **free string**, not a closed IADT enum: this ecosystem
> classifies by ISO 29148, and an external user classifying by 29119-4
> technique family must be able to (FR-054-CON-1). And `applicability` is an
> open map of rule name to values, because the engine stores and surfaces the
> rules and interprets none of them (FR-054-CON-2) — a schema that enumerated
> the axes would close a set the engine deliberately left open.

> **CR-002 (schema fixture refresh + single-source packaging — 2026-08-17):**
> the bundled FR-035 fixture is refreshed to the shipped engine surface, and it
> moves from `tests/` to **package data** at
> `spec_artifacts_iso/module-manifest.schema.json`, reachable as
> `spec_artifacts_iso.module_manifest_schema()`. agent-ix/spec-artifacts-iso#15.
>
> **Why it drifted.** AC-1 gates *this* manifest, and CR-001 established the
> procedure — each new engine key gains a property + definition, "exactly as
> `grammar_severity` and `lexicon` did". Three keys shipped without it:
> `observable_verbs` and `vacuous_predicates` (quire-rs FR-047 / CR-014) and the
> whole `traceability:` model (quire-rs FR-050 / FR-051), plus four
> `LocatorAssert` keys — `optional_columns` (CR-023), `choices`,
> `column_choices`, `column_patterns` (CR-010) — and `nav` (filament-core
> FR-039), which five `spec-objects-*` modules declare and this fixture rejected.
> A module using any of them failed the FR-035 schema while the engine accepted
> it happily.
>
> **Why package data, not a copy per repo.** The contract is not this
> repository's private fixture: every module repository's manifest is gated by
> the same one. `spec-artifacts-process` shipped **no** copy, so its
> `test_manifest_validates_against_fr035_schema` **skipped in silence** — the
> process manifest's entire `traceability:` block and its CR-010/CR-023 assert
> keys were validated by nothing but the Rust engine at load time. A copied
> fixture plus a drift check would have added a second thing to keep in sync;
> one importable source removes the failure mode instead of detecting it.
>
> **A skipped gate now fails.** Both escape hatches are deleted: `jsonschema` is
> a hard dev dependency rather than an `ImportError` skip, and a missing schema
> raises `FileNotFoundError` naming the packaging bug rather than returning
> `None`. A gate that reports "passed" because it could not run is the defect
> this CR exists to close.
>
> **[RAN]** the refreshed fixture over all eight ecosystem module manifests. Five
> that previously failed on `nav` now pass. The remaining **13 findings in three
> modules are real data corruption**, not fixture staleness:
> `lexicon: {definition: a confidential value (key, password) kept out of code}`
> is a YAML flow mapping whose unquoted scalar contains a comma, so it parses as
> a truncated `definition` plus a garbage second key. `LexiconTermDef` is not
> `deny_unknown_fields`, so the engine stored the truncation without complaint.
> Filed as agent-ix/spec-objects-architecture#7 (8 terms),
> agent-ix/spec-objects-operational#5 (3) and agent-ix/spec-objects-security#6
> (2) rather than corrected here — lexicon vocabulary changes are
> sweep-and-report.

> **CR-001 (property-idiom registry — 2026-08-07):** the manifest additionally
> declares a **`property_idioms:`** registry (quire-rs
> [FR-052](ix://agent-ix/quire-rs/spec/functional/FR-052), umbrella
> agent-ix/quire-rs#20): phrase → `{definition, shape}`, merged first-wins over
> the engine's built-in idioms. It is a **booster, never a prerequisite** —
> quire-rs FR-052-CON-4 derives `extractable` from the closed structural signals
> alone, so a declared phrase can only sharpen a criterion's *label* to a
> higher-precedence shape and can never make a criterion extractable, nor remove
> one from extraction. Nothing on that path emits a finding, so this declaration
> cannot change any validation verdict. The registry is deliberately small and
> every phrase is attested in the authored corpus; quire-rs CR-014 retired
> `no-observable-outcome` because an open set whose membership was *required* to
> earn a label reached ~13% sampled precision, and a speculative phrase list here
> would recreate that shape. This is the first numbered CR in this repo; the two
> earlier notes (FR-002, StR-001, "render removal") predate the sequence.
> AC-1 already covers the addition: the bundled FR-035 schema fixture is
> `additionalProperties: false`, so the new key is gated by that criterion and
> the fixture gains a `property_idioms` property with a `PropertyIdiomEntry`
> definition, exactly as `grammar_severity` and `lexicon` did before it.

The system **SHALL** publish a Filament Module manifest (`spec_artifacts_iso/manifest.yaml`) that conforms to filament-core-service [FR-035](ix://agent-ix/filament-core-service/FR-035) v1.0.0 and activates idempotently against `POST /api/v1/modules/activate`.


## Inputs

- `manifest.yaml` (this repo's package)
- Activation endpoint: `POST /api/v1/modules/activate`

## Outputs

- Module row in `modules` table
- Contributed archetypes, object_types, grammars, artifact_types per the manifest

## Behavior

The manifest **SHALL** validate against `module-manifest.schema.json` v1.0.0. Re-activation **SHALL** be a no-op (idempotent by content hash per FR-026-AC-1).

## Acceptance Criteria

| ID | Criteria | Verification |
|----|----------|--------------|
| FR-001-AC-1 | Manifest validates against FR-035 JSON Schema | Schema Test |
| FR-001-AC-2 | Activation against clean filament-core succeeds with 200 | Integration Test |
| FR-001-AC-3 | Re-activation returns no-op (same content hash) | Integration Test |
| FR-001-AC-4 | Each declared archetype/object_type/artifact_type appears in the corresponding filament-core table after activation | Integration Test |

## Dependencies

- **Upstream**: filament-core-service [FR-035](ix://agent-ix/filament-core-service/FR-035), FR-026, FR-034
- **Downstream**: consumer agents/editors discovering this module's contributions
