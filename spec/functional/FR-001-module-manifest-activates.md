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

> **CR-001 (property-idiom registry — 2026-08-07):** the manifest additionally
> declares a **`property_idioms:`** registry (quire-rs
> [FR-052](ix://agent-ix/quire-rs/spec/functional/FR-052), umbrella
> agent-ix/quire-rs#20): phrase → `{definition, shape}`, merged first-wins over
> the engine's built-in idioms. It is a **booster, never a prerequisite** —
> quire-rs FR-052-CON-4 derives `extractable` from the closed structural signals
> alone, so a declared phrase can only sharpen a criterion's *label* to a
> higher-precedence shape and can never make a criterion extractable, nor remove
> one from extraction. Nothing on that path emits a finding, so this declaration
> cannot change any validation verdict. The registry is deliberately small and
> every phrase is attested in the authored corpus; quire-rs CR-014 retired
> `no-observable-outcome` because an open set whose membership was *required* to
> earn a label reached ~13% sampled precision, and a speculative phrase list here
> would recreate that shape. This is the first numbered CR in this repo; the two
> earlier notes (FR-002, StR-001, "render removal") predate the sequence.
> AC-1 already covers the addition: the bundled FR-035 schema fixture is
> `additionalProperties: false`, so the new key is gated by that criterion and
> the fixture gains a `property_idioms` property with a `PropertyIdiomEntry`
> definition, exactly as `grammar_severity` and `lexicon` did before it.

The system **SHALL** publish a Filament Module manifest (`spec_artifacts_iso/manifest.yaml`) that conforms to filament-core-service [FR-035](ix://agent-ix/filament-core-service/FR-035) v1.0.0 and activates idempotently against `POST /api/v1/modules/activate`.


## Inputs

- `manifest.yaml` (this repo's package)
- Activation endpoint: `POST /api/v1/modules/activate`

## Outputs

- Module row in `modules` table
- Contributed archetypes, object_types, grammars, artifact_types per the manifest

## Behavior

The manifest **SHALL** validate against `module-manifest.schema.json` v1.0.0. Re-activation **SHALL** be a no-op (idempotent by content hash per FR-026-AC-1).

## Acceptance Criteria

| ID | Criteria | Verification |
|----|----------|--------------|
| FR-001-AC-1 | Manifest validates against FR-035 JSON Schema | Schema Test |
| FR-001-AC-2 | Activation against clean filament-core succeeds with 200 | Integration Test |
| FR-001-AC-3 | Re-activation returns no-op (same content hash) | Integration Test |
| FR-001-AC-4 | Each declared archetype/object_type/artifact_type appears in the corresponding filament-core table after activation | Integration Test |

## Dependencies

- **Upstream**: filament-core-service [FR-035](ix://agent-ix/filament-core-service/FR-035), FR-026, FR-034
- **Downstream**: consumer agents/editors discovering this module's contributions
