"""FR-007 — mapping failure semantics (TC-045).

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
    with pytest.raises(rm.MappingError) as raised:
        _map("fr-wrong-prefix-row-id.md", declaration)
    (failure,) = raised.value.failures
    assert failure.line == 20, "the failure names the offending row's line"
    assert "FR-002-CON-1" in failure.message
    assert "^FR-001-CON-[0-9]+$" in failure.message
    assert not hasattr(raised.value, "record"), "no partial record is emitted"


def test_tc045_repeated_row_id_fails_naming_the_line(declaration: dict) -> None:
    """TC-045: FR-007-AC-6: a row id repeated within one table fails the
    mapping naming the repeat's line and the line it first appeared on.
    """
    with pytest.raises(rm.MappingError) as raised:
        _map("fr-repeated-row-id.md", declaration)
    (failure,) = raised.value.failures
    assert failure.line == 21
    assert "repeated" in failure.message
    assert "first at line 20" in failure.message


def test_tc045_duplicated_heading_fails_naming_the_line(declaration: dict) -> None:
    """TC-045: FR-007-AC-6: a level-2 heading the mapping names twice fails
    naming the second occurrence's line.
    """
    with pytest.raises(rm.MappingError) as raised:
        _map("fr-duplicated-heading.md", declaration)
    (failure,) = raised.value.failures
    assert failure.line == 16
    assert "Description" in failure.message


def test_tc045_malformed_story_fails_naming_the_line(declaration: dict) -> None:
    """TC-045: FR-007-AC-6: a `## Story` section that does not carry the
    As-a / I-want / So-that anchors fails the mapping naming the section's line.
    """
    with pytest.raises(rm.MappingError) as raised:
        _map("us-malformed-story.md", declaration)
    (failure,) = raised.value.failures
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
    with pytest.raises(rm.MappingError) as raised:
        _map("fr-three-defects.md", declaration)
    failures = raised.value.failures
    assert len(failures) == 3, (
        "one-pass reporting: three defects must report three failures, not the "
        f"first — got {[str(f) for f in failures]}"
    )
    assert raised.value.lines == (16, 24, 31)
    messages = " | ".join(f.message for f in failures)
    assert "Description" in messages
    assert "FR-002-CON-1" in messages
    assert "repeated" in messages


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
    }
    schema_layer = {
        "fr-missing-required-section.md",
        "fr-empty-typed-table.md",
        "fr-empty-verification-cell.md",
        "fr-status-outside-pattern.md",
    }
    clean = {"fr-crlf-source.md"}
    fixtures = {path.name for path in MUTATIONS.glob("*.md")}
    assert fixtures == mapping_layer | schema_layer | clean, (
        "every mutation fixture must be attributed to a layer: "
        f"{sorted(fixtures - (mapping_layer | schema_layer | clean))}"
    )

    for name in sorted(fixtures):
        data = _fixture(name)
        model = rm.model_for(data, declaration)
        if name in mapping_layer:
            with pytest.raises(rm.MappingError) as raised:
                _map(name, declaration)
            assert all(
                failure.line >= 1 for failure in raised.value.failures
            ), f"{name}: a mapping failure must name a document line"
            continue
        result = _map(name, declaration)  # the mapping does not fail
        errors = _schema_errors(result.record, model, declaration, bundle)
        if name in clean:
            assert not errors, f"{name} is the clean control and must validate"
        else:
            assert errors, f"{name} was accepted by both layers"
