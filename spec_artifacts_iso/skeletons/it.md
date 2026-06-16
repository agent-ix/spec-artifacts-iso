---
id: IT-001
title: "Checksum mismatch rejects the import"
type: IT
relationships:
  - target: "ix://agent-ix/example/FR-001"
    type: "verifies"
---
<!-- IT authoring skeleton (spec-artifacts-iso). ISO/IEC/IEEE 29119 integration
     test. Fill every section with substantive content. Contract (manifest
     body_extraction asserts):
     - REQUIRED (level 2): Objective, Target Integration, Preconditions,
       Inputs, Test Procedure, Expected Results.
     - OPTIONAL (level 2): Metadata, Dependencies, Notes, Traceability.
     - Test Procedure SHOULD declare per-step success criteria as
       IT-XXX-SC-NN tokens (the `it-success-criteria` lint advisory checks
       this); give each discrete action its own step.
     - Keep headings unique per level; nest ≤2 levels below the H1 title. -->
# [IT-001] Checksum mismatch rejects the import

## Objective

Verify the integration boundary between the import service and the artifact store
for the failure path: an artifact whose declared digest does not match its bytes
must be rejected end to end and never persisted. Without this test, silent
acceptance of a corrupted artifact would go undetected.

## Target Integration

The service under test is the import service. The external dependency is the
artifact store it persists to, reached over its HTTP persistence API. The
integration type exercised is an HTTP client call from the import service to the
store, triggered by submitting an artifact to the import endpoint.

## Preconditions

The import service and the artifact store are both running and reachable, and the
store is empty so the absence of a persisted row is meaningful. A unique artifact
identifier is allocated for this run to avoid collision with other tests.

## Inputs

A single artifact payload whose body is a known fixed byte sequence, accompanied
by a declared SHA-256 digest that is deliberately altered so it does not match the
payload. The mismatch is the property under test; all other fields are valid.

## Test Procedure

Each step performs one discrete action and has its own success criterion.

1. Submit the artifact and its mismatched declared digest to the import endpoint.
   - IT-001-SC-01: the endpoint returns a rejection status rather than success.
2. Inspect the rejection response.
   - IT-001-SC-02: the response carries both the declared and the computed digest.
3. Query the artifact store for the run's artifact identifier.
   - IT-001-SC-03: the store reports no artifact persisted for that identifier.

## Expected Results

The import is rejected with a digest-mismatch error that reports the declared and
computed digests, and the artifact store contains zero rows for the run's
identifier. The test passes only when every per-step success criterion holds.

## Metadata

- Priority: High
- Target Integration: artifact store HTTP persistence API
- Automation: Automated

## Dependencies

**Upstream**: the functional requirement for checksum verification on import,
which this test verifies. **Downstream**: none — no other test depends on this one.

## Notes

The complementary success path (a matching digest is accepted and persisted) is
covered by a separate integration test and is intentionally out of scope here.

## Traceability

This integration test verifies the checksum-verification functional requirement
and exercises the stakeholder need for tamper-evident imports.
