---
id: SR-045
title: "Spec review (integrity) — FR-004 SOUP requirement verbs (PLAT-1855, #77)"
type: SpecReview
analysis: integrity
scope: "agent-ix/spec-artifacts-iso; spec/functional/FR-004-edge-type-vocabulary.md (SOUP requirement verbs section, FR-004-AC-9), spec/tests.md (FR-004-AC-9 and TC-080 rows)"
review_set: subset
relationships:
  - { target: "ix://agent-ix/spec-artifacts-iso/FR-004", type: references }
---
# SR-045: Spec review (integrity) — FR-004 SOUP requirement verbs (PLAT-1855, #77)

## Summary

Ticket: PLAT-1855. I checked the new FR-004 section "SOUP requirement verbs",
its SHALL statement, FR-004-AC-9 and the two `spec/tests.md` rows. I read them
against the rest of FR-004 ("Inverses", "Merge", "Unknown verbs are advisory",
FR-004-CON-1, FR-004-CON-2), against spec-objects-security FR-030 (origin/main
d7abe37), and against measured quire 0.52.0 (engine 0.62.2) behaviour.

- **Ownership:** the section's statement that `spec-objects-security` owns both
  verbs and that iso declares neither matches FR-030 and FR-004-CON-1 ("a verb
  is declared by the module that needs it").
- **AC-9:** it is atomic enough and testable, it mirrors AC-8's shape, and it is
  traced to TC-080 in both tables of `spec/tests.md`, each row in the correct
  table. `quire validate --module spec_artifacts_iso` of FR-004 exits 0.
- **Numbering:** AC-9 follows AC-8 and TC-080 follows TC-079. Neither id exists
  on `origin/main` or on the other open PRs.
- **Statement:** "The `FR` and `NFR` archetypes SHALL allow … and the vocabulary
  SHALL NOT declare either verb" joins two obligations in one sentence, as the
  AC-8 statement does. The precedent is accepted, so this is not raised.

## Verdict

Sound in ownership and traceability. Two sentences of the new section state
engine behaviour that does not match what quire 0.52.0 does, and the
Dependencies list omits the FR the section derives from.

## Findings

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-001 | medium | The section says that without iso's allowance "a served requirement that authors `has_soup_requirement`, draws an advisory `disallowed-edge-type` finding although the security module's relation counts the edge". Measured, this is false. With spec-objects-security #80 loaded (which declares `has_soup_requirement` as the inverse) and iso `origin/main` (no allowance), an FR or NFR authoring `has_soup_requirement` draws no `disallowed-edge-type`. A declared inverse label is type-allowed (quire-rs FR-041-AC-2). FR-004's own "Inverses" section says the same, and FR-030's Dependencies says "Authoring the inverse from the served requirement avoids the warning". Only `soup_requirement_for` needs the allowance. Either state the inverse is listed because FR-030 asks for both (and that it is redundant when the security module is loaded), or drop `has_soup_requirement` from the allowance, the SHALL and AC-9. | spec/functional/FR-004-edge-type-vocabulary.md:109 |
| FND-002 | medium | "Where the security module is not loaded the two verbs are in no loaded vocabulary and draw the advisory `UnknownEdgeType`" reads as a per-use advisory, like the per-relationship one in "Unknown verbs are advisory". The measured effect is a load-time diagnostic. Each iso load without a declaring module prints 4 lines (`archetype 'FR'/'NFR' allowed_links uses '<verb>' which is not in any edge_types registry`) on every run, whatever the documents contain. The same happens when spec-objects-security is loaded at a version without FR-030's declaration (origin/main d7abe37, installed v0.18.0). State it exactly so an iso-only user is not surprised. FR-004-CON-2 still holds, since the exit code is unchanged under `--strict`. | spec/functional/FR-004-edge-type-vocabulary.md:111 |
| FND-003 | low | The new SHALL derives from spec-objects-security FR-030, which the section links inline, but FR-004's Dependencies section (Upstream: StR-001 only) and its frontmatter `relationships` do not name FR-030. A reader of FR-004's dependencies cannot see that two `allowed_links` entries exist for another module's relation. Add FR-030 as an upstream dependency. | spec/functional/FR-004-edge-type-vocabulary.md:190 |
