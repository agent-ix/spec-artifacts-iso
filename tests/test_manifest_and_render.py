"""Manifest validation + unified-shape (FR-002) assert↔skeleton parity tests.

Render templates were removed (FR-002 CR, 2026-06-04): the per-archetype
skeletons are the authoring source of truth and quire-rs ``validate_document``
enforces structure with no render step. These tests therefore cover:

* manifest loads + validates against the FR-035 module-manifest schema;
* the unified archetype shape (no ``template_ref`` / ``required_sections`` /
  ``variants``; ``body_extraction`` carries ``assert`` facets);
* I1/I2/I3 (FR-002-AC-6/7/8): the manifest asserts and the per-archetype
  skeleton are mutually consistent (heading sets + levels, literal table
  headers, id patterns), and heading-presence locators are distinguished from
  ``section_body`` locators whose body the skeleton fills substantively;
* IT-002: each filled skeleton passes ``validate_document``, mutations fail,
  and ``extract`` yields a record (requires the quire wheel exposing the
  FR-032 markdown validator; skipped cleanly otherwise).
"""

from __future__ import annotations

import json
import pathlib
import re

import pytest
import yaml

PKG_ROOT = pathlib.Path(__file__).resolve().parent.parent / "spec_artifacts_iso"
MANIFEST_PATH = PKG_ROOT / "manifest.yaml"
SKELETONS_DIR = PKG_ROOT / "skeletons"

_SKELETON_FILE = {
    "FR": "fr",
    "NFR": "nfr",
    "StR": "str",
    "US": "us",
    "IT": "it",
    "TC": "tc",
    "AC": "ac",
    "CON": "con",
}


def test_manifest_loads() -> None:
    manifest = yaml.safe_load(MANIFEST_PATH.read_text())
    assert manifest["manifest_version"] == "1.0.0"
    assert manifest["name"] == "spec-artifacts-iso"
    assert manifest["version"]


def test_manifest_validates_against_fr035_schema() -> None:
    """Skip when jsonschema lacks draft 2020-12 support (CI uses check-jsonschema)."""
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        pytest.skip("jsonschema lib missing draft 2020-12 support")
    schema_path = (
        pathlib.Path(__file__).resolve().parent / "module-manifest.schema.json"
    )
    if not schema_path.exists():
        pytest.skip("FR-035 schema not bundled with tests")
    schema = json.loads(schema_path.read_text())
    manifest = yaml.safe_load(MANIFEST_PATH.read_text())
    errors = list(Draft202012Validator(schema).iter_errors(manifest))
    assert not errors, [
        f"{'.'.join(str(p) for p in e.absolute_path)}: {e.message}" for e in errors
    ]


def _artifact_types():
    manifest = yaml.safe_load(MANIFEST_PATH.read_text())
    return manifest.get("artifact_types", [])


_HEADING_REGEX_RE = re.compile(r"^\^(?P<name>.+?)\$$")


def _required_sections(at: dict, level: int | None = None) -> list[dict]:
    """Derive ``[{name, level, kind}]`` from the unified-shape ``body_extraction``.

    FR-035 CR-002 retired ``required_sections``; structural completeness is now
    expressed by locators that each pin a heading the document must carry:

    * ``from: section_body`` — the heading whose *body* must be substantive
      (FR-002-AC-8 / I3). ``assert.level`` gives its level. ``kind ==
      "section_body"``.
    * ``from: heading`` — a heading-presence locator (e.g. FR's ``Specification``
      H2). Its name comes from the anchored ``regex`` (``^Name$``) and its level
      from ``level``. ``kind == "heading"``.
    * ``from: table_row`` / ``list_item`` / ``code_block`` with ``under_section``
      — requires the named section heading to exist (so its child element can be
      located). Level comes from ``assert.section_level`` when present, else 2.
      ``kind == "heading"``.

    Pass ``level`` to restrict to a single heading level.
    """
    be = at.get("body_extraction") or {}
    match = (be.get("yield_pattern") or {}).get("match") or {}
    out: list[dict] = []
    seen: set[tuple[int, str]] = set()

    def add(name: str, sec_level: int, kind: str) -> None:
        if level is not None and sec_level != level:
            return
        key = (sec_level, name.lower())
        if key in seen:
            return
        seen.add(key)
        out.append({"name": name, "level": sec_level, "kind": kind})

    for loc in match.values():
        if not isinstance(loc, dict):
            continue
        from_ = loc.get("from")
        assert_facet = loc.get("assert") or {}
        if from_ == "section_body":
            add(loc["after_heading"], assert_facet.get("level", 2), "section_body")
        elif from_ == "heading":
            m = _HEADING_REGEX_RE.match(loc.get("regex") or "")
            if m:
                add(m.group("name"), loc.get("level", 2), "heading")
        elif loc.get("under_section"):
            # table_row / list_item / code_block pin their parent section.
            add(loc["under_section"], assert_facet.get("section_level", 2), "heading")
    return out


def _asserted_tables(at: dict) -> list[dict]:
    """Return ``[{section, columns}]`` for every table locator with ``columns``."""
    be = at.get("body_extraction") or {}
    match = (be.get("yield_pattern") or {}).get("match") or {}
    out: list[dict] = []
    for loc in match.values():
        if not isinstance(loc, dict) or loc.get("from") != "table_row":
            continue
        cols = (loc.get("assert") or {}).get("columns")
        if cols:
            out.append({"section": loc.get("under_section"), "columns": list(cols)})
    return out


def _asserted_id_patterns(at: dict) -> list[str]:
    """Return every ``assert.id_pattern`` declared by a table locator."""
    be = at.get("body_extraction") or {}
    match = (be.get("yield_pattern") or {}).get("match") or {}
    out: list[str] = []
    for loc in match.values():
        if not isinstance(loc, dict):
            continue
        pat = (loc.get("assert") or {}).get("id_pattern")
        if pat:
            out.append(pat)
    return out


def _strip_frontmatter(markdown: str) -> str:
    return re.sub(r"^---\n.*?\n---\n", "", markdown, count=1, flags=re.DOTALL)


def _skeleton_text(name: str) -> str:
    return (SKELETONS_DIR / f"{_SKELETON_FILE[name]}.md").read_text()


def _skeleton_doc_id(name: str) -> str:
    fm = re.match(r"---\n(.*?)\n---\n", _skeleton_text(name), re.DOTALL)
    assert fm, f"{name} skeleton missing frontmatter"
    return yaml.safe_load(fm.group(1))["id"]


def _skeleton_headings(markdown: str) -> list[tuple[int, str]]:
    """Return ``[(level, text)]`` for every ATX heading below the H1 title."""
    body = _strip_frontmatter(markdown)
    out: list[tuple[int, str]] = []
    for line in body.splitlines():
        m = re.match(r"^(#{1,6})\s+(.*\S)\s*$", line)
        if m and len(m.group(1)) >= 2:  # skip the H1 document title
            out.append((len(m.group(1)), m.group(2).strip()))
    return out


def _skeleton_table_headers(markdown: str) -> list[list[str]]:
    """Return the column list of every markdown table header row in the body."""
    body = _strip_frontmatter(markdown)
    lines = body.splitlines()
    out: list[list[str]] = []
    for i, line in enumerate(lines):
        if not line.lstrip().startswith("|"):
            continue
        nxt = lines[i + 1] if i + 1 < len(lines) else ""
        # Header row is the one immediately followed by the |---|---| separator.
        if re.match(r"^\s*\|[\s:|-]+\|\s*$", nxt) and "-" in nxt:
            cols = [c.strip() for c in line.strip().strip("|").split("|")]
            out.append([c for c in cols])
    return out


def _split_sections(markdown: str, level: int = 2) -> dict:
    """Return {section_name: body_text} for headings at the given level."""
    body = _strip_frontmatter(markdown)
    sections: dict[str, str] = {}
    current: str | None = None
    buf: list[str] = []
    prefix = "#" * level + " "
    for line in body.splitlines():
        if line.startswith(prefix) and not line[level + 1 :].startswith("#"):
            if current is not None:
                sections[current] = "\n".join(buf).strip()
            current = line[len(prefix) :].strip()
            buf = []
        elif current is not None:
            buf.append(line)
    if current is not None:
        sections[current] = "\n".join(buf).strip()
    return sections


_PLACEHOLDER_TOKENS = ("TODO", "TBD", "{{", "}}", "placeholder", "none specified")


# ─── Unified shape (FR-002-AC-1 / AC-4) ──────────────────────────────────


@pytest.mark.parametrize("at", _artifact_types(), ids=lambda at: at["name"])
def test_fr002_ac1_unified_shape_no_retired_fields(at: dict) -> None:
    """FR-002-AC-1: every archetype declares ``body_extraction`` with asserts and
    declares none of ``template_ref`` / ``required_sections`` / ``variants``."""
    assert "template_ref" not in at, f"{at['name']} still declares template_ref"
    assert "required_sections" not in at, f"{at['name']} declares required_sections"
    assert "variants" not in at, f"{at['name']} still declares variants"
    be = at.get("body_extraction") or {}
    match = (be.get("yield_pattern") or {}).get("match") or {}
    assert match, f"{at['name']} has no body_extraction match locators"
    assert any(
        isinstance(loc, dict) and loc.get("assert") for loc in match.values()
    ), f"{at['name']} has no assert facets"


def test_fr002_ac1_no_template_dir_or_refs() -> None:
    """FR-002-AC-1: templates/ is removed and no archetype references one."""
    assert not (PKG_ROOT / "templates").exists(), "templates/ directory still present"
    raw = MANIFEST_PATH.read_text()
    assert "template_ref" not in raw, "manifest still mentions template_ref"
    assert ".md.j2" not in raw, "manifest still references a .md.j2 template"


@pytest.mark.parametrize("at", _artifact_types(), ids=lambda at: at["name"])
def test_fr002_ac4_headings_unique_per_level(at: dict) -> None:
    """FR-002-AC-4: declared section headings are unique per level."""
    seen: set[tuple[int, str]] = set()
    for sec in _required_sections(at):
        key = (sec["level"], sec["name"].lower())
        assert key not in seen, f"{at['name']} duplicate heading at level: {sec}"
        seen.add(key)


# ─── Skeleton presence (FR-002-AC-5 structural half) ─────────────────────


@pytest.mark.parametrize("name", sorted(_SKELETON_FILE), ids=lambda n: n)
def test_fr002_skeleton_exists_and_has_required_headings(name: str) -> None:
    """Each archetype ships an authoring skeleton carrying its required headings."""
    path = SKELETONS_DIR / f"{_SKELETON_FILE[name]}.md"
    assert path.exists(), f"missing skeleton {path}"
    text = path.read_text()
    at = next(a for a in _artifact_types() if a["name"] == name)
    for sec in _required_sections(at):
        heading = "#" * sec["level"] + " " + sec["name"]
        assert heading in text, f"{name} skeleton missing heading: {heading}"


# ─── I1: assert ↔ skeleton parity (FR-002-AC-6) ──────────────────────────


@pytest.mark.parametrize("name", sorted(_SKELETON_FILE), ids=lambda n: n)
def test_fr002_ac6_asserts_derived_from_skeleton(name: str) -> None:
    """FR-002-AC-6 (I1): the manifest asserts are consistent with / derived from
    the skeleton — every asserted heading exists in the skeleton at the asserted
    level, every asserted table's header row is present in the skeleton, and every
    asserted id_pattern matches the skeleton's seeded ids."""
    at = next(a for a in _artifact_types() if a["name"] == name)
    md = _skeleton_text(name)
    skel_headings = set(_skeleton_headings(md))
    skel_tables = _skeleton_table_headers(md)
    doc_id = _skeleton_doc_id(name)

    # 1. every asserted heading exists at the asserted level
    for sec in _required_sections(at):
        assert (sec["level"], sec["name"]) in skel_headings, (
            f"{name}: asserted heading {sec['name']!r} (H{sec['level']}) "
            f"absent from skeleton"
        )

    # 2. every asserted table header row appears verbatim in the skeleton
    for tbl in _asserted_tables(at):
        assert tbl["columns"] in skel_tables, (
            f"{name}: asserted table columns {tbl['columns']} "
            f"(section {tbl['section']}) not found in skeleton tables {skel_tables}"
        )

    # 3. every asserted id_pattern (after {id} interpolation) matches a seeded id
    seeded_ids = re.findall(rf"\|\s*({re.escape(doc_id)}-[A-Z]+-\d+)\s*\|", md)
    for pat in _asserted_id_patterns(at):
        rx = re.compile(pat.replace("{id}", re.escape(doc_id)))
        matching = [sid for sid in seeded_ids if rx.match(sid)]
        assert matching, (
            f"{name}: id_pattern {pat!r} matches none of the skeleton's "
            f"seeded ids {seeded_ids}"
        )


# ─── I2: literal consistency, both directions (FR-002-AC-7) ──────────────


@pytest.mark.parametrize("name", sorted(_SKELETON_FILE), ids=lambda n: n)
def test_fr002_ac7_literal_consistency_both_directions(name: str) -> None:
    """FR-002-AC-7 (I2): the skeleton's heading set and literal table header rows
    match the archetype's asserts exactly — a diff in either direction fails.

    Forward: skeleton ⊇ asserts (covered by AC-6). Reverse: every *asserted-level*
    skeleton heading and every skeleton table that carries an asserted column set
    must itself be asserted, so the skeleton can't drift ahead of the contract."""
    at = next(a for a in _artifact_types() if a["name"] == name)
    md = _skeleton_text(name)

    asserted_headings = {(s["level"], s["name"]) for s in _required_sections(at)}
    asserted_levels = {lvl for lvl, _ in asserted_headings}
    # Reverse-direction: any skeleton heading at an asserted level must be asserted.
    for lvl, text in _skeleton_headings(md):
        if lvl in asserted_levels:
            assert (lvl, text) in asserted_headings, (
                f"{name}: skeleton heading {text!r} (H{lvl}) is not asserted "
                f"by the manifest (skeleton drifted ahead of the contract)"
            )

    asserted_cols = [t["columns"] for t in _asserted_tables(at)]
    for cols in _skeleton_table_headers(md):
        assert cols in asserted_cols, (
            f"{name}: skeleton table {cols} has no matching manifest assert "
            f"(asserted column sets: {asserted_cols})"
        )


# ─── I3: locator-kind distinction + substantive bodies (FR-002-AC-8) ─────


@pytest.mark.parametrize("name", sorted(_SKELETON_FILE), ids=lambda n: n)
def test_fr002_ac8_locator_kinds_and_substantive_bodies(name: str) -> None:
    """FR-002-AC-8 (I3): heading-presence locators are distinguished from
    ``section_body`` locators; the skeleton supplies substantive (non-empty,
    non-placeholder) body for every ``section_body``-asserted section."""
    at = next(a for a in _artifact_types() if a["name"] == name)
    sections = _required_sections(at)
    kinds = {s["kind"] for s in sections}
    assert kinds, f"{name}: no required sections derived"
    assert kinds <= {"section_body", "heading"}, f"{name}: unexpected locator kinds"

    md = _skeleton_text(name)
    body_sections = _split_sections(md, level=2)
    for sec in sections:
        if sec["kind"] != "section_body" or sec["level"] != 2:
            continue
        name_ = sec["name"]
        assert name_ in body_sections, f"{name}: section_body {name_!r} missing"
        body = body_sections[name_]
        assert body, f"{name}: section_body {name_!r} is empty in skeleton"
        lowered = body.lower()
        for token in _PLACEHOLDER_TOKENS:
            assert token.lower() not in lowered, (
                f"{name}: section_body {name_!r} carries placeholder token "
                f"{token!r}"
            )
        if name_ == "Dependencies":
            up = re.search(r"\*\*Upstream\*\*:\s*(.+)", body)
            down = re.search(r"\*\*Downstream\*\*:\s*(.+)", body)
            up_v = up.group(1).strip().lower() if up else "none"
            down_v = down.group(1).strip().lower() if down else "none"
            assert not (
                up_v in ("none", "") and down_v in ("none", "")
            ), f"{name}: Dependencies only carries default 'none' values"


# ─── IT-002: validate / mutate / extract against the quire wheel ─────────


def _quire_doc_validator():
    """Return the quire wheel iff it exposes the FR-032 markdown validator."""
    try:
        import quire
    except ImportError:
        return None
    if not hasattr(quire, "validate_document"):
        return None
    return quire


@pytest.mark.parametrize("name", sorted(_SKELETON_FILE), ids=lambda n: n)
def test_it002_ac1_skeleton_validates(name: str) -> None:
    """IT-002-AC-1 / FR-002-AC-5: a filled skeleton passes validate_document.

    Skips when the installed quire wheel predates the markdown-default validator
    (FR-032); build/install a local quire-rs >=0.3.6 wheel to exercise it."""
    quire = _quire_doc_validator()
    if quire is None:
        pytest.skip("quire wheel lacks validate_document (FR-032)")
    text = _skeleton_text(name)
    res = quire.validate_document(name, str(PKG_ROOT), text)
    assert res["is_valid"], res["errors"]


def test_it002_ac2_fr_mutations_fail() -> None:
    """IT-002-AC-2: deleting a section, breaking AC columns, breaking an AC id,
    and duplicating a heading each fail validation with the expected reason."""
    quire = _quire_doc_validator()
    if quire is None:
        pytest.skip("quire wheel lacks validate_document (FR-032)")
    base = _skeleton_text("FR")
    root = str(PKG_ROOT)

    def reasons(doc: str) -> set[str]:
        res = quire.validate_document("FR", root, doc)
        assert not res["is_valid"], doc
        return {e["reason"] for e in res["errors"]}

    # a. delete the Acceptance Criteria section
    deleted = re.sub(
        r"## Acceptance Criteria.*?(?=\n## Dependencies)", "", base, flags=re.DOTALL
    )
    # Guard the mutation: a section-order change would make the lookahead a
    # no-op, leaving deleted == base and silently asserting on the unmutated doc.
    assert (
        "## Acceptance Criteria" not in deleted and deleted != base
    ), "AC-deletion mutation did not apply (section order changed?)"
    assert "missing" in reasons(deleted)
    # b. break an Acceptance-Criteria column header
    bad_cols = base.replace(
        "| ID | Criteria | Verification |", "| ID | Criterion | Verification |"
    )
    assert "assert" in reasons(bad_cols)
    # c. renumber an AC id to a non-matching prefix ({id} interpolation)
    bad_id = base.replace("| FR-001-AC-1 |", "| FR-999-AC-1 |")
    assert "assert" in reasons(bad_id)
    # d. duplicate a heading at the same level
    dup = base.replace(
        "## Dependencies", "## Description\n\nDuplicate.\n\n## Dependencies", 1
    )
    assert "duplicate-heading" in reasons(dup)


@pytest.mark.parametrize("name", sorted(_SKELETON_FILE), ids=lambda n: n)
def test_it002_ac3_extract_yields_record(name: str) -> None:
    """IT-002-AC-3: extract over the conformant skeleton yields a record whose
    fields match the archetype's body_extraction (validate + extract share one
    declaration)."""
    quire = _quire_doc_validator()
    if quire is None or not hasattr(quire, "extract"):
        pytest.skip("quire wheel lacks extract")
    text = _skeleton_text(name)
    out = quire.extract(name, str(PKG_ROOT), text)
    assert out["extraction"], out
