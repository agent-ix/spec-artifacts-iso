---
id: FR-002
title: "Archetypes use the unified shape and validate authored markdown"
type: FR
relationships:
  - target: "ix://agent-ix/filament-core-service/FR-035"
    type: "implements"
  - target: "ix://agent-ix/quire-rs/spec/functional/FR-032"
    type: "consumes"
  - target: "ix://agent-ix/spec-artifacts-iso/FR-001"
    type: "extends"
---
# [FR-002] Archetypes use the unified shape and validate authored markdown

## Description

> **CR (render removal — 2026-06-04):** templates are **removed** (parity with
> filament-core FR-035 CR-002 corrected and the quire-rs render retirement, commit
> 500a3d3). `template_ref` is no longer optional/legacy — it is **removed and
> rejected** by the manifest schema. The per-archetype **skeletons are the
> authoring source of truth** (replacing the former `.md.j2` templates and template
> placeholder defaults). The skeleton-removal of `templates/` and `template_ref:`
> manifest lines is an implementation task; this FR fixes the contract.

The system **SHALL** declare every ISO **artifact** archetype (FR, NFR, StR, US, IT,
TC, AC, CON) in the **unified archetype shape** (filament-core FR-035 CR-002;
quire-rs ADR 0003): `frontmatter_schema_ref` + `body_extraction` with `assert`
facets; **no `template_ref`**, no `required_sections`, no `variants`.

> **Note (master-requirements):** the module also registers a ninth archetype,
> `master-requirements` (the root `spec.md`), specified by **[FR-003](./FR-003-master-requirements-archetype.md)**. Its contract
> differs from the eight ISO artifact archetypes — it has no `id`/`title`
> frontmatter, asserts the canonical master-spec sections, and constrains
> `component_type` to a kebab-case pattern — so the "all eight" criteria below
> scope to the ISO **artifact** archetypes; `master-requirements` is covered by
> [FR-003-AC-1](./FR-003-master-requirements-archetype.md)/AC-8.

Each archetype's `body_extraction` **SHALL** assert its required structure such that
quire-rs `validate_document` (quire-rs FR-032) accepts a conformant authored
markdown artifact and rejects structural violations — without any render step. The
per-archetype **skeleton** is the canonical example an author fills; it is the
authoring source of truth and its structure **SHALL** be consistent with the
archetype's `body_extraction` asserts.


## Inputs

- `spec_artifacts_iso/manifest.yaml` (unified archetype declarations)
- An authored markdown artifact for an archetype

## Outputs

- A `ValidationResult` (pass / line-numbered failures) from `validate_document`
- An extracted data record from `extract` over the same `body_extraction`

## Behavior

- Each archetype **SHALL** assert section presence at the declared heading level, required tables (exact `columns`, `min_rows`), required lists (`min_items`), and id patterns where applicable.
- Acceptance-criteria / constraint id asserts **SHALL** use `{id}` interpolation (quire-rs FR-034) so row ids are prefixed with the document's own id and contiguous.
- Archetype structure **SHALL** keep headings unique per level (quire-rs FR-035) and fit the 2-level nesting ceiling (quire-rs ADR 0005 #4).
- Each archetype **SHALL** ship an authoring **skeleton** (the canonical example an author fills) — the authoring source of truth, replacing the removed `.md.j2` templates and their placeholder defaults.
- The manifest `body_extraction` asserts (`columns`, `level`, `id_pattern`, etc.) and the per-archetype skeleton **SHALL** be **mutually consistent**: the skeleton is a conformant instance of its own asserts, and the asserts are derived from / describe the skeleton's structure — neither is authoritative in isolation.

## Acceptance Criteria

| ID | Criteria | Verification |
|----|----------|--------------|
| FR-002-AC-1 | Every registered `artifact_types` entry (the eight ISO artifact archetypes plus `master-requirements`) declares `body_extraction` with `assert` facets; none declare `template_ref`, `required_sections`, or `variants` | Schema Test |
| FR-002-AC-2 | A conformant authored `FR` markdown artifact passes `validate_document`; copies with a missing required section, wrong Acceptance-Criteria columns, or a non-contiguous AC id each fail with a line-numbered diagnostic | Integration Test |
| FR-002-AC-3 | Acceptance-Criteria id asserts use `{id}` so a row prefixed with a different artifact's id fails | Integration Test |
| FR-002-AC-4 | Every archetype's declared headings are unique per level across its skeleton | Schema Test |
| FR-002-AC-5 | Each archetype ships an authoring skeleton that itself passes `validate_document` once filled with substantive content | Integration Test |
| FR-002-AC-6 | **(I1 — assert↔skeleton parity)** For every archetype, the manifest `body_extraction` asserts (heading set + levels, table `columns`, `id_pattern`s) are **consistent with / derived from** that archetype's skeleton: each asserted heading exists in the skeleton at the asserted level, each asserted table's literal header row matches the skeleton's table headers exactly, and each `id_pattern` matches the skeleton's seeded ids. This is a parity requirement, not mere presence. | Schema Test |
| FR-002-AC-7 | **(I2 — literal-consistency)** Each skeleton's heading set and literal table header rows match its archetype's asserts **exactly** (same text, same order, same level) — a diff in either direction fails. | Schema Test |
| FR-002-AC-8 | **(I3 — locator-kind distinction)** The asserts distinguish **heading-presence** locators (assert a heading exists at a given level) from **`section_body`** locators (assert the section's content is non-empty / non-placeholder per quire-rs FR-032). Each required ISO section is classified as one or the other, and the skeleton supplies substantive (non-placeholder) body for every `section_body`-asserted section. | Schema + Integration Test |

## Dependencies

- **Upstream**: filament-core-service FR-035 (CR-002 unified shape, render removed), quire-rs FR-031/FR-032/FR-033/FR-034/FR-035
- **Downstream**: the `/specify` authoring workflow; consumers validating ISO artifacts
