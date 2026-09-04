"""Mapping failure semantics for the ISO records (FR-007, matrix row TC-045).

Some tests here are deliberately untagged. The TC-045 row enumerates its own
cases, and the oracle's remaining declared error paths — a column-list
mismatch, a row cell-count mismatch, a malformed table delimiter, an escaped
pipe, an undated history bullet, a `### <row id>` subsection naming no row —
are not among them, so tagging them would mint a trace the row does not claim.
They are covered because an untested error branch reports nothing, not because
a matrix row asks for them.

A mapping that silently produces a half-record is worse than one that fails.
Every failure the requirements name is pinned here, and so is the layer that
reports it:

* the **mapping** names a document **line** — a wrong-prefix row id, a row id
  repeated within one table, a heading it names twice, a `## Story` that does
  not match the grammar;
* the **schema** names a **JSON path** — an extra property, a removed required
  section, a typed table with a header and zero rows (`minItems`), a `line: 0`
  (`minimum`), an empty `Verification` cell (`minLength`), a `status` outside
  its pattern.

A case reported by the wrong layer is a finding, not a pass, so each test
asserts both that the right layer rejects and that the other one does not.

The empty `Verification` cell is deliberately a schema rejection: FR-005 gives
every prose cell `minLength: 1` and FR-007 Description says a document carrying
an empty required cell is rejected on that ground. It is not relaxed to make
anything pass.

The CRLF case is built in memory, not committed: `.gitattributes` normalizes
committed line endings to LF, so a committed CRLF fixture would arrive as LF
and the case would prove nothing.
"""

from __future__ import annotations

import json
import pathlib

import pytest
from support import reference_mapping as rm
from support.schema_bundle import load_bundle, validation_errors

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
PKG_ROOT = REPO_ROOT / "spec_artifacts_iso"
MUTATIONS = REPO_ROOT / "tests" / "fixtures" / "mutations"


@pytest.fixture(scope="module")
def declaration() -> dict:
    return rm.load_mappings()


@pytest.fixture(scope="module")
def bundle() -> dict:
    return load_bundle()


def _fixture(name: str) -> bytes:
    path = MUTATIONS / name
    assert path.exists(), f"{path} is missing; the mutation fixtures are committed"
    return path.read_bytes()


def _map(name_or_bytes: str | bytes, declaration: dict) -> rm.MappingResult:
    data = _fixture(name_or_bytes) if isinstance(name_or_bytes, str) else name_or_bytes
    return rm.map_bytes(data, path="tests/fixtures/mutations", declaration=declaration)


def _failing_map(name_or_bytes: str | bytes, declaration: dict) -> rm.MappingError:
    """Map a document that must fail, and assert it yielded **no record**.

    FR-007 Failure discipline: the mapping "SHALL emit no record when any
    failure is found". `pytest.raises` alone does not pin that — it would pass
    just as well for a mapping that built a half-record, handed it back through
    some other channel, and raised afterwards. So the result name is bound
    before the call and asserted to have stayed unbound: the only way this
    assertion holds is that nothing was returned. The error is also asserted to
    carry the failures it found, so an empty `MappingError` is not a pass
    either.
    """
    outcome: rm.MappingResult | None = None
    try:
        outcome = _map(name_or_bytes, declaration)
    except rm.MappingError as error:
        assert outcome is None, "the mapping produced a record and then failed"
        assert error.failures, "the mapping raised carrying no failure at all"
        assert all(
            failure.line >= 1 and failure.message for failure in error.failures
        ), "every failure names a 1-based document line and says what is wrong"
        return error
    raise AssertionError(
        "the mapping emitted a record where a failure was required: "
        f"{sorted(outcome.record)}"
    )


def _schema_errors(record: dict, model: str, declaration: dict, bundle: dict):
    return validation_errors(
        record, declaration["models"][model]["schema"].split("/")[-1], bundle
    )


def _golden(model: str) -> dict:
    return json.loads(
        (PKG_ROOT / "examples" / f"{model}.record.json").read_text(encoding="utf-8")
    )


# ---------------------------------------------------------------------------
# Failures the mapping reports, naming the document line
# ---------------------------------------------------------------------------
def test_tc045_wrong_prefix_row_id_fails_naming_the_line(declaration: dict) -> None:
    """TC-045: FR-007-AC-6: a typed-table row whose id does not match the
    locator's `id_pattern` fails the mapping naming the line, and no record is
    emitted.
    """
    (failure,) = _failing_map("fr-wrong-prefix-row-id.md", declaration).failures
    assert failure.line == 20, "the failure names the offending row's line"
    assert "FR-002-CON-1" in failure.message
    assert r"^FR-001-CON-\d+$" in failure.message


def test_tc045_repeated_row_id_fails_naming_the_line(declaration: dict) -> None:
    """TC-045: FR-007-AC-6: a row id repeated within one table fails the
    mapping naming the repeat's line and the line it first appeared on.
    """
    (failure,) = _failing_map("fr-repeated-row-id.md", declaration).failures
    assert failure.line == 21
    assert "repeated" in failure.message
    assert "first at line 20" in failure.message


def test_tc045_duplicated_heading_fails_naming_the_line(declaration: dict) -> None:
    """TC-045: FR-007-AC-6: a level-2 heading the mapping names twice fails
    naming the second occurrence's line.
    """
    (failure,) = _failing_map("fr-duplicated-heading.md", declaration).failures
    assert failure.line == 16
    assert "Description" in failure.message


def test_tc045_malformed_story_fails_naming_the_line(declaration: dict) -> None:
    """TC-045: FR-007-AC-6: a `## Story` section that does not carry the
    As-a / I-want / So-that anchors fails the mapping naming the section's line.
    """
    (failure,) = _failing_map("us-malformed-story.md", declaration).failures
    assert failure.line == 11
    assert "story grammar" in failure.message
    for anchor in ("`As a`", "`I want`", "`So that`"):
        assert anchor in failure.message


def test_tc045_all_failures_in_one_document_are_reported_together(
    declaration: dict,
) -> None:
    """TC-045: FR-007 Failure discipline: the mapping reports every failure it
    finds in one pass, not only the first, and emits no record when any failure
    is found.

    The fixture carries three defects — a duplicated `## Description`, a
    wrong-prefix constraint id, and a repeated acceptance-criterion id — and all
    three are reported.
    """
    raised = _failing_map("fr-three-defects.md", declaration)
    failures = raised.failures
    assert len(failures) == 3, (
        "one-pass reporting: three defects must report three failures, not the "
        f"first — got {[str(f) for f in failures]}"
    )
    assert raised.lines == (16, 24, 31)
    messages = " | ".join(f.message for f in failures)
    assert "Description" in messages
    assert "FR-002-CON-1" in messages
    assert "repeated" in messages


# ---------------------------------------------------------------------------
# The rest of the oracle's declared error paths
#
# Deliberately untagged — see the module docstring for why. These are the error
# semantics of the reference mapping itself: the code that decides whether a
# defect is reported or silently swallowed, where an untested error branch is a
# branch that reports nothing.
# ---------------------------------------------------------------------------
def test_table_whose_columns_differ_from_the_declaration_fails(
    declaration: dict,
) -> None:
    """FR-007 Golden records: a `table`/`typed-table` column list equals the
    locator's `assert.columns`. A document whose header renames a column
    therefore fails naming the header's line, rather than mapping the cell into
    the wrong property.
    """
    (failure,) = _failing_map("fr-table-columns-mismatch.md", declaration).failures
    assert failure.line == 18, "the failure names the header row's line"
    assert "'Verification Method'" in failure.message
    assert "FR.acceptanceCriteria" in failure.message


def test_row_with_the_wrong_cell_count_fails_naming_the_line(
    declaration: dict,
) -> None:
    """FR-007 Behavior: a `table` mapping fills one object per data row with a
    cell per declared column. A row carrying fewer cells than the table has
    columns fails naming the row's line — it is never zipped short into a row
    missing a property, which the schema would then report as the author's
    fault at the wrong layer.
    """
    (failure,) = _failing_map("fr-row-cell-count.md", declaration).failures
    assert failure.line == 20
    assert "2 cells" in failure.message
    assert "3 columns" in failure.message


def test_a_section_with_no_table_leaves_the_property_absent(
    declaration: dict, bundle: dict
) -> None:
    """FR-007: a named section carrying no table at all is not a mapping
    failure — the mapping has no row to name a line on — so the property is
    absent and the schema reports the omission by path. Both halves are
    asserted, or the case would pass for a mapping that invented an empty
    array.
    """
    result = _map("fr-acceptance-table-missing.md", declaration)
    assert "acceptanceCriteria" not in result.record
    assert _schema_errors(result.record, "FR", declaration, bundle) == [
        ": 'acceptanceCriteria' is a required property"
    ]


def test_a_header_row_with_no_delimiter_is_not_a_table(
    declaration: dict, bundle: dict
) -> None:
    """FR-007: a pipe row that is not followed by a `|---|` delimiter is not a
    table. The mapping does not read the following rows as data — which would
    silently promote the header itself into a row — and the absent property is
    reported by the schema.
    """
    result = _map("fr-acceptance-delimiter-malformed.md", declaration)
    assert "acceptanceCriteria" not in result.record
    assert _schema_errors(result.record, "FR", declaration, bundle) == [
        ": 'acceptanceCriteria' is a required property"
    ]


def test_an_escaped_pipe_stays_inside_its_cell(declaration: dict, bundle: dict) -> None:
    """FR-007 Behavior: cells are split on unescaped `|` only. A `\\|` inside a
    cell is one literal `|` in the cell's text and never a column boundary, so
    a criterion that talks about the pipe character keeps its bytes and the row
    keeps its declared cell count.
    """
    result = _map("fr-escaped-pipe-cell.md", declaration)
    (row,) = result.record["acceptanceCriteria"]
    assert row["criteria"] == "Given a digest of `a | b`, the artifact is persisted"
    assert row["verification"]["method"] == "Test"
    assert not _schema_errors(result.record, "FR", declaration, bundle)


def test_a_history_bullet_with_no_date_fails_naming_the_line(
    declaration: dict,
) -> None:
    """FR-007 Behavior: a `list` mapping fills `Log.history` with one object per
    matching bullet. A bullet carrying no `YYYY-MM-DD` date cannot fill
    `LogEntry.date`, so it fails naming the bullet's line and quotes the text —
    it is not skipped, which would drop an authored entry from the record
    without a word.
    """
    (failure,) = _failing_map("log-history-without-date.md", declaration).failures
    assert failure.line == 11
    assert "YYYY-MM-DD" in failure.message
    assert "Renamed the bundle index" in failure.message


def test_a_type_that_names_no_model_is_refused(declaration: dict) -> None:
    """FR-007: the model of a document is its frontmatter `type`. A `type` that
    names no model in `mappings.yaml` is refused naming the value and listing
    the models that exist — the document is never mapped against some default
    model, which would produce a record of the wrong shape.
    """
    document = b"---\ntype: NotAModel\n---\n# X\n\n## Description\n\nText.\n"
    for call in (
        lambda: rm.model_for(document, declaration),
        lambda: rm.map_bytes(document, path="tests/fixtures", declaration=declaration),
    ):
        with pytest.raises(ValueError) as raised:
            call()
        message = str(raised.value)
        assert "NotAModel" in message
        assert "FR" in message and "log" in message, (
            "the refusal lists the models that do exist: " f"{message}"
        )


# ---------------------------------------------------------------------------
# `typed-table` detail subsections
#
# Also deliberately untagged, for the reason the module docstring gives. The
# requirement's Behavior section declares the `### <row id>` cases and both of
# their failure branches.
# ---------------------------------------------------------------------------
def test_a_row_id_subsection_fills_the_row_detail(
    declaration: dict, bundle: dict
) -> None:
    """FR-007 Behavior: a `typed-table` mapping reads a supplementary
    `### <row id>` subsection into that row's `detail`, and only that row's —
    the rows the document does not supplement carry no `detail` at all, and the
    detail is the subsection's byte-exact body, ending where the next heading
    begins.

    The fixture also carries a `### Notes` subsection under the same table: a
    `###` heading naming no row id is ordinary prose, so it is passed over
    rather than failing as a subsection that "matches no row".
    """
    result = _map("fr-detail-subsection.md", declaration)
    first, second = result.record["acceptanceCriteria"]
    assert first["id"] == "FR-001-AC-1"
    assert first["detail"] == (
        "\nThe digest is computed over the bytes as read, with no line-ending\n"
        "normalization, and compared to the declared value.\n\n"
    )
    assert "Notes" not in first["detail"], "the detail ran past the next heading"
    assert "detail" not in second, "an unsupplemented row gains no detail"
    assert not _schema_errors(result.record, "FR", declaration, bundle)


def test_a_row_id_subsection_naming_no_row_fails_naming_the_line(
    declaration: dict,
) -> None:
    """FR-007 Failure discipline: a `### <row id>` subsection whose id matches
    no row fails naming the line. The subsection is authored *about* a
    criterion, so an id that has drifted from the table is a defect, not
    content to drop.
    """
    (failure,) = _failing_map("fr-detail-names-no-row.md", declaration).failures
    assert failure.line == 22
    assert "FR-001-AC-9" in failure.message
    assert "matches no row" in failure.message


def test_a_second_subsection_for_one_row_fails_naming_the_line(
    declaration: dict,
) -> None:
    """FR-007 Failure discipline: a `### <row id>` subsection naming a row that
    already carries a `detail` fails naming the second subsection's line —
    neither body silently wins.
    """
    (failure,) = _failing_map("fr-detail-repeated.md", declaration).failures
    assert failure.line == 26
    assert "already carries a detail subsection" in failure.message


# ---------------------------------------------------------------------------
# Failures the schema reports, naming the JSON path
# ---------------------------------------------------------------------------
def test_tc045_extra_property_fails_the_schema_naming_the_path(
    declaration: dict, bundle: dict
) -> None:
    """TC-045: FR-005-AC-4: a record carrying one property the sealed model does
    not declare is rejected by the schema, which names the path. The mapping
    never emits such a property — an undeclared frontmatter key is dropped by
    policy — so this is a record mutation, not a document one.
    """
    record = _golden("FR")
    record["notAModelProperty"] = "smuggled in"
    errors = _schema_errors(record, "FR", declaration, bundle)
    assert errors, "the sealed model accepted an undeclared property"
    assert any("notAModelProperty" in error for error in errors)


def test_tc045_removed_required_section_fails_the_schema(
    declaration: dict, bundle: dict
) -> None:
    """TC-045: FR-005-AC-4: a document with a required section removed maps
    cleanly — a missing section is not a mapping failure — and the schema
    rejects the record naming the property that has no value.
    """
    result = _map("fr-missing-required-section.md", declaration)
    assert "description" not in result.record
    errors = _schema_errors(result.record, "FR", declaration, bundle)
    assert errors == [": 'description' is a required property"]


def test_tc045_typed_table_with_no_rows_fails_min_items(
    declaration: dict, bundle: dict
) -> None:
    """TC-045: FR-005-AC-4: a typed table with a header and zero data rows maps
    to an empty array — never to an absent property, which would hide the
    authored-but-empty table — and the schema rejects it on the `minItems`
    boundary, naming the path.
    """
    result = _map("fr-empty-typed-table.md", declaration)
    assert result.record["acceptanceCriteria"] == []
    errors = _schema_errors(result.record, "FR", declaration, bundle)
    assert errors == ["acceptanceCriteria: [] should be non-empty"]


def test_tc045_line_zero_fails_the_minimum_boundary(
    declaration: dict, bundle: dict
) -> None:
    """TC-045: FR-005-AC-4: `line: 0` is rejected on the `minimum` boundary
    naming the path. Document lines are 1-based, so the mapping cannot produce
    a zero; this is the boundary a hand-built or third-party record could hit.
    """
    record = _golden("FR")
    record["acceptanceCriteria"][0]["line"] = 0
    errors = _schema_errors(record, "FR", declaration, bundle)
    assert errors == ["acceptanceCriteria/0/line: 0 is less than the minimum of 1"]


def test_tc045_empty_verification_cell_fails_min_length(
    declaration: dict, bundle: dict
) -> None:
    """TC-045: FR-005-AC-4, FR-007 Description: an empty `Verification` cell is
    a rejection, not a form this module admits. The mapping does not fail on it
    — it is not one of the failures FR-007 lists — and the schema rejects the
    record on `minLength: 1`, naming the path down to `verification/method`.

    The census counts such cells in the corpus. That is a finding about those
    documents; `minLength: 1` is not relaxed to accommodate them.
    """
    result = _map("fr-empty-verification-cell.md", declaration)
    assert result.record["acceptanceCriteria"][0]["verification"] == {
        "method": "",
        "testRefs": [],
    }
    errors = _schema_errors(result.record, "FR", declaration, bundle)
    assert errors == [
        "acceptanceCriteria/0/verification/method: '' should be non-empty"
    ]


def test_tc045_status_outside_its_pattern_fails_the_schema(
    declaration: dict, bundle: dict
) -> None:
    """TC-045: FR-005-AC-4: a `status` outside `^[A-Za-z][A-Za-z_-]*$` is
    rejected by the schema naming the path. The value set is open, the *shape*
    is not.
    """
    result = _map("fr-status-outside-pattern.md", declaration)
    assert result.record["status"] == "not a status"
    errors = _schema_errors(result.record, "FR", declaration, bundle)
    assert len(errors) == 1
    assert errors[0].startswith("status: 'not a status' does not match")


# ---------------------------------------------------------------------------
# CRLF — both halves
# ---------------------------------------------------------------------------
def test_tc045_crlf_document_trims_cells_and_keeps_section_bytes(
    declaration: dict, bundle: dict
) -> None:
    """TC-045: FR-005 Sections and tables: in a CRLF document every table cell
    is trimmed of leading and trailing whitespace including `\\r`, while
    `Section.text` keeps the CR bytes verbatim (quire-rs FR-008).

    Both halves are asserted, or the case proves nothing: a mapping that
    stripped CR everywhere would pass the cell half and silently normalize the
    section slice.
    """
    source = _fixture("fr-crlf-source.md")
    crlf = source.replace(b"\n", b"\r\n")
    assert b"\r\n" in crlf and b"\r" not in source

    record = _map(crlf, declaration).record

    # Cells: trimmed, `\r` included.
    (constraint,) = record["constraints"]
    assert constraint["type"] == "Security"
    assert constraint["validation"] == {"method": "Inspection", "testRefs": []}
    for value in (
        constraint["constraint"],
        record["acceptanceCriteria"][0]["criteria"],
        record["acceptanceCriteria"][0]["verification"]["method"],
    ):
        assert "\r" not in value, "a cell kept a CR byte the trim must remove"

    # Section text: byte-exact, CR bytes preserved.
    assert "\r\n" in record["description"]["text"], (
        "`Section.text` normalized the line endings; FR-005 requires the "
        "byte-exact slice, CR bytes included"
    )

    # The digest is over the bytes as read, so it differs from the LF document.
    assert (
        record["provenance"]["digest"]
        != _map(source, declaration).record["provenance"]["digest"]
    ), "the digest normalized line endings"

    assert not _schema_errors(record, "FR", declaration, bundle)


# ---------------------------------------------------------------------------
# Layer attribution
# ---------------------------------------------------------------------------
def test_tc045_each_case_is_reported_by_exactly_one_layer(
    declaration: dict, bundle: dict
) -> None:
    """TC-045: FR-007: the mapping names a document line and the schema names a
    JSON path; a case reported by the wrong layer is a finding, not a pass.

    Every committed mutation fixture is enumerated here, so a new fixture that
    is silently accepted by both layers fails this test.
    """
    mapping_layer = {
        "fr-wrong-prefix-row-id.md",
        "fr-repeated-row-id.md",
        "fr-duplicated-heading.md",
        "fr-three-defects.md",
        "us-malformed-story.md",
        "fr-table-columns-mismatch.md",
        "fr-row-cell-count.md",
        "fr-detail-names-no-row.md",
        "fr-detail-repeated.md",
        "log-history-without-date.md",
    }
    schema_layer = {
        "fr-missing-required-section.md",
        "fr-empty-typed-table.md",
        "fr-empty-verification-cell.md",
        "fr-status-outside-pattern.md",
        "fr-acceptance-table-missing.md",
        "fr-acceptance-delimiter-malformed.md",
    }
    clean = {
        "fr-crlf-source.md",
        "fr-escaped-pipe-cell.md",
        "fr-detail-subsection.md",
    }
    fixtures = {path.name for path in MUTATIONS.glob("*.md")}
    assert fixtures == mapping_layer | schema_layer | clean, (
        "every mutation fixture must be attributed to a layer: "
        f"{sorted(fixtures - (mapping_layer | schema_layer | clean))}"
    )

    for name in sorted(fixtures):
        data = _fixture(name)
        model = rm.model_for(data, declaration)
        if name in mapping_layer:
            error = _failing_map(name, declaration)
            assert all(
                failure.line >= 1 for failure in error.failures
            ), f"{name}: a mapping failure must name a document line"
            continue
        result = _map(name, declaration)  # the mapping does not fail
        errors = _schema_errors(result.record, model, declaration, bundle)
        if name in clean:
            assert not errors, f"{name} is the clean control and must validate"
        else:
            assert errors, f"{name} was accepted by both layers"
