---
id: SR-001
title: "Retroactive code review — traceability.source_exclude schema key (PR #28)"
type: SpecReview
analysis: code-review
scope: "spec_artifacts_iso/module-manifest.schema.json, tests/test_manifest_and_validate.py, spec/functional/FR-001-module-manifest-activates.md, spec/tests.md"
review_set: subset
relationships:
  - { target: "ix://agent-ix/spec-artifacts-iso/spec/functional/FR-001", type: references }
  - { target: "ix://agent-ix/spec-artifacts-iso/spec/tests", type: references }
---

# SR-001: Retroactive code review — traceability.source_exclude schema key (PR #28)

## Summary

Retroactive review of PR #28 (`88ce642`, FR-001 CR-010: add
`traceability.source_exclude[]` to the module-manifest schema), merged
2026-08-21 with zero reviews as part of the trace-status-integrity batch.
Verified against merged main: the tests are real and the PR is clean — the one
substantive gap is that the schema constrains shape only, leaving the
"`tests/**` MUST NEVER appear here" invariant as an unenforceable description
string (ticketed as #29). The review also names a recurring sequencing pattern
this repository's gate keeps absorbing: engine keys shipping before the
contract has heard of them.

## Verdict

**APPROVED** with one ticketed follow-up (#29). Nothing in the merged change
needs to move.

## Findings

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-001 | low | Clean PR: two real tests (`test_tc_schema_027_source_exclude_is_accepted`, `test_tc_schema_027_source_exclude_is_not_exclude`) cover accept, reject and key-distinctness cases; matrix row TC-035 is bound by docstring tags; suite green at HEAD (125 passed, 100% coverage gate) | tests/test_manifest_and_validate.py:1122 |
| FND-002 | medium | Shape-only constraint: the schema accepts any non-empty string, so `["tests/**"]` and `["**"]` validate cleanly — the safety invariant lives only in the `description` string, which validates nothing | spec_artifacts_iso/module-manifest.schema.json:814, #29 |
| FND-003 | low | Sequencing debt, recurring: source_exclude is yet another key the engine shipped before this contract could express it — the same arrival mode as CR-005, CR-007, CR-008 and CR-009, per the PR's own account | spec/log.md:21 |
| FND-004 | low | Both new test functions share the `tc_schema_027` number; every prior number in the file maps to exactly one function — a trivial local echo of the batch-wide duplicate-test-id theme | tests/test_manifest_and_validate.py:1122 |

## Detail

**FND-001 — what a clean PR in this batch looks like.** Unlike its
spec-artifacts-process counterpart (SAP #55, reviewed in that repository's
SR-006), this PR shipped its tests in the same diff: acceptance of a well-formed
glob list and of the empty list, rejection of an empty string and of a bare
string, and a dedicated test that `exclude` and `source_exclude` coexist as
distinct keys — pinning the design decision (documents vs the source walk) that
the whole change argues for. The matrix row TC-035 names the backing functions
inline and both docstrings carry the `TC-035: FR-001 CR-010` binding. Re-run at
review time: 125 passed, coverage gate at 100% (for calibration: the coverage
figure counts the 9 statements of `spec_artifacts_iso/__init__.py` — the
package is a data carrier and the real substance is the 125 schema tests).

**FND-002 — the gap, and why it matters here specifically.** The new property is
`{"type": "array", "items": {"type": "string", "minLength": 1}}`. Everything
that makes the key safe — anchor at a fixture directory, never `tests/**`,
never a bare or leading wildcard — is prose in the `description`. This schema is
the `additionalProperties: false` gate the whole ecosystem loads manifests
through, which makes it the one place a value constraint would protect every
consumer at once: a manifest declaring `["tests/**"]` today passes this gate,
loads in the engine, and silently subtracts the evidence tree (excluded files'
trace tags never bind; their matrix rows read as unbacked). The fix is cheap and
ticketed as **#29**: `not`-pattern constraints rejecting `^\*\*$`, `^tests/`
and a leading wildcard (`^[*?]` — globset compiles with
`literal_separator=false`, so `*/fixtures/**` would match at any depth), with
TC-schema tests in the existing `test_tc_schema_*` pattern. The companion
contract test pinning the concrete glob list lives in spec-artifacts-process
(#56 there).

**FND-003 — name the pattern, not just the instance.** The PR's own rationale:
"without the key here, `additionalProperties: false` rejects the manifest before
the engine ever sees it, so a module cannot declare what quire-rs v0.41.0
already reads" — and it notes this is the same reason CR-005
(`required_relations`, quire-rs FR-058), CR-007 (`vocabulary_coverage`, FR-059),
CR-008 (`ObligationSource.combinatorial`, FR-061) and CR-009
(`trace_tags.implements`, FR-062) were filed. That is a good record for the gate
and a poor one for the sequencing: the engine keeps growing keys first, and this
contract keeps finding out when a manifest fails load. One number nit while
recording it: the PR body says the gate "has now caught four keys", but it names
four predecessors and adds a fifth — by its own list, source_exclude is at least
the fourth and arguably the fifth arrival. No code change follows from this
finding; it exists so the next engine-side key lands with the schema change in
the same wave rather than after the failure.

**FND-004 — numbering nit.** The file's convention to date is one
`tc_schema_NNN` number per test function (…025, …026 each map to one). The two
new functions both use `027`. Both trace to the single matrix row TC-035, so no
coverage claim is wrong; noted only because the wider batch shipped genuine
duplicate test-case ids (quire-rs TC-943/TC-944 each on two functions) and the
cheap time to keep numbers unique is while the convention is young.
