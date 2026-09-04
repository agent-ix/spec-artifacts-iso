---
id: SR-012
title: "Code review — semantic data schemas and Markdown mappings (#34)"
type: SpecReview
analysis: code-review
scope: "spec_artifacts_iso/semantic/, spec_artifacts_iso/schemas/, spec_artifacts_iso/mappings.yaml, spec_artifacts_iso/mappings.schema.json, spec_artifacts_iso/examples/, spec_artifacts_iso/manifest.yaml, spec_artifacts_iso/module-manifest.schema.json, scripts/, tests/, Makefile, pyproject.toml, package.json, poetry.lock"
review_set: subset
---
# SR-012: Code review — semantic data schemas and Markdown mappings (#34)

## Summary

Review of the whole `spec/34-semantic-data-schemas` branch against `main`
(6 commits, 155 files): the TypeSpec models and their emitted JSON Schema
bundle (FR-005), the manifest `semantic` block and digest references (FR-006),
`mappings.yaml` with the reference mapping and ten golden records (FR-007), the
reproducibility gates (NFR-001), the census script, the packaging lists, and
the whole test suite. Every gate was executed rather than assumed.

One high finding: the committed `package-lock.json` resolved 75 of 76 packages
from the local `http://npm.ix/` registry, including public packages, so
`npm ci` could not have worked on any machine off this network — while NFR-001
claims the only npm precondition is scope routing for `@agent-ix`. Twelve
mediums, mostly checks that looked like evidence and were not: a tautological
assertion behind "no partial record", a declared mapping kind whose
implementation never executed, a reproducibility test that compared two fresh
runs to each other instead of to the committed bytes, and two acceptance
criteria that attributed a failure to the wrong layer.

All findings below are fixed on the branch except FND-016 and FND-017, which
are defects in the vendored upstream schema that FR-006-AC-4 requires to stay
byte-identical; both were filed upstream instead.

## Verdict

**PASS** — the one high and every medium is fixed and re-gated on the branch;
the two remaining items are filed upstream with tickets, and the four lows left
open are recorded with their reason. Gates at the time of writing: `make lint`
green, `make test` 255 passed / 1 xfailed, `make schemas-check` clean,
`make manifest-digests` idempotent, `quire validate --scope . "spec/**/*.md"`
zero errors, `quire coverage` 61/64 matrix rows backed (the three unbacked are
the manual gates TC-055, TC-057, TC-064).

## Findings

| ID | Severity | Summary | Refs |
| --- | --- | --- | --- |
| FND-001 | high | `package-lock.json` resolved 75 of 76 packages from `http://npm.ix/` — public `@typespec/compiler`, `ajv`, `mustache` included — over plaintext http, because the machine's global npm config points the default registry there. `npm ci` could not resolve anything off this network, contradicting NFR-001's claim that only `@agent-ix` needs scope routing. FIXED: regenerated against the public registry with only `@agent-ix` routed to npm.ix; 74 packages now resolve from registry.npmjs.org over https. The projection is byte-identical afterwards, which proves the packages are the same. | spec_artifacts_iso/semantic/package-lock.json |
| FND-002 | medium | `assert not hasattr(raised.value, "record")` can never fail — `MappingError.__init__` sets only `failures` and nothing attaches `.record` — yet it was the only assertion behind FR-007-AC-6's "yield no record". FIXED: the result name is bound before the call and asserted to have stayed unbound, so a mapping that builds a half-record and raises afterwards now fails. | tests/test_mapping_failures.py:89, tests/test_invariants_clause.py:182 |
| FND-003 | medium | The `detail` mapping kind is declared for two models and `AcceptanceCriterion.detail` is a shipped property, but `_attach_details` never executed — 0% of its body, including both FR-007 line-naming failure branches. No skeleton, golden or fixture carried a `### <row id>` subsection. FIXED with three fixtures; the branch is now fully covered without changing the shipped skeleton. | tests/support/reference_mapping.py:517-548, spec_artifacts_iso/mappings.yaml:162 |
| FND-004 | medium | TC-056 ran `make schemas` twice into the working tree with no `finally` and compared run 1 to run 2 in memory, so it never compared against the committed bytes and a non-deterministic emitter would have left the tree drifted into TC-047/TC-061. FIXED: it asserts the tree starts clean, compares both runs to the committed bundle, and restores. It caught its own regression during this review. | tests/test_reproducibility.py:46-72 |
| FND-005 | medium | Seven declared error paths of the mapping oracle were never executed — column-list mismatch, row cell-count mismatch, missing/malformed table delimiter, escaped `\|`, an undated history bullet, a `###` clause heading with no fence, and the unknown-`type` `ValueError`. These are the paths that decide whether a defect is reported or swallowed. FIXED; oracle line coverage is now 99%. | tests/support/reference_mapping.py:449-811 |
| FND-006 | medium | FR-005-AC-4 required a wrong-prefix row id to "fail validation naming the path", but `AcceptanceCriterionId`/`ConstraintId` are anchored to the artifact type, not the document, so `FR-002-CON-1` inside `FR-001` validates cleanly and no schema test could ever discharge it. FIXED: the criterion now attributes that case to the FR-007 mapping, which checks it against the locator's `id_pattern`. | spec/functional/FR-005-semantic-data-schemas.md:305 |
| FND-007 | medium | FR-005-AC-8 claimed the Python validator "rejects every mutation of TC-045", but the five mapping-layer mutations raise before a record exists, so only six of eleven ever reach a validator. FIXED: narrowed to the mutations that produce a record, with the rest explicitly FR-007-AC-6's. | spec/functional/FR-005-semantic-data-schemas.md:309 |
| FND-008 | medium | `tspconfig.yaml` defaulted `emitter-output-dir` to `{project-root}/generated/json-schema` — inside the shipped `semantic/generated/` directory, which npm packs wholesale — so a bare `tsp compile` dropped 48 emitter files into the payload. FIXED: the default is an ignored scratch directory. | spec_artifacts_iso/semantic/tspconfig.yaml:8 |
| FND-009 | medium | npm shipped `examples/` and `semantic/generated/` as directories while pyproject shipped `examples/*.record.json` and `semantic/generated/toolchain.json`, so any stray file in either directory made the two payloads differ — exactly what FR-005-AC-9 forbids. FIXED: both sides name the same things. | package.json:22,24 vs pyproject.toml:19,21 |
| FND-010 | medium | The census matched frontmatter with an LF-only `^---\n…` pattern, so the measurement and FR-005's own CRLF rule disagreed on paper. FIXED. Re-measuring moved no figure: `read_text` opens in universal-newline mode, and a read-only probe found zero CR bytes in all 9,030 corpus documents — the population at risk was empty twice over. | scripts/corpus_census.py:67 |
| FND-011 | medium | The census aborted the whole run on one unreadable directory (`rglob` and `is_file()` unguarded) and read every matched file with no size cap over a user-supplied glob. FIXED: both are counted, reported skips with their own metrics rather than a traceback or a silent drop. | scripts/corpus_census.py:243-250 |
| FND-012 | medium | `manifest_digests.py` joined a manifest-supplied `data_schema.schema` string onto a filesystem path with no traversal guard, named the module-constant path in errors raised against a different `--manifest`, and let `--write-legacy-fixture` overwrite the committed fixture from an unrelated manifest. All three FIXED. | scripts/manifest_digests.py:103-141 |
| FND-013 | medium | `generate.mjs` read the emitter's scratch directory with a flat `readdirSync` and no `Dirent` check, so a future emitter writing into a subdirectory would have silently dropped files from both the bundle and the digest. FIXED: an unexpected entry is now a loud failure naming the offenders. | spec_artifacts_iso/semantic/scripts/generate.mjs:110-113 |
| FND-014 | medium | The census figures quoted in FR-005 were a hand count, and re-measuring corrected six: "30 distinct constraint categories" was a `most_common(30)` display limit rather than a measurement (the true count is 335), verification-method spellings are 1,144 not "more than thirty", empty verification cells 7 not 41, `status` declarations 863 documents not 973, `US` stories matching neither form 0 not 8, and log undated entries 104 across 9 repositories not ~30 across 4. FIXED, and the figures are now labelled as the dated snapshot of a live corpus that they are. | spec/functional/FR-005-semantic-data-schemas.md, scripts/corpus_census.py |
| FND-015 | medium | The Test Matrix still marked every automated row 🚧 Pending although all of them pass on this branch, so a reader could not tell what it discharged. FIXED: 56 rows moved to ✅, and the three manual gates (TC-055, TC-057, TC-064) record that they were actually run. | spec/tests.md |
| FND-016 | medium | The vendored FR-035 `data_schema` path guard is `^(?!/)(?!.*\.\.)[^ ]+\.json$` — two ECMA negative lookaheads. The Rust `jsonschema` crate is built on the `regex` crate, which rejects lookarounds, so the traversal guard is a no-op in any Rust consumer of the manifest schema. NOT FIXED HERE: FR-006-AC-4 requires the vendored parts to stay byte-identical to a77f31e, so the fix belongs upstream — filed as agent-ix/filament-core-service#24. Latent rather than live: no emitted model schema uses a lookaround, so FR-005-AC-8's Python/Rust agreement is unaffected, and quire-rs compiles `data_schema` rather than the manifest schema. Recorded in FR-006 Inputs. | spec_artifacts_iso/module-manifest.schema.json:414,506 |
| FND-017 | low | The vendored `semantic.exports` description reads "Object-type names … each must be declared in `object_types`", which contradicts this manifest's artifact-type exports for anyone reading the bundle without the spec. NOT FIXED HERE for the same byte-identity reason; it is the prose face of agent-ix/quoin#336, and is recorded in FR-006 Inputs. | spec_artifacts_iso/module-manifest.schema.json |
| FND-018 | low | The 100% coverage gate measures `spec_artifacts_iso` only — nine statements. The 871-line test oracle and the 736-line census script (a cited FR-005 Inputs deliverable) sit outside any coverage gate, which is why FND-003 and FND-005 were invisible until read by hand. NOT FIXED: widening the gate to those trees at `--cov-fail-under=100` would either fail immediately or invite pragma suppressions. Left as a recorded follow-up rather than a silent gap. | pyproject.toml:130 |
| FND-019 | low | `test_tc052_every_model_property_is_declared_exactly_once` cannot fail on the "exactly one" half: `properties` is a YAML mapping, so a duplicate key collapses at parse time before the assertion runs. Only the set-equality half is real. NOT FIXED: catching it needs a duplicate-key-rejecting YAML loader, which is a larger change than the risk warrants while `mappings.schema.json` seals the shape. | tests/test_markdown_mappings.py:274-297 |
| FND-020 | low | TC-050 is largely a re-run of TC-044: only `fr.md` changed since 3d87196, so nine of the ten "pre-change" documents are byte-identical to the ones TC-044 already maps, and only `fr.md` supplies genuine pre-change evidence for FR-007-AC-5. NOT FIXED — this is a true fact about the diff, not a defect in the test; it will carry weight the next time a skeleton changes. | tests/test_markdown_mappings.py:181-206 |
| FND-021 | low | The census fixture corpus contains no negative documents, so four asserted metrics are zero by construction (`documents_unreadable`, `us_story_neither`, the malformed-YAML and unknown-`type` branches). PARTLY FIXED — the unreadable-directory and oversized-document paths gained tests with the fixes above; the remaining branches are recorded. | tests/test_corpus_census.py:47-80 |

## Recommendations

- FND-018 is the one that would have caught FND-003 and FND-005 automatically.
  A separate, lower threshold over `tests/support/` and `scripts/` would be
  worth more than raising the existing gate, which is calibrated for a
  nine-statement package.
- Re-run this review when agent-ix/quire-rs#388 publishes a wheel: TC-063's
  strict expected failure flips to a failure-because-it-passed, and FND-016's
  latent Rust exposure becomes live the moment any Rust consumer validates a
  manifest against the bundled FR-035 schema.
