"""The manifest ``semantic`` block and its ``data_schema`` references (FR-006).

Covers TC-046, TC-047 and TC-048 of the FR-006 test matrix:

* TC-046 — the block carries exactly the nine declared keys, and the
  legacy-manifest fixture (block and references removed) is this manifest with
  exactly those removals and loads under quire with the same eleven archetypes
  (FR-006-AC-1, AC-7, CON-1). CON-1's "adds no required key" is now carried by
  that load rather than by reading the schema's ``required`` lists: a manifest
  with neither addition loading unchanged is the consumer-facing fact the
  constraint is about;
* TC-047 — every exported artifact type carries a ``schema`` reference to an
  existing file and ``exports`` equals the referencing set (FR-006-AC-2);
* TC-048 — ``Registry.load_from`` lists all eleven archetypes with the block and the
  ten references present, and ``validate_document`` passes every skeleton
  (FR-006-AC-3);

FR-006-AC-4 — refusal of a malformed ``semantic`` block — is verified nowhere
here. It used to be, against a copy of the FR-035 schema this package shipped;
the copy is removed (PLAT-902) and the criterion is retired rather than
restated over the loader; FR-006-AC-4 stays retired per PLAT-902.

No check in this module skips. A missing or too-old engine is a failure and
not a silent pass.
"""

from __future__ import annotations

import copy
import pathlib
import shutil

import pytest
import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
PKG_ROOT = REPO_ROOT / "spec_artifacts_iso"
MANIFEST_PATH = PKG_ROOT / "manifest.yaml"
SKELETONS_DIR = PKG_ROOT / "skeletons"
FIXTURES_DIR = pathlib.Path(__file__).resolve().parent / "fixtures"
LEGACY_FIXTURE = FIXTURES_DIR / "manifest-legacy.yaml"

# FR-005 Outputs, restated by FR-006: export name -> emitted model file.
EXPORT_SCHEMA_FILE = {
    "FR": "schemas/FR.json",
    "NFR": "schemas/NFR.json",
    "StR": "schemas/StR.json",
    "US": "schemas/US.json",
    "IT": "schemas/IT.json",
    "TC": "schemas/TC.json",
    "master-requirements": "schemas/MasterRequirements.json",
    "index": "schemas/Index.json",
    "log": "schemas/Log.json",
    "Glossary": "schemas/Glossary.json",
}

# FR-006 Outputs: the nine of ten admitted keys the block carries.
SEMANTIC_KEYS = {
    "contract_version",
    "semantic_core",
    "package",
    "exports",
    "imports",
    "targets",
    "mappings",
    "compatibility_posture",
    "legacy_forms",
}

# The eleven archetypes quire lists for this module: the ``Spec`` container
# archetype plus the ten artifact types.
ARCHETYPE_NAMES = {"Spec", *EXPORT_SCHEMA_FILE}

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
    "Glossary": "glossary",
}


def _manifest() -> dict:
    return yaml.safe_load(MANIFEST_PATH.read_text())


def _artifact_types(manifest: dict) -> dict[str, dict]:
    return {at["name"]: at for at in manifest.get("artifact_types") or []}


def _object_types(manifest: dict) -> dict[str, dict]:
    """The mapping-form object types, keyed by name.

    ``object_types`` is empty in this manifest today and an entry may be a bare
    string, so only mapping entries are returned — but the list is walked, not
    assumed empty, because ``_derive_legacy`` strips ``data_schema`` from it."""
    return {
        str(ot.get("name", index)): ot
        for index, ot in enumerate(manifest.get("object_types") or [])
        if isinstance(ot, dict)
    }


def _derive_legacy(manifest: dict) -> dict:
    """Return the manifest minus the ``semantic`` block, every ref and the version.

    This is the FR-006-CON-1 consumer that predates the block: nothing it needs
    is expressed by either addition, so removing both must leave a manifest that
    validates and loads exactly as before.
    """
    legacy = copy.deepcopy(manifest)
    legacy.pop("semantic", None)
    legacy.pop("version", None)
    for at in legacy.get("artifact_types") or []:
        at.pop("data_schema", None)
    for ot in legacy.get("object_types") or []:
        if isinstance(ot, dict):
            ot.pop("data_schema", None)
    return legacy


def _module_tree(parent: pathlib.Path, manifest_text: str) -> pathlib.Path:
    """Materialise a loadable copy of the module under ``parent``.

    Only the payload quire reads at load time is copied (the manifest, the
    frontmatter and emitted schemas, and the skeletons), so the copy is cheap
    and carries no TypeSpec toolchain.
    """
    module = parent / PKG_ROOT.name
    module.mkdir(parents=True, exist_ok=True)
    (module / "manifest.yaml").write_text(manifest_text)
    for sub in ("schemas", "skeletons", "examples"):
        src = PKG_ROOT / sub
        if src.is_dir():
            shutil.copytree(src, module / sub, dirs_exist_ok=True)
    for extra in ("mappings.yaml", "mappings.schema.json"):
        src = PKG_ROOT / extra
        if src.is_file():
            shutil.copy2(src, module / extra)
    return module


def _registry_archetypes(parent: pathlib.Path) -> set[str]:
    import quire

    registry = quire.Registry.load_from([str(parent)])
    return set(registry.archetype_names())


# ─── TC-046: the block, its key set, and the legacy fixture ──────────────


def test_tc046_manifest_carries_a_semantic_block() -> None:
    """TC-046: FR-006-AC-1: the manifest declares a ``semantic`` block."""
    manifest = _manifest()
    assert "semantic" in manifest, "manifest declares no semantic block"


def test_tc046_semantic_block_key_set_and_values() -> None:
    """TC-046: FR-006-AC-1: the block's key set is exactly the nine declared
    keys with the values of FR-006 Outputs; ``sweep_report`` stays absent."""
    semantic = _manifest()["semantic"]
    assert set(semantic) == SEMANTIC_KEYS, set(semantic) ^ SEMANTIC_KEYS
    assert "sweep_report" not in semantic
    assert semantic["contract_version"] == "1.0.0"
    assert semantic["package"] == "agent-ix/spec-artifacts-iso"
    assert set(semantic["exports"]) == set(EXPORT_SCHEMA_FILE)
    assert semantic["imports"] == {}
    assert semantic["targets"] == ["json-schema", "markdown"]
    assert semantic["mappings"] == [
        "frontmatter",
        "section",
        "table",
        "typed-table",
        "ocl-clause",
        "list",
        "token",
        "provenance",
    ]
    assert semantic["compatibility_posture"] == "additive"
    assert semantic["legacy_forms"] == "warning"


def test_tc046_legacy_fixture_is_in_sync_with_the_manifest() -> None:
    """TC-046: FR-006-CON-1: the committed legacy fixture is this manifest with
    the block and every ``data_schema`` removed, and nothing else — a second
    hand-maintained copy would stop proving anything about *this* manifest."""
    assert LEGACY_FIXTURE.is_file(), f"missing legacy fixture {LEGACY_FIXTURE}"
    fixture = yaml.safe_load(LEGACY_FIXTURE.read_text())
    assert fixture == _derive_legacy(_manifest()), (
        f"{LEGACY_FIXTURE} has drifted from spec_artifacts_iso/manifest.yaml; "
        f"regenerate it from the real manifest"
    )


def test_tc046_legacy_fixture_carries_neither_addition() -> None:
    """TC-046: FR-006-AC-7: the fixture is the pre-change form — no ``semantic``
    block and no ``data_schema`` on any artifact type *or object type*.

    ``_derive_legacy`` strips ``data_schema`` from both lists, so both are
    walked here: checking only ``artifact_types`` would leave the object-type
    half of the derivation unasserted, and a ``data_schema`` reaching an object
    type would ride into the fixture unnoticed.
    """
    fixture = yaml.safe_load(LEGACY_FIXTURE.read_text())
    assert "semantic" not in fixture
    typed = {
        **_artifact_types(fixture),
        **_object_types(fixture),
    }
    assert typed, "the fixture declares no type at all; the walk proves nothing"
    for name, entry in typed.items():
        assert "data_schema" not in entry, f"{name} still carries a data_schema"


def test_tc046_legacy_fixture_loads_under_quire(tmp_path: pathlib.Path) -> None:
    """TC-046: FR-006-AC-7: the legacy fixture loads under quire with the same
    eleven archetypes the current manifest lists."""
    _module_tree(tmp_path, LEGACY_FIXTURE.read_text())
    assert _registry_archetypes(tmp_path) == ARCHETYPE_NAMES


# ─── TC-047: the references ──────────


def test_tc047_every_export_carries_a_reference_to_its_mapped_file() -> None:
    """TC-047: FR-006-AC-2: each of the ten exported artifact types carries a
    ``data_schema.schema`` naming the existing file the FR-005 map fixes."""
    manifest = _manifest()
    types = _artifact_types(manifest)
    for name, expected in EXPORT_SCHEMA_FILE.items():
        assert name in types, f"manifest declares no {name} artifact_type"
        ref = types[name].get("data_schema")
        assert ref, f"{name} carries no data_schema reference"
        assert ref["schema"] == expected, f"{name}: {ref['schema']} != {expected}"
        assert (PKG_ROOT / expected).is_file(), f"{name}: {expected} does not exist"


def test_tc047_exports_equals_the_referencing_set() -> None:
    """TC-047: FR-006-AC-2: ``semantic.exports`` equals the set of artifact types
    carrying a ``data_schema`` reference — in both directions."""
    manifest = _manifest()
    referencing = {
        name for name, at in _artifact_types(manifest).items() if at.get("data_schema")
    }
    assert set(manifest["semantic"]["exports"]) == referencing


# ─── TC-048: the published quire floor still loads the module ────────────


def test_tc048_registry_lists_eleven_archetypes_with_the_block_present() -> None:
    """TC-048: FR-006-AC-3: ``Registry.load_from`` over the module's parent
    directory lists all eleven archetypes with the ``semantic`` block and the ten
    ``data_schema``
    references present — adding the block breaks no consumer.

    This check never skips. FR-006's Inputs fix the floor at a wheel that loads
    this manifest, so an absent or too-old engine is a defect to report and not
    a green tick for a check that did not run."""
    assert _registry_archetypes(PKG_ROOT.parent) == ARCHETYPE_NAMES


@pytest.mark.parametrize("name", sorted(_SKELETON_FILE), ids=lambda n: n)
def test_tc048_validate_document_passes_every_skeleton(name: str) -> None:
    """TC-048: FR-006-AC-3: ``validate_document`` passes every skeleton with the
    block and the references in place."""
    import quire

    text = (SKELETONS_DIR / f"{_SKELETON_FILE[name]}.md").read_text()
    result = quire.validate_document(name, str(PKG_ROOT), text)
    assert result["is_valid"], result["errors"]


# ─── PLAT-1085: the FR/NFR Verification lint rule stays gone ─────────────


def _lint_rule(manifest: dict, rule_id: str) -> dict | None:
    for rule in manifest.get("lint_rules") or []:
        if rule.get("id") == rule_id:
            return rule
    return None


def test_manifest_declares_no_ac_verification_method_rule() -> None:
    """PLAT-1085: `ac-verification-method` is deleted, not merely disabled —
    spec-artifacts-process now owns the FR/NFR Verification column vocabulary,
    and the registry merging both modules' rules on that column is the defect
    this pins against. Fails on the pre-PLAT-1085 manifest, which declares it."""
    assert _lint_rule(_manifest(), "ac-verification-method") is None


def test_vc_validation_method_rule_carries_no_annotation_pattern() -> None:
    """PLAT-1085: the StR sibling keeps its four-class vocabulary but drops the
    `(TC-nnn)` `annotation_pattern` — TC ids are retired epic-wide; a test
    binds to its acceptance criterion by criterion id, not a cell annotation.
    Fails on the pre-PLAT-1085 manifest, which carries the pattern."""
    rule = _lint_rule(_manifest(), "vc-validation-method")
    assert rule is not None, "vc-validation-method rule is missing entirely"
    assert "annotation_pattern" not in rule
    assert rule["allowed"] == ["Inspection", "Analysis", "Demonstration", "Test"]
