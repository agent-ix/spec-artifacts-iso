"""Auto-generated test: manifest validates against FR-035 + every template renders.

Pulls the FR-035 JSON Schema URL or uses a local copy bundled with the package.
"""

from __future__ import annotations

import json
import pathlib
import re

import pytest
import yaml
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


def _artifact_types():
    manifest = yaml.safe_load(MANIFEST_PATH.read_text())
    return manifest.get("artifact_types", [])


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
    issues = required_section_issues(output, at["required_sections"])
    assert issues == [], f"happy FR still has placeholder required sections: {issues}"


def test_fr_sparse_context_leaves_placeholder_required_sections() -> None:
    """A minimal FR context renders placeholder required sections and is rejected."""
    at = _fr_artifact_type()
    template = (PKG_ROOT / at["template_ref"]).read_text()
    output = _render(template, _SPARSE_FR_CTX)
    issues = required_section_issues(output, at["required_sections"])
    flagged = " ".join(issues)
    assert issues, "sparse FR unexpectedly passed required-section validation"
    assert "Acceptance Criteria" in flagged
    assert "Dependencies" in flagged


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
    for sec in at.get("required_sections", []):
        heading = "#" * sec["level"] + " " + sec["name"]
        assert heading in output, f"missing required section heading: {heading}"
