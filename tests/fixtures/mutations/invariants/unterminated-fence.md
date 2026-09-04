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

## Invariants

### digest_matches_declared

```ocl
context Artifact
inv digest_matches_declared:
  self.persisted implies self.computedDigest = self.declaredDigest
