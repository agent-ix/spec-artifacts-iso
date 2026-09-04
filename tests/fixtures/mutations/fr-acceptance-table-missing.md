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

The criteria of this document were never tabulated: the section carries prose
where the table belongs.

## Dependencies

- **Upstream**: [US-001](../usecase/US-001-artifact-import.md) artifact import
