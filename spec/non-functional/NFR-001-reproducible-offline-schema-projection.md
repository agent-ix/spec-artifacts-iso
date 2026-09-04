---
id: NFR-001
title: "Schema projection is reproducible and offline"
type: NFR
quality_attribute: maintainability
relationships:
  - target: "ix://agent-ix/spec-artifacts-iso/FR-005"
    type: "constrains"
  - target: "ix://agent-ix/spec-artifacts-iso/FR-006"
    type: "constrains"
---
# NFR-001: Schema projection is reproducible and offline

## Statement

The module SHALL reproduce its emitted schema bundle byte-for-byte from the
committed TypeSpec source and lockfile on any machine with the pinned toolchain,
and SHALL validate and resolve the bundle with no network read.

## Scope

- Applies to: `make schemas`, `make schemas-check`, the digests in
  `manifest.yaml`, and every `$ref` resolution performed by this module's tests.
- Operational context: a clean clone with `npm ci` in the TypeSpec package and
  the pinned quire wheel installed; the only network access is the package
  install itself.

## Rationale

The manifest binds each archetype to a digest. If the projection drifted with
the machine that produced it, every consumer would see a different digest for
the same source and the binding would mean nothing. Offline resolution is the
FR-073-CON-1 boundary quoin and quire both enforce.

## Measurement and Evaluation

| Metric | Target | Threshold | Method |
|--------|--------|-----------|--------|
| Byte differences between two consecutive `make schemas` runs on one tree | 0 files | 0 files | Run `make schemas` twice and `git status --porcelain spec_artifacts_iso/schemas` |
| Network reads during `make schemas-check` and `make test` | 0 | 0 | Run with the network namespace disabled after `npm ci` and `poetry install`; both exit 0 |
| Wall time of `make schemas-check` | 10 s | 30 s | `time make schemas-check` on the reference machine |

## Verification

A test regenerates the bundle into a scratch directory and compares every file
to the committed one; a second test recomputes the `toolchain.json` digest and
each manifest `data_schema.digest`; the offline run is a manual gate recorded in
the release notes until the corpus promotion gate makes it a CI job.

## Dependencies

- **Upstream**: [FR-005](../functional/FR-005-semantic-data-schemas.md), [FR-006](../functional/FR-006-semantic-manifest-block.md)
- **Downstream**: the release gauntlet of this module
