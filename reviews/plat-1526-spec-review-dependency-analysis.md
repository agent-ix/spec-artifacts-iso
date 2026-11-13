---
id: SR-034
title: "Dependency review — FR-009 software safety class field (PLAT-1526, #73)"
type: SpecReview
analysis: dependency
scope: "agent-ix/spec-artifacts-iso; spec/functional/FR-009-software-safety-class-field.md"
review_set: subset
---
# SR-034: Dependency review — FR-009 software safety class field (PLAT-1526, #73)

## Summary

Ticket: PLAT-1526, PR agent-ix/spec-artifacts-iso#73. FR-009 adds four new frontmatter edges: `satisfies` StR-001,
`extends` FR-002, FR-005 and FR-007, and `references` FR-008. All of them resolve and fit their purpose. The
cross-repo links go only in the body: spec-objects-architecture FR-012, quire-rs FR-090/FR-091 and quoin FR-160,
which exist on sibling PRs #45, #669 and #855.

The enablement part is the module's own data: schemas, `main.tsp`, `mappings.yaml` and skeletons (AC-1..11).
AC-12 is the exception, because it depends on engine work. The current quire-rs `TraceabilityModel`
(`src/traceability.rs:350`, `#[serde(deny_unknown_fields)]`) has no `carried_fields` member. A manifest that declares
the AC-12 entry therefore fails module load until FR-090 is implemented. The reviewer of quire-rs#669 also raised
high findings against FR-090's model on PLAT-1526: carrying the value as a top-level key named by module data
does not fit the published coverage contract.

## Verdict

**Changes requested.** There are two medium findings. AC-12 binds this module to an engine model that is not settled,
and FR-009 records that dependency in the wrong direction.

## Findings

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-001 | medium | AC-12 is compound and goes beyond this module. Its first half is module data: a `carried_fields` entry with `name`/`key` `software_safety_class` and `from: [StR, US, FR, NFR]`, and none for `criticality`. That shape matches FR-090 as written. Its second half ("a corpus over the module carries the stated class onto the coverage matrix entry and each obligation") is quire-rs FR-090-AC-1 behaviour restated. It inherits FR-090's open model: the top-level key under `name`, and an `additionalProperties: false` coverage contract. If FR-090 moves the value, for example into a nested map, AC-12 is wrong. | spec/functional/FR-009-software-safety-class-field.md:68 |
| FND-002 | medium | quire-rs FR-090 is listed under **Downstream** ("carries the stated class"). For AC-12 it is upstream: the engine must accept `traceability.carried_fields` before the module can declare it. quire-rs today seals `TraceabilityModel` with `deny_unknown_fields`, so landing the manifest entry first breaks module load for every corpus. No frontmatter edge to FR-090 exists, so blast-radius tooling cannot see the dependency. AC-12 needs a stated ordering ("after quire-rs FR-090 ships") and a typed edge such as `depends_on`. | spec/functional/FR-009-software-safety-class-field.md:79-80 |
