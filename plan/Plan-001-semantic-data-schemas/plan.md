---
id: Plan-001
title: "spec-artifacts-iso — semantic data schemas and Markdown mappings"
type: Plan
status: active
relationships:
  - target: ix://agent-ix/spec-artifacts-iso/US-001
    type: references
  - target: ix://agent-ix/spec-artifacts-iso/FR-005
    type: references
  - target: ix://agent-ix/spec-artifacts-iso/FR-006
    type: references
  - target: ix://agent-ix/spec-artifacts-iso/FR-007
    type: references
  - target: ix://agent-ix/spec-artifacts-iso/NFR-001
    type: references
---
# Implementation Plan: semantic data schemas and Markdown mappings

Ticket agent-ix/spec-artifacts-iso#34. The module gains a semantic layer: one
TypeSpec model per ISO artifact type, a deterministic JSON Schema projection of
those models, a manifest that binds each archetype to the shipped schema bytes
by digest, and a declared Markdown-to-record mapping with golden records that
prove the three agree.

## Requirements Summary

### Stakeholder Requirements

None new. StR-001 (module activation) is unchanged and already discharged.

### User Stories

- [x] **US-001**: a consumer loads the module and gets typed ISO artifact
  records — schemas it can validate against, and a mapping that says how a
  document becomes one.

### Functional Requirements

- [x] **FR-005**: one semantic data model per ISO artifact type, declared in
  TypeSpec importing `@agent-ix/semantic-core` 0.1.0, projected to JSON Schema
  2020-12 at `spec_artifacts_iso/schemas/<Model>.json` by the official
  `@typespec/json-schema` emitter, with `make schemas` / `make schemas-check`
  and a `toolchain.json` recording the toolchain and the bundle digest.
- [x] **FR-006**: the manifest carries the quoin FR-070 `semantic` block and
  references each emitted schema by module-relative path and SHA-256 digest,
  with no inline `data_schema` left and no new required key.
- [x] **FR-007**: `mappings.yaml` declares, per model property, the mapping kind
  and its source across eight kinds, plus the round-trip policy; one golden
  record per skeleton under `examples/`; a Python reference mapping in test
  support as the oracle.

### Non-Functional Requirements

- [x] **NFR-001**: the projection is byte-reproducible from the committed
  TypeSpec source and lockfile, and resolves with no network read.

## Dependency Graph

- `FR-005 -> FR-006`
  Reason: FR-006 references the emitted files by path and digest, so the files
  and their bytes must exist and be final before a digest means anything.
- `FR-005 -> FR-007`
  Reason: `mappings.yaml` must name exactly the properties the models declare,
  and the golden records must validate against the emitted schemas.
- `FR-006 -> FR-007`
  Reason: the `invariants` locator FR-006 adds to the FR archetype is what the
  `ocl-clause` mapping reads, and the FR skeleton's new `## Invariants` heading
  must be declared before a document carrying it can validate.
- `FR-005, FR-006, FR-007 -> NFR-001`
  Reason: reproducibility is a property of the projection, the digests, and the
  golden records together; it cannot be measured until all three exist.
- `manifest version bump -> FR-005`
  Reason: every emitted `$id` embeds the manifest `version`, so the bump is the
  first edit of the change and the projection is computed once afterwards.
  (Done: `manifest.yaml` is already at `0.2.0` and the bundle carries
  `/0.2.0/` `$id`s.)

Shared deliverables, extracted so two tracks do not build them twice:

- The **reference mapping** (`tests/support/reference_mapping.py`) is consumed by
  TC-044, TC-045, TC-050, TC-051 and TC-053. It is one deliverable owned by one
  task, not a helper each test grows for itself.
- The **digest helper** (`sha256:` over shipped bytes) is consumed by the
  manifest refresh target and by TC-047 and TC-063. The suite never
  hand-computes a digest.

## Test Plan

Every row below is `spec/tests.md` TC-039..TC-063. The suite carries the trace
tag form this repository already uses, so `quire coverage` binds each row.

| TC | Type | Verifies |
|----|------|----------|
| TC-039 | Unit | FR-005-CON-1 — every locator output is a model property and every property traces back |
| TC-040 | Unit | FR-005-AC-3, CON-1 — every property constrained, or `free text:` with a reason from the closed list |
| TC-041 | Unit | FR-005-AC-1, AC-2, CON-2 — ten exported schemas, 2020-12 `$schema`, versioned `$id`, every `$ref` resolves offline |
| TC-042 | Integration | FR-005-AC-5 — `make schemas-check` exits 0 clean, non-zero naming the file after a one-byte edit |
| TC-043 | Static | FR-005-AC-6, CON-4 — no execution-result property; `TC.json` says results are not modelled |
| TC-044 | Snapshot | FR-005-AC-4, FR-007-AC-2 — reference mapping reproduces every golden record; each validates |
| TC-045 | Unit | FR-005-AC-4, FR-007-AC-6 — ten negative cases fail, all reported together, no partial record |
| TC-046 | Unit | FR-006-AC-1, AC-7, CON-1 — manifest validates with the block; nine keys exactly; legacy fixture still validates and loads |
| TC-047 | Unit | FR-006-AC-2, AC-5, CON-2 — every reference resolves and digests match; a one-byte edit fails naming both digests |
| TC-048 | Integration | FR-006-AC-3 — at the published floor, eleven archetypes load and every skeleton validates |
| TC-049 | Unit | FR-006-AC-4 — the bundled FR-035 schema rejects the four malformed forms and matches a77f31e |
| TC-050 | Snapshot | FR-007-AC-5, CON-1 — the pre-change skeletons at 3d87196 still map to valid records |
| TC-051 | Unit | FR-007-AC-4, CON-2 — the `ocl-clause` mapping, its five failures and its two absences |
| TC-052 | Unit | FR-007-AC-1, AC-7 — `mappings.yaml` validates, covers every property once, records the policy |
| TC-053 | Unit | FR-007-AC-3 — the FR skeleton's AC and constraint rows split as specified |
| TC-054 | Static | FR-005-CON-3 — pinned toolchain, committed lockfile, no `file:`/`link:`, no `.npmrc` |
| TC-055 | Manual | FR-006-AC-6 — the `quoin module install` refusal recorded against agent-ix/quoin#336 |
| TC-056 | Property | NFR-001 metric 1 — two consecutive `make schemas` runs are byte-identical |
| TC-057 | Manual | NFR-001 metric 2 — no network read with the namespace disabled |
| TC-058 | Benchmark | NFR-001 metric 3 — `make schemas-check` within 30 s |
| TC-059 | Static | FR-007-CON-3 — nothing in the module writes Markdown; the mapping opens documents read-only |
| TC-060 | Unit | FR-005-AC-8 — properties declared inline; the Python validator accepts every golden and rejects every mutation |
| TC-061 | Unit | FR-005-AC-7 — emitted file set and digest equal `toolchain.json`, with no toolchain run |
| TC-062 | Integration | FR-005-AC-9 — the sdist/wheel and npm payload entry sets agree and carry no toolchain file |
| TC-063 | Integration | FR-006-AC-8 — a one-digit digest edit is refused at load; strict expected failure until agent-ix/quire-rs#388 |

## Remaining Work

### Track A: Critical Path (serial)

- **A1 = Task-001** TypeSpec models realigned with the reviewed FR-005 — Medium;
  exit: `make schemas` regenerates a bundle in which `Verification` carries
  `annotation`, `Constraint.validation` is a `Verification`, `Relationship` is
  sealed to three properties, and two runs are byte-identical.
- **A2 = Task-002** Schema-projection suite — Medium; exit: the emitted bundle's
  shape, constraint coverage, offline `$ref` closure, digest identity and
  drift gate are all asserted by tests that fail when the bundle changes.
- **A3 = Task-003** Manifest `semantic` block and digest references — Medium;
  exit: the manifest carries the block and ten reference-form `data_schema`
  entries, `make manifest-digests` rewrites them from shipped bytes, and the
  module still loads with eleven archetypes at the published floor.
- **Gate = Task-004** Record-shape gate — measures whether a record built from a
  real skeleton validates against its emitted schema; pass: all ten skeletons
  produce a record their model accepts. If it fails, the models and the
  locators disagree and Track C must not start.
- **A4 = Task-005** `mappings.yaml`, its schema, and the golden records — Hard;
  exit: every model property has exactly one mapping entry, the ten golden
  records are reproduced byte-for-byte, and the mapping file validates.

### Track B: Parallel (independent agent, can start now)

- **B1 = Task-006** Packaging and toolchain conformance — Easy; exit: the sdist,
  the wheel and the npm tarball carry the same payload entry set and no
  TypeSpec toolchain file, and the pinned-dependency rules are asserted.
- **B2 = Task-007** Corpus census script — Easy; exit: the census the spec cites
  is reproducible from a committed script with a smoke test, over a corpus root
  given as an argument rather than a hard-coded path.

### Track C: Post-Gate

- **C1 = Task-008** Mapping failure semantics — Hard; exit: every negative case
  named by FR-007-AC-6 and FR-005-AC-4 fails at the right line, all failures in
  one document are reported together, and no partial record is emitted.
- **C2 = Task-009** `## Invariants` and the `ocl-clause` mapping — Medium; exit:
  the FR skeleton's clause maps to a `ClauseRef`, the five failure forms fail
  naming the line, a prose `## Invariants` is not a failure, and the FR-002
  skeleton/assert parity checks still pass.
- **C3 = Task-010** Reproducibility and offline measurements — Easy; exit: the
  three NFR-001 metrics have runnable evidence and the two manual gates say
  plainly what was run and on what.

## Parallel Execution Summary

```
 Track A  A1 ──> A2 ──> A3 ──> [Gate] ──> A4
 Track B  B1 ─────────────────────────────────>
          B2 ─────────────────────────────────>
 Track C                        └──> C1, C2, C3 (after the gate)
```

## Task File Mapping

| Task | Track | Owns (references) | Verified by (verifies) | Status |
|------|-------|-------------------|------------------------|--------|
| Task-001 | A | FR-005 | TC-039, TC-040 | done        |
| Task-002 | A | FR-005 | TC-041, TC-042, TC-043, TC-060, TC-061 | done        |
| Task-003 | A | FR-006 | TC-046, TC-047, TC-048, TC-049 | done        |
| Task-004 | Gate | US-001 | TC-044 | done        |
| Task-005 | A | FR-007 | TC-044, TC-050, TC-052, TC-053 | done        |
| Task-006 | B | FR-005 | TC-054, TC-062 | done        |
| Task-007 | B | FR-005 | TC-040 | done        |
| Task-008 | C | FR-007 | TC-045 | done        |
| Task-009 | C | FR-007 | TC-051, TC-059 | done        |
| Task-010 | C | NFR-001 | TC-056, TC-057, TC-058, TC-063, TC-055 | done        |

## Coordination Rules

- **`main.tsp` is single-writer.** Task-001 owns it. No other task edits the
  TypeSpec source; a task that needs a model change files it against Task-001
  rather than editing in place, because a concurrent edit invalidates every
  digest downstream.
- **Freeze `manifest.yaml` `version` at 0.2.0** for the whole plan. Every
  emitted `$id` and every recorded digest embeds it, so a second bump means a
  second full regeneration.
- **Never hand-edit an emitted schema.** `spec_artifacts_iso/schemas/<Model>.json`
  is generated; `make schemas` is the only writer and `make schemas-check` is
  the gate. A hand edit is exactly the drift the gate exists to catch.
- **Do not start Track C before the gate.** Task-008 and Task-009 both build on
  the reference mapping Task-005 delivers; starting them early means two
  implementations of the same oracle.
- **No corpus repository edits.** The census reads `~/dev/*/spec` and writes
  nothing. Any corpus defect it finds is reported, never fixed here.
- **Merge order** is A1, A2, A3, gate, A4, then C1..C3; Track B merges whenever
  it is green, because it touches only packaging files and `scripts/`.
