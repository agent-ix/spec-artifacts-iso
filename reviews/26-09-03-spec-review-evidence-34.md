---
id: SR-007
title: "Evidence review of the semantic data schema requirements (US-001, FR-005..FR-007, NFR-001)"
type: SpecReview
analysis: evidence
scope: "spec/usecase/US-001-consume-typed-iso-artifact-records.md, spec/functional/FR-005-semantic-data-schemas.md, spec/functional/FR-006-semantic-manifest-block.md, spec/functional/FR-007-markdown-mappings.md, spec/non-functional/NFR-001-reproducible-offline-schema-projection.md, spec/tests.md"
review_set: all
---
# SR-007: Evidence review of the semantic data schema requirements

## Summary

Reviewed the verification method authored on every acceptance criterion and
constraint of FR-005, FR-006, FR-007 and the three NFR-001 measurements (32
obligations), against the module's `ac-verification-method` vocabulary
(Inspection | Analysis | Demonstration | Test), the catalog served by
`quoin advise` / `quoin catalog methods`, and the matrix rows TC-039..TC-059
(Type vocabulary Unit | Integration | E2E | Property | Fuzz | Benchmark |
Static | Compile | Snapshot | Manual). US-001 carries illustrative examples
only and mints no obligation.

**[RAN]** `quoin advise` (48 obligations module-wide; 25 in scope): 1 mismatch
(FR-006-AC-6, authored Demonstration vs recommended unit-testing), 3
uncatalogued (the NFR-001 Method cells carry procedures, not method tokens),
0 inconclusive. Constraints are not obligations to the advisor, so the eleven
`Validation` cells were judged by hand and are labelled as judgement below.

The authored methods are almost all right: 22 of 25 advisor-visible
obligations agree with the catalog, and the constraint cells are defensible.
What needs attention is the **matrix row typing and the discharge path**: one
constraint cell names a different test than the matrix binds (FR-005-CON-3),
one Inspection obligation is shadowed by a Static row with no nameable oracle
(FR-007-CON-3 / TC-059), one criterion passes on its own failure branch
(FR-006-AC-6), three rows depend on external toolchains that this suite's
existing skip-guard would silently turn into passes, and two oracles are
phrase matches an author satisfies by typing the phrase. No finding is high:
every obligation has a method that can discharge it once the edits below land.

## Findings

| ID | Severity | Summary | Refs |
|----|----------|---------|------|
| FND-260 | medium | FR-005-CON-3's Validation cell says `Test (TC-042)` but the matrix binds CON-3 to TC-054 (Static) and TC-042 traces only to AC-5/AC-7; the obligation's method (the cell) and the evidence plan (the matrix) disagree. | FR-005-CON-3, TC-042, TC-054 |
| FND-261 | medium | FR-006-AC-6 is a disjunction whose second branch is a failure (`semantic.unknown-export`) with process obligations (record verbatim in this requirement, file an issue) as its evidence; a criterion that passes when the product fails cannot go red, and its evidence is an edit to the spec. Split: AC-6 = install succeeds; the known quoin gap is a recorded deviation, not a passing branch. Authored Demonstration and TC-055 Manual are also the wrong class for a subprocess call. | FR-006-AC-6, TC-055 |
| FND-262 | medium | FR-007-CON-3 is authored Inspection (right: "no file derives Markdown from a record" has no executable oracle) but the matrix binds it to TC-059 typed Static, which names no check. An inspection wearing a test id discharges nothing; either narrow TC-059 to a nameable check or drop it and discharge CON-3 through the inspection record. | FR-007-CON-3, TC-059 |
| FND-263 | medium | TC-042 (node/TypeSpec toolchain), TC-048 (a quire wheel whose `Registry` reports digests, quire-rs#388) and TC-055 (quoin CLI) run only when an external tool is present. Under the suite's existing skip-guard pattern (`pytest.skip("quire wheel lacks validate_document")`) an absent tool reports pass-by-absence, the failure mode FR-001 CR-002 closed for TC-001. Require fail-not-skip, and split FR-005-AC-7 (file set + digest vs `toolchain.json`) out of TC-042 into a toolchain-free Unit row. | FR-005-AC-5, FR-005-AC-7, FR-006-AC-3, FR-006-AC-6, TC-042, TC-048, TC-055 |
| FND-264 | medium | Two oracles are phrase matches the author satisfies by writing the phrase: FR-005-AC-3's `free text:` escape (the token is mechanically checkable; "followed by the reason" is not, and any property becomes exempt by carrying the token) and FR-005-AC-6's "doc comment states that execution results are not modelled". Close AC-3 by asserting the set of `free text:` properties equals the list FR-005 Behavior enumerates; make AC-6's doc-comment clause Inspection or name an exact token. | FR-005-AC-3, FR-005-AC-6, TC-040, TC-043 |
| FND-265 | low | TC-043 is typed Static but is a pytest over emitted JSON (name denylist) — that is Unit. As the sole evidence for FR-005-CON-4 the denylist is weak (`run_status`, `verdict` pass); CON-4's cell should read `Inspection; Test (TC-043)`. | FR-005-CON-4, FR-005-AC-6, TC-043 |
| FND-266 | low | TC-056 is typed Property but generates nothing: it is a two-run determinism check on one fixed tree, and its first run is exactly TC-042's "schemas-check exits 0 on the committed tree". Retype Integration, or fold NFR-001 M-1 into TC-042 and drop the row. | NFR-001, TC-056, TC-042 |
| FND-267 | low | TC-057 Manual is acceptable as the interim NFR-001 itself declares, only if the evidence location (release-notes entry) is named in the row; the metric is automatable (`unshare -rn make schemas-check`, pytest-socket for `make test`). Separately, TC-041 says "offline" but a Unit test with sockets open proves nothing about network reads — add socket blocking so "offline" is an oracle. | NFR-001, TC-057, TC-041, FR-005-AC-2 |
| FND-268 | low | TC-050 Snapshot is right for FR-007-CON-1 only if the 3d87196 skeletons are committed fixtures; a test that `git show`s a commit breaks in an sdist and on a shallow clone. FR-007-AC-5's oracle ("validates") is weaker than its claim ("semantically equivalent"): assert record(pre-change skeleton) equals the post-change golden minus `invariants`. | FR-007-AC-5, FR-007-CON-1, TC-050 |
| FND-269 | low | TC-044's golden `examples/<type>.record.json` is minted by the mapping under test, so it detects drift, never wrongness; the only independent oracle is TC-053's literal values for one model. Extend TC-053 to one hand-asserted row per typed table (Constraint, ValidationCriterion, MeasurementRow, GlossaryTerm, IndexEntry, LogEntry, Story, SuccessCriterion). | FR-005-AC-4, FR-007-AC-2, FR-007-AC-3, TC-044, TC-053 |
| FND-270 | low | TC-039's third disjunct ("or a `mappings.yaml` entry") lets any added field pass CON-1 by adding a mapping entry, reducing the check to TC-052. Require each mapping entry to name a locator, frontmatter key, or one of the computed fields (`line`, `provenance`, `startLine`/`endLine`). | FR-005-CON-1, TC-039, TC-052 |
| FND-271 | low | NFR-001 matrix row 3 uses `Benchmark` as the verification method; Benchmark is a matrix Type, not a member of Inspection/Analysis/Demonstration/Test. M-3's "reference machine" is undefined, so its 10 s / 30 s numbers are not reproducible. `quoin advise` reports all three NFR rows uncatalogued because the Method cells carry procedures. | NFR-001, TC-058 |
| FND-272 | low | FR-006 Behavior admits "ten" `semantic` keys while AC-1 and TC-046 assert an exact nine-key set; the tenth (`sweep_report`) is admitted-but-absent. State the oracle once: nine present, `sweep_report` admitted by schema and absent here. | FR-006-AC-1, FR-006-AC-4, TC-046, TC-049 |
| FND-273 | low | Advisor residue recorded as judgement: FR-005-AC-3's `dast`/`iast` recommendation matched the `security` characteristic spuriously (no attack surface exists); FR-007-AC-5's `concolic-execution` matched `reference-equivalence` — take golden comparison first per the cost ordering; FR-005-AC-2's `sca-sbom` (Static) is the right class for the pin check but belongs to CON-3/TC-054, not AC-2. | FR-005-AC-2, FR-005-AC-3, FR-007-AC-5 |
| FND-274 | low | The eleven Constraint `Validation` cells are outside both the `ac-verification-method` lint (Acceptance Criteria only) and `quoin advise` (no CON obligations); nothing mechanical checks their vocabulary or binds them. Recorded so the matrix owner knows the constraint rows were reviewed by hand only. | FR-005-CON-1, FR-006-CON-1, FR-007-CON-1 |

## Verdict

**Revise before the matrix is frozen; no obligation is unverifiable.** The
authored Verification cells stay as they are except FR-005-CON-3 (cite TC-054),
FR-005-CON-4 (add Inspection), FR-006-AC-6 (split; Test not Demonstration) and
FR-005-AC-6 (doc-comment clause to Inspection). Six matrix rows change Type or
binding: TC-042 (split), TC-043 (Unit), TC-055 (Integration), TC-056
(Integration or dropped), TC-059 (narrowed or dropped), TC-058 (method Test).
TC-057 stays Manual with a named evidence location. Findings: 0 high, 5
medium, 10 low.

## Evidence Map

| Obligation | Authored method | Recommended method | Matrix row | Agree? |
|------------|-----------------|--------------------|------------|--------|
| FR-005-AC-1 | Test (TC-041) | Test — unit-testing (advisor: example) | TC-041 Unit | yes |
| FR-005-AC-2 | Test (TC-041) | Test — unit-testing with sockets blocked (advisor: property-based, sca-sbom; judgement: resolution over a fixed bundle is enumerable, not generative) | TC-041 Unit | yes, add socket block (FND-267) |
| FR-005-AC-3 | Test (TC-040) | Test for the token and the constraint keywords; Inspection for the reasons (advisor: dast/iast spurious, FND-273) | TC-040 Unit | partly (FND-264) |
| FR-005-AC-4 | Test (TC-044, TC-045) | Test — golden-approval (Snapshot) + unit negative cases | TC-044 Snapshot, TC-045 Unit | yes (FND-269 on golden provenance) |
| FR-005-AC-5 | Test (TC-042) | Test — integration-testing (crosses into the TypeSpec toolchain), fail-not-skip | TC-042 Integration | yes (FND-263) |
| FR-005-AC-6 | Test (TC-043) | Test (unit) for the name denylist; Inspection for the doc-comment statement | TC-043 Static | no — Unit, and split (FND-264, FND-265) |
| FR-005-AC-7 | Test (TC-042) | Test — unit-testing, toolchain-free | TC-042 Integration | no — own Unit row (FND-263) |
| FR-005-CON-1 | Test (TC-039, TC-040) | Test — unit (judgement; CONs not advised) | TC-039 Unit, TC-040 Unit | yes (FND-270 tightens) |
| FR-005-CON-2 | Test (TC-041) | Test — unit with sockets blocked (judgement) | TC-041 Unit | yes (FND-267) |
| FR-005-CON-3 | Test (TC-042) | Analysis — sca-sbom / static-quality (Static) | TC-054 Static | no — cell cites the wrong row (FND-260) |
| FR-005-CON-4 | Test (TC-043) | Inspection + Test (unit denylist) | TC-043 Static | partly (FND-265) |
| FR-006-AC-1 | Test (TC-046) | Test — unit-testing | TC-046 Unit | yes (FND-272 oracle wording) |
| FR-006-AC-2 | Test (TC-047) | Test — unit-testing | TC-047 Unit | yes |
| FR-006-AC-3 | Test (TC-048) | Test — integration-testing against the pinned wheel, fail-not-skip | TC-048 Integration | yes (FND-263) |
| FR-006-AC-4 | Test (TC-049) | Test — unit-testing (negative cases) | TC-049 Unit | yes |
| FR-006-AC-5 | Test (TC-047) | Test — unit-testing (advisor: property-based; judgement: one mutation suffices, the digest is total) | TC-047 Unit | yes |
| FR-006-AC-6 | Demonstration | Test — integration-testing (subprocess `quoin module install`), advisor mismatch confirmed | TC-055 Manual | no (FND-261, FND-263) |
| FR-006-CON-1 | Test (TC-046) | Test — unit (judgement) | TC-046 Unit | yes |
| FR-006-CON-2 | Test (TC-047) | Test — unit (judgement) | TC-047 Unit | yes |
| FR-007-AC-1 | Test (TC-052) | Test — unit-testing | TC-052 Unit | yes |
| FR-007-AC-2 | Test (TC-044) | Test — golden-approval-testing | TC-044 Snapshot | yes (FND-269) |
| FR-007-AC-3 | Test (TC-053) | Test — unit-testing (hand-asserted literals) | TC-053 Unit | yes; extend (FND-269) |
| FR-007-AC-4 | Test (TC-051) | Test — unit-testing | TC-051 Unit | yes |
| FR-007-AC-5 | Test (TC-050) | Test — golden-approval-testing (Snapshot) with equality oracle; advisor's concolic deferred (FND-273) | TC-050 Snapshot | yes; strengthen oracle (FND-268) |
| FR-007-AC-6 | Test (TC-045) | Test — unit negative cases (advisor: property-based; judgement: three named mutations, no generator needed) | TC-045 Unit | yes |
| FR-007-AC-7 | Test (TC-052) | Test — unit-testing | TC-052 Unit | yes |
| FR-007-CON-1 | Test (TC-050) | Test — golden against committed pre-change fixtures | TC-050 Snapshot | yes (FND-268) |
| FR-007-CON-2 | Test (TC-051) | Test — unit (clause bytes equal fence body) + Inspection that nothing tokenizes it (judgement) | TC-051 Unit | yes |
| FR-007-CON-3 | Inspection | Inspection (catalog: no-executable-oracle) | TC-059 Static | no — row has no oracle (FND-262) |
| NFR-001 M-1 | procedure (Method cell) | Test — integration (determinism over one tree; not Property) | TC-056 Property | no — Integration or fold into TC-042 (FND-266) |
| NFR-001 M-2 | procedure (Method cell) | Demonstration now (named evidence), automate via network namespace | TC-057 Manual | yes, conditionally (FND-267) |
| NFR-001 M-3 | procedure (Method cell) | Test — performance-benchmarking (Benchmark) | TC-058 Benchmark | Type yes; method column wrong (FND-271) |

## Recommendations

1. **FR-005 Constraints table** — FR-005-CON-3 Validation: `Test (TC-042)` →
   `Analysis (TC-054)`; FR-005-CON-4 Validation: `Test (TC-043)` →
   `Inspection; Test (TC-043)`.
2. **FR-005-AC-3** — append: "the set of properties carrying `free text:`
   equals {`Section.text`, `Constraint.type`, `Verification.method`,
   `MeasurementRow.target`, `MeasurementRow.threshold`, `ArtifactStatus`} and
   no other" so TC-040 has a closed oracle; the reasons themselves are
   Inspection.
3. **FR-005-AC-6** — keep the denylist under `Test (TC-043)`; move "the `TC`
   model's doc comment states…" to a separate criterion verified by
   `Inspection`, or name the exact token the comment must carry.
4. **FR-006-AC-6** — rewrite as "`quoin module install path:<module root>` on
   quoin main at 3e842ce or later exits 0" with Verification `Test (TC-055)`;
   move the `semantic.unknown-export` branch to a Behavior clause that names
   the deviation record (change log + quoin issue) and is not a passing
   outcome of the criterion.
5. **spec/tests.md** —
   - TC-042: keep Integration for AC-5; add a new Unit row (next free id) for
     FR-005-AC-7 (file set + bundle digest vs `toolchain.json`, no toolchain).
   - TC-043: Type Static → Unit.
   - TC-054: add a title note that it is the sole binding of FR-005-CON-3.
   - TC-055: Type Manual → Integration; title: subprocess `quoin module
     install`, exit 0, fail (not skip) when `quoin` is absent.
   - TC-056: Type Property → Integration, or delete and add
     `NFR-001 (metric 1)` to TC-042's Traces To.
   - TC-057: keep Manual; add "evidence: release-notes entry for the tag" to
     the title, and file the automation (`unshare -rn`) as a follow-up.
   - TC-058: NFR coverage table Verification Method `Benchmark` →
     `Test (TC-058)`; define the reference machine in NFR-001 M-3.
   - TC-059: either narrow to a checkable statement ("the installed package
     data contains no `.py` beyond `__init__.py`; the reference mapping's entry
     point takes document text and returns a dict; no test writes a `.md`") and
     keep Static, or delete the row and discharge FR-007-CON-3 through the
     inspection record.
6. **Skip discipline** — TC-042, TC-048, TC-055 must fail, not skip, when the
   toolchain, the digest-reporting wheel, or the quoin CLI is absent (FR-001
   CR-002 precedent in `tests/test_manifest_and_validate.py::TC-001`).
7. **TC-041 / TC-057 offline claim** — run TC-041 under a socket-blocking
   fixture so "offline" is asserted, not asserted-in-prose.
8. **TC-050 fixtures** — commit the ten 3d87196 skeletons under
   `tests/fixtures/pre-change/`; add the equality oracle from FND-268 to
   FR-007-AC-5.
9. **TC-053** — one hand-asserted literal row per typed table so the TC-044
   goldens have an independent oracle.
10. **FR-006-AC-1/AC-4** — replace "the admitted ten" with "the nine keys of
    AC-1 plus `sweep_report`" wherever the key count appears.
