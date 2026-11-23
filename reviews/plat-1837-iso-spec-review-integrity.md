---
id: SR-041
title: "Spec review (integrity) — FR-004 control verification verbs (PLAT-1837, #76)"
type: SpecReview
analysis: integrity
scope: "agent-ix/spec-artifacts-iso; spec/functional/FR-004-edge-type-vocabulary.md (Control verification verbs section, FR-004-AC-8, FR-004-CON-1), spec/tests.md"
review_set: subset
relationships:
  - { target: "ix://agent-ix/spec-artifacts-iso/FR-004", type: references }
---
# SR-041: Spec review (integrity) — FR-004 control verification verbs (PLAT-1837, #76)

## Summary

Ticket: PLAT-1837. I checked the new FR-004 section, AC-8 and the edited CON-1
against the rest of FR-004 ("What a category means", "Inverses", "Adding a verb")
and against the manifest.

- **Category:** `traceability` fits. The section says the verbs record a fact
  about the specification, which matches the category table.
- **No inverse:** this matches `verifies`. FR-004's "Inverses" section allows a
  verb to have no inverse when only one direction is meaningful to author. The
  safety module checks these verbs as incoming edges on the control, so a
  reverse verb is never authored.
- **"Adding a verb" criteria:** criterion 1 (do not add a near-synonym) is
  answered by the stated reason: one `verifies` edge cannot say whether it
  verifies the implementation or the effectiveness. The verbs are not added to
  make an existing document validate.
- **NFR:** NFR is listed because it already allows `verifies` on main. Whether
  an NFR is a suitable source for an effectiveness verification is the consuming
  module's rule, as the section says.
- **CON-1:** the edit does not weaken an invariant. "Adds and removes no verb"
  was a scope statement for this requirement, and removing a verb is still
  excluded.

## Verdict

Sound, with one wording defect in CON-1.

## Findings

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-001 | low | CON-1 now says FR-004 "adds and removes no verb other than the two control verification verbs of FR-004-AC-8", followed by "Additions belong to the module that needs them". That is a list of exceptions, and every later shared verb would need another entry. It also conflicts with the next sentence: the module that needs these verbs is spec-objects-safety, yet they are added here. CON-1 should state the actual rule instead, for example: a verb authored by an archetype this module owns, or shared by several modules, is declared here; a verb that only one domain module's archetypes author belongs to that module. All additions follow "Adding a verb". | spec/functional/FR-004-edge-type-vocabulary.md:169 |

## New findings (disposition pass 1)

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-002 | low | The rewritten CON-1 again says this requirement "adds and removes no verb", but the same FR now says "The vocabulary SHALL declare `verifies_implementation` and `verifies_effectiveness`" (line 100) and AC-8 asserts both verbs. FR-004 therefore requires two verbs that its own constraint says it does not add. Restrict the clause to removals and clarifications, for example "it removes no verb, and adds one only under the rule below", or drop "adds and". | spec/functional/FR-004-edge-type-vocabulary.md:171 |

## Dispositions

| FND | outcome | reason |
| --- | --- | --- |
| FND-001 | fixed | Round 1, head 3084a3d. CON-1 now reads: "A verb is declared by the module that needs it, unless several modules consume it, in which case it is shared vocabulary here, as the control verification verbs of FR-004-AC-8 are. Every addition follows the criteria above." That is a sound ownership rule. The list of exceptions and the conflicting "Additions belong to the module that needs them" sentence are gone. The residual "adds … no verb" clause is recorded separately as FND-002. |
| FND-002 | still-open | New in disposition pass 1. No fix has landed yet: CON-1 still says "adds and removes no verb" while line 100 and AC-8 require two new verbs. |
| FND-002 | fixed | Round 2, head 779564f. CON-1 now reads "...; it removes no verb. A verb is declared by the module that needs it, unless several modules consume it, ...". This is consistent with the SHALL at line 100 and with AC-8. |
