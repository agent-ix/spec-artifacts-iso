"""FR-007 — the Markdown mappings, the golden records, and the declaration.

``spec_artifacts_iso/mappings.yaml`` is what this module publishes about how a
document becomes a record; the golden records under ``examples/`` are what that
declaration produces on the ten authoring skeletons. These tests hold both to
independent truth:

* TC-052 checks the declaration against the *emitted schemas* (the property
  set) and against ``manifest.yaml`` (the locator column lists) — never against
  itself, and never against a list generated from either, which would make the
  assertion prove nothing;
* TC-044 rebuilds each golden from its skeleton and compares bytes, then
  validates it against its model;
* TC-050 maps the pre-change skeletons read out of git at 3d87196 and checks
  that a document conforming before FR-005 still maps to a valid record;
* TC-053 pins the `Verification` split and the constraint row of the FR
  skeleton.

There are no skip guards. Regenerating a golden is deliberate: run the mapping
over the skeleton with the caller inputs `mappings.yaml` declares under
`golden_records` and write `canonical_json(record)`.
"""

from __future__ import annotations

import json
import pathlib
import subprocess

import pytest
import yaml
from support import reference_mapping as rm
from support.schema_bundle import load_bundle, validation_errors

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
PKG_ROOT = REPO_ROOT / "spec_artifacts_iso"
MANIFEST_PATH = PKG_ROOT / "manifest.yaml"

#: The commit the pre-change skeletons are read from (FR-007-AC-5).
PRE_CHANGE_COMMIT = "3d87196"

#: FR-007-AC-7: the kinds whose text is the byte-exact slice.
LOSSLESS_KINDS = frozenset({"section", "ocl-clause"})

#: FR-003: the decorative annotation keys a master-requirements relationship
#: item admits, which the sealed `Relationship` model cannot carry.
RELATIONSHIP_ANNOTATION_KEYS = frozenset({"note", "models", "endpoints"})


@pytest.fixture(scope="module")
def declaration() -> dict:
    return rm.load_mappings()


@pytest.fixture(scope="module")
def manifest() -> dict:
    return yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def bundle() -> dict:
    return load_bundle()


def _archetypes(manifest: dict) -> dict[str, dict]:
    return {a["name"]: a for a in manifest["artifact_types"]}


def _locators(archetype: dict) -> dict[str, dict]:
    return ((archetype.get("body_extraction") or {}).get("yield_pattern") or {}).get(
        "match"
    ) or {}


def _build(model: str, declaration: dict, source_identity: str | None = ...):
    """Map a model's skeleton with the caller inputs the declaration names."""
    model_declaration = declaration["models"][model]
    golden = declaration["golden_records"]
    skeleton = PKG_ROOT / model_declaration["skeleton"]
    identity = golden["source_identity"] if source_identity is ... else source_identity
    return rm.map_file(
        skeleton,
        path=f"{golden['path_prefix']}/{skeleton.name}",
        model=model,
        source_identity=identity,
        declaration=declaration,
    )


# ---------------------------------------------------------------------------
# TC-044 — the golden records
# ---------------------------------------------------------------------------
def test_tc044_every_skeleton_reproduces_its_golden_record(
    declaration: dict, bundle: dict
) -> None:
    """TC-044: FR-005-AC-4, FR-007-AC-2: for each of the ten skeletons the
    reference mapping produces the committed `examples/<type>.record.json`
    byte-for-byte after canonical serialization, and that record validates
    against `schemas/<Model>.json`.
    """
    assert len(declaration["models"]) == 10

    for model, model_declaration in declaration["models"].items():
        result = _build(model, declaration)
        golden = PKG_ROOT / model_declaration["example"]
        assert golden.exists(), (
            f"{golden} is missing; the golden records are shipped module data "
            "(FR-007 Outputs), not a build product"
        )
        assert rm.canonical_json(result.record) == golden.read_text(encoding="utf-8"), (
            f"{golden.name} is not what the reference mapping builds from "
            f"{model_declaration['skeleton']}"
        )
        assert (
            json.loads(golden.read_text(encoding="utf-8"))["type"] == model
        ), f"{golden.name} carries a `type` that is not the archetype name"
        errors = validation_errors(
            result.record, model_declaration["schema"].split("/")[-1], bundle
        )
        assert not errors, f"{model} record does not validate: {errors}"


def test_tc044_golden_filenames_are_the_archetype_names(declaration: dict) -> None:
    """TC-044: FR-007-AC-2: `examples/<type>.record.json` is named by the
    archetype name — `master-requirements`, `index`, `log` — not the model
    name, so a consumer finds the record by the name it already writes.
    """
    on_disk = sorted(p.name for p in (PKG_ROOT / "examples").glob("*.record.json"))
    declared = sorted(
        m["example"].split("/")[-1] for m in declaration["models"].values()
    )
    assert on_disk == declared
    for model, model_declaration in declaration["models"].items():
        assert model_declaration["example"] == f"examples/{model}.record.json"


def test_tc044_provenance_carries_the_bytes_as_read(declaration: dict) -> None:
    """TC-044: FR-007 Behavior: `provenance.digest` is the SHA-256 of the
    document bytes as read with no line-ending normalization, `path` is the
    corpus-relative path, and `sourceIdentity` comes from the caller alone —
    absent when the caller supplies none, never synthesized.
    """
    import hashlib

    for model, model_declaration in declaration["models"].items():
        skeleton = PKG_ROOT / model_declaration["skeleton"]
        data = skeleton.read_bytes()
        with_identity = _build(model, declaration).record["provenance"]
        assert with_identity["digest"] == f"sha256:{hashlib.sha256(data).hexdigest()}"
        assert with_identity["path"] == (
            f"{declaration['golden_records']['path_prefix']}/{skeleton.name}"
        )
        assert (
            with_identity["sourceIdentity"]
            == declaration["golden_records"]["source_identity"]
        )

        without = _build(model, declaration, source_identity=None).record["provenance"]
        assert (
            "sourceIdentity" not in without
        ), f"{model} synthesized a sourceIdentity the caller did not supply"


# ---------------------------------------------------------------------------
# TC-050 — the pre-change skeletons
# ---------------------------------------------------------------------------
def _git_show(path: str) -> bytes:
    completed = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "show", f"{PRE_CHANGE_COMMIT}:{path}"],
        capture_output=True,
    )
    assert completed.returncode == 0, (
        f"`git show {PRE_CHANGE_COMMIT}:{path}` failed: "
        f"{completed.stderr.decode('utf-8', 'replace')}. The pre-change "
        "skeletons are read out of git, never copied by hand — a hand copy "
        "would prove nothing about what was committed."
    )
    return completed.stdout


def test_tc050_pre_change_skeletons_still_map_and_validate(
    declaration: dict, bundle: dict
) -> None:
    """TC-050: FR-007-AC-5: a document copied from each of the ten skeletons as
    committed at 3d87196 — before FR-005 and FR-007 — maps to a record that
    validates against the new schema, so existing conforming Markdown is
    semantically equivalent under the new models.
    """
    for model, model_declaration in declaration["models"].items():
        relative = f"spec_artifacts_iso/{model_declaration['skeleton']}"
        data = _git_show(relative)
        result = rm.map_bytes(
            data,
            path=relative,
            model=model,
            source_identity=None,
            declaration=declaration,
        )
        errors = validation_errors(
            result.record, model_declaration["schema"].split("/")[-1], bundle
        )
        assert not errors, (
            f"the {PRE_CHANGE_COMMIT} {model} skeleton maps to a record the new "
            f"schema rejects: {errors}"
        )


def test_tc050_no_heading_or_table_header_changed(declaration: dict) -> None:
    """TC-050: FR-007-CON-1: the mapping keeps every existing heading, table
    header, and column order the corpus uses; the only Markdown form added is
    the optional `## Invariants` section on FR.
    """
    added_by_this_change = {"fr.md": {"Invariants", "digest_matches_declared"}}

    for model_declaration in declaration["models"].values():
        name = model_declaration["skeleton"].split("/")[-1]
        before = rm.Document(
            _git_show(f"spec_artifacts_iso/{model_declaration['skeleton']}").decode(
                "utf-8"
            )
        )
        after = rm.Document(
            (PKG_ROOT / model_declaration["skeleton"]).read_text(encoding="utf-8")
        )
        before_headings = [(h.level, h.text) for h in before.headings]
        after_headings = [(h.level, h.text) for h in after.headings]
        removed = [h for h in before_headings if h not in after_headings]
        added = {text for _level, text in after_headings} - {
            text for _level, text in before_headings
        }
        assert not removed, f"{name} lost headings {removed}"
        assert added == added_by_this_change.get(name, set()), (
            f"{name} gained headings {sorted(added)}; the only Markdown form "
            "this change adds is the FR `## Invariants` section"
        )
        assert _table_headers(before) == _table_headers(
            after
        ), f"{name} changed a table header or column order"


def _table_headers(document: rm.Document) -> list[list[str]]:
    headers: list[list[str]] = []
    for index, line in enumerate(document.lines):
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        if index + 1 >= len(document.lines):
            continue
        following = document.lines[index + 1].strip()
        if following.startswith("|") and set(following) <= set("|:- \t"):
            headers.append([cell.strip() for cell in stripped.strip("|").split("|")])
    return headers


# ---------------------------------------------------------------------------
# TC-052 — the declaration
# ---------------------------------------------------------------------------
def test_tc052_mappings_validates_against_its_own_schema(declaration: dict) -> None:
    """TC-052: FR-007-AC-1: `mappings.yaml` validates against
    `mappings.schema.json`, so a malformed mapping is a schema error rather
    than a reader's surprise.
    """
    from jsonschema import Draft202012Validator

    schema = rm.load_mappings_schema()
    Draft202012Validator.check_schema(schema)
    errors = [
        f"{'/'.join(str(part) for part in error.absolute_path)}: {error.message}"
        for error in Draft202012Validator(schema).iter_errors(declaration)
    ]
    assert not errors, f"mappings.yaml does not validate: {errors}"


def test_tc052_every_model_property_is_declared_exactly_once(
    declaration: dict, bundle: dict, manifest: dict
) -> None:
    """TC-052: FR-007-AC-1: every property of every exported model has exactly
    one entry in `mappings.yaml`, and no entry names a property the model does
    not declare.

    The property set comes from the emitted schemas — the independent truth —
    not from a list kept beside the mapping.
    """
    archetypes = _archetypes(manifest)
    assert sorted(declaration["models"]) == sorted(manifest["semantic"]["exports"])

    for model, model_declaration in declaration["models"].items():
        schema_file = model_declaration["schema"].split("/")[-1]
        assert (
            model_declaration["schema"] == archetypes[model]["data_schema"]["schema"]
        ), f"{model} maps a schema the manifest does not bind to the archetype"
        declared = set(bundle[schema_file]["properties"])
        mapped = set(model_declaration["properties"])
        assert mapped == declared, (
            f"{model}: properties with no mapping entry {sorted(declared - mapped)}; "
            f"entries naming no model property {sorted(mapped - declared)}"
        )


def test_tc052_only_the_eight_kinds_and_each_is_used(
    declaration: dict, manifest: dict
) -> None:
    """TC-052: FR-007-AC-1: every entry uses one of the eight mapping kinds the
    manifest lists, and every one of the eight is used, so the vocabulary
    `manifest.yaml` publishes and the vocabulary `mappings.yaml` uses are the
    same eight.
    """
    eight = manifest["semantic"]["mappings"]
    assert len(eight) == 8
    assert declaration["kinds"] == eight

    used = {
        entry["kind"]
        for model in declaration["models"].values()
        for entry in model["properties"].values()
    }
    assert used <= set(
        eight
    ), f"kinds outside the manifest list: {sorted(used - set(eight))}"
    assert used == set(
        eight
    ), f"kinds the manifest lists and nothing uses: {sorted(set(eight) - used)}"


def test_tc052_table_columns_equal_the_locator_columns(
    declaration: dict, manifest: dict
) -> None:
    """TC-052: FR-007-AC-1: each `table`/`typed-table` column list equals the
    `assert.columns` of the corresponding `manifest.yaml` locator.

    `mappings.yaml` is authored, not generated from these columns; that is what
    makes this assertion mean something.
    """
    archetypes = _archetypes(manifest)
    checked = 0
    for model, model_declaration in declaration["models"].items():
        locators = _locators(archetypes[model])
        for name, entry in model_declaration["properties"].items():
            if entry["kind"] not in ("table", "typed-table"):
                continue
            section = entry["source"]["section"]
            matching = [
                locator
                for locator in locators.values()
                if locator.get("from") == "table_row"
                and locator.get("under_section") == section
            ]
            assert len(matching) == 1, (
                f"{model}.{name} names section {section!r}, which has "
                f"{len(matching)} `table_row` locators in the manifest"
            )
            assert entry["source"]["columns"] == matching[0]["assert"]["columns"], (
                f"{model}.{name} declares columns {entry['source']['columns']}; "
                f"the locator asserts {matching[0]['assert']['columns']}"
            )
            assert set(entry["cells"]) == set(
                entry["source"]["columns"]
            ), f"{model}.{name} does not give every column a cell rule"
            checked += 1
    assert checked == 6, (
        "expected the six asserted tables of the corpus archetypes, " f"found {checked}"
    )


def test_tc052_row_id_patterns_match_the_locator_patterns(
    declaration: dict, manifest: dict
) -> None:
    """TC-052: FR-007-AC-1: a typed table's `row_id.pattern` is the locator's
    own `id_pattern`, so the mapping rejects exactly the row ids the archetype
    rejects.
    """
    archetypes = _archetypes(manifest)
    for model, model_declaration in declaration["models"].items():
        locators = _locators(archetypes[model])
        for name, entry in model_declaration["properties"].items():
            if entry["kind"] != "typed-table":
                continue
            locator = next(
                spec
                for spec in locators.values()
                if spec.get("from") == "table_row"
                and spec.get("under_section") == entry["source"]["section"]
            )
            expected = locator["assert"]["id_pattern"].replace(r"\d", "[0-9]")
            assert entry["row_id"]["pattern"] == expected, (
                f"{model}.{name} declares row ids {entry['row_id']['pattern']}; "
                f"the locator asserts {locator['assert']['id_pattern']}"
            )
            assert entry["row_id"]["column"] == locator["assert"]["id_column"]


def test_tc052_round_trip_policy_and_lossless_flags(declaration: dict) -> None:
    """TC-052: FR-007-AC-7: every model records `authority: markdown` and
    `round_trip: derived`; `section` and `ocl-clause` properties carry
    `lossless: true`, and `table`, `typed-table`, `list`, `token`,
    `frontmatter` and `provenance` properties carry `lossless: false`.
    """
    for model, model_declaration in declaration["models"].items():
        assert model_declaration["authority"] == "markdown"
        assert model_declaration["round_trip"] == "derived"
        for name, entry in model_declaration["properties"].items():
            expected = entry["kind"] in LOSSLESS_KINDS
            assert entry["lossless"] is expected, (
                f"{model}.{name} is a {entry['kind']} mapping with "
                f"lossless: {entry['lossless']}"
            )


def test_tc052_dropped_frontmatter_keys_are_declared(
    declaration: dict, bundle: dict
) -> None:
    """TC-052: FR-007-AC-7: every model records the frontmatter keys its
    mapping drops — the keys the frontmatter schema beside it declares that the
    sealed model does not carry, and the FR-003 relationship annotation keys a
    sealed `Relationship` cannot hold.

    The expected set is computed from the frontmatter schemas and the emitted
    models, so a new frontmatter key with no home in the record fails here.
    """
    manifest = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    archetypes = _archetypes(manifest)

    for model, model_declaration in declaration["models"].items():
        frontmatter_schema = json.loads(
            (PKG_ROOT / archetypes[model]["frontmatter_schema_ref"]).read_text(
                encoding="utf-8"
            )
        )
        admitted = set(frontmatter_schema.get("properties") or {})
        mapped = {
            entry["source"]["key"]
            for entry in model_declaration["properties"].values()
            if entry["kind"] == "frontmatter"
        }
        declared = set(model_declaration["dropped_frontmatter_keys"])
        expected = admitted - mapped

        assert {k for k in declared if "[" not in k} == expected, (
            f"{model} declares dropped keys "
            f"{sorted(k for k in declared if '[' not in k)}; the frontmatter "
            f"schema admits {sorted(admitted)} and the mapping reads "
            f"{sorted(mapped)}"
        )

        item_schema = (
            (frontmatter_schema.get("properties") or {})
            .get("relationships", {})
            .get("items", {})
        )
        annotations = {
            key.split(".", 1)[1]
            for key in declared
            if key.startswith("relationships[]")
        }
        if item_schema.get("additionalProperties") is True:
            assert annotations == RELATIONSHIP_ANNOTATION_KEYS, (
                f"{model} admits annotation keys on a relationship item but "
                f"declares {sorted(annotations)} as dropped"
            )
        else:
            assert not annotations, (
                f"{model} declares relationship annotation keys as dropped, but "
                "its frontmatter schema seals the relationship item"
            )


# ---------------------------------------------------------------------------
# TC-053 — the Verification split and the constraint row
# ---------------------------------------------------------------------------
def test_tc053_acceptance_rows_split_the_verification_cell(
    declaration: dict,
) -> None:
    """TC-053: FR-007-AC-3: the FR skeleton's `## Acceptance Criteria` rows map
    to `AcceptanceCriterion` objects whose `verification` splits `Test (TC-001)`
    into `method: Test`, `annotation: TC-001`, and `testRefs: [TC-001]`.
    """
    record = _build("FR", declaration).record
    criteria = record["acceptanceCriteria"]
    assert [row["id"] for row in criteria] == ["FR-001-AC-1", "FR-001-AC-2"]
    assert criteria[0]["verification"] == {
        "method": "Test",
        "annotation": "TC-001",
        "testRefs": ["TC-001"],
    }
    assert criteria[1]["verification"] == {
        "method": "Test",
        "annotation": "TC-002",
        "testRefs": ["TC-002"],
    }
    assert criteria[0]["line"] < criteria[1]["line"], "rows are in authored order"


def test_tc053_constraint_row_carries_its_type_and_validation(
    declaration: dict,
) -> None:
    """TC-053: FR-007-AC-3: the FR skeleton's `## Constraints` row maps to a
    `Constraint` with `type: Security` and a `validation` of the same
    `Verification` shape as a criterion cell.
    """
    record = _build("FR", declaration).record
    (constraint,) = record["constraints"]
    assert constraint["id"] == "FR-001-CON-1"
    assert constraint["type"] == "Security"
    assert constraint["constraint"] == "Digest computation SHALL use SHA-256 only"
    assert constraint["validation"] == {
        "method": "Integration Test",
        "testRefs": [],
    }, "a cell with no parentheses is `method` alone, with no `annotation`"


def test_tc053_verification_split_keeps_every_byte() -> None:
    """TC-053: FR-007-AC-3: the split keeps every byte the author wrote —
    `annotation` is the text between the first `(` and the last `)` verbatim,
    and a cell with no parentheses is the method alone.
    """
    assert rm.split_verification("Test (TC-035, TC-036)") == {
        "method": "Test",
        "annotation": "TC-035, TC-036",
        "testRefs": ["TC-035", "TC-036"],
    }
    assert rm.split_verification("Analysis (see the note (2026-09-03))") == {
        "method": "Analysis",
        "annotation": "see the note (2026-09-03)",
        "testRefs": [],
    }
    assert rm.split_verification("  Inspection  ") == {
        "method": "Inspection",
        "testRefs": [],
    }
