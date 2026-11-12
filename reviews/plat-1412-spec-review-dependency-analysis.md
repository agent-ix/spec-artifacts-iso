---
id: SR-023
title: "Dependency review — FR-008 criticality field (PLAT-1412, #70)"
type: SpecReview
analysis: dependency
scope: "agent-ix/spec-artifacts-iso; spec/functional/FR-008-criticality-field.md (relationships, Dependencies)"
review_set: subset
---
# SR-023: Dependency review — FR-008 criticality field (PLAT-1412, #70)

## Summary

Ticket: PLAT-1412. Checked the three new `relationships:` edges against the
manifest `edge_types` registry and the FR `allowed_links` list, and against the
Dependencies section. `satisfies` to StR-001 (lineage, per FR-004) and
`extends` to FR-002 are correct. FR-082 exists only on the open quire-rs PR
agent-ix/quire-rs#645, so the edge resolves once that PR lands. Land the two
PRs together.

## Verdict

**Changes requested.** One edge is wrong in both verb and direction.

## Findings

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-001 | medium | FR-008 declares `consumes` to quire-rs FR-082. In this manifest `consumes` is a dataflow verb ("Asynchronous reception from a channel"), not a spec dependency. It also points the wrong way: FR-082 consumes FR-008, and FR-008's own Dependencies section lists FR-082 as Downstream. With FR-082's `consumes` back to FR-008, the graph has a two-node `consumes` cycle. Drop the edge, or use `references`. | spec/functional/FR-008-criticality-field.md:10-11, :51; spec_artifacts_iso/manifest.yaml:846 |

## Dispositions

| FND | outcome | reason |
| --- | --- | --- |
| FND-001 | fixed | Round 1 (42fc231): edge to quire-rs FR-082 is now `references`; FR-082 (quire-rs#645) references FR-008 and lands with it. |
