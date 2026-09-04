---
id: FR-001
title: "The alpha requirement"
type: FR
object: widget
status: approved
relationships:
  - target: "ix://agent-ix/repo-alpha/US-001"
    type: "implements"
    cardinality: "1:N"
---
# FR-001: The alpha requirement

## Description

The system SHALL do the alpha thing.

## Constraints

| ID | Constraint | Type | Validation |
|----|------------|------|------------|
| FR-001-CON-1 | The thing SHALL be bounded. | Boundary | Test (TC-001) |
| FR-001-CON-2 | The thing SHALL be whole. | Integrity | Inspection |

## Acceptance Criteria

| ID | Criteria | Verification |
|----|----------|--------------|
| FR-001-AC-1 | The thing happens. | Test (TC-001) |
| FR-001-AC-2 | The thing is whole. | Analysis |
