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
     - Validation Criteria table headers MUST be exactly:
       ID | Criteria | Validation with >=1 data row, ids `StR-NNN-VC-N`.
       The column is `Validation`, not `Verification`: ISO/IEC/IEEE 29148
       validates a stakeholder requirement against the stakeholder's real
       need, and verifies a system requirement against the spec. The method
       vocabulary is the same four
       (Inspection | Analysis | Demonstration | Test, optionally annotated
       `(TC-035)`) — a `vc-validation-method` lint advisory checks it — but
       expect `Demonstration` to dominate, because a stakeholder need is
       confirmed in an operational context rather than quantified over an
       input domain. That is correct, not a quality failure, and downstream
       property-test extraction should not treat it as one.
     - OPTIONAL (level 2): Stakeholders, Context and Assumptions, Stakeholder
       Constraints (Contextual), Dependencies, Priority and Risk
       (Informative), Notes (Informative), Traceability.
     - State the need normatively (shall/must/require) — a `str-shall-language`
       lint advisory checks this. The need SHOULD also follow EARS (advisory
       grammar `iso-spec-core`, FR-042): one `shall`, a concrete response;
       the subject may be the stakeholder or product (`The operator shall
       …`), not only "the system". `quire validate` warns on violations.
     - Keep headings unique per level; nest ≤2 levels below the H1 title. -->
# StR-001: Operators need tamper-evident artifact imports

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

| ID | Criteria | Validation |
|----|----------|------------|
| StR-001-VC-1 | An artifact whose declared digest does not match its bytes is rejected at import and never persisted. | Demonstration |
| StR-001-VC-2 | An artifact whose declared digest matches its bytes is accepted and persisted. | Demonstration |

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
