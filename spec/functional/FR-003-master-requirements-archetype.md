---
id: FR-003
title: "The master requirements spec is a validated archetype"
artifact_type: FR
relationships:
  - target: "ix://agent-ix/quire-rs/spec/functional/FR-032"
    type: "consumes"
  - target: "ix://agent-ix/spec-artifacts-iso/FR-002"
    type: "extends"
---
# [FR-003] The master requirements spec is a validated archetype

## Description

The root `spec/spec.md` of every component declares `artifact_type:
master-requirements` and carries the most consequential frontmatter in the spec
tree — `component_type`, `org`, `name`, `relationships` — yet no archetype
validated it (`quire validate spec.md` failed with `UnknownArchetype`). This was
an oversight: the eight ISO artifact archetypes (FR/NFR/StR/US/IT/TC/AC/CON) each
ship a frontmatter schema and a body-structure contract; the master spec shipped
neither.

The system **SHALL** register a ninth archetype, `master-requirements`, in the
unified shape (filament-core FR-035; quire-rs ADR 0003) so that `quire validate
spec.md` validates the master spec's frontmatter and canonical body structure.

The master-requirements archetype is **generic**: a single frontmatter type and a
single canonical body shape serve every `component_type` (library, service,
react, application, …). Component-type variation is expressed by *which other
artifacts exist* (domain/endpoint FRs for services, component FRs for react), not
by a different `spec.md` shape. This supersedes the prior two-template split
(`spec-template.md` vs `app-spec-template.md`); the application-specific sections
(Domain Model, Security Model) become **optional** sections of the one shape.

## Specification

### Inputs

- `spec_artifacts_iso/manifest.yaml` (the `master-requirements` artifact_type)
- An authored `spec/spec.md` master requirements document

### Outputs

- A `ValidationResult` (pass / line-numbered failures) from `validate_document`

### Behavior

- The frontmatter schema **SHALL** require `artifact_type` (const
  `master-requirements`), `name` (non-empty string), `org` (non-empty string), and
  `component_type`; it **SHALL** constrain `component_type` to a kebab-case token
  (`^[a-z][a-z0-9-]*$`), rejecting embedded spaces, comments, or empty values.
- The frontmatter schema **SHALL** type the optional fields it observes across the
  corpus — `implementation_language` (string|null), `tags` (array of string),
  `depends_on` (array), `standards_alignment` (array of string), `relationships`
  (array of `{target ^ix://, type, cardinality}`), `security_critical` (boolean) —
  and **SHALL** keep `additionalProperties: true` so a spec carrying an extra key
  is not rejected (the known keys are still type-checked). Unlike the FR/US
  schemas, it **SHALL NOT** require `id` or `title` (the master spec has neither).
- The body contract **SHALL** assert the canonical core: the H1 title `Master
  Requirements Specification`, and the H2 sections **Purpose**, **Scope**, **System
  Overview**, **Requirements Architecture**, **References**. **Purpose** and
  **References** are leaf prose, asserted as `section_body` (non-empty,
  non-placeholder); **Scope**, **System Overview**, and **Requirements
  Architecture** are containers (they may carry only `###` subsections) and are
  asserted as heading-presence locators.
- Optional sections (e.g. **Domain Model**, **Security Model**) and any additional
  H2 sections **SHALL** be accepted (the contract asserts required structure, it
  does not forbid extra sections), subject to per-level heading uniqueness
  (quire-rs FR-035).
- The archetype **SHALL** ship an authoring **skeleton** (`skeletons/spec.md`) — the
  single canonical master-spec example, the authoring source of truth — whose
  structure is consistent with the body asserts (FR-002-AC-6/7/8 parity).

## Constraints

| ID | Constraint | Type | Validation |
|----|------------|------|------------|
| FR-003-CON-1 | `master-requirements` is one generic archetype; component-type variation is not expressed as a distinct `spec.md` shape | Design | Schema Test |
| FR-003-CON-2 | `component_type` SHALL match `^[a-z][a-z0-9-]*$` (kebab-case, no enum) | Data | Schema Test |

## Acceptance Criteria

| ID | Criteria | Verification |
|----|----------|--------------|
| FR-003-AC-1 | The manifest declares a `master-requirements` artifact_type with a `frontmatter_schema_ref` and a `body_extraction` carrying `assert` facets | Schema Test |
| FR-003-AC-2 | The frontmatter schema requires `artifact_type` (const), `name`, `org`, `component_type`, does not require `id`/`title`, and constrains `component_type` to `^[a-z][a-z0-9-]*$` | Schema Test |
| FR-003-AC-3 | A conformant master `spec.md` passes `validate_document` | Integration Test |
| FR-003-AC-4 | A master spec missing `component_type` (or with an empty value) fails frontmatter validation with a diagnostic naming the field | Integration Test |
| FR-003-AC-5 | A master spec whose `component_type` is multi-word / capitalized / underscored / empty (e.g. `"Fast API Service"`, `React_Lib`, `""`) fails the kebab-case pattern. (An unquoted trailing `# …` is a YAML comment and is correctly ignored, not a violation.) | Integration Test |
| FR-003-AC-6 | A master spec missing the H1 title or any required canonical section (Purpose/Scope/System Overview/Requirements Architecture/References) fails with a line-numbered diagnostic | Integration Test |
| FR-003-AC-7 | A master spec carrying optional sections (Domain Model, Security Model) and additional H2 sections still passes | Integration Test |
| FR-003-AC-8 | The `master-requirements` skeleton (`skeletons/spec.md`) itself passes `validate_document` and satisfies the assert↔skeleton parity checks (FR-002-AC-6/7/8) | Schema + Integration Test |

## Dependencies

- **Upstream**: quire-rs FR-031/FR-032 (markdown validate, frontmatter schema), filament-core FR-035 (unified manifest shape)
- **Downstream**: the `/specify` master-spec authoring workflow; the spec-create-spec single-template merge; the ecosystem normalization sweep
