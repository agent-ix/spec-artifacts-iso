"""Smoke test for ``scripts/corpus_census.py`` over a hand-built fixture corpus.

FR-005 Inputs cites ``scripts/corpus_census.py`` as the record of the
2026-09-03 census — the measurement that fixes the id, status, cardinality,
verification-cell and constraint-type populations its constraints admit. A
cited measurement has to be reproducible by someone who is not its author, so
the script is a committed deliverable and this test is what keeps it one: a
tiny corpus under ``tests/fixtures/census/`` whose counts are obvious by
inspection, checked against what the script reports.

The fixture corpus is two bundles:

* ``repo-alpha/spec`` — a master-requirements document with a two-entry
  ``dependsOn``, an index with four link lines, a log with two dated entries
  and one undated one, an FR with a constraint table and an FR whose
  ``## Constraints`` section is prose, and one document with no frontmatter;
* ``repo-beta/spec`` — a master-requirements document with an empty
  ``dependsOn``, a bold-form and a plain-form user story, an IT with success
  criteria and an IT without, and an StR with one validation criterion.

No trace tag: the census measures the corpus, it does not verify a property of
the emitted models, so it backs neither FR-005-AC-3 nor FR-005-CON-1 (TC-040).
"""

from __future__ import annotations

import json
import pathlib

import pytest

from scripts.corpus_census import (
    DEFAULT_ROOT_GLOB,
    Census,
    expand_roots,
    main,
)

FIXTURE_ROOT = pathlib.Path(__file__).resolve().parent / "fixtures" / "census"
FIXTURE_GLOB = str(FIXTURE_ROOT / "*" / "spec")
SCRIPT_PATH = (
    pathlib.Path(__file__).resolve().parent.parent / "scripts" / "corpus_census.py"
)

#: The counts the fixture corpus obviously has, by inspection of the twelve
#: documents listed in this module's docstring.
EXPECTED_METRICS = {
    "bundles": 2,
    "repositories": 2,
    "documents_scanned": 12,
    "documents_unreadable": 0,
    "documents_with_frontmatter": 11,
    "documents_typed": 11,
    "documents_identified": 7,
    "status_documents": 8,
    "constraint_rows": 2,
    "verification_cells": 6,
    "verification_cells_empty": 1,
    "verification_methods_lint_admitted": 5,
    "fr_documents": 2,
    "fr_with_object": 1,
    "fr_prose_constraints": 1,
    "us_documents": 2,
    "us_story_bold": 1,
    "us_story_plain": 1,
    "us_story_neither": 0,
    "it_documents": 2,
    "it_with_success_criteria": 1,
    "index_documents": 1,
    "index_link_lines": 4,
    "index_dash_bullets": 1,
    "index_without_summary": 2,
    "log_documents": 1,
    "log_dated_entries": 2,
    "log_undated_entries": 1,
    "log_undated_repositories": 1,
    "master_requirements_documents": 2,
    "depends_on_lists": 1,
    "depends_on_empty": 1,
}


@pytest.fixture(scope="module")
def fixture_census() -> Census:
    roots = expand_roots([FIXTURE_GLOB])
    assert roots, f"fixture corpus not found under {FIXTURE_ROOT}"
    census = Census()
    census.run(roots)
    return census


def _corpus_snapshot() -> dict[str, bytes]:
    return {
        str(path.relative_to(FIXTURE_ROOT)): path.read_bytes()
        for path in sorted(FIXTURE_ROOT.rglob("*"))
        if path.is_file()
    }


def test_fixture_corpus_is_the_twelve_documents_the_counts_assume() -> None:
    """The fixture is small enough that its counts are checkable by eye."""
    documents = sorted(
        str(path.relative_to(FIXTURE_ROOT)) for path in FIXTURE_ROOT.rglob("*.md")
    )
    assert documents == [
        "repo-alpha/spec/functional/FR-001-alpha.md",
        "repo-alpha/spec/functional/FR-002-beta.md",
        "repo-alpha/spec/index.md",
        "repo-alpha/spec/log.md",
        "repo-alpha/spec/notes.md",
        "repo-alpha/spec/spec.md",
        "repo-beta/spec/spec.md",
        "repo-beta/spec/stakeholder/StR-001-consumer.md",
        "repo-beta/spec/test/IT-001-with-criteria.md",
        "repo-beta/spec/test/IT-002-without-criteria.md",
        "repo-beta/spec/usecase/US-001-bold-story.md",
        "repo-beta/spec/usecase/US-002-plain-story.md",
    ]


def test_census_counts_match_the_fixture(fixture_census: Census) -> None:
    """Every reported metric equals the count the fixture obviously has."""
    reported = {name: metric.value for name, metric in fixture_census.metrics().items()}
    assert reported == EXPECTED_METRICS


def test_every_metric_states_unit_population_and_method(
    fixture_census: Census,
) -> None:
    """A number nobody can read is not a measurement (Task-007 subtask 2)."""
    for name, metric in fixture_census.metrics().items():
        assert metric.unit, f"{name} states no unit"
        assert metric.population, f"{name} states no population"
        assert metric.method in {
            "by document",
            "by line",
            "by table row",
            "by relationship entry",
            "by directory",
        }, f"{name} states an unrecognised method: {metric.method!r}"


def test_distributions_carry_the_fixture_value_sets(fixture_census: Census) -> None:
    distributions = fixture_census.distributions()

    assert distributions["artifact_types"].counter == {
        "FR": 2,
        "IT": 2,
        "US": 2,
        "master-requirements": 2,
        "StR": 1,
        "index": 1,
        "log": 1,
    }
    # Three spellings of two states — the open ``status`` vocabulary FR-005
    # keeps open is exactly this shape, in miniature.
    assert distributions["status_spellings"].counter == {
        "approved": 6,
        "draft": 1,
        "Draft": 1,
    }
    assert distributions["cardinality_forms"].counter == {"1:N": 2, "1:1": 1}
    assert distributions["id_patterns"].counter == {
        "FR-N": 2,
        "IT-N": 2,
        "US-N": 2,
        "StR-N": 1,
    }
    assert distributions["constraint_types"].counter == {
        "Boundary": 1,
        "Integrity": 1,
    }
    assert distributions["verification_methods"].counter == {
        "Test": 2,
        "Analysis": 1,
        "Demonstration": 1,
        "Inspection": 1,
    }
    for name, distribution in distributions.items():
        assert distribution.unit, f"{name} states no unit"
        assert distribution.population, f"{name} states no population"
        assert distribution.method, f"{name} states no method"


def test_default_root_is_a_glob_not_one_developers_path() -> None:
    """Task-007 subtask 1: the corpus root is an argument with a portable default."""
    assert DEFAULT_ROOT_GLOB == "~/dev/*/spec"
    source = SCRIPT_PATH.read_text(encoding="utf-8")
    assert "/home/" not in source, "the census hard-codes an absolute home path"


def test_root_is_repeatable_on_the_command_line(capsys) -> None:
    alpha = str(FIXTURE_ROOT / "repo-alpha" / "spec")
    beta = str(FIXTURE_ROOT / "repo-beta" / "spec")
    assert main(["--root", alpha, "--root", beta, "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["root_patterns"] == [alpha, beta]
    assert payload["metrics"]["bundles"]["value"] == 2


def test_json_output_carries_every_metric_and_its_provenance(capsys) -> None:
    """Task-007 subtask 3: a later run is diffable against this one."""
    assert main(["--root", FIXTURE_GLOB, "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["census_version"] == 1
    assert payload["source"] == "scripts/corpus_census.py"
    assert payload["root_patterns"] == [FIXTURE_GLOB]
    assert len(payload["roots"]) == 2

    reported = {name: entry["value"] for name, entry in payload["metrics"].items()}
    assert reported == EXPECTED_METRICS
    for name, entry in payload["metrics"].items():
        assert set(entry) == {"value", "unit", "population", "method"}, name

    statuses = payload["distributions"]["status_spellings"]
    assert statuses["distinct"] == 3
    assert statuses["total"] == 8
    assert statuses["counts"]["approved"] == 6


def test_table_output_names_the_unit_population_and_method(capsys) -> None:
    assert main(["--root", FIXTURE_GLOB]) == 0
    table = capsys.readouterr().out

    assert "Bundles matched: 2" in table
    assert "documents_scanned" in table
    assert "documents / every *.md file under the matched bundles / by document" in (
        table
    )
    assert "status_spellings: 3 distinct value(s) over 8 documents" in table
    assert "by relationship entry" in table


def test_table_output_truncates_a_distribution_and_says_so(capsys) -> None:
    assert main(["--root", FIXTURE_GLOB, "--top", "1"]) == 0
    table = capsys.readouterr().out
    assert "... 2 more value(s)" in table


def test_no_matching_bundle_is_an_error_not_an_empty_census(capsys) -> None:
    """An unmatched root reports a failure rather than a census of nothing."""
    assert main(["--root", str(FIXTURE_ROOT / "no-such-repo" / "spec")]) == 1
    assert "no bundle matched" in capsys.readouterr().err


def test_census_writes_nothing_to_the_corpus(capsys) -> None:
    """Task-007: the census reads the corpus and writes nothing to it."""
    before = _corpus_snapshot()
    assert main(["--root", FIXTURE_GLOB, "--json"]) == 0
    capsys.readouterr()
    assert _corpus_snapshot() == before
