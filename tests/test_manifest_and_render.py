"""Auto-generated test: manifest validates against FR-035 + every template renders.

Pulls the FR-035 JSON Schema URL or uses a local copy bundled with the package.
"""

from __future__ import annotations

import json
import pathlib
import re

import pytest
import yaml
from jinja2 import StrictUndefined
from jinja2.sandbox import SandboxedEnvironment

PKG_ROOT = pathlib.Path(__file__).resolve().parent.parent / "spec_artifacts_iso"
MANIFEST_PATH = PKG_ROOT / "manifest.yaml"


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


def _render(template_text: str, ctx: dict) -> str:
    env = SandboxedEnvironment(keep_trailing_newline=True)
    return env.from_string(template_text).render(**ctx)


def _render_strict(template_text: str, ctx: dict) -> str:
    """Render the way quire does: undefined access is an error, not "".

    The default SandboxedEnvironment silently swallows undefined values, so it
    never catches templates that crash quire's strict-undefined engine on a
    missing optional field (e.g. `{% if relationships %}` with no relationships).
    """
    env = SandboxedEnvironment(keep_trailing_newline=True, undefined=StrictUndefined)
    return env.from_string(template_text).render(**ctx)


def _artifact_types():
    manifest = yaml.safe_load(MANIFEST_PATH.read_text())
    return manifest.get("artifact_types", [])


def _required_sections(at: dict, level: int | None = None) -> list[dict]:
    """Derive ``[{name, level}]`` from the unified-shape ``body_extraction``.

    FR-035 CR-002 retired ``required_sections``; structural completeness is
    now expressed by ``section_body`` locators that carry an ``assert.level``
    facet. This helper recovers the section list the render parity tests need.
    Pass ``level`` to restrict to a single heading level (e.g. the top-level
    content-quality checks only inspect ``level=2`` sections).
    """
    be = at.get("body_extraction") or {}
    match = (be.get("yield_pattern") or {}).get("match") or {}
    out: list[dict] = []
    for loc in match.values():
        if not isinstance(loc, dict) or loc.get("from") != "section_body":
            continue
        assert_facet = loc.get("assert") or {}
        sec_level = assert_facet.get("level", 2)
        if level is not None and sec_level != level:
            continue
        out.append({"name": loc["after_heading"], "level": sec_level})
    return out


def _fr_artifact_type() -> dict:
    for at in _artifact_types():
        if at["name"] == "FR":
            return at
    raise AssertionError("FR artifact type missing from manifest")


def _split_sections(markdown: str, level: int = 2) -> dict:
    """Return {section_name: body_text} for headings at the given level."""
    body = re.sub(r"^---\n.*?\n---\n", "", markdown, count=1, flags=re.DOTALL)
    sections: dict[str, str] = {}
    current: str | None = None
    buf: list[str] = []
    prefix = "#" * level + " "
    for line in body.splitlines():
        # A heading at exactly `level` opens a section; deeper headings stay in body.
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


def required_section_issues(markdown: str, required_sections: list[dict]) -> list[str]:
    """Flag required sections that are missing, empty, or placeholder/default-filled.

    Mirrors the specify workflow's validate stage: `quire validate` passing is
    necessary but not sufficient — required sections must carry substantive content.
    """
    sections = _split_sections(markdown, level=2)
    issues: list[str] = []
    for sec in required_sections:
        name = sec["name"]
        if name not in sections:
            issues.append(f"{name}: missing")
            continue
        body = sections[name]
        if not body:
            issues.append(f"{name}: empty")
            continue
        lowered = body.lower()
        for token in _PLACEHOLDER_TOKENS:
            if token.lower() in lowered:
                issues.append(f"{name}: contains placeholder token {token!r}")
                break
        else:
            # Dependencies default to `none` on both ends — treat as unfilled.
            if name == "Dependencies":
                up = re.search(r"\*\*Upstream\*\*:\s*(.+)", body)
                down = re.search(r"\*\*Downstream\*\*:\s*(.+)", body)
                up_v = up.group(1).strip().lower() if up else "none"
                down_v = down.group(1).strip().lower() if down else "none"
                if up_v in ("none", "") and down_v in ("none", ""):
                    issues.append(
                        "Dependencies: only default 'none' upstream/downstream"
                    )
    return issues


_HAPPY_FR_CTX = {
    "id": "FR-9002",
    "title": "Verify checksums on artifact import",
    "artifact_type": "FR",
    "object": "artifact-import",
    "relationships": [{"target": "ix://spec/usecase/US-001", "type": "implements"}],
    "description": (
        "The system SHALL verify the SHA-256 checksum of every imported artifact "
        "before persisting it, rejecting any artifact whose computed digest does "
        "not match the declared digest."
    ),
    "inputs": (
        "- Imported artifact bytes\n"
        "- Declared SHA-256 digest from the import manifest"
    ),
    "outputs": (
        "- Accepted artifact persisted to the store\n"
        "- Rejection error with the digest pair"
    ),
    "behavior": (
        "- The system SHALL compute the SHA-256 digest of the artifact bytes "
        "on import.\n"
        "- The system SHALL reject the artifact when the computed digest "
        "differs from the declared digest.\n"
        "- The system SHALL persist the artifact only after a successful "
        "digest match."
    ),
    "constraints": (
        "| ID | Constraint | Type | Validation |\n"
        "|----|------------|------|------------|\n"
        "| FR-9002-CON-1 | Digest computation SHALL use SHA-256 only "
        "| Security | Integration Test |"
    ),
    "acceptance_criteria": (
        "| ID | Criteria | Verification |\n"
        "|----|----------|--------------|\n"
        "| FR-9002-AC-1 | Given a matching digest, the artifact is persisted "
        "| Integration Test |\n"
        "| FR-9002-AC-2 | Given a mismatched digest, the import is rejected "
        "| Integration Test |"
    ),
    "upstream": "US-001 artifact import",
    "downstream": "IT-001 checksum rejection coverage",
}

_SPARSE_FR_CTX = {
    "id": "FR-9001",
    "title": "Underfilled FR",
    "artifact_type": "FR",
    "description": "The system SHALL do the thing.",
}


def test_fr_happy_context_has_no_placeholder_required_sections() -> None:
    """A full FR context renders every required section with substantive content.

    Fails against the pre-fix template, which hardcoded a TODO Acceptance
    Criteria table with no input variable, so even a perfect context produced
    placeholders.
    """
    at = _fr_artifact_type()
    template = (PKG_ROOT / at["template_ref"]).read_text()
    output = _render(template, _HAPPY_FR_CTX)
    issues = required_section_issues(output, _required_sections(at, level=2))
    assert issues == [], f"happy FR still has placeholder required sections: {issues}"


def test_fr_sparse_context_leaves_placeholder_required_sections() -> None:
    """A minimal FR context renders placeholder required sections and is rejected."""
    at = _fr_artifact_type()
    template = (PKG_ROOT / at["template_ref"]).read_text()
    output = _render(template, _SPARSE_FR_CTX)
    issues = required_section_issues(output, _required_sections(at, level=2))
    flagged = " ".join(issues)
    assert issues, "sparse FR unexpectedly passed required-section validation"
    assert "Acceptance Criteria" in flagged
    assert "Dependencies" in flagged


@pytest.mark.parametrize("at", _artifact_types(), ids=lambda at: at["name"])
def test_template_renders_under_strict_undefined_minimal_context(at: dict) -> None:
    """Every template must render under strict-undefined with ONLY the required
    fields — no relationships, object, or scope supplied.

    This mirrors quire's render engine. Guards against the regression where an
    unguarded `{% if relationships %}` (or `scope.applies_to` on an undefined
    `scope`) crashed every non-FR archetype while the non-strict suite stayed
    green.
    """
    template = (PKG_ROOT / at["template_ref"]).read_text()
    ctx = {
        "id": f"{at['name']}-001",
        "title": f"Sample {at['name']}",
        "artifact_type": at["name"],
        "description": "Render test.",
    }
    output = _render_strict(template, ctx)
    for sec in _required_sections(at):
        heading = "#" * sec["level"] + " " + sec["name"]
        assert heading in output, f"missing required section heading: {heading}"


@pytest.mark.parametrize("at", _artifact_types(), ids=lambda at: at["name"])
def test_template_renders_and_contains_required_sections(at: dict) -> None:
    template_path = PKG_ROOT / at["template_ref"]
    assert template_path.exists(), f"missing template {template_path}"
    ctx = {
        "id": f"{at['name']}-001",
        "title": f"Sample {at['name']}",
        "artifact_type": at["name"],
        "description": "Render test.",
        "relationships": [],
        "scope": {"applies_to": "test", "context": "rendering"},
    }
    output = _render(template_path.read_text(), ctx)
    # Frontmatter present and round-trips
    m = re.match(r"---\n(.*?)\n---\n", output, re.DOTALL)
    assert m, "rendered output missing frontmatter"
    fm = yaml.safe_load(m.group(1))
    assert fm["id"] == ctx["id"]
    assert fm["artifact_type"] == ctx["artifact_type"]
    # Required sections present
    for sec in _required_sections(at):
        heading = "#" * sec["level"] + " " + sec["name"]
        assert heading in output, f"missing required section heading: {heading}"


# ─── Unified-shape (FR-002 / FR-035 CR-002) ──────────────────────────────

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


@pytest.mark.parametrize("at", _artifact_types(), ids=lambda at: at["name"])
def test_fr002_ac1_unified_shape_no_retired_fields(at: dict) -> None:
    """FR-002-AC-1: every archetype declares body_extraction with asserts and
    declares neither required_sections nor variants."""
    assert "required_sections" not in at, f"{at['name']} declares required_sections"
    assert "variants" not in at, f"{at['name']} still declares variants"
    be = at.get("body_extraction") or {}
    match = (be.get("yield_pattern") or {}).get("match") or {}
    assert match, f"{at['name']} has no body_extraction match locators"
    assert any(
        isinstance(loc, dict) and loc.get("assert") for loc in match.values()
    ), f"{at['name']} has no assert facets"


@pytest.mark.parametrize("at", _artifact_types(), ids=lambda at: at["name"])
def test_fr002_ac4_headings_unique_per_level(at: dict) -> None:
    """FR-002-AC-4: declared section headings are unique per level."""
    seen: set[tuple[int, str]] = set()
    for sec in _required_sections(at):
        key = (sec["level"], sec["name"].lower())
        assert key not in seen, f"{at['name']} duplicate heading at level: {sec}"
        seen.add(key)


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

    Skips when the installed quire wheel predates the markdown-default
    validator (FR-032); the round-trip is verified out-of-band against a
    locally-built quire-rs wheel until that ships to the registry.
    """
    quire = _quire_doc_validator()
    if quire is None:
        pytest.skip("quire wheel lacks validate_document (FR-032)")
    text = (SKELETONS_DIR / f"{_SKELETON_FILE[name]}.md").read_text()
    res = quire.validate_document(name, str(PKG_ROOT), text)
    assert res["is_valid"], res["errors"]


def test_it002_ac2_fr_mutations_fail() -> None:
    """IT-002-AC-2: deleting a section, breaking AC columns, breaking an AC id,
    and duplicating a heading each fail validation with the expected reason."""
    quire = _quire_doc_validator()
    if quire is None:
        pytest.skip("quire wheel lacks validate_document (FR-032)")
    base = (SKELETONS_DIR / "fr.md").read_text()
    root = str(PKG_ROOT)

    def reasons(doc: str) -> set[str]:
        res = quire.validate_document("FR", root, doc)
        assert not res["is_valid"], doc
        return {e["reason"] for e in res["errors"]}

    # a. delete the Acceptance Criteria section
    deleted = re.sub(
        r"## Acceptance Criteria.*?(?=\n## Dependencies)", "", base, flags=re.DOTALL
    )
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
    text = (SKELETONS_DIR / f"{_SKELETON_FILE[name]}.md").read_text()
    out = quire.extract(name, str(PKG_ROOT), text)
    assert out["extraction"], out
