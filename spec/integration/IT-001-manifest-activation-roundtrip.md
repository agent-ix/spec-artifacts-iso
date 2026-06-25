---
id: IT-001
title: "Manifest activation roundtrip against filament-core"
type: IT
relationships:
  - target: "ix://agent-ix/spec-artifacts-iso/FR-001"
    type: "verifies"
---
# IT-001: Manifest activation roundtrip

## Objective

Verify that this Module's manifest activates against a clean filament-core-service
instance and that every contribution it declares — archetypes, object types,
grammars, and artifact types — lands in the database, and that re-activating the
same manifest is an idempotent no-op rather than a duplicate.

## Target Integration

The system under test is filament-core-service, reached over its HTTP module API.
The integration exercised is the module-activation path: a POST of this Module's
`manifest.yaml` to `/api/v1/modules/activate`, followed by GETs of
`/api/v1/archetypes`, `/api/v1/object-types`, `/api/v1/grammars`, and
`/api/v1/artifact-types` to read back what activation registered.

## Preconditions

A clean filament-core-service instance is running and reachable (the kind dev
cluster, or a freshly deployed instance) with no prior activation of this Module,
so that the presence of the declared contributions after activation is meaningful.

## Inputs

This Module's `spec_artifacts_iso/manifest.yaml`, posted unchanged to the
activation endpoint. The same manifest bytes are posted a second time to exercise
the idempotency path.

## Test Procedure

Each step performs one discrete action and has its own success criterion.

1. Deploy filament-core-service to a clean cluster (or use the kind dev cluster).
   - IT-001-SC-01: the service is reachable and reports no Module already activated.
2. POST `spec_artifacts_iso/manifest.yaml` to `/api/v1/modules/activate`.
   - IT-001-SC-02: the endpoint returns 200 OK and a Module row is created.
3. GET `/api/v1/archetypes`, `/api/v1/object-types`, `/api/v1/grammars`, and
   `/api/v1/artifact-types`.
   - IT-001-SC-03: each declared item is present with its correct attributes.
4. Re-POST the same manifest to `/api/v1/modules/activate`.
   - IT-001-SC-04: the re-activation is an idempotent no-op (same `modules.id`,
     no row duplication, same SHA-256 content hash).

## Expected Results

Activation returns 200 OK and creates exactly one Module row; every archetype,
object type, grammar, and artifact type this Module declares is readable back with
correct attributes; and re-posting the identical manifest produces the same
`modules.id` and SHA-256 content hash with no duplicated rows.

## Acceptance Criteria

| ID | Criteria |
|----|----------|
| IT-001-AC-1 | All success criteria in steps 1-3 hold (activation registers every declared contribution) |
| IT-001-AC-2 | Re-activation (step 4) produces the same SHA-256 content hash and no row duplication |
