"""FR-007 — the `## Invariants` section, the `ocl-clause` mapping (TC-051), and
the read-only boundary (TC-059).

This is the one Markdown form the FR-007 change adds and the only place the
module touches semantic-core's clause types. The clause text is opaque bytes:
it is carried beside the record in the `invariantsText` sidecar and nothing
here tokenizes, typechecks, or evaluates it (FR-007-CON-2).

`sourceSpan` is emitted only when the caller supplies a `sourceIdentity`,
because semantic-core's `SourceLocus` requires `sourceIdentity`, `path`,
`startLine` and `startColumn` — without a caller identity the span cannot be
built, and an `ix://` value is never synthesized to fill the hole.
"""

from __future__ import annotations

import ast
import json
import pathlib

import pytest
from support import reference_mapping as rm
from support.schema_bundle import load_bundle, validation_errors

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
PKG_ROOT = REPO_ROOT / "spec_artifacts_iso"
SUPPORT_ROOT = REPO_ROOT / "tests" / "support"
CLAUSES = REPO_ROOT / "tests" / "fixtures" / "mutations" / "invariants"

CALLER_IDENTITY = "ix://agent-ix/example/spec"

#: semantic-core `SourceLocus` requires all four; the mapping cannot build one
#: without a caller identity.
SOURCE_LOCUS_REQUIRED = ("sourceIdentity", "path", "startLine", "startColumn")


@pytest.fixture(scope="module")
def declaration() -> dict:
    return rm.load_mappings()


@pytest.fixture(scope="module")
def bundle() -> dict:
    return load_bundle()


def _clause_fixture(name: str) -> bytes:
    path = CLAUSES / name
    assert path.exists(), f"{path} is missing; the clause fixtures are committed"
    return path.read_bytes()


def _map(data: bytes, declaration: dict, identity: str | None = CALLER_IDENTITY):
    return rm.map_bytes(
        data,
        path="spec/functional/FR-001-verify-checksums.md",
        source_identity=identity,
        declaration=declaration,
    )


def _skeleton(declaration: dict) -> bytes:
    return (PKG_ROOT / declaration["models"]["FR"]["skeleton"]).read_bytes()


# ---------------------------------------------------------------------------
# TC-051 — the clause mapping
# ---------------------------------------------------------------------------
def test_tc051_skeleton_clause_maps_to_a_clause_ref(
    declaration: dict, bundle: dict
) -> None:
    """TC-051: FR-007-AC-4: the FR skeleton's `## Invariants` clause maps to a
    `ClauseRef` with `language: ocl` and `clauseId` equal to the `###` heading,
    and the record validates against `FR.json`.
    """
    result = _map(_skeleton(declaration), declaration)
    (clause,) = result.record["invariants"]
    assert clause["language"] == "ocl"
    assert clause["clauseId"] == "digest_matches_declared"
    assert set(clause) <= {
        "language",
        "clauseId",
        "sourceSpan",
    }, "a `ClauseRef` carries no clause text; the text lives in the sidecar"
    assert not validation_errors(result.record, "FR.json", bundle)


def test_tc051_source_span_only_with_a_caller_source_identity(
    declaration: dict, bundle: dict
) -> None:
    """TC-051: FR-007-AC-4: with a caller-supplied `sourceIdentity` the clause
    carries a `sourceSpan` whose `startLine`/`endLine` are the fence lines;
    without one it carries no `sourceSpan`, because `SourceLocus` requires a
    `sourceIdentity` and the mapping never synthesizes an `ix://` value.
    """
    data = _skeleton(declaration)
    lines = data.decode("utf-8").split("\n")
    open_line = lines.index("```ocl") + 1
    close_line = lines.index("```", open_line) + 1

    with_identity = _map(data, declaration).record["invariants"][0]
    span = with_identity["sourceSpan"]
    for key in SOURCE_LOCUS_REQUIRED:
        assert key in span, f"`SourceLocus` requires {key}"
    assert span["sourceIdentity"] == CALLER_IDENTITY
    assert span["path"] == "spec/functional/FR-001-verify-checksums.md"
    assert span["startLine"] == open_line
    assert span["endLine"] == close_line
    assert span["startColumn"] == 1
    assert span["endColumn"] == 3, "the closing ``` fence ends at column 3"

    without = _map(data, declaration, identity=None)
    assert "sourceSpan" not in without.record["invariants"][0]
    assert "sourceIdentity" not in without.record["provenance"]
    assert not validation_errors(without.record, "FR.json", bundle)


def test_tc051_invariants_text_is_the_fence_body_byte_for_byte(
    declaration: dict,
) -> None:
    """TC-051: FR-007-AC-4, FR-007-CON-2: the `invariantsText` sidecar entry
    equals the fence body byte-for-byte, records the fence's lines, and is the
    only place the clause text appears — the record never carries it.
    """
    data = _skeleton(declaration)
    text = data.decode("utf-8")
    lines = text.split("\n")
    open_index = lines.index("```ocl")
    close_index = lines.index("```", open_index + 1)
    expected = "\n".join(lines[open_index + 1 : close_index]) + "\n"

    result = _map(data, declaration)
    (entry,) = result.invariants_text
    assert entry["clauseId"] == "digest_matches_declared"
    assert entry["startLine"] == open_index + 1
    assert entry["endLine"] == close_index + 1
    assert entry["text"] == expected
    assert expected not in json.dumps(
        result.record
    ), "the clause text reached the record; FR-007 keeps it beside the record"


def test_tc051_clause_text_is_opaque_bytes(declaration: dict) -> None:
    """TC-051: FR-007-CON-2: the clause text is carried as opaque bytes. A body
    that is not OCL at all — that no tokenizer, typechecker or evaluator would
    accept — maps to exactly the same `ClauseRef` and is carried verbatim.
    """
    original = _clause_fixture("one-clause.md")
    gibberish = original.replace(
        b"context Artifact", b"\xc2\xa7 not ocl at all ((( ".decode().encode()
    )
    baseline = _map(original, declaration)
    mutated = _map(gibberish, declaration)
    assert mutated.record["invariants"] == baseline.record["invariants"]
    assert "not ocl at all (((" in mutated.invariants_text[0]["text"]


@pytest.mark.parametrize(
    ("fixture", "line", "needle"),
    [
        ("not-an-identifier-heading.md", 18, "not an Identifier"),
        ("fence-tagged-tla.md", 20, "tagged 'tla'"),
        ("two-fences-one-heading.md", 26, "more than one fenced block"),
        ("unterminated-fence.md", 20, "unterminated fence"),
        ("repeated-clause-id.md", 26, "already used in this document"),
        ("orphan-fence.md", 18, "owned by no `###` heading"),
    ],
)
def test_tc051_each_clause_defect_fails_naming_the_line(
    declaration: dict, fixture: str, line: int, needle: str
) -> None:
    """TC-051: FR-007-AC-4: a `### not-an-identifier` heading, a ```tla fence, a
    second fence under one heading, an unterminated fence, a repeated
    `clauseId`, and an `ocl` fence owned by no `###` heading each fail the
    mapping naming the line, and yield no record.
    """
    with pytest.raises(rm.MappingError) as raised:
        _map(_clause_fixture(fixture), declaration)
    (failure,) = raised.value.failures
    assert failure.line == line, f"{fixture}: failure named line {failure.line}"
    assert needle in failure.message
    assert not hasattr(raised.value, "record"), "no partial record is emitted"


def test_tc051_prose_invariants_leaves_the_property_absent(
    declaration: dict, bundle: dict
) -> None:
    """TC-051: FR-007-AC-4: a prose `## Invariants` with no fenced block leaves
    `invariants` absent and does NOT fail — the census counts 54 corpus FR
    documents in exactly that shape, and they keep validating. A document with
    no `## Invariants` at all is likewise unaffected.
    """
    for fixture in ("prose-invariants.md", "no-invariants-section.md"):
        result = _map(_clause_fixture(fixture), declaration)
        assert "invariants" not in result.record, fixture
        assert result.invariants_text == ()
        assert not validation_errors(result.record, "FR.json", bundle), fixture


# ---------------------------------------------------------------------------
# TC-059 — the read-only boundary
# ---------------------------------------------------------------------------
#: Every file-mutating API a Python file could reach for. `open` is checked
#: separately, on its mode.
WRITE_APIS = frozenset(
    {
        "write",
        "write_text",
        "write_bytes",
        "writelines",
        "touch",
        "mkdir",
        "makedirs",
        "unlink",
        "remove",
        "rmdir",
        "rmtree",
        "rename",
        "symlink_to",
        "hardlink_to",
        "copy",
        "copy2",
        "copyfile",
        "copytree",
        "move",
        "dump",  # json.dump / yaml.dump to a stream
        "safe_dump",
    }
)

#: The read-only file APIs the reference mapping is allowed to use.
READ_APIS = frozenset({"read_text", "read_bytes"})

#: Render-template suffixes: a module that shipped one could derive Markdown
#: from a record without any Python at all.
TEMPLATE_SUFFIXES = (".j2", ".jinja", ".jinja2", ".tera", ".hbs", ".mustache")


def _module_python_files() -> list[pathlib.Path]:
    """Every Python file of the module tree, excluding the vendored TypeSpec
    toolchain, which is a build input and does not ship (FR-005 Outputs)."""
    return sorted(
        path for path in PKG_ROOT.rglob("*.py") if "node_modules" not in path.parts
    )


def _support_python_files() -> list[pathlib.Path]:
    return sorted(SUPPORT_ROOT.rglob("*.py"))


def _write_calls(path: pathlib.Path) -> list[str]:
    """Every file-mutating call in a Python file, as `name:line` strings."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        function = node.func
        if isinstance(function, ast.Attribute) and function.attr in WRITE_APIS:
            found.append(
                f"{path.relative_to(REPO_ROOT)}:{node.lineno} .{function.attr}"
            )
        if isinstance(function, ast.Name) and function.id == "open":
            found.extend(_open_violation(path, node))
    return found


def _open_violation(path: pathlib.Path, node: ast.Call) -> list[str]:
    """A builtin `open` is a violation unless its mode is a read-only literal."""
    mode: str | None = "r"
    if len(node.args) > 1:
        mode = node.args[1].value if isinstance(node.args[1], ast.Constant) else None
    for keyword in node.keywords:
        if keyword.arg == "mode":
            mode = (
                keyword.value.value if isinstance(keyword.value, ast.Constant) else None
            )
    if mode is None or not mode.startswith("r") or set(mode) & set("+wax"):
        return [f"{path.relative_to(REPO_ROOT)}:{node.lineno} open(mode={mode!r})"]
    return []


def test_tc059_no_module_or_support_file_writes_a_document() -> None:
    """TC-059: FR-007-CON-3: no file in the module tree and no file in the test
    support writes a document — the tree is enumerated, not sampled, so a new
    file that writes is a failure the moment it lands.
    """
    files = _module_python_files() + _support_python_files()
    assert files, "the enumeration found no Python file; it would prove nothing"
    assert (
        SUPPORT_ROOT / "reference_mapping.py"
    ) in files, "the reference mapping itself must be inside the enumeration"

    offenders = [call for path in files for call in _write_calls(path)]
    assert not offenders, (
        "files in the module or its test support that write to disk: "
        f"{offenders}. FR-007-CON-3: the mapping reads Markdown and writes "
        "nothing back."
    )


def test_tc059_the_mapping_opens_every_document_read_only() -> None:
    """TC-059: FR-007-CON-3: the reference mapping reads every document with a
    read-only API and no other file API, so no document it maps can be
    modified by mapping it.
    """
    source = (SUPPORT_ROOT / "reference_mapping.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    file_calls = {
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr in WRITE_APIS | READ_APIS
    }
    assert file_calls, "the mapping performs no file access at all"
    assert file_calls <= READ_APIS, (
        "the reference mapping uses non-read file APIs: "
        f"{sorted(file_calls - READ_APIS)}"
    )
    assert "read_bytes" in file_calls, (
        "documents are read as bytes, because `provenance.digest` is taken over "
        "the bytes as read with no line-ending normalization"
    )


def test_tc059_the_module_ships_no_render_template() -> None:
    """TC-059: FR-007-CON-3: the module carries no render template either — no
    file in the shipped tree can derive Markdown from a record without any
    Python at all.
    """
    templates = [
        path.relative_to(REPO_ROOT)
        for path in PKG_ROOT.rglob("*")
        if path.is_file()
        and "node_modules" not in path.parts
        and path.suffix in TEMPLATE_SUFFIXES
    ]
    assert not templates, f"the module ships render templates: {templates}"
