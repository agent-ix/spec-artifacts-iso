---
type: log
title: "Update Log"
description: "Chronological log of structural changes to this bundle."
---
# Update Log

## History

* **2026-08-18** — **CR-005**: new **FR-004** documents the `edge_types` and `roles` vocabulary (agent-ix/spec-artifacts-iso#16). 76 edge verbs across 7 categories, 27 inverse declarations and 9 capability roles were load-bearing module data that no document in this repository described — quire-rs FR-040 normalizes `allowed_links` against it, FR-041 reads its inverses, and every `spec-objects-*` module writes its link declarations in it. `spec-objects-security#5` is about to extend it with safety-chain verbs, and extending an unspecified vocabulary is how drift starts.

  The FR states what a category means, what an inverse is, how vocabularies merge across modules (first-wins by verb name), why an unrecognised verb stays **advisory** — a corpus that refuses to load on an unknown verb cannot be migrated onto a new one — and the criteria for adding a verb, of which the load-bearing one is: **do not add a verb to make an existing document validate.**

  **Two acceptance criteria I wrote were wrong, and reading the owning requirement is what settled it.** AC-2 originally asserted that every `inverse` names a verb itself declared in `edge_types`; it failed on 26 of 27. AC-3 asserted inverse pairs are symmetric; it failed on `contained_by`. Both looked like vocabulary defects. They are not: quire-rs **FR-041-AC-2** type-allows an authored edge whose verb is a declared inverse label *"even when the label is absent from `edge_types`"*, and **FR-041-AC-3** governs both a label shared by two verbs (first-wins, `part_of` from `contains` and `aggregates`) and a label that is also a forward verb (forward registration governs, `contains`). An inverse is a **derived name, not a second declaration**, and requiring otherwise would double the vocabulary with entries no author writes. The criteria were rewritten to the design rather than the data being changed to fit them — and rather than the tests being weakened to pass, which is the same mistake wearing the other hat.

  What the corrected criteria pin instead is the thing that *can* silently break: the set of shared inverse labels, because a new collision changes which forward verb a label normalizes onto, first-wins and without a word.

  **[RAN]** the finding the FR records rather than fixes, over 237 `~/dev` spec bundles: **four verbs compete for requirement lineage.** `implements` carries 956 authored edges and is categorised `dependency` with the declared meaning "fulfils an interface/contract" — it is not a traceability verb, yet it is the corpus's dominant spelling of requirement parentage. The vocabulary spells that `satisfies` (38 edges), which is itself only an inverse label rather than a forward verb. `traces_to` (368) is declared for matrix/coverage, `derives_from` (131) for decomposition lineage, `exercises` (25) for US→FR. And **`refines` is not in the vocabulary at all**, yet is authored twice — two `UnknownEdgeType` findings.

  Either the corpus is wrong or `implements`'s declared meaning is too narrow. FR-004 does not decide it, because deciding it changes the vocabulary and this FR's scope is to describe it. But it blocks quire-rs FR-058, whose upward-trace relations today accept `implements` and `refines` — one verb used outside its documented meaning, and one that does not exist. Matrix: TC-SCHEMA-009..013.

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
