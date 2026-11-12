"""FR-008 criticality field: optional, enumerated, never defaulted.

Frontmatter acceptance runs through the `quire validate` binary against this
module; the TypeSpec projection and mapping are checked on the committed files.
"""

from __future__ import annotations

import json
import pathlib
import shutil
import subprocess

import pytest
from support import reference_mapping as rm

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
PKG_ROOT = REPO_ROOT / "spec_artifacts_iso"
SCHEMAS = PKG_ROOT / "schemas"

ARCHETYPES = ["FR", "NFR", "StR", "US"]
SKELETON = {"FR": "fr", "NFR": "nfr", "StR": "str", "US": "us"}
FRONTMATTER = {a: SCHEMAS / f"{SKELETON[a]}-frontmatter.schema.json" for a in ARCHETYPES}

needs_quire = pytest.mark.skipif(
    shutil.which("quire") is None, reason="quire CLI not installed"
)


def _doc(archetype: str, criticality_line: str | None) -> str:
    text = (PKG_ROOT / "skeletons" / f"{SKELETON[archetype]}.md").read_text(
        encoding="utf-8"
    )
    if criticality_line is None:
        return text
    marker = f"\ntype: {archetype}\n"
    assert marker in text
    return text.replace(marker, f"{marker}{criticality_line}\n", 1)


def _validate(tmp_path: pathlib.Path, text: str) -> subprocess.CompletedProcess:
    doc = tmp_path / "doc.md"
    doc.write_text(text, encoding="utf-8")
    return subprocess.run(
        ["quire", "validate", "--module", str(PKG_ROOT), str(doc)],
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.parametrize("archetype", ARCHETYPES)
def test_fr008_ac1_frontmatter_schema_declares_optional_inline_enum(
    archetype: str,
) -> None:
    """FR-008-AC-1"""
    schema = json.loads(FRONTMATTER[archetype].read_text(encoding="utf-8"))
    assert schema["properties"]["criticality"]["enum"] == ["low", "medium", "high"]
    assert "criticality" not in schema["required"]
    assert not list(SCHEMAS.glob("*[Cc]riticality*"))


@pytest.mark.parametrize("archetype", ARCHETYPES)
def test_fr008_ac3_projected_record_schema_carries_optional_criticality(
    archetype: str,
) -> None:
    """FR-008-AC-3"""
    schema = json.loads((SCHEMAS / f"{archetype}.json").read_text(encoding="utf-8"))
    prop = schema["properties"]["criticality"]
    assert [o["const"] for o in prop["anyOf"]] == ["low", "medium", "high"]
    assert "criticality" not in schema.get("required", [])


@needs_quire
@pytest.mark.parametrize("archetype", ARCHETYPES)
@pytest.mark.parametrize("value", ["low", "medium", "high"])
def test_fr008_ac2_each_enumerated_value_validates(
    archetype: str, value: str, tmp_path: pathlib.Path
) -> None:
    """FR-008-AC-2"""
    result = _validate(tmp_path, _doc(archetype, f"criticality: {value}"))
    assert result.returncode == 0, result.stderr


@needs_quire
@pytest.mark.parametrize("archetype", ARCHETYPES)
def test_fr008_ac4_omitted_criticality_validates_and_maps_to_no_value(
    archetype: str, tmp_path: pathlib.Path
) -> None:
    """FR-008-AC-4"""
    text = _doc(archetype, None)
    assert "criticality" not in text
    result = _validate(tmp_path, text)
    assert result.returncode == 0, result.stderr
    record = rm.map_bytes(
        text.encode("utf-8"), path="tests", declaration=rm.load_mappings()
    ).record
    assert "criticality" not in record


@pytest.mark.parametrize("archetype", ARCHETYPES)
def test_fr007_ac8_criticality_maps_into_the_record_as_written(
    archetype: str,
) -> None:
    """FR-007-AC-8"""
    text = _doc(archetype, "criticality: medium")
    record = rm.map_bytes(
        text.encode("utf-8"), path="tests", declaration=rm.load_mappings()
    ).record
    assert record["criticality"] == "medium"


@needs_quire
@pytest.mark.parametrize("archetype", ARCHETYPES)
@pytest.mark.parametrize(
    "line,ac",
    [
        ("criticality: critical", "FR-008-AC-5"),
        ("criticality: High", "FR-008-AC-6"),
        ('criticality: ""', "FR-008-AC-7"),
    ],
)
def test_fr008_invalid_values_fail_naming_the_field(
    archetype: str, line: str, ac: str, tmp_path: pathlib.Path
) -> None:
    """FR-008-AC-5, FR-008-AC-6, FR-008-AC-7 (value is neither normalised nor treated as absent)."""
    result = _validate(tmp_path, _doc(archetype, line))
    assert result.returncode != 0
    assert "criticality" in result.stderr


@pytest.mark.parametrize("archetype", ARCHETYPES)
def test_fr008_ac8_no_default_for_criticality(archetype: str) -> None:
    """FR-008-AC-8"""
    for path in (FRONTMATTER[archetype], SCHEMAS / f"{archetype}.json"):
        schema = json.loads(path.read_text(encoding="utf-8"))
        assert "default" not in schema["properties"]["criticality"]
