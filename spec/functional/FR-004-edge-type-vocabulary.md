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
  - target: "ix://agent-ix/spec-objects-security/FR-030"
    type: "references"
---
# FR-004: The edge-type and role vocabulary is declared module data

## Description

`manifest.yaml` declares the ecosystem's entire relationship vocabulary — edge verbs across
7 categories, many of which name an inverse, plus capability roles — and until this
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

An inverse label is a **derived name, not a second declaration**. Most inverse labels
(`part_of`, `called_by`, `implemented_by`, …) appear nowhere as `edge_types` keys, and that is
correct: quire-rs FR-041-AC-2 type-allows an authored edge whose verb is a declared inverse label
"even when the label is absent from `edge_types`". Requiring every inverse to be independently
declared would double the vocabulary with entries no author writes.

Two consequences follow, both governed by FR-041-AC-3 rather than forbidden here:

- **A label may be shared.** Two forward verbs naming the same inverse label resolve
  first-wins with a diagnostic, so which forward verb the label normalizes onto depends on
  declaration order. No label is shared today (`contains` names `contained_in`, `aggregates`
  names `part_of`); a new collision would silently change that, so avoid one.
- **A label may also be a forward verb.** `contains` is one: `contained_by` names it as
  its inverse while `contains` names `contained_in` as its own. The forward registration governs.
  Notably `satisfies` is **not** a forward verb — it exists only as `satisfied_by`'s inverse
  label, yet the corpus authors it directly 38 times, which FR-041-AC-2 permits.

### Merge

Vocabularies merge across loaded modules **first-wins by verb name**, matching every other
registry in the manifest. A module redeclaring a verb another module already declared does not
replace it; the first declaration stands and the collision is a non-fatal diagnostic. Load order
is module load order, so the merged vocabulary is deterministic.

### Archetype `allowed_links` and the NFR `mitigates` edge

Each archetype's `allowed_links` is the set of verbs a document of that archetype may author
outward; a verb outside it is flagged `disallowed-edge-type` by single-file `quire validate`.
The `NFR` archetype's `allowed_links` **SHALL** include `mitigates`. A security or safety NFR
(`quality_attribute` `security` or `safety`) is required by `spec-objects-security` FR-008 and
`spec-objects-safety` FR-009 to mitigate a threat, hazard or failure mode, so the NFR-to-target
`mitigates` edge is a legitimate authored edge, not a vocabulary violation. The verb already
exists (`governance`); this adds it to the NFR's allowance and adds no verb.

### Control verification verbs

A control is verified in two different ways: that it was built as specified, and that it does its
job. One `verifies` edge cannot say which, so the vocabulary declares two further `traceability`
verbs, `verifies_implementation` and `verifies_effectiveness`. They record a fact about the
specification, name no inverse, and sit beside `verifies`, which stays as it was. The `NFR`, `IT`
and `TC` archetypes, which may author `verifies`, may author both. Whether a given control needs
either edge is a rule in the module that owns the control, not here.

The vocabulary SHALL declare `verifies_implementation` and `verifies_effectiveness` as `traceability` verbs, and the `NFR`, `IT` and `TC` archetypes SHALL allow both in `allowed_links`.

### SOUP requirement verb

A requirement a third-party (SOUP) record serves is asked for the requirements placed on that SOUP item. The verb
`soup_requirement_for` belongs to `spec-objects-security`
[FR-030](ix://agent-ix/spec-objects-security/FR-030), which declares it, with its inverse `has_soup_requirement`, in its
own `edge_types`. This vocabulary declares neither, so the module declaring them stays their single owner. The `FR` and
`NFR` archetypes author the statement, so their `allowed_links` SHALL include `soup_requirement_for`; otherwise a
statement that authors it draws an advisory `disallowed-edge-type` finding although the security module's relation counts
the edge. The inverse `has_soup_requirement` is not listed: an inverse label a loaded module declares is allowed on every
archetype (quire-rs FR-041-AC-2, as the Inverses section above states).

Listing a verb that this vocabulary does not declare has a cost, accepted because the security module and this one are
default modules released together: whenever `soup_requirement_for` is in no loaded vocabulary (this module loaded without
spec-objects-security, or with a security version that predates its declaration) every load prints the advisory
`UnknownEdgeType` for it, once per archetype, whether or not a document uses the verb. The advisory leaves the exit status
unchanged and goes away when a module that declares the verb is loaded.

The `FR` and `NFR` archetypes SHALL allow `soup_requirement_for` in `allowed_links`, and the vocabulary SHALL NOT declare it or `has_soup_requirement` in `edge_types`.

### Unknown verbs are advisory

A relationship whose verb is in no loaded module's vocabulary produces an **advisory**
`UnknownEdgeType` diagnostic and is **still harvested as an edge**. The vocabulary describes what
the ecosystem has agreed to say; it does not gate what an author may write, because a corpus that
refuses to load on an unrecognised verb cannot be migrated onto a new one.

### Adding a verb

A verb is added when an authored relationship in the corpus has no existing verb that records the
same **kind** of fact. Before adding one:

1. **Check the existing verbs.** A near-synonym is a reason not to add, not a reason to add — see the
   finding below.
2. **State the category**, and check the verb records that kind of fact rather than a different
   one with a similar name.
3. **Declare the inverse** if the reverse reading is something an author would write.
4. **Do not add a verb to make an existing document validate.** That is fitting the vocabulary to
   the corpus rather than describing the relationships the ecosystem means to have.

## Decided: `satisfied_by` owns stakeholder-requirement lineage

**The decision:** `implements` keeps its declared meaning — an interface
or contract being fulfilled — and is **not** overloaded for requirement lineage.
**`satisfied_by` is the generic stakeholder-requirement-to-artifact relationship**, authorable
from either end via its `satisfies` inverse.

The two descriptions are tightened to say so, which is a clarification of existing entries rather
than a change to the vocabulary: `implements` now states the exclusion explicitly, and
`satisfied_by` states that it is the generic StR-to-artifact link rather than a narrow one.

Two consequences, both **corpus debt** rather than vocabulary gaps:

- **Edges that spell requirement lineage `implements`.** They are wrong under the decision above
  and should be `satisfies` (or the stakeholder requirement's own `satisfied_by`). This is the
  largest single migration the vocabulary implies and it is tracked separately — it is not fixed
  here, and it is not a reason to soften either verb's meaning.
- **`refines` is not in the vocabulary**, so edges using it are
  `UnknownEdgeType` findings and should become `satisfies` or `derives_from` depending on what
  their authors meant.

quire-rs FR-058's upward-trace relations follow this decision: they accept `satisfies` and
`satisfied_by`, not `implements`.

## Acceptance Criteria

| ID | Criteria | Verification |
|----|----------|--------------|
| FR-004-AC-1 | Every entry in `edge_types` carries a non-empty `description` and a `category` drawn from the seven declared categories. | Test (TC-017) |
| FR-004-AC-4 | Every entry in `roles` carries a non-empty `description`. | Test (TC-020) |
| FR-004-AC-5 | The manifest declares both registries, and an `edge_types` entry that loses its `category` costs the module every archetype at load — a broken entry does not load partially. Asserted against the engine that reads the vocabulary, with an unmutated control proving the load is real. | Test (TC-021) |
| FR-004-AC-6 | `specifies` declares the inverse `specified_by`, so the object-FR to behavioral-FR edge is readable from the behavioral requirement. | Test (TC-065) |
| FR-004-AC-7 | The `NFR` archetype's `allowed_links` contains `mitigates`: single-file `quire validate` of an NFR carrying a `mitigates` relationship emits no `disallowed-edge-type` for it, while an NFR carrying a verb outside `allowed_links` still does. | Test (TC-070) |
| FR-004-AC-8 | The manifest declares `verifies_implementation` and `verifies_effectiveness` in the `traceability` category, and `verifies` is still declared. Single-file `quire validate` of an `NFR`, `IT` and `TC` carrying either verb to a control emits no `disallowed-edge-type`, while a verb outside `allowed_links` on the same file still does. | Test (TC-079) |
| FR-004-AC-9 | The `FR` and `NFR` archetypes' `allowed_links` contain `soup_requirement_for`, and the manifest's `edge_types` declares neither it nor `has_soup_requirement`. Single-file `quire validate` of an `FR` and of an `NFR` carrying the verb to a requirement emits no `disallowed-edge-type`, while a verb outside `allowed_links` on the same file still does. | Test (TC-080) |

**What FR-004-AC-5 no longer claims.** Until PLAT-902 this criterion was
verified by validating the manifest against a copy of the FR-035 module-manifest
schema this package shipped, and it asserted that an entry with an *unknown key*
also fails module load. It does not: an `edge_types` entry gaining an undeclared key loads all
nine archetypes. Removing both registries outright also loads. So the
criterion now states only what is observed — the declaration (also covered by
AC-1 and AC-4) and the `category` refusal, which empties the registry. The
unknown-key obligation belongs to whatever applies the FR-035 schema, and is not
asserted here rather than being asserted against a copy.

## Constraints

| ID | Constraint | Type | Validation |
|----|-----------|------|------------|
| FR-004-CON-1 | This requirement describes the vocabulary and may **clarify** an existing entry's description; it removes no verb. A verb is declared by the module that needs it, unless several modules consume it, in which case it is shared vocabulary here, as the control verification verbs of FR-004-AC-8 are. Every addition follows the criteria above. | Process | Inspection |
| FR-004-CON-2 | An unrecognised verb SHALL stay advisory. Making `UnknownEdgeType` fatal would make the vocabulary unmigratable — every rename would break every document using the old verb before any could be updated. | Design | Inspection |

## Dependencies

- **Upstream**: [StR-001](../stakeholder/StR-001-module-activation.md)
- **Downstream**: quire-rs FR-040 (`allowed_links` normalization and `UnknownEdgeType`), quire-rs FR-041 (authorable inverse edges), quire-rs FR-058 (upward-trace relations, which take their verbs from the decision above), `spec-objects-*` link declarations
- **Cross-repository**: spec-objects-security [FR-030](ix://agent-ix/spec-objects-security/FR-030) declares `soup_requirement_for` and its inverse; this module only allows the forward verb on `FR` and `NFR`.
