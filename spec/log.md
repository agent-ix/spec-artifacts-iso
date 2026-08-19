---
type: log
title: "Update Log"
description: "Chronological log of structural changes to this bundle."
---
# Update Log

## History

* **2026-08-18** — FR-001 CR-005: the fixture gains `traceability.required_relations[]`, `traceability.acyclic_edges[]` and a `RequiredRelation` definition (quire-rs FR-058) — the upward half of traceability, where a hazard with no mitigating requirement is a risk nobody addressed. Stricter than its neighbours on purpose: an empty `edges` list reports every document of a kind, so the schema rejects it rather than letting a quiet declaration read as a corpus-wide defect. agent-ix/spec-objects-security#5.
* **2026-08-18** — **CR-008**: this module now DECLARES `traceability.vocabulary_coverage` for the ISO 25010 quality characteristics (quire-rs FR-059), and declares **`quire` as a dev dependency**. Two fixes to one problem: the engine capability shipped in quire-rs v0.33.0 and no module declared it, so the check fired nowhere.

  Declared here because this module owns both halves — the `NFR` archetype and the `quality_attribute` enum in its own frontmatter schema — so the vocabulary is read from the schema beside it and nothing is restated.

  **The dev dependency is the load-bearing half.** A `quire` 0.14.0 wheel was sitting in the venv that no file in this repo mentioned: absent from `pyproject.toml`, absent from `poetry.lock`, invisible to `poetry show`, and therefore never updated. The IT-002 checks stand down on a stale wheel by design, so adding the declaration turned **108 passed into 87 passed / 21 skipped** and the suite still reported green. Declaring the engine makes the version a stated fact; with 0.33.0 installed the suite is 108 passed, 0 skipped, with the declaration in place.

  Dev-only on purpose: this module is DATA and quire reads it, so a runtime dependency would invert that relationship and couple every module release to an engine release.

  Verified end to end rather than by inspection — the module loads under the v0.33.0 engine and reports 7 unowned characteristics against `quoin/spec`. agent-ix/spec-artifacts-iso#23.

* **2026-08-19** — FR-001 CR-009: the fixture gains `trace_tags.implements[]`, the same `TraceMarkerForm` shape as `markers` (quire-rs FR-062). **A separate list, deliberately**: `markers` mint `verifies`, which may back an acceptance criterion; these mint `implements`, which never may. quire-rs CR-061 stopped `verifies` binding production symbols precisely because a doc comment citing a criterion would otherwise count as evidence for it, and a shared list with a discriminator would put one typo between scope and evidence. `TraceMarkerForm` stays `additionalProperties: false` so a module cannot invent that discriminator — TC-SCHEMA-025 asserts the rejection rather than trusting it. Without this key a module declaring the forms fails load outright, so quire-rs FR-062 would mint nothing however the engine behaved. TC-SCHEMA-024..026.

* **2026-08-19** — FR-001 CR-008: the fixture gains `ObligationSource.combinatorial` and a `CombinatorialColumns` definition (quire-rs FR-061) — read a source's table as a **configuration space** and mint ONE obligation for the whole table rather than one per row. A new source *kind*, not a new mechanism: hash, suspect link and `parameters` are FR-053's; what differs is arity, because a t-way obligation is a statement about the interaction of every row. `strength` is rejected at `0` and unknown keys are rejected outright — a plural typo like `dimensions_column` reads correctly and would mint nothing. **Filed because the engine half shipped in Wave D with no module able to declare it**: `additionalProperties: false` rejected the key, so quire-rs FR-061 and quoin FR-035 could never fire and zero combinatorial obligations existed anywhere in the ecosystem. TC-SCHEMA-021..023.

* **2026-08-18** — FR-001 CR-007: the fixture gains `traceability.vocabulary_coverage[]` and a `VocabularyCoverage` definition (quire-rs FR-059) — which declared vocabulary values no document claims. **The definition has no `values` key on purpose**: the vocabulary is read from the projected archetype's own frontmatter-schema `enum`, and `additionalProperties: false` makes a module writing one an error rather than a silently ignored line. The 25010 list already lives in this repo's `schemas/nfr-frontmatter.schema.json` with twelve values; quire-rs#162 was filed against a scope proposing a hardcoded nine-item copy. TC-SCHEMA-018..020.

* **2026-08-18** — **CR-006**: new **FR-004** documents the `edge_types` and `roles` vocabulary (agent-ix/spec-artifacts-iso#16). 76 edge verbs across 7 categories, 27 inverse declarations and 9 capability roles were load-bearing module data that no document in this repository described — quire-rs FR-040 normalizes `allowed_links` against it, FR-041 reads its inverses, and every `spec-objects-*` module writes its link declarations in it. `spec-objects-security#5` is about to extend it with safety-chain verbs, and extending an unspecified vocabulary is how drift starts.

  The FR states what a category means, what an inverse is, how vocabularies merge across modules (first-wins by verb name), why an unrecognised verb stays **advisory** — a corpus that refuses to load on an unknown verb cannot be migrated onto a new one — and the criteria for adding a verb, of which the load-bearing one is: **do not add a verb to make an existing document validate.**

  **Two acceptance criteria I wrote were wrong, and reading the owning requirement is what settled it.** AC-2 originally asserted that every `inverse` names a verb itself declared in `edge_types`; it failed on 26 of 27. AC-3 asserted inverse pairs are symmetric; it failed on `contained_by`. Both looked like vocabulary defects. They are not: quire-rs **FR-041-AC-2** type-allows an authored edge whose verb is a declared inverse label *"even when the label is absent from `edge_types`"*, and **FR-041-AC-3** governs both a label shared by two verbs (first-wins, `part_of` from `contains` and `aggregates`) and a label that is also a forward verb (forward registration governs, `contains`). An inverse is a **derived name, not a second declaration**, and requiring otherwise would double the vocabulary with entries no author writes. The criteria were rewritten to the design rather than the data being changed to fit them — and rather than the tests being weakened to pass, which is the same mistake wearing the other hat.

  What the corrected criteria pin instead is the thing that *can* silently break: the set of shared inverse labels, because a new collision changes which forward verb a label normalizes onto, first-wins and without a word.

  **[RAN]** the finding the FR records rather than fixes, over 237 `~/dev` spec bundles: **four verbs compete for requirement lineage.** `implements` carries 956 authored edges and is categorised `dependency` with the declared meaning "fulfils an interface/contract" — it is not a traceability verb, yet it is the corpus's dominant spelling of requirement parentage. The vocabulary spells that `satisfies` (38 edges), which is itself only an inverse label rather than a forward verb. `traces_to` (368) is declared for matrix/coverage, `derives_from` (131) for decomposition lineage, `exercises` (25) for US→FR. And **`refines` is not in the vocabulary at all**, yet is authored twice — two `UnknownEdgeType` findings.

  Either the corpus is wrong or `implements`'s declared meaning is too narrow. FR-004 does not decide it, because deciding it changes the vocabulary and this FR's scope is to describe it. But it blocks quire-rs FR-058, whose upward-trace relations today accept `implements` and `refines` — one verb used outside its documented meaning, and one that does not exist. Matrix: TC-SCHEMA-009..013.

  Renumbered from CR-005 to CR-006 on merge: `FR-001 CR-005` (the `required_relations` schema keys) landed on `main` first and a published change id is not reused.

* **2026-08-17** — FR-001 CR-004: the fixture gains `traceability.obligations[]`
  and its `ObligationSource` definition (quire-rs FR-053). The schema permits
  both `target:` and `archetype:` and quire-rs rejects the combination at parse:
  JSON Schema cannot express that exclusivity without `oneOf` branches that
  report a confusing union of failures, so the schema gates the shape and the
  engine gates the coherence. agent-ix/quoin#79.
* **2026-08-17** — FR-001 CR-003: the fixture gains `verification_catalog`
  (quire-rs FR-054) and `ambiguity_terms` (FR-056), the two manifest keys
  v0.29.0 introduced. Found by CR-002 doing its job — `spec-artifacts-process`
  declared the catalog and its suite failed on an unexpected top-level property,
  where before CR-002 the check skipped in silence.
  agent-ix/spec-artifacts-process#35.
* **2026-06-15** — Adopted OKF-compatible bundle structure with directory indexes.
* **2026-08-17** — FR-001 CR-002: the FR-035 schema fixture is refreshed to the
  shipped surface (`observable_verbs`, `vacuous_predicates`, `traceability`,
  four `LocatorAssert` keys, `nav`) and moves to package data as the ecosystem's
  single source; both silent skips in the schema tests are deleted. Surfaced 13
  truncated `lexicon` definitions across three `spec-objects-*` modules, filed
  not fixed. agent-ix/spec-artifacts-iso#15.
* **2026-08-07** — FR-001 CR-001: the manifest declares a `property_idioms:`
  registry (quire-rs FR-052) — 7 corpus-attested phrases boosting `round-trip`,
  `idempotence` and `ordering` labels. Label-only by FR-052-CON-4; emits no
  finding and changes no validation verdict.
