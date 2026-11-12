---
id: SR-021
title: "Base spec review — FR-008 optional criticality field (PLAT-1412, #70)"
type: SpecReview
analysis: base
scope: "agent-ix/spec-artifacts-iso; spec/functional/FR-008-criticality-field.md, spec/functional/index.md"
review_set: subset
---
# SR-021: Base spec review — FR-008 optional criticality field (PLAT-1412, #70)

## Summary

Ticket: PLAT-1412. PR agent-ix/spec-artifacts-iso#70, diff `origin/main...8f142c1`:
new FR-008 and one index line. Checked against the spec-review checklist,
FR-005 (schema projection rules), the module manifest and
`spec_artifacts_iso/semantic/scripts/generate.mjs`. Review set: subset (base,
ears-conformance, dependency, integrity). No AssuranceProfile exists in the
repo, so no enforced spec-review run applies.

`quire validate --scope . spec/functional/FR-008-criticality-field.md spec/functional/index.md`
exits 0 (quire 0.40.0, engine 0.56.0); the two printed warnings are about the
local module environment, not these files. No hash, digest, pin or
tracking-record instruction is present. IDs are well formed and sequential.

## Verdict

**Changes requested.** The intent is sound: optional, never defaulted,
human-authored, vocabulary owned by the module. Strict case and the
empty-string rejection are well covered. But the single-source mechanism the
FR mandates does not fit how this module's frontmatter schemas and projection
directory work (FND-001). The semantic records are left out (FND-002). The
enumeration values need an owner decision against the project's
safety-class goal (FND-003).

## Findings

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-001 | high | FR-008-CON-1 / AC-1 mandate that the hand-authored `*-frontmatter.schema.json` files `$ref` a shared `Criticality.json`. No frontmatter schema in this module, or any sibling module, uses a cross-file `$ref` (engineering-assurance uses only `#/$defs`). These schemas have no `$id`. quire-rs compiles them with no base URI or resource registry, and the wasm build drops `resolve-file`. Also, `generate.mjs` treats every `schemas/*.json` that is not `*-frontmatter.schema.json` as a TypeSpec projection. So a hand-written `Criticality.json` is reported `(stale)` by `make schemas-check` and deleted by `make schemas`, unless it is emitted from `main.tsp`, and FR-008 does not say so. The precedent (`quality_attribute`) inlines the enum in the frontmatter schema and emits `QualityAttribute.json` from TypeSpec. State the real mechanism. | spec/functional/FR-008-criticality-field.md:23-25, :36, :47; spec_artifacts_iso/semantic/scripts/generate.mjs:125-160; spec_artifacts_iso/schemas/nfr-frontmatter.schema.json |
| FND-002 | medium | FR-008 changes only the frontmatter schemas. The FR-005 semantic models for `FR`, `NFR`, `StR` and `US` are sealed (`unevaluatedProperties: {not: {}}`). Nothing adds an optional `criticality` field or a `frontmatter_field` locator, the way `qualityAttribute` was added for NFR. So the typed record never carries the value even when it is authored. AC-3's "the validated record carries no `criticality` value" names no record and passes trivially. | spec/functional/FR-008-criticality-field.md:22-30, :38; spec_artifacts_iso/semantic/main.tsp:315; spec_artifacts_iso/manifest.yaml:241-247 |
| FND-003 | medium | The values `low`/`medium`/`high` come with no rationale, no stated order and no mapping. The ticket gave no guidance. The owning project is "Criticality and Software Safety Class", and M2 is per-software-safety-class evidence floors, which suggests IEC 62304 class A/B/C or a similar scheme. Three generic ordinal levels are a reasonable standard-agnostic choice, but closing a vocabulary is an owner decision. State whether `criticality` is the safety class or a separate axis that M2 maps, and state the order low < medium < high. | spec/functional/FR-008-criticality-field.md:23-25 |
