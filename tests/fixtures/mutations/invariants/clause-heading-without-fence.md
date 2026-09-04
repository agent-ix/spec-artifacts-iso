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

### stated_in_prose_only

The persisted digest always equals the declared digest. This clause heading
carries no fence, so it yields no `ClauseRef`.

### digest_matches_declared

```ocl
context Artifact
inv digest_matches_declared:
  self.persisted implies self.computedDigest = self.declaredDigest
```

## Acceptance Criteria

| ID | Criteria | Verification |
|----|----------|--------------|
| FR-001-AC-1 | Given a matching digest, the artifact is persisted | Test (TC-001) |

## Dependencies

- **Upstream**: [US-001](../usecase/US-001-artifact-import.md) artifact import
