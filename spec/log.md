---
type: log
title: "Update Log"
description: "Chronological log of structural changes to this bundle."
---
# Update Log

## History

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
