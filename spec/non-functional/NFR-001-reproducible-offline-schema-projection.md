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
committed TypeSpec source and lockfile on any machine that satisfies the
toolchain and npm-configuration preconditions of Scope.

The emitted bundle SHALL validate and resolve with no network read.

## Scope

- Applies to: `make schemas`, `make schemas-check`, the digests in
  `manifest.yaml`, and every `$ref` resolution performed by this module's tests.
- Operational context: a clean clone with `npm ci` in the TypeSpec package and
  the quire wheel installed; the only network access is the package install
  itself.
- npm-configuration precondition: `@agent-ix/semantic-core` 0.3.0 resolves only
  from the registry the developer's npm configuration routes the `@agent-ix`
  scope to — today the local npm.ix registry; the public publish is tracked by
  agent-ix/filament-core-data#11. The repository carries no `.npmrc`
  (FR-005-CON-3), so the scope routing is the machine's and not the
  repository's, and a machine whose npm configuration does not route the scope
  cannot reproduce the bundle at all.
- Engine floor: the suite runs against `quire >= 0.33.0` installed from the
  internal package index. The engine work that would validate an artifact-type
  record against `data_schema` (quire-rs FR-069) is in no published wheel, so
  no engine reproduces this module's record validation offline today; see
  agent-ix/quire-rs#393 and agent-ix/quire-rs#388.
- Line endings: the repository pins LF line endings via `.gitattributes`
  (`* text=auto eol=lf`), so the emitted bundle, the golden records, and every
  `manifest.yaml` digest are checkout-independent — the digests are computed
  over bytes with no line-ending normalization, and a CRLF checkout would
  change every one of them.

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
each manifest `data_schema.digest`; the offline run is a manual gate of this
repository, recorded in the release notes. No CI job is claimed by this
requirement or by the ticket that introduces it; the manual gate stands until a
CI job for it is filed against this repository.

## Dependencies

- **Upstream**: [FR-005](../functional/FR-005-semantic-data-schemas.md), [FR-006](../functional/FR-006-semantic-manifest-block.md)
- **Downstream**: the release gauntlet of this module
