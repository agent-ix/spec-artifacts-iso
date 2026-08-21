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
from jsonschema import Draft202012Validator, ValidationError

from spec_artifacts_iso import module_manifest_schema

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
    "master-requirements": "spec",
    "index": "index",
    "log": "log",
}


def test_manifest_loads() -> None:
    manifest = yaml.safe_load(MANIFEST_PATH.read_text())
    assert manifest["manifest_version"] == "1.0.0"
    assert manifest["name"] == "spec-artifacts-iso"
    assert manifest["version"]


def test_manifest_validates_against_fr035_schema() -> None:
    """TC-001: FR-001-AC-1: the manifest validates against the FR-035 schema.

    FR-001 CR-002: neither the missing-library nor the missing-schema branch
    skips any more. A gate that reports "passed" because it could not run is
    the failure mode this whole ticket exists to close — ``jsonschema`` is a
    hard dev dependency and the schema is package data, so both absences are
    now errors that say which one happened.
    """
    schema = module_manifest_schema()
    manifest = yaml.safe_load(MANIFEST_PATH.read_text())
    errors = list(Draft202012Validator(schema).iter_errors(manifest))
    assert not errors, [
        f"{'.'.join(str(p) for p in e.absolute_path)}: {e.message}" for e in errors
    ]


def test_fr002_schema_rejects_template_ref_on_artifact_type() -> None:
    """TC-002: FR-002: the bundled FR-035 schema must REJECT ``template_ref`` on an
    ArtifactTypeEntry (render is gone; additionalProperties:false → error)."""
    schema = module_manifest_schema()
    manifest = yaml.safe_load(MANIFEST_PATH.read_text())
    artifact_types = manifest.get("artifact_types") or []
    assert artifact_types, "manifest declares no artifact_types to mutate"
    mutated = artifact_types[0] | {"template_ref": "fr.md.j2"}
    manifest = {**manifest, "artifact_types": [mutated, *artifact_types[1:]]}
    errors = list(Draft202012Validator(schema).iter_errors(manifest))
    assert any(
        "template_ref" in e.message for e in errors
    ), "schema accepted template_ref on an artifact type; it must be rejected"


def _artifact_types():
    manifest = yaml.safe_load(MANIFEST_PATH.read_text())
    return manifest.get("artifact_types", [])


# ─── FR-003: master-requirements archetype ───────────────────────────────


def test_fr003_ac1_master_requirements_archetype_registered() -> None:
    """TC-003: FR-003-AC-1: a ``master-requirements`` artifact_type is declared with a
    frontmatter_schema_ref and a body_extraction carrying assert facets."""
    at = next(
        (a for a in _artifact_types() if a["name"] == "master-requirements"), None
    )
    assert at is not None, "manifest declares no master-requirements artifact_type"
    assert at.get("frontmatter_schema_ref"), "master-requirements lacks a schema ref"
    match = ((at.get("body_extraction") or {}).get("yield_pattern") or {}).get(
        "match"
    ) or {}
    assert match, "master-requirements has no body_extraction match locators"
    assert any(
        isinstance(loc, dict) and loc.get("assert") for loc in match.values()
    ), "master-requirements has no assert facets"


def test_fr003_ac2_master_requirements_frontmatter_schema_shape() -> None:
    """TC-004: FR-003-AC-2: the master-requirements frontmatter schema
    requires type/name/org/component_type, does NOT require id/title, and
    constrains component_type to kebab-case ``^[a-z][a-z0-9-]*$``."""
    at = next(a for a in _artifact_types() if a["name"] == "master-requirements")
    schema_path = PKG_ROOT / at["frontmatter_schema_ref"]
    schema = json.loads(schema_path.read_text())
    required = set(schema.get("required", []))
    assert required == {"type", "name", "org", "component_type"}, required
    assert "id" not in required and "title" not in required
    props = schema["properties"]
    assert props["type"] == {"const": "master-requirements"}
    assert props["component_type"]["pattern"] == "^[a-z][a-z0-9-]*$"


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


def _skeleton_doc_id(name: str) -> str | None:
    """Return the skeleton's frontmatter ``id``, or ``None`` if it has none.

    The eight ISO artifact archetypes seed an ``id`` (used for ``{id}``-pattern
    parity); the ``master-requirements`` master spec has no ``id`` field, so this
    is optional and callers guard on it before use."""
    fm = re.match(r"---\n(.*?)\n---\n", _skeleton_text(name), re.DOTALL)
    assert fm, f"{name} skeleton missing frontmatter"
    return yaml.safe_load(fm.group(1)).get("id")


def _skeleton_headings(markdown: str) -> list[tuple[int, str]]:
    """Return ``[(level, text)]`` for every ATX heading, including the H1 title.

    The H1 is included so an archetype that asserts a literal H1 (e.g.
    ``master-requirements`` → ``# Master Requirements Specification``) is covered
    by the parity checks. Archetypes whose H1 carries a variable title (``[FR-001]
    …``) simply never assert level 1, so the reverse-parity check skips it."""
    body = _strip_frontmatter(markdown)
    out: list[tuple[int, str]] = []
    for line in body.splitlines():
        m = re.match(r"^(#{1,6})\s+(.*\S)\s*$", line)
        if m:
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
    """TC-005.

    FR-002-AC-1: every archetype declares ``body_extraction`` with asserts and
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
    """TC-006: FR-002-AC-1: templates/ is removed and no archetype references one."""
    assert not (PKG_ROOT / "templates").exists(), "templates/ directory still present"
    raw = MANIFEST_PATH.read_text()
    assert "template_ref" not in raw, "manifest still mentions template_ref"
    assert ".md.j2" not in raw, "manifest still references a .md.j2 template"


@pytest.mark.parametrize("at", _artifact_types(), ids=lambda at: at["name"])
def test_fr002_ac4_headings_unique_per_level(at: dict) -> None:
    """TC-007: FR-002-AC-4: declared section headings are unique per level."""
    seen: set[tuple[int, str]] = set()
    for sec in _required_sections(at):
        key = (sec["level"], sec["name"].lower())
        assert key not in seen, f"{at['name']} duplicate heading at level: {sec}"
        seen.add(key)


# ─── Skeleton presence (FR-002-AC-5 structural half) ─────────────────────


@pytest.mark.parametrize("name", sorted(_SKELETON_FILE), ids=lambda n: n)
def test_fr002_skeleton_exists_and_has_required_headings(name: str) -> None:
    """TC-008.

    Each archetype ships an authoring skeleton carrying its required headings."""
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
    """TC-009: FR-002-AC-6 (I1): the manifest asserts are consistent with / derived from
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

    # 3. every asserted id_pattern (after {id} interpolation) matches a seeded id.
    # The master-requirements archetype asserts no id_patterns and has no doc id.
    id_patterns = _asserted_id_patterns(at)
    if id_patterns:
        assert doc_id, (
            f"{name}: declares id_pattern asserts but the skeleton frontmatter "
            f"has no id to interpolate"
        )
        seeded_ids = re.findall(rf"\|\s*({re.escape(doc_id)}-[A-Z]+-\d+)\s*\|", md)
        for pat in id_patterns:
            rx = re.compile(pat.replace("{id}", re.escape(doc_id)))
            matching = [sid for sid in seeded_ids if rx.match(sid)]
            assert matching, (
                f"{name}: id_pattern {pat!r} matches none of the skeleton's "
                f"seeded ids {seeded_ids}"
            )


# ─── I2: literal consistency, both directions (FR-002-AC-7) ──────────────


@pytest.mark.parametrize("name", sorted(_SKELETON_FILE), ids=lambda n: n)
def test_fr002_ac7_literal_consistency_both_directions(name: str) -> None:
    """TC-010.

    FR-002-AC-7 (I2): the skeleton's heading set and literal table header rows
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
    """TC-011: FR-002-AC-8 (I3): heading-presence locators are distinguished from
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
    """Return the quire wheel iff it can load and validate against this module.

    Skips (returns ``None``) when the installed wheel lacks the FR-032 markdown
    validator OR is too old to parse the engine features this module now relies
    on. The ISO-standard manifest (2026-06-16) uses a ``section_body`` ``matches``
    assert (and a ``section_body_pattern`` lint rule); a wheel predating those
    fails manifest load and reports every archetype as ``unknown``. The local
    quire-cli binary is the validation authority for those features — these
    in-process IT-002 checks simply stand down rather than report a stale-wheel
    failure, mirroring the FR-032 skip intent."""
    try:
        import quire
    except ImportError:
        return None
    if not hasattr(quire, "validate_document"):
        return None
    # Probe that the wheel can actually load this module's manifest; an older
    # wheel rejects newer assert/lint keys with ``unknown archetype``.
    try:
        quire.validate_document("FR", str(PKG_ROOT), _skeleton_text("FR"))
    except Exception:
        return None
    return quire


@pytest.mark.parametrize("name", sorted(_SKELETON_FILE), ids=lambda n: n)
def test_it002_ac1_skeleton_validates(name: str) -> None:
    """TC-012: IT-002-AC-1 / FR-002-AC-5: a filled skeleton passes validate_document.

    Skips when the installed quire wheel predates the markdown-default validator
    (FR-032); build/install a local quire-rs >=0.3.6 wheel to exercise it."""
    quire = _quire_doc_validator()
    if quire is None:
        pytest.skip("quire wheel lacks validate_document (FR-032)")
    text = _skeleton_text(name)
    res = quire.validate_document(name, str(PKG_ROOT), text)
    assert res["is_valid"], res["errors"]


def test_it002_ac2_fr_mutations_fail() -> None:
    """TC-013: IT-002-AC-2: deleting a section, breaking AC columns, breaking an AC id,
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


def test_str_validation_criteria_table_is_binding() -> None:
    """TC-014: StR binding criteria are addressable rows under `## Validation Criteria`.

    The heading and the `Validation` column are deliberately NOT renamed to the
    FR spelling: ISO/IEC/IEEE 29148 validates a stakeholder requirement against
    the stakeholder's real need and verifies a system requirement against the
    spec. Only the table shape is unified (spec-artifacts-iso#9)."""
    quire = _quire_doc_validator()
    if quire is None:
        pytest.skip("quire wheel lacks validate_document (FR-032)")
    base = _skeleton_text("StR")
    root = str(PKG_ROOT)

    def reasons(doc: str) -> set[str]:
        res = quire.validate_document("StR", root, doc)
        assert not res["is_valid"], doc
        return {e["reason"] for e in res["errors"]}

    # a. the pre-change shape — a prose paragraph — no longer validates.
    prose = re.sub(
        r"\| ID \| Criteria \| Validation \|.*?(?=\n## )",
        "This need is satisfied when the digest is checked at import.\n",
        base,
        flags=re.DOTALL,
    )
    assert "| ID | Criteria | Validation |" not in prose and prose != base
    assert "missing" in reasons(prose)

    # b. the FR column spelling is rejected — the naming split is enforced,
    #    not merely documented.
    assert "assert" in reasons(
        base.replace(
            "| ID | Criteria | Validation |", "| ID | Criteria | Verification |"
        )
    )

    # c. the sub-id kind is `-VC-`, not `-AC-`.
    assert "assert" in reasons(base.replace("StR-001-VC-1", "StR-001-AC-1"))


def test_nfr_acceptance_criteria_is_absent_or_well_formed() -> None:
    """TC-015.

    NFR's AC section stays optional but takes the FR table shape when present.

    A *measurable* NFR's criteria are its `Metric | Target | Threshold | Method`
    rows and it omits the section; a *policy* NFR authors the table. What is no
    longer accepted is a present-but-unstructured section — the case a bare
    `required: false` on the table would have let through (spec-artifacts-iso#9)."""
    quire = _quire_doc_validator()
    if quire is None:
        pytest.skip("quire wheel lacks validate_document (FR-032)")
    base = _skeleton_text("NFR")
    root = str(PKG_ROOT)

    # a. omitting the section entirely is legitimate — the measurable case.
    without = re.sub(r"## Acceptance Criteria.*?(?=\n## )", "", base, flags=re.DOTALL)
    assert "## Acceptance Criteria" not in without and without != base
    assert quire.validate_document("NFR", root, without)["is_valid"]

    # b. present but unstructured is not.
    prose = re.sub(
        r"\| ID \| Criteria \| Verification \|.*?(?=\n## )",
        "Optional prose about policy NFRs.\n",
        base,
        flags=re.DOTALL,
    )
    assert prose != base
    res = quire.validate_document("NFR", root, prose)
    assert not res["is_valid"]
    assert "assert" in {e["reason"] for e in res["errors"]}

    # c. present and well-formed is.
    assert quire.validate_document("NFR", root, base)["is_valid"]


@pytest.mark.parametrize("name", sorted(_SKELETON_FILE), ids=lambda n: n)
def test_it002_ac3_extract_yields_record(name: str) -> None:
    """TC-016: IT-002-AC-3: extract over the conformant skeleton yields a record whose
    fields match the archetype's body_extraction (validate + extract share one
    declaration)."""
    quire = _quire_doc_validator()
    if quire is None or not hasattr(quire, "extract"):
        pytest.skip("quire wheel lacks extract")
    text = _skeleton_text(name)
    out = quire.extract(name, str(PKG_ROOT), text)
    assert out["extraction"], out


# ── FR-004: the edge-type and role vocabulary ────────────────────────────────
#
# The vocabulary is load-bearing module data — quire-rs FR-040 reads it to
# normalize `allowed_links`, FR-041 reads its inverses, and every
# `spec-objects-*` module writes its declarations in it — and until FR-004 no
# document in this repo described it. These tests are the contract.

_EDGE_CATEGORIES = {
    "structural",
    "behavioral",
    "dataflow",
    "dependency",
    "realization",
    "governance",
    "traceability",
}


def _edge_types() -> dict:
    manifest = yaml.safe_load(MANIFEST_PATH.read_text())
    return manifest.get("edge_types") or {}


def _roles() -> dict:
    manifest = yaml.safe_load(MANIFEST_PATH.read_text())
    return manifest.get("roles") or {}


def test_fr004_ac1_every_edge_type_has_a_description_and_known_category() -> None:
    """TC-017: (FR-004-AC-1).

    A verb with no description is a verb nobody can use correctly, and a
    category outside the declared seven is a typo that would silently create an
    eighth.
    """
    edges = _edge_types()
    assert edges, "the module declares an edge vocabulary"
    for verb, entry in edges.items():
        assert isinstance(entry, dict), f"{verb}: entry is a mapping"
        description = entry.get("description", "")
        assert description.strip(), f"{verb}: has a non-empty description"
        category = entry.get("category")
        assert category in _EDGE_CATEGORIES, (
            f"{verb}: category {category!r} is not one of the seven declared "
            f"categories {sorted(_EDGE_CATEGORIES)}"
        )


def test_fr004_ac2_shared_inverse_labels_are_the_recorded_set() -> None:
    """TC-018: (FR-004-AC-2).

    An inverse label declared by two forward verbs resolves first-wins with a
    diagnostic (quire-rs FR-041-AC-3), so which verb it normalizes onto depends
    on declaration order. That is designed. What is *not* designed is a new
    collision appearing silently and changing an existing normalization, so the
    current set is pinned here.
    """
    edges = _edge_types()
    by_label: dict[str, list[str]] = {}
    for verb, entry in edges.items():
        inverse = entry.get("inverse")
        if inverse is None:
            continue
        assert (
            isinstance(inverse, str) and inverse.strip()
        ), f"{verb}: inverse is a non-empty label"
        by_label.setdefault(inverse, []).append(verb)

    shared = {label: sorted(v) for label, v in by_label.items() if len(v) > 1}
    assert shared == {"part_of": ["aggregates", "contains"]}, (
        "a new shared inverse label changes which forward verb it normalizes "
        f"onto, first-wins and silently: {shared}"
    )


def test_fr004_ac3_inverse_labels_need_not_be_declared_verbs() -> None:
    """TC-019: (FR-004-AC-3).

    Deliberately the opposite of the invariant it is tempting to assert.
    quire-rs FR-041-AC-2 type-allows an edge whose verb is a declared inverse
    label "even when the label is absent from ``edge_types``" — so requiring
    every inverse to be independently declared would double the vocabulary with
    entries no author ever writes.

    The ratio is pinned rather than the rule inverted: a drift toward declaring
    inverses as verbs is a real change of approach and should be deliberate.
    """
    edges = _edge_types()
    inverses = {e["inverse"] for e in edges.values() if e.get("inverse")}
    also_forward = sorted(inverses & set(edges))
    derived_only = sorted(inverses - set(edges))

    assert also_forward == ["contains"], (
        "labels that are also forward verbs (forward registration governs, "
        f"FR-041-AC-3): {also_forward}"
    )
    assert (
        len(derived_only) == 25
    ), f"derived-only inverse labels: {len(derived_only)} — {derived_only}"


def test_fr004_ac4_every_role_has_a_description() -> None:
    """TC-020: (FR-004-AC-4)."""
    roles = _roles()
    assert roles, "the module declares a role registry"
    for role, entry in roles.items():
        assert isinstance(entry, dict), f"{role}: entry is a mapping"
        assert entry.get("description", "").strip(), f"{role}: has a description"


def test_fr004_ac5_vocabulary_validates_under_the_module_manifest_schema() -> None:
    """TC-021: (FR-004-AC-5).

    The FR-035 gate covers the whole manifest; this asserts the vocabulary is
    *present* when it passes, so a future edit that drops `edge_types` entirely
    cannot slip through a green schema run.
    """
    manifest = yaml.safe_load(MANIFEST_PATH.read_text())
    Draft202012Validator(module_manifest_schema()).validate(manifest)
    assert manifest.get("edge_types"), "edge_types survives schema validation"
    assert manifest.get("roles"), "roles survives schema validation"


def _relation(**over: object) -> dict:
    """A well-formed RequiredRelation, overridable field by field."""
    base = {
        "name": "hazard-has-mitigation",
        "from": "hazard",
        "edges": ["mitigates"],
        "to": ["FR"],
        "direction": "incoming",
        "check": "unmitigated-hazard",
    }
    base.update(over)
    return base


def _with_traceability(model: dict) -> dict:
    """The smallest manifest this schema accepts, carrying `model`."""
    return {
        "manifest_version": "1.0.0",
        "name": "probe",
        "version": "0.1.0",
        "traceability": model,
    }


def test_tc_schema_014_required_relations_is_accepted() -> None:
    """TC-022: FR-001 CR-005: a well-formed `required_relations` and
    `acyclic_edges` declaration validates.

    Assumptions: the shipped schema is the one quire-rs FR-058 reads against.
    Criteria: the exact shape `spec-objects-security#5` needs to declare —
    an incoming `mitigates` obligation on `hazard` — is accepted. Before
    CR-005 this failed with ``Additional properties are not allowed
    ('required_relations' was unexpected)``, which is what blocked the module
    from declaring bidirectional hazard coverage at all.
    """
    Draft202012Validator(module_manifest_schema()).validate(
        _with_traceability(
            {"required_relations": [_relation()], "acyclic_edges": ["arises_from"]}
        )
    )


@pytest.mark.parametrize(
    ("label", "relation"),
    [
        ("no accepted verb", _relation(edges=[])),
        ("colon in check token", _relation(check="trace:orphan")),
        ("whitespace in check token", _relation(check="orphan fr")),
        ("empty check token", _relation(check="")),
        ("unknown direction", _relation(direction="sideways")),
        ("empty from", _relation(**{"from": ""})),
        ("unknown key", {**_relation(), "severity": "error"}),
        ("missing check", {k: v for k, v in _relation().items() if k != "check"}),
    ],
    ids=lambda v: v if isinstance(v, str) else "",
)
def test_tc_schema_015_unexecutable_relations_are_rejected(
    label: str, relation: dict
) -> None:
    """TC-023: FR-001 CR-005: a declaration that cannot be executed is
    rejected by the schema, not discovered as a corpus-wide false alarm.

    Assumptions: `check` becomes the `<check>` half of a `trace:<check>`
    severity key (quire-rs FR-057).
    Criteria: each shape above fails validation. The first is the one that
    motivates the strictness — `edges: []` accepts no verb, so nothing can
    satisfy the relation and EVERY `hazard` document is reported. That is not
    a silent no-op, it is a loud wrong answer, and it looks exactly like a
    corpus-wide defect.
    """
    validator = Draft202012Validator(module_manifest_schema())
    with pytest.raises(ValidationError):
        validator.validate(_with_traceability({"required_relations": [relation]}))


def test_tc_schema_016_empty_to_means_any_target() -> None:
    """TC-024: FR-001 CR-005: `to` is the one field where empty carries
    meaning rather than being a defect.

    Assumptions: quire-rs reads an empty/absent `to` as "any document in the
    bundle".
    Criteria: both the empty list and the absent key validate, so a module
    constraining the verb but not the target can say so. A blank *entry*
    inside the list is still rejected — that is a typo, not a position.
    """
    validator = Draft202012Validator(module_manifest_schema())
    validator.validate(_with_traceability({"required_relations": [_relation(to=[])]}))
    without = {k: v for k, v in _relation().items() if k != "to"}
    validator.validate(_with_traceability({"required_relations": [without]}))
    with pytest.raises(ValidationError):
        validator.validate(
            _with_traceability({"required_relations": [_relation(to=[""])]})
        )


def test_tc_schema_017_blank_acyclic_verb_is_rejected() -> None:
    """TC-025: FR-001 CR-005: a blank verb in `acyclic_edges` is rejected.

    Assumptions: the cycle check walks the graph of edges matching each verb.
    Criteria: the empty string fails. It would match no edge, so the check
    would cover nothing while the declaration read as present — the same
    quiet-wrong-answer failure mode `edges: []` has.
    """
    validator = Draft202012Validator(module_manifest_schema())
    validator.validate(_with_traceability({"acyclic_edges": ["derives_from"]}))
    with pytest.raises(ValidationError):
        validator.validate(_with_traceability({"acyclic_edges": [""]}))


def _coverage(**over: object) -> dict:
    """A well-formed VocabularyCoverage, overridable field by field."""
    base = {
        "name": "quality-characteristics",
        "from": "NFR",
        "field": "quality_attribute",
        "check": "unowned-quality-characteristic",
    }
    base.update(over)
    return base


def test_tc_schema_018_vocabulary_coverage_is_accepted() -> None:
    """TC-026: FR-001 CR-007: a well-formed declaration validates.

    Assumptions: quire-rs FR-059 reads this shape.
    Criteria: the exact declaration the 25010 characteristic check needs is
    accepted, including the optional justified-absence field.
    """
    validator = Draft202012Validator(module_manifest_schema())
    validator.validate(_with_traceability({"vocabulary_coverage": [_coverage()]}))
    validator.validate(
        _with_traceability(
            {
                "vocabulary_coverage": [
                    _coverage(
                        justified_absence_field="quality_attributes_not_applicable"
                    )
                ]
            }
        )
    )


def test_tc_schema_019_the_schema_declares_no_values_key() -> None:
    """TC-027: FR-001 CR-007: the vocabulary cannot be restated here.

    Assumptions: the vocabulary is read from the projected archetype's own
    frontmatter-schema ``enum`` (quire-rs FR-059-AC-2).
    Criteria: ``VocabularyCoverage`` has no ``values`` property and rejects
    one. This is the whole point of the design — quire-rs#162 was filed
    against a scope proposing a hardcoded list, and a second list in the
    manifest would be free to drift from the schema that already declares it
    (the defect quire-rs CR-015 closed). A schema that merely *ignored*
    ``values`` would let a module write one and silently have it mean nothing.
    """
    schema = module_manifest_schema()
    definition = schema["$defs"]["VocabularyCoverage"]
    assert "values" not in definition["properties"]
    assert definition["additionalProperties"] is False

    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate(
            _with_traceability(
                {"vocabulary_coverage": [_coverage(values=["reliability", "security"])]}
            )
        )


@pytest.mark.parametrize(
    ("label", "coverage"),
    [
        ("colon in check token", _coverage(check="trace:unowned")),
        ("whitespace in check token", _coverage(check="unowned characteristic")),
        ("empty field", _coverage(field="")),
        ("empty from", _coverage(**{"from": ""})),
        ("missing check", {k: v for k, v in _coverage().items() if k != "check"}),
        ("missing field", {k: v for k, v in _coverage().items() if k != "field"}),
    ],
    ids=lambda v: v if isinstance(v, str) else "",
)
def test_tc_schema_020_malformed_coverage_is_rejected(
    label: str, coverage: dict
) -> None:
    """TC-028: FR-001 CR-007: a declaration that cannot run is rejected.

    Assumptions: ``check`` becomes the ``<check>`` half of a ``trace:<check>``
    severity key.
    Criteria: each shape fails. A check token carrying a colon or whitespace
    leaves a check whose severity no ``--severity`` flag and no module override
    can ever name.
    """
    with pytest.raises(ValidationError):
        Draft202012Validator(module_manifest_schema()).validate(
            _with_traceability({"vocabulary_coverage": [coverage]})
        )


def _obligation_source(**over: object) -> dict:
    """The smallest `ObligationSource` this schema accepts."""
    base: dict = {"name": "configuration-matrix", "statement_column": "Dimension"}
    base.update(over)
    return base


def _combinatorial(**over: object) -> dict:
    base: dict = {
        "dimension_column": "Dimension",
        "values_column": "Values",
        "strength": 2,
    }
    base.update(over)
    return base


def test_tc_schema_021_combinatorial_source_is_accepted() -> None:
    """TC-029: FR-001 CR-008: a well-formed declaration validates.

    Assumptions: quire-rs FR-061 reads this shape and mints ONE obligation for
    the whole table rather than one per row.
    Criteria: the declaration a configuration-dimensions table needs is
    accepted, with and without the optional exclusions column.
    """
    validator = Draft202012Validator(module_manifest_schema())
    validator.validate(
        _with_traceability(
            {"obligations": [_obligation_source(combinatorial=_combinatorial())]}
        )
    )
    validator.validate(
        _with_traceability(
            {
                "obligations": [
                    _obligation_source(
                        combinatorial=_combinatorial(excludes_column="Excludes")
                    )
                ]
            }
        )
    )


def test_tc_schema_022_zero_strength_is_rejected() -> None:
    """TC-030: FR-001 CR-008: `strength: 0` cannot be declared.

    Assumptions: quire-rs `ConfigurationSpace::tuples` returns 0 for a strength
    of 0.
    Criteria: a 0-way obligation demands nothing. Accepting it here would let a
    module declare a check that reads as present and covers nothing, which is
    the shape this whole program exists to catch — so it is rejected at the
    schema rather than left to produce an empty target at runtime.
    """
    with pytest.raises(ValidationError):
        Draft202012Validator(module_manifest_schema()).validate(
            _with_traceability(
                {
                    "obligations": [
                        _obligation_source(combinatorial=_combinatorial(strength=0))
                    ]
                }
            )
        )


@pytest.mark.parametrize(
    ("label", "combinatorial"),
    [
        ("missing dimension_column", {"values_column": "Values", "strength": 2}),
        ("missing values_column", {"dimension_column": "Dimension", "strength": 2}),
        ("missing strength", {"dimension_column": "D", "values_column": "V"}),
        ("empty dimension_column", _combinatorial(dimension_column="")),
        ("empty values_column", _combinatorial(values_column="")),
        ("unknown key", _combinatorial(dimensions_column="D")),
    ],
    ids=lambda v: v if isinstance(v, str) else "",
)
def test_tc_schema_023_malformed_combinatorial_is_rejected(
    label: str, combinatorial: dict
) -> None:
    """TC-031: FR-001 CR-008: a malformed declaration fails at load.

    Assumptions: `CombinatorialColumns` is `additionalProperties: false`, and
    quire-rs `deny_unknown_fields` would reject the same input.
    Criteria: every way of getting the declaration wrong is a load error, not a
    silently ignored line. `dimensions_column` is included because a plural
    typo reads correctly and would mint nothing.
    """
    with pytest.raises(ValidationError):
        Draft202012Validator(module_manifest_schema()).validate(
            _with_traceability(
                {"obligations": [_obligation_source(combinatorial=combinatorial)]}
            )
        )


def _marker(**over: object) -> dict:
    base: dict = {
        "name": "rust-implements-attr",
        "language": "rust",
        "pattern": r'#\[implements\("([^"]+)"\)\]',
    }
    base.update(over)
    return base


def test_tc_schema_024_implements_marker_forms_are_accepted() -> None:
    """TC-032: FR-001 CR-009: a well-formed declaration validates.

    Assumptions: quire-rs FR-062 reads this shape.
    Criteria: `trace_tags.implements` takes the same `TraceMarkerForm` shape as
    `markers`, with and without the optional `template`.
    """
    validator = Draft202012Validator(module_manifest_schema())
    validator.validate(_with_traceability({"trace_tags": {"implements": [_marker()]}}))
    validator.validate(
        _with_traceability(
            {
                "trace_tags": {
                    "markers": [_marker(name="rust-trace-attr")],
                    "implements": [_marker(template='#[implements("{ids}")]')],
                }
            }
        )
    )


def test_tc_schema_025_implements_is_a_separate_list() -> None:
    """TC-033: FR-001 CR-009: scope and evidence cannot be one list.

    Assumptions: quire-rs CR-061 stopped `verifies` binding production symbols
    because a doc comment citing a criterion would otherwise count as evidence.
    Criteria: `implements` is its own key, not a flag on a `markers` entry. A
    module cannot express the relation by decorating a `markers` entry —
    `TraceMarkerForm` is `additionalProperties: false`, so the discriminator
    that would put one typo between scope and evidence is rejected outright.
    """
    schema = module_manifest_schema()
    grammar = schema["$defs"]["TraceTagGrammar"]
    assert "implements" in grammar["properties"]
    assert grammar["additionalProperties"] is False

    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate(
            _with_traceability({"trace_tags": {"markers": [_marker(implements=True)]}})
        )


@pytest.mark.parametrize(
    ("label", "marker"),
    [
        ("missing name", {k: v for k, v in _marker().items() if k != "name"}),
        ("missing pattern", {k: v for k, v in _marker().items() if k != "pattern"}),
        ("missing language", {k: v for k, v in _marker().items() if k != "language"}),
        ("unknown language", _marker(language="cobol")),
        ("unknown key", _marker(kind="production")),
    ],
    ids=lambda v: v if isinstance(v, str) else "",
)
def test_tc_schema_026_malformed_implements_marker_is_rejected(
    label: str, marker: dict
) -> None:
    """TC-034: FR-001 CR-009: a malformed form fails at load.

    Criteria: the same rejections `markers` gets, because it is the same
    definition. An unknown key matters most — a marker that reads correctly and
    binds nothing is the shape this program keeps finding.
    """
    with pytest.raises(ValidationError):
        Draft202012Validator(module_manifest_schema()).validate(
            _with_traceability({"trace_tags": {"implements": [marker]}})
        )


def test_tc_schema_027_source_exclude_is_accepted() -> None:
    """TC-035: FR-001 CR-010: `traceability.source_exclude` validates.

    Assumptions: quire-rs FR-050-AC-22 (CR-085) reads this key. Without it here,
    `additionalProperties: false` rejects the manifest before the engine ever
    sees it — the gate that has now caught four keys the engine accepts and this
    contract had never heard of.
    Criteria: a list of non-empty glob strings is accepted; an empty string and a
    non-array are rejected.
    """
    validator = Draft202012Validator(module_manifest_schema())
    validator.validate(
        _with_traceability({"source_exclude": ["tests/fixtures/**", "fixtures/**"]})
    )
    # An empty list is a module that declares the key and excludes nothing.
    validator.validate(_with_traceability({"source_exclude": []}))

    with pytest.raises(ValidationError):
        validator.validate(_with_traceability({"source_exclude": [""]}))
    with pytest.raises(ValidationError):
        validator.validate(_with_traceability({"source_exclude": "tests/fixtures/**"}))


def test_tc_schema_028_source_exclude_is_not_exclude() -> None:
    """TC-036: FR-001 CR-010: the two exclusion keys stay distinct.

    Assumptions: `exclude` scopes documents, `source_exclude` scopes the source
    walk, and quire-rs merges them separately.
    Criteria: declaring both is legal and neither is an alias for the other — a
    module can exclude a document tree without excluding a source tree.
    """
    validator = Draft202012Validator(module_manifest_schema())
    validator.validate(
        _with_traceability(
            {
                "exclude": ["spec/fixtures/**"],
                "source_exclude": ["tests/fixtures/**"],
            }
        )
    )


def test_tc_schema_029_anchored_source_exclude_globs_stay_legal() -> None:
    """TC-037: FR-001 CR-011: the globs modules actually declare stay legal.

    Assumptions: `spec-artifacts-process` is the reference declarer — its
    manifest ships exactly the first three globs below, and its companion
    contract test (spec-artifacts-process#56) pins the same list.
    Criteria: the value constraints reject evidence-deleting patterns without
    touching the anchored fixture-directory form the CR-010 description tells
    every module to write. `tests/fixtures/**` is the load-bearing case: it
    starts with `tests/` yet is the RECOMMENDED spelling, so the mechanical
    rule must be narrower than a blanket `tests/` prefix ban. A literal
    segment re-anchors at ANY depth: `tests/**/fixtures/**` subtracts only
    fixture directories and stays legal too (SR-002 FND-001, the case the
    pre-fix `^tests(/([*?].*)?)?$` regex over-rejected).
    """
    Draft202012Validator(module_manifest_schema()).validate(
        _with_traceability(
            {
                "source_exclude": [
                    "tests/fixtures/**",
                    "tests_integration/fixtures/**",
                    "fixtures/**",
                    "tests/**/fixtures/**",
                ]
            }
        )
    )


@pytest.mark.parametrize(
    ("label", "pattern"),
    [
        ("bare **", "**"),
        ("tests/**", "tests/**"),
        ("leading wildcard", "*/fixtures/**"),
        ("bare tests", "tests"),
        ("bare tests slash", "tests/"),
        ("wildcard tail", "tests/**/*.py"),
        ("mixed-wildcard segment", "tests/x*"),
        ("wildcard in every segment", "tests/f*/**"),
        ("empty segment", "tests//**"),
    ],
    ids=lambda v: v if isinstance(v, str) else "",
)
def test_tc_schema_030_evidence_deleting_source_exclude_is_rejected(
    label: str, pattern: str
) -> None:
    """TC-038: FR-001 CR-011: an evidence-deleting glob fails at load.

    Assumptions: excluded files' trace tags never bind, so their matrix rows
    read as unbacked — indistinguishable from missing tests. globset compiles
    with ``literal_separator=false``, so an unanchored `*/fixtures/**` matches
    at ANY depth, not one level down.
    Criteria: a bare `**` (excludes everything), a pattern opening with a
    wildcard (unanchored), and any form naming the `tests` tree with no
    literal anchor after it — every later segment empty or wildcard-carrying,
    the semantics the spec-artifacts-process contract test pins — are each
    schema errors rather than prose violations. Before CR-011 every case here
    validated cleanly; `tests/x*`, `tests/f*/**` and `tests//**` still did
    until the SR-002 FND-001 regex fix.
    """
    with pytest.raises(ValidationError):
        Draft202012Validator(module_manifest_schema()).validate(
            _with_traceability({"source_exclude": [pattern]})
        )
