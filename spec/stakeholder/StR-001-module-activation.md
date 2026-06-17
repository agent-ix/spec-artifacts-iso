---
id: StR-001
title: "ISO-style spec artifact archetypes"
type: StR
---
# [StR-001] ISO-style spec artifact archetypes

> **CR (render removal — 2026-06-04):** templates are removed; the per-archetype
> **skeletons** are the authoring source of truth. The need is reframed from
> "generation" to fast, validated **authoring + structural validation**. The
> validation criterion below is revised off templates.

## Stakeholder Need

The Filament platform, its spec authors, and agent CLI authors and validators
require fast, structurally **validated authoring** of FR/NFR/StR/US/IT/TC
documents with consistent structure. The artifacts shall be authored as markdown
from the per-archetype skeletons and checked by `validate_document`, so authors
get a structurally conformant document without a render step.

## Rationale

ISO-style requirement artifacts only deliver value when every artifact of a given
class shares one predictable structure that tools and reviewers can rely on.
Authoring them by hand without a checked shape produces drift, and the prior
generation-from-templates approach was retired (render removal, 2026-06-04). A
Module that contributes the archetypes, skeletons, and structural asserts gives
authors a single source of truth and lets the platform validate conformance
mechanically rather than by review.

## Validation Criteria

This need is considered satisfied when both of the following hold:

- A Module activation against filament-core registers the contributions this
  Module declares (its archetype, grammar, artifact types, and frontmatter
  schemas).
- Agent CLI authors (quire-cli) can author and validate artifacts using the
  skeletons, the `body_extraction` asserts, and the frontmatter schemas this
  Module ships, with no template render.

## Dependencies

- **Upstream**: filament-core-service [FR-035](ix://agent-ix/filament-core-service/FR-035) (Module Manifest Schema)
