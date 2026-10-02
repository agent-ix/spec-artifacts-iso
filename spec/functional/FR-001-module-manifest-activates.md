---
id: FR-001
title: "Module manifest activates against filament-core"
type: FR
relationships:
  - target: "ix://agent-ix/filament-core-service/FR-035"
    type: "implements"
---
# FR-001: Module manifest activates against filament-core

## Description

The system **SHALL** publish a Filament Module manifest (`spec_artifacts_iso/manifest.yaml`) that conforms to filament-core-service [FR-035](ix://agent-ix/filament-core-service/FR-035) v1.0.0 and activates idempotently against `POST /api/v1/modules/activate`.


## Inputs

- `manifest.yaml` (this repo's package)
- Activation endpoint: `POST /api/v1/modules/activate`

## Outputs

- Module row in `modules` table
- Contributed archetypes, object_types, grammars, artifact_types per the manifest

## Behavior

The manifest **SHALL** conform to the FR-035 module-manifest schema
`filament-core-service` applies at activation, and re-activation **SHALL** be a
no-op (idempotent by content hash per FR-026-AC-1). This repository ships no copy
of that schema and states no criterion over it as a document (PLAT-902).

**Conformance to FR-035 is verified nowhere in this repository**, and this
requirement claims no otherwise. It is observable where the schema is applied, at
`POST /api/v1/modules/activate` — FR-001-AC-2 through AC-4, every one of which is
`🚧 Pending` with no test case, so FR-001 now has no covered criterion at all.
What is executed here is narrower and stands in for none of it: the module and
its `semantic` block load under quire (FR-006-AC-3, TC-048), and `quoin module
install` accepts it (FR-006-AC-6, TC-055, a Demonstration).

## Acceptance Criteria

| ID | Criteria | Verification |
|----|----------|--------------|
| FR-001-AC-2 | Activation against clean filament-core succeeds with 200 | Integration Test |
| FR-001-AC-3 | Re-activation returns no-op (same content hash) | Integration Test |
| FR-001-AC-4 | Each declared archetype/object_type/artifact_type appears in the corresponding filament-core table after activation | Integration Test |

## Dependencies

- **Upstream**: filament-core-service [FR-035](ix://agent-ix/filament-core-service/FR-035), FR-026, FR-034
- **Downstream**: consumer agents/editors discovering this module's contributions
