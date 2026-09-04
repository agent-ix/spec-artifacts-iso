---
id: FR-001
title: "Verify checksums on artifact import"
type: FR
relationships:
  - target: "ix://agent-ix/example/US-001"
    type: "implements"
---
# FR-001: Verify checksums on artifact import

## Description

The system SHALL verify the SHA-256 checksum of every imported artifact before
persisting it.

## Acceptance Criteria

| ID | Criteria | Verification |
|----|----------|--------------|
| FR-001-AC-1 | Given a matching digest, the artifact is persisted |
| FR-001-AC-2 | Given a mismatched digest, the import is rejected | Test (TC-002) |

## Dependencies

- **Upstream**: [US-001](../usecase/US-001-artifact-import.md) artifact import
