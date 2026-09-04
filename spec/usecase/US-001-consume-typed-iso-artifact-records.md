---
id: US-001
title: "Consume ISO artifacts as typed semantic records"
type: US
relationships:
  - target: "ix://agent-ix/spec-artifacts-iso/StR-001"
    type: "traces_to"
  - target: "ix://agent-ix/spec-artifacts-iso/FR-005"
    type: "exercises"
  - target: "ix://agent-ix/spec-artifacts-iso/FR-006"
    type: "exercises"
  - target: "ix://agent-ix/spec-artifacts-iso/FR-007"
    type: "exercises"
---
# US-001: Consume ISO artifacts as typed semantic records

## Story

**As a** semantic consumer of ISO artifacts (the quire-contract-ir frontends,
the filament-core-data code generators, and the Filament extraction API)
**I want** every ISO artifact type this module declares to publish a typed data
schema and an explicit Markdown mapping
**So that** I can read a requirement, test, index, log, or glossary as a record
whose fields, rows, relationships, and source locations are declared once,
instead of re-parsing the section prose in every consumer.

The story is stated from the consumer's side. It does not choose the schema
language, the emitter, or the manifest keys; those are decided by the functional
requirements that implement it.

## Context

The module's archetypes today carry `body_extraction` locators and frontmatter
schemas. The locators say which sections and tables a document must have; they
do not say what type the extracted values have. A consumer that receives the
extracted record gets a string per section and a tab-joined string for the first
table row, so an acceptance criterion, a constraint, or a glossary term is text
to be parsed again. Wave 4 of the semantic program (agent-ix/quoin#286)
introduced a module contract in which an archetype references its emitted JSON
Schema by path and digest (quoin FR-073) and Markdown forms map to semantic-core
declarations (quoin FR-071, FR-072). This module is one of the two read-only
fixture sources for that program.

## Acceptance Examples (Illustrative)

These examples clarify the consumer's expectations. They are illustrative only,
not test cases and not verification criteria.

### US-001-EX-1: Acceptance criteria arrive as rows

- **Given** a functional requirement whose `## Acceptance Criteria` table has
  three rows
- **When** the consumer reads its record
- **Then** it sees three criterion objects, each with an id, the criterion text,
  a verification method, and the test-case references the cell annotates

### US-001-EX-2: An unchanged document keeps validating

- **Given** a functional requirement that validated before this change
- **When** the module publishes the data schemas
- **Then** the document still validates and its record carries the same
  sections and rows the locators already extracted

## Options (Exploratory)

Approaches discussed during discovery, none of which imply commitment on this
story: hand-authored JSON Schema per type; a TypeSpec source compiled to JSON
Schema; a schema derived mechanically from the locator DSL. The functional
requirements select among them.

## Constraints (Contextual)

Consumers read the emitted schemas offline from the installed module; nothing may
require a network fetch of `https://schemas.agent-ix.org`. This context is
carried into the requirements as a constraint rather than restated as a story.

## Dependencies (Contextual)

Upstream: `@agent-ix/semantic-core` 0.1.0 (agent-ix/filament-core-data#35), the
quoin semantic module contract (agent-ix/quoin#293), the quire-rs semantic
extraction surface (agent-ix/quire-rs#388). Downstream: agent-ix/filament-core-data#36
and agent-ix/quire-contract-ir#52, which consume this module's schemas and
skeletons as fixtures.

## Priority and Risk (Informative)

P1 on the Wave 4 track: two downstream tickets wait on it. Risk if unmet is
that each consumer re-parses the same Markdown with its own rules and the
records disagree.

## Notes (Informative)

Requirement *definitions* are what the records carry. A test-case record
describes a test; the result of running it is not part of any record here.

## Traceability (Informative)

Traces to StR-001 (validated authoring of ISO artifacts) and is exercised by
FR-005, FR-006, and FR-007.
