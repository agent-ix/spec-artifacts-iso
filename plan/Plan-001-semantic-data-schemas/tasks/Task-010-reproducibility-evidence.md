---
id: Task-010
title: "NFR-001 — reproducibility, offline resolution, and the blocked gates"
type: Task
status: done
track: C
priority: P1
relationships:
  - target: ix://agent-ix/spec-artifacts-iso/Task-005
    type: depends_on
  - target: ix://agent-ix/spec-artifacts-iso/NFR-001
    type: references
  - target: ix://agent-ix/spec-artifacts-iso/TC-055
    type: verifies
  - target: ix://agent-ix/spec-artifacts-iso/TC-056
    type: verifies
  - target: ix://agent-ix/spec-artifacts-iso/TC-057
    type: verifies
  - target: ix://agent-ix/spec-artifacts-iso/TC-058
    type: verifies
  - target: ix://agent-ix/spec-artifacts-iso/TC-063
    type: verifies
---
# Task-010: NFR-001 — reproducibility, offline resolution, and the blocked gates

## Scope

Evidence for the three NFR-001 measurements, and honest handling of the two
things that cannot be green here yet.

## Subtasks

- [ ] **TC-056** (metric 1): two consecutive `make schemas` runs on one tree
  produce byte-identical bundles for every emitted file.
- [ ] **TC-058** (metric 3): `make schemas-check` completes within 30 s.
- [ ] **TC-057** (metric 2): the offline run with the network namespace
  disabled. A manual gate; record the exact command and the machine.
- [ ] **TC-055**: run `quoin module install path:<module root>` and record the
  verbatim refusal against agent-ix/quoin#336, then restore the previously
  installed registry version. A manual gate.
- [ ] **TC-063**: a copy of the module with one `data_schema.digest` altered by
  one hex digit is refused at load. Recorded as a **strict** expected failure
  naming agent-ix/quire-rs#388 — never a skip, and never a pass. When the wheel
  arrives the strict marker turns the newly passing assertion into a failure,
  which is the signal to delete the marker.

## Deliverables

- `tests/test_reproducibility.py`
- The recorded manual-gate results in the PR body

## Notes

- The engine floor is `quire >= 0.33.0` from the internal index. quire-rs
  FR-069 is on main only (engine 0.46.0) and in no published wheel; pinning a
  locally built wheel would make the lockfile unreproducible on any other
  machine, which is the opposite of what NFR-001 asks for (SR-011 FND-411).
- `make schemas-check` cannot run in CI while `@agent-ix/semantic-core`
  resolves only from a scope-routed registry and the repository ships no
  `.npmrc` (SR-011 FND-410, agent-ix/filament-core-data#11). Say so; do not
  claim a CI job.
