---
id: SR-002
title: "Code review — source_exclude value constraints (d16adbd + 902f9bf, #29)"
type: SpecReview
analysis: code-review
scope: "spec_artifacts_iso/module-manifest.schema.json, tests/test_manifest_and_validate.py (TC-035..TC-038), spec/functional/FR-001-module-manifest-activates.md, spec/tests.md, spec/log.md"
review_set: subset
---

# SR-002: Code review — CR-011 source_exclude value constraints (#29)

## Summary

Pre-release review of the unreviewed fix commits `d16adbd` (CR-011 value
constraints, TC-035..038 renumbering, closes #29) and `902f9bf` (tests-tree
rejection realigned with the SAP contract semantics). The constraints are
real schema (`not`/`pattern` under the suite's `Draft202012Validator`), the
FND-004 renumbering is correct, and the deliberate deviation from the
ticket's literal "starts with `tests/`" bullet is right. But the `902f9bf`
regex did **not** implement the semantics its own commit message states
("first segment is the literal `tests` with no literal anchor in a later
segment"): a 23-case side-by-side execution against spec-artifacts-process's
contract guard found six divergent edge cases. Fixed in this pass (FND-001);
the two guards now agree on every case tested.

## Verdict

**CONDITIONAL** — one medium finding, fixed in this pass with tests; one low
observation needing no action.

## Findings

| ID      | Severity | Summary                                                                                                                                                                                                                            | Refs                                                |
| ------- | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------- |
| FND-001 | medium   | `^tests(/([*?].*)?)?$` diverged from the SAP guard on 6 edge cases — under-rejected `tests/x*`, `tests/f*/**`, `tests/a?b/**`, `tests//`, `tests//**`; over-rejected the legally anchored `tests/**/fixtures/**`. FIXED: regex is now the segment rule `^tests(/([^/]*[*?][^/]*)?)*$`; TC-037/TC-038 extended; suite 135 passed (#29). Escape cause: implementation-bug-despite-evidence | spec_artifacts_iso/module-manifest.schema.json:827  |
| FND-002 | low      | JSON Schema `pattern` is specified as ECMA-262 but enforced here by Python `re`, whose `$` also matches before a trailing newline — Python-side validation is strictly stricter (e.g. rejects `"tests\n"`); no action needed while the suite's `Draft202012Validator` is the enforcing gate | spec_artifacts_iso/module-manifest.schema.json:819  |

## Guard-agreement matrix (SAP contract test vs iso schema)

Executed empirically: SAP's `_source_exclude_violation` (verbatim from
`spec-artifacts-process/tests/test_manifest.py` @ `fe3adcc`) against this
repo's `source_exclude` items schema under `Draft202012Validator`.

| Pattern                         | SAP guard | iso schema (before fix) | iso schema (after fix) | Agree now |
| ------------------------------- | --------- | ----------------------- | ---------------------- | --------- |
| `tests`                         | reject    | reject                  | reject                 | yes       |
| `tests/`                        | reject    | reject                  | reject                 | yes       |
| `tests/**`                      | reject    | reject                  | reject                 | yes       |
| `tests/fixtures/**`             | accept    | accept                  | accept                 | yes       |
| `*/fixtures/**`                 | reject    | reject                  | reject                 | yes       |
| `**`                            | reject    | reject                  | reject                 | yes       |
| `?x/**`                         | reject    | reject                  | reject                 | yes       |
| `tests_integration/fixtures/**` | accept    | accept                  | accept                 | yes       |
| `tests/*`                       | reject    | reject                  | reject                 | yes       |
| `tests/**/*.py`                 | reject    | reject                  | reject                 | yes       |
| `tests/*x`                      | reject    | reject                  | reject                 | yes       |
| `tests/x*`                      | reject    | **accept** (diverged)   | reject                 | yes       |
| `tests/f*/**`                   | reject    | **accept** (diverged)   | reject                 | yes       |
| `tests/a?b/**`                  | reject    | **accept** (diverged)   | reject                 | yes       |
| `tests//`                       | reject    | **accept** (diverged)   | reject                 | yes       |
| `tests//**`                     | reject    | **accept** (diverged)   | reject                 | yes       |
| `tests/**/fixtures/**`          | accept    | **reject** (diverged)   | accept                 | yes       |
| `tests/fixtures`                | accept    | accept                  | accept                 | yes       |
| `fixtures/**`                   | accept    | accept                  | accept                 | yes       |
| `src/tests/**`                  | accept    | accept                  | accept                 | yes       |
| `?ests/fixtures/**`             | reject    | reject                  | reject                 | yes       |
| `testsX/**`                     | accept    | accept                  | accept                 | yes       |
| `tests/?`                       | reject    | reject                  | reject                 | yes       |

All eight coordination cases named in the review brief agree in
every column; the fixed regex implements exactly the SAP segment rule:
reject iff the first segment is literally `tests` and every later segment is
empty or wildcard-carrying.

## Review detail

- **Do the regexes do what the test names claim under Draft 2020-12?** Yes,
  under the suite's `Draft202012Validator`: TC-038's reject set and
  TC-037's accept set were re-executed and each case behaves as named. The
  claim held for the *tested* cases before the fix — the divergences were
  all in untested territory, which is why FND-001's escape cause is
  implementation-bug-despite-evidence.
- **FND-004 renumbering (d16adbd).** Verified: the two PR #28 functions no
  longer share `tc_schema_027`; the key-distinctness test is
  `test_tc_schema_028_source_exclude_is_not_exclude` with its own row
  TC-036, TC-035 narrowed to accept/reject-shape, and the FR-001-AC-1
  coverage cell carries TC-035..038.
- **Deliberate ticket deviation.** The narrower-than-`^tests/` rule is
  correct: a blanket prefix ban would reject `tests/fixtures/**`, the
  anchored form CR-010 mandates and spec-artifacts-process ships. The
  deviation is documented in the commit, FR-001's CR-011 note, and the
  schema description.
- **Test style.** Plain-function pytest with TC/CR-traced docstrings
  matches the file's convention; parametrized reject cases carry readable
  ids; no mocks, no database, real validator throughout.

## Gap analysis — does #29's acceptance hold?

| Acceptance claim                                                     | Holds? | Evidence                                                                       |
| -------------------------------------------------------------------- | ------ | ------------------------------------------------------------------------------ |
| "`tests/**` MUST NEVER appear here" moves from prose into the schema  | yes    | `not`/`pattern` constraints on items; TC-038 rejects it at load                |
| Bare `**` and leading-wildcard patterns are schema errors             | yes    | TC-038 parametrized cases `**`, `*/fixtures/**`                                |
| Anchored declarations stay legal (`tests/fixtures/**` et al.)         | yes    | TC-037 validates the exact SAP list (+ depth-anchored form after FND-001 fix)  |
| Semantics match the SAP contract test (902f9bf's stated purpose)      | now    | held on the 8 coordinated cases only; FND-001 fixed the 6 divergences — matrix above |
| Suite green, coverage 100%                                            | yes    | 135 passed, coverage 100% after the fix (was 132)                              |
