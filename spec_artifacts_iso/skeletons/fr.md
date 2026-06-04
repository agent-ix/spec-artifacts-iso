---
id: FR-001
title: "Verify checksums on artifact import"
artifact_type: FR
relationships:
  - target: "ix://agent-ix/example/US-001"
    type: "implements"
---
<!-- FR authoring skeleton (spec-artifacts-iso). Fill every section with
     substantive content. Contract (manifest body_extraction asserts):
     - All H2 sections below are required (heading level 2).
     - Constraints table headers MUST be exactly: ID | Constraint | Type | Validation
       with ≥1 data row; the ID column matches ^<this-doc-id>-CON-\d+$.
     - Acceptance Criteria table headers MUST be exactly: ID | Criteria | Verification
       with ≥1 data row; the ID column matches ^<this-doc-id>-AC-\d+$.
     - Keep headings unique per level; nest ≤2 levels below the H1 title (through H3). -->
# [FR-001] Verify checksums on artifact import

## Description

The system SHALL verify the SHA-256 checksum of every imported artifact before
persisting it, rejecting any artifact whose computed digest does not match the
declared digest.

## Specification

### Inputs

- Imported artifact bytes
- Declared SHA-256 digest from the import manifest

### Outputs

- Accepted artifact persisted to the store
- Rejection error carrying the declared/computed digest pair

### Behavior

- The system SHALL compute the SHA-256 digest of the artifact bytes on import.
- The system SHALL reject the artifact when the computed digest differs from the
  declared digest.
- The system SHALL persist the artifact only after a successful digest match.

## Constraints

| ID | Constraint | Type | Validation |
|----|------------|------|------------|
| FR-001-CON-1 | Digest computation SHALL use SHA-256 only | Security | Integration Test |

## Acceptance Criteria

| ID | Criteria | Verification |
|----|----------|--------------|
| FR-001-AC-1 | Given a matching digest, the artifact is persisted | Integration Test |
| FR-001-AC-2 | Given a mismatched digest, the import is rejected | Integration Test |

## Dependencies

- **Upstream**: US-001 artifact import
- **Downstream**: IT-001 checksum rejection coverage
