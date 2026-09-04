---
id: Task-007
title: "FR-005 — the corpus census the constraints are drawn from"
type: Task
status: done
track: B
priority: P2
relationships:
  - target: ix://agent-ix/spec-artifacts-iso/FR-005
    type: references
  - target: ix://agent-ix/spec-artifacts-iso/TC-040
    type: verifies
---
# Task-007: FR-005 — the corpus census the constraints are drawn from

## Scope

FR-005 names the census as the source of every population it admits — 16 status
spellings over 973 documents, nine cardinality forms, 30 constraint categories,
41 empty verification cells, 6,242 index link lines. FR-005 Inputs cites
`scripts/corpus_census.py` as where that measurement lives, so the script is
part of the deliverable and has to be reproducible by someone else.

## Subtasks

- [ ] **Take the corpus root as an argument**, defaulting to `~/dev/*/spec`,
  rather than hard-coding one developer's path.
- [ ] **State what each number counts** in the output: the unit, the population,
  and the method (by document or by line).
- [ ] **Emit JSON as well as the human table**, so a later run can be diffed
  against this one rather than re-read by eye.
- [ ] **A smoke test** over a small fixture corpus in `tests/fixtures/census/`:
  the counts are the ones the fixture obviously has. This is what makes the
  script a committed artifact rather than a scratch file.

## Deliverables

- `scripts/corpus_census.py`
- `tests/fixtures/census/`, `tests/test_corpus_census.py`

## Notes

- The census reads the corpus and writes nothing. No corpus repository is
  edited by this ticket, and a defect the census finds is reported, not fixed
  here.
