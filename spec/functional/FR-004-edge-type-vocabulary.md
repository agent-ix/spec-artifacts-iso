---
id: FR-004
title: "The edge-type and role vocabulary is declared module data"
type: FR
relationships:
  - target: "ix://agent-ix/spec-artifacts-iso/StR-001"
    type: "satisfies"
  - target: "ix://agent-ix/quire-rs/spec/functional/FR-040"
    type: "consumes"
  - target: "ix://agent-ix/quire-rs/spec/functional/FR-041"
    type: "consumes"
---
# FR-004: The edge-type and role vocabulary is declared module data

## Description

`manifest.yaml` declares the ecosystem's entire relationship vocabulary — **76 edge verbs across
7 categories**, 27 of which name an inverse, plus **9 capability roles** — and until this
requirement no document in this repository described any of it. It is load-bearing and it was
undocumented: quire-rs FR-040's `allowed_links` normalization reads it, the `UnknownEdgeType`
advisory is computed against it, and every `spec-objects-*` module's link declarations are written
in it.

The module **SHALL** declare each edge verb with a `description`, a `category`, and — where the
relationship is directional and both readings are authorable — an `inverse`. It **SHALL** declare
each role with a `description`.

### What a category means

A category states **what kind of fact** the verb records. It is not a namespace and it does not
constrain which archetypes may use the verb.

| Category | What its verbs record | Examples |
|---|---|---|
| `structural` | Composition and ownership of lifecycle | `contains`, `aggregates`, `composes` |
| `behavioral` | One thing invoking or driving another | `calls`, `triggers`, `transitions_to` |
| `dataflow` | Data moving or being acted on | `reads`, `writes`, `publishes`, `emits` |
| `dependency` | One thing needing another to exist or function | `depends_on`, `requires`, `implements`, `uses` |
| `realization` | A concrete artifact standing for an abstract one | `represents`, `exposes`, `realizes` |
| `governance` | Cross-cutting control, risk, and lifecycle management | `protects`, `mitigates`, `grants`, `rotates` |
| `traceability` | Spec-meta links between artifacts about artifacts | `satisfied_by`, `traces_to`, `derives_from`, `verifies` |

The `traceability` category is the one requirement-lineage checks read. A verb outside it records
a fact about the **system**; a verb inside it records a fact about the **specification**.

### Inverses

An `inverse` declares the same relationship authored from the other end. `satisfied_by` and
`satisfies` are one edge: a stakeholder requirement may declare `satisfied_by` pointing down, or
the functional requirement may declare `satisfies` pointing up, and a consumer that understands
the inverse sees one relationship either way (quire-rs FR-041).

A verb with **no** declared inverse is one where the reverse reading has no name — either because
the relationship is symmetric (`peer`) or because only one direction is meaningful to author
(`transitions_to`).

An inverse label is a **derived name, not a second declaration**. 25 of the 26 distinct inverse labels
(`part_of`, `called_by`, `implemented_by`, …) appear nowhere as `edge_types` keys, and that is
correct: quire-rs FR-041-AC-2 type-allows an authored edge whose verb is a declared inverse label
"even when the label is absent from `edge_types`". Requiring every inverse to be independently
declared would double the vocabulary with entries no author writes.

Two consequences follow, both governed by FR-041-AC-3 rather than forbidden here:

- **A label may be shared.** `contains` and `aggregates` both name `part_of`. Resolution is
  first-wins with a diagnostic, so which forward verb `part_of` normalizes onto depends on
  declaration order — and a *new* collision would silently change that. AC-2 pins the current
  set so a new one has to be deliberate.
- **A label may also be a forward verb.** `contains` is the only one: `contained_by` names it as
  its inverse while `contains` names `part_of` as its own. The forward registration governs.
  Notably `satisfies` is **not** a forward verb — it exists only as `satisfied_by`'s inverse
  label, yet the corpus authors it directly 38 times, which FR-041-AC-2 permits.

### Merge

Vocabularies merge across loaded modules **first-wins by verb name**, matching every other
registry in the manifest. A module redeclaring a verb another module already declared does not
replace it; the first declaration stands and the collision is a non-fatal diagnostic. Load order
is module load order, so the merged vocabulary is deterministic.

### Unknown verbs are advisory

A relationship whose verb is in no loaded module's vocabulary produces an **advisory**
`UnknownEdgeType` diagnostic and is **still harvested as an edge**. The vocabulary describes what
the ecosystem has agreed to say; it does not gate what an author may write, because a corpus that
refuses to load on an unrecognised verb cannot be migrated onto a new one.

### Adding a verb

A verb is added when an authored relationship in the corpus has no existing verb that records the
same **kind** of fact. Before adding one:

1. **Check the existing 76.** A near-synonym is a reason not to add, not a reason to add — see the
   finding below.
2. **State the category**, and check the verb records that kind of fact rather than a different
   one with a similar name.
3. **Declare the inverse** if the reverse reading is something an author would write.
4. **Do not add a verb to make an existing document validate.** That is fitting the vocabulary to
   the corpus rather than describing the relationships the ecosystem means to have.

## Decided: `satisfied_by` owns stakeholder-requirement lineage

**[RAN]** over 237 `~/dev` spec bundles, counting authored `relationships` entries:

| Verb | Edges | Declared category | Declared meaning |
|---|---|---|---|
| `implements` | 956 | **dependency** | "Fulfils an interface/contract" |
| `traces_to` | 368 | traceability | "Traceability link (matrix/coverage)" |
| `satisfied_by` | 328 | traceability | "Stakeholder requirement satisfied by the target" |
| `derives_from` | 131 | traceability | "derived/refined from the target (decomposition lineage)" |
| `satisfies` | 38 | traceability | inverse of `satisfied_by` |
| `exercises` | 25 | traceability | "User story exercises a functional requirement" |
| `refines` | 2 | **undeclared** | — |

**The decision (2026-08-18, kreneskyp):** `implements` keeps its declared meaning — an interface
or contract being fulfilled — and is **not** overloaded for requirement lineage.
**`satisfied_by` is the generic stakeholder-requirement-to-artifact relationship**, authorable
from either end via its `satisfies` inverse.

The two descriptions are tightened to say so, which is a clarification of existing entries rather
than a change to the vocabulary: `implements` now states the exclusion explicitly, and
`satisfied_by` states that it is the generic StR-to-artifact link rather than a narrow one.

Two consequences, both **corpus debt** rather than vocabulary gaps:

- **956 edges spell requirement lineage `implements`.** They are wrong under the decision above
  and should be `satisfies` (or the stakeholder requirement's own `satisfied_by`). This is the
  largest single migration the vocabulary implies and it is tracked separately — it is not fixed
  here, and it is not a reason to soften either verb's meaning.
- **`refines` is not in the vocabulary** and is authored twice, so those two edges are
  `UnknownEdgeType` findings and should become `satisfies` or `derives_from` depending on what
  their authors meant.

quire-rs FR-058's upward-trace relations follow this decision: they accept `satisfies` and
`satisfied_by`, not `implements`.

## Acceptance Criteria

| ID | Criteria | Verification |
|----|----------|--------------|
| FR-004-AC-1 | Every entry in `edge_types` carries a non-empty `description` and a `category` drawn from the seven declared categories. | Test (TC-SCHEMA-009) |
| FR-004-AC-2 | Every `inverse` label is a non-empty identifier, and the set of labels declared by more than one verb is exactly the recorded set — so a **new** collision, which FR-041-AC-3 resolves first-wins and would silently change which forward verb the label normalizes onto, fails rather than passing quietly. | Test (TC-SCHEMA-010) |
| FR-004-AC-3 | An inverse label is **not** required to be a declared `edge_types` key: FR-041-AC-2 type-allows it regardless, and requiring it would double the vocabulary with entries no author writes. The recorded count of labels that are not forward verbs is asserted, so a change in that ratio is visible. | Test (TC-SCHEMA-011) |
| FR-004-AC-4 | Every entry in `roles` carries a non-empty `description`. | Test (TC-SCHEMA-012) |
| FR-004-AC-5 | The manifest loads under the module-manifest schema with the vocabulary present, and a malformed entry (missing `category`, unknown key) fails module load rather than loading partially. | Test (TC-SCHEMA-013) |

## Constraints

| ID | Constraint | Verification |
|----|-----------|--------------|
| FR-004-CON-1 | This requirement describes the vocabulary and may **clarify** an existing entry's description; it adds and removes no verb. Additions belong to the module that needs them (`spec-objects-security#5` owns the safety-chain verbs) and follow the criteria above. | Inspection |
| FR-004-CON-2 | An unrecognised verb SHALL stay advisory. Making `UnknownEdgeType` fatal would make the vocabulary unmigratable — every rename would break every document using the old verb before any could be updated. | Inspection |

## Dependencies

- **Upstream**: [StR-001](../stakeholder/StR-001-module-activation.md)
- **Downstream**: quire-rs FR-040 (`allowed_links` normalization and `UnknownEdgeType`), quire-rs FR-041 (authorable inverse edges), quire-rs FR-058 (upward-trace relations, which take their verbs from the decision above), `spec-objects-*` link declarations
