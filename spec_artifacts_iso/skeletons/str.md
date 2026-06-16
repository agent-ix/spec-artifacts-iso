---
id: StR-001
title: "Operators need tamper-evident artifact imports"
type: StR
relationships:
  - target: "ix://agent-ix/example/FR-001"
    type: "satisfied_by"
---
<!-- StR authoring skeleton (spec-artifacts-iso). ISO/IEC/IEEE 29148 stakeholder
     requirement. Fill every section with substantive content. Contract
     (manifest body_extraction asserts):
     - REQUIRED (level 2): Stakeholder Need (what the stakeholder needs, no
       solution), Rationale (why the need exists), Validation Criteria (how
       satisfaction is judged).
     - OPTIONAL (level 2): Stakeholders, Context and Assumptions, Stakeholder
       Constraints (Contextual), Dependencies, Priority and Risk
       (Informative), Notes (Informative), Traceability.
     - State the need normatively (shall/must/require) — a `str-shall-language`
       lint advisory checks this.
     - Keep headings unique per level; nest ≤2 levels below the H1 title. -->
# [StR-001] Operators need tamper-evident artifact imports

## Stakeholder Need

Platform operators require that every artifact entering the platform shall be
verifiable against a declared cryptographic digest, so that corruption or
tampering is detected and rejected before any downstream system trusts the
artifact. The need is stated from the operators' perspective and avoids
prescribing a mechanism.

## Rationale

Operators are accountable for the integrity of distributed artifacts. Silent
corruption during transfer and the possibility of malicious substitution both
erode trust in the whole distribution pipeline, and today there is no signal that
the stored bytes match what was intended. Detecting tampering at the boundary
contains the blast radius and preserves confidence in the catalog.

## Validation Criteria

This need is considered satisfied when an artifact whose declared digest does not
match its bytes is rejected at import and never persisted, and when an artifact
whose digest matches is accepted. Satisfaction is judged by demonstrating both
outcomes against the import boundary with known-good and known-bad artifacts.

## Stakeholders

The primary stakeholders are platform operators, who are accountable for artifact
integrity and act as decision-makers for import policy. Downstream consumers of
the catalog are affected parties who rely on the guarantee but do not set it.

## Context and Assumptions

Artifacts arrive from an external build pipeline over a network that is not
assumed to be reliable. It is assumed that a trustworthy digest can be associated
with each artifact at or before import. The existing import workflow performs no
integrity check today.

## Stakeholder Constraints (Contextual)

Operators expect integrity verification to add only negligible overhead to an
import, since the import path is already perceived as slow. This is a
stakeholder-level expectation that may be refined into a concrete non-functional
requirement later.

## Dependencies

Relationships at the stakeholder level. **Upstream**: the platform's security
policy mandating tamper detection at trust boundaries. **Downstream**: an
anticipated functional requirement for checksum verification on import and a
non-functional requirement bounding its overhead.

## Priority and Risk (Informative)

Business value is high because the guarantee underpins trust in the catalog;
urgency is high given known transfer corruption; risk if unmet is acceptance of
tampered artifacts. Used for planning and sequencing only.

## Notes (Informative)

Discussion point for later analysis: whether the same guarantee should extend to
artifacts already stored before this need was adopted. Captured here without
introducing a new requirement.

## Traceability

This stakeholder need is expected to be satisfied by a functional requirement for
checksum verification on import and supported by a non-functional requirement
bounding verification overhead. Links are added incrementally as the
specification evolves.
