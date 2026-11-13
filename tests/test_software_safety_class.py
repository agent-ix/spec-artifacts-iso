"""The software safety class fields: optional, ordered, human-assigned, never defaulted.

Frontmatter acceptance runs through the `quire validate` binary against this
module; the TypeSpec projection and mapping are checked on the committed files.
The `traceability.carried_fields` entry (FR-009-AC-14) is read by the engine;
its coverage row loads this module beside spec-artifacts-process, which declares
the trace targets that mint the matrix rows (installed filament modules,
`IX_FILAMENT_MODULES_PATH`, default `~/.ix/filament/modules`).
"""

from __future__ import annotations

import json
import os
import pathlib
import shutil
import subprocess

import pytest
import yaml
from support import reference_mapping as rm

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
PKG_ROOT = REPO_ROOT / "spec_artifacts_iso"
SCHEMAS = PKG_ROOT / "schemas"

ARCHETYPES = ["FR", "NFR", "StR", "US"]
SKELETON = {"FR": "fr", "NFR": "nfr", "StR": "str", "US": "us"}
FRONTMATTER = {
    a: SCHEMAS / f"{SKELETON[a]}-frontmatter.schema.json" for a in ARCHETYPES
}
CLASSES = ["class-1", "class-2", "class-3"]
KEYS = [
    "software_safety_class",
    "software_safety_class_assigned_by",
    "software_safety_class_rationale",
]
RECORD_KEYS = [
    "softwareSafetyClass",
    "softwareSafetyClassAssignedBy",
    "softwareSafetyClassRationale",
]

needs_quire = pytest.mark.skipif(
    shutil.which("quire") is None, reason="quire CLI not installed"
)


def _doc(archetype: str, lines: list[str]) -> str:
    text = (PKG_ROOT / "skeletons" / f"{SKELETON[archetype]}.md").read_text(
        encoding="utf-8"
    )
    if not lines:
        return text
    marker = f"\ntype: {archetype}\n"
    assert marker in text
    return text.replace(marker, f"{marker}{chr(10).join(lines)}\n", 1)


def _full(value: str) -> list[str]:
    return [
        f"software_safety_class: {value}",
        "software_safety_class_assigned_by: Ada Example",
        "software_safety_class_rationale: Failure can injure the operator.",
    ]


def _validate(tmp_path: pathlib.Path, text: str) -> subprocess.CompletedProcess:
    doc = tmp_path / "doc.md"
    doc.write_text(text, encoding="utf-8")
    return subprocess.run(
        ["quire", "validate", "--module", str(PKG_ROOT), str(doc)],
        capture_output=True,
        text=True,
        check=False,
    )


def _record(text: str) -> dict:
    return rm.map_bytes(
        text.encode("utf-8"), path="tests", declaration=rm.load_mappings()
    ).record


@pytest.mark.trace("TC-071", "FR-009-AC-1")
@pytest.mark.parametrize("archetype", ARCHETYPES)
def test_fr009_ac1_frontmatter_schema_declares_optional_inline_enum(
    archetype: str,
) -> None:
    schema = json.loads(FRONTMATTER[archetype].read_text(encoding="utf-8"))
    props = schema["properties"]
    assert props["software_safety_class"]["enum"] == CLASSES
    for key in KEYS[1:]:
        assert props[key]["type"] == "string"
        assert props[key]["minLength"] == 1
    for key in KEYS:
        assert key not in schema["required"]
    assert not list(SCHEMAS.glob("*[Ss]afety*"))


@pytest.mark.trace("TC-071", "FR-009-AC-3")
@pytest.mark.parametrize("archetype", ARCHETYPES)
def test_fr009_ac3_projected_record_schema_carries_optional_class(
    archetype: str,
) -> None:
    schema = json.loads((SCHEMAS / f"{archetype}.json").read_text(encoding="utf-8"))
    prop = schema["properties"]["softwareSafetyClass"]
    assert [o["const"] for o in prop["anyOf"]] == CLASSES
    frontmatter = json.loads(FRONTMATTER[archetype].read_text(encoding="utf-8"))
    assert frontmatter["properties"]["software_safety_class"]["enum"] == [
        o["const"] for o in prop["anyOf"]
    ]
    for key in RECORD_KEYS:
        assert key in schema["properties"]
        assert key not in schema.get("required", [])


@pytest.mark.trace("TC-071", "FR-009-AC-8")
@pytest.mark.parametrize("archetype", ARCHETYPES)
def test_fr009_ac8_no_default_in_any_schema(archetype: str) -> None:
    for path, keys in (
        (FRONTMATTER[archetype], KEYS),
        (SCHEMAS / f"{archetype}.json", RECORD_KEYS),
    ):
        schema = json.loads(path.read_text(encoding="utf-8"))
        for key in keys:
            assert "default" not in schema["properties"][key]


@pytest.mark.trace("TC-072", "FR-009-AC-2")
@needs_quire
@pytest.mark.parametrize("archetype", ARCHETYPES)
@pytest.mark.parametrize("value", CLASSES)
def test_fr009_ac2_each_class_with_assigner_and_rationale_validates(
    archetype: str, value: str, tmp_path: pathlib.Path
) -> None:
    result = _validate(tmp_path, _doc(archetype, _full(value)))
    assert result.returncode == 0, result.stderr


@pytest.mark.trace("TC-072", "FR-009-AC-4")
@needs_quire
@pytest.mark.parametrize("archetype", ARCHETYPES)
def test_fr009_ac4_omitted_class_validates_and_maps_to_no_value(
    archetype: str, tmp_path: pathlib.Path
) -> None:
    text = _doc(archetype, [])
    assert "software_safety_class" not in text
    result = _validate(tmp_path, text)
    assert result.returncode == 0, result.stderr
    record = _record(text)
    for key in RECORD_KEYS:
        assert key not in record


@pytest.mark.trace("TC-074", "FR-009-AC-9")
@pytest.mark.parametrize("archetype", ARCHETYPES)
def test_fr009_ac9_class_maps_into_the_record_as_written(archetype: str) -> None:
    record = _record(_doc(archetype, _full("class-2")))
    assert record["softwareSafetyClass"] == "class-2"
    assert record["softwareSafetyClassAssignedBy"] == "Ada Example"
    assert record["softwareSafetyClassRationale"] == (
        "Failure can injure the operator."
    )


@pytest.mark.trace("TC-073", "FR-009-AC-5", "FR-009-AC-6", "FR-009-AC-7")
@needs_quire
@pytest.mark.parametrize("archetype", ARCHETYPES)
@pytest.mark.parametrize("value", ["class-9", "Class-1", '""'])
def test_fr009_invalid_class_values_fail_naming_the_field(
    archetype: str, value: str, tmp_path: pathlib.Path
) -> None:
    result = _validate(tmp_path, _doc(archetype, _full(value)))
    assert result.returncode != 0
    assert "software_safety_class" in result.stderr


@pytest.mark.trace("TC-075", "FR-009-AC-10")
@needs_quire
@pytest.mark.parametrize("archetype", ARCHETYPES)
@pytest.mark.parametrize("criticality,value", [("high", "class-1"), ("low", "class-3")])
def test_fr009_ac10_class_is_independent_of_criticality(
    archetype: str, criticality: str, value: str, tmp_path: pathlib.Path
) -> None:
    lines = [f"criticality: {criticality}", *_full(value)]
    result = _validate(tmp_path, _doc(archetype, lines))
    assert result.returncode == 0, result.stderr


@pytest.mark.trace("TC-076", "FR-009-AC-13")
@needs_quire
@pytest.mark.parametrize("archetype", ARCHETYPES)
@pytest.mark.parametrize(
    "lines,named",
    [
        (
            [
                "software_safety_class: class-1",
                "software_safety_class_assigned_by: Ada Example",
            ],
            "software_safety_class_rationale",
        ),
        (
            [
                "software_safety_class: class-1",
                "software_safety_class_rationale: A reason.",
            ],
            "software_safety_class_assigned_by",
        ),
        (
            [
                "software_safety_class: class-1",
                'software_safety_class_assigned_by: ""',
                "software_safety_class_rationale: A reason.",
            ],
            "software_safety_class_assigned_by",
        ),
        (
            [
                "software_safety_class: class-1",
                "software_safety_class_assigned_by: Ada Example",
                'software_safety_class_rationale: ""',
            ],
            "software_safety_class_rationale",
        ),
        (
            [
                "software_safety_class_assigned_by: Ada Example",
                "software_safety_class_rationale: A reason.",
            ],
            "software_safety_class",
        ),
    ],
)
def test_fr009_ac13_assigned_class_needs_assigner_and_rationale(
    archetype: str, lines: list[str], named: str, tmp_path: pathlib.Path
) -> None:
    result = _validate(tmp_path, _doc(archetype, lines))
    assert result.returncode != 0
    assert named in result.stderr


@pytest.mark.trace("TC-077", "FR-009-AC-12")
@pytest.mark.parametrize("archetype", ARCHETYPES)
def test_fr009_skeletons_carry_none_of_the_fields(archetype: str) -> None:
    text = (PKG_ROOT / "skeletons" / f"{SKELETON[archetype]}.md").read_text(
        encoding="utf-8"
    )
    assert "software_safety_class" not in text


@pytest.mark.trace("TC-077", "FR-009-AC-11")
@pytest.mark.parametrize("archetype", ARCHETYPES)
def test_fr009_ac11_class_and_criticality_never_refer_to_each_other(
    archetype: str,
) -> None:
    schema = json.loads(FRONTMATTER[archetype].read_text(encoding="utf-8"))
    record = json.loads((SCHEMAS / f"{archetype}.json").read_text(encoding="utf-8"))
    for key in KEYS:
        assert "criticality" not in json.dumps(schema["properties"][key])
    for key in RECORD_KEYS:
        assert "criticality" not in json.dumps(record["properties"][key])
    assert "software" not in json.dumps(schema["properties"]["criticality"])
    assert "software" not in json.dumps(record["properties"]["criticality"])
    mapping = rm.load_mappings()["models"][archetype]
    fields = mapping["properties"]
    for key in RECORD_KEYS:
        assert "criticality" not in json.dumps(fields[key])
    assert "software" not in json.dumps(fields["criticality"])


@pytest.mark.trace("TC-078", "FR-009-AC-14")
def test_fr009_ac14_manifest_carries_the_class_and_never_criticality() -> None:
    manifest = yaml.safe_load((PKG_ROOT / "manifest.yaml").read_text(encoding="utf-8"))
    carried = manifest["traceability"]["carried_fields"]
    assert carried == [
        {
            "name": "software_safety_class",
            "key": "software_safety_class",
            "from": ["StR", "US", "FR", "NFR"],
        }
    ]


@pytest.mark.trace("TC-078", "FR-009-AC-14")
@needs_quire
def test_fr009_ac14_coverage_carries_the_class_as_written_with_its_vocabulary(
    tmp_path: pathlib.Path,
) -> None:
    modules = pathlib.Path(
        os.environ.get("IX_FILAMENT_MODULES_PATH")
        or pathlib.Path.home() / ".ix" / "filament" / "modules"
    )
    process = modules / "spec-artifacts-process"
    assert (process / "manifest.yaml").is_file(), f"{process} is not installed"
    spec = tmp_path / "spec"
    spec.mkdir()
    (spec / "FR-001.md").write_text(
        _doc("FR", ["criticality: high", *_full("class-2")]), encoding="utf-8"
    )
    (spec / "FR-002.md").write_text(
        _doc("FR", ["criticality: low"]).replace("FR-001", "FR-002"), encoding="utf-8"
    )
    result = subprocess.run(
        [
            "quire",
            "coverage",
            "--json",
            "--module",
            str(PKG_ROOT),
            "--module",
            str(process),
            "--scope",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["carried_vocabulary"] == {"software_safety_class": CLASSES}
    carried = {r["document"]: r.get("carried") for r in report["coverage_matrix"]}
    assert carried["spec/FR-001.md"] == {"software_safety_class": "class-2"}
    assert "spec/FR-002.md" not in carried or carried["spec/FR-002.md"] is None
