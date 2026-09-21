---
type: log
title: "Plan-001 — Update Log"
description: "Chronological log of changes to the Plan-001 bundle."
---
# Plan-001 — Update Log

## History

* **2026-09-20** — **PLAT-902 retires TC-049 and FR-006-AC-4 from this bundle's
  Test Matrix.** Both named the FR-035 module-manifest schema this package
  shipped as package data and the four rejections asserted against it. The
  schema, its public API and those tests are deleted; the criterion is retired
  rather than restated over quire's loader, because at the declared engine floor
  (quire 0.33.0) the loader ignores the `semantic` block and every such mutation
  still loads all eleven archetypes. This bundle's tasks are `done` and its rows
  are left as the record of what was built; the row naming TC-049 describes a
  test that no longer exists, and is not an outstanding obligation.

* **2026-09-04** — All ten tasks landed and the gate passed: a record built from each of the ten skeletons validates against its emitted model. Code review SR-012 raised 1 high (the committed npm lockfile resolved 75 of 76 packages from the local registry, so `npm ci` could not have worked off this network) and 12 mediums; all are fixed on the branch except two defects in the vendored FR-035 schema, which FR-006-AC-4 requires to stay byte-identical and which were filed as agent-ix/filament-core-service#24 and agent-ix/quoin#336.
* **2026-09-03** — Plan created from the spec after the composite review round SR-003..SR-011; scoped to US-001, FR-005, FR-006, FR-007 and NFR-001, covering matrix rows TC-039..TC-063. Decomposed into 10 tasks across tracks A, B and C with one gate (Task-004, record shape). Two external blockers recorded rather than worked around: agent-ix/quire-rs#388 (no published wheel carrying FR-069, so TC-063 is a strict expected failure) and agent-ix/filament-core-data#11 (semantic-core resolves only from a scope-routed registry, so `make schemas-check` stays a local gate).
