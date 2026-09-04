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
| FR-001-AC-1 | Given a matching digest, the artifact is persisted | Test (TC-001) |

### FR-001-AC-1

The first supplement of this row.

### FR-001-AC-1

The second supplement of the same row.

## Dependencies

- **Upstream**: [US-001](../usecase/US-001-artifact-import.md) artifact import
