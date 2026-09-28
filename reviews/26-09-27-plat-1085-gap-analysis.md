---
id: SR-014
title: "Gap analysis — drop ac-verification-method (PLAT-1085, #46)"
type: SpecReview
analysis: gap-analysis
scope: "agent-ix/spec-artifacts-iso@608cd5314c8eb756bf96a71303f90cc39378b6df; PLAT-1085 change list vs diff; spec/functional/FR-005, FR-007; spec/tests.md; tests/test_markdown_mappings.py"
review_set: subset
---
# SR-014: Gap analysis — drop ac-verification-method (PLAT-1085, #46)

## Summary

Ticket: PLAT-1085. Manual acceptance-criteria-to-change check (the PR is
manifest/skeleton/data plus one test; quoin gap-analysis over the whole repo
is out of proportion). Plan completion: not assessed.

| Ticket item | Delivered | Evidence |
| --- | --- | --- |
| Remove FR/NFR `ac-verification-method` | yes | manifest.yaml, legacy fixture; no test (SR-013 FND-002) |
| StR rule drops `(TC-nnn)` annotation, keeps classes | yes | manifest.yaml:818-823 |
| fr/nfr skeletons drop `Test (TC-…)`; README, FR-005 prose | yes | skeletons, README.md:90, FR-005:246 |
| legacy fixture / corpus_census | yes | fixture equals derive_legacy; census comment only |
| Release + quoin pin bump | no (post-merge) | SR-013 FND-004 |

Spec-to-test trace: FR-007-AC-3 no longer matches TC-053 (SR-013 FND-001).
No shipped file other than historical reviews/, plan/ and test fixtures names
`ac-verification-method`.

## Verdict

**PASS with findings** — every code item of the ticket is delivered; the one
gap is the stale FR-007-AC-3 / TC-053 text recorded in SR-013 FND-001.

## Findings

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-001 | medium | FR-007-AC-3 (and tests.md TC-053) still specify the `Test (TC-001)` split on the FR skeleton; the skeleton and TC-053 no longer carry it. Same defect as SR-013 FND-001, recorded here as the trace gap. | spec/functional/FR-007-markdown-mappings.md:216, spec/tests.md:149 |

## Dispositions

| FND | outcome | sha/reason |
| --- | --- | --- |
| FND-001 | fixed | 4e8fe49 |
