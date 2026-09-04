"""FR-006: the manifest ``semantic`` block and the ``data_schema`` digest refs.

Covers TC-046, TC-047, TC-048 and TC-049 of the FR-006 test matrix:

* TC-046 — the block validates under the bundled FR-035 schema, carries exactly
  the nine declared keys, adds no required key, and the legacy-manifest fixture
  (block and references removed) validates under the same schema and loads
  under quire with the same eleven archetypes (FR-006-AC-1, AC-7, CON-1);
* TC-047 — every exported artifact type carries a ``{schema, digest}`` reference
  to an existing file whose SHA-256 equals the digest, ``exports`` equals the
  referencing set, no inline ``data_schema`` remains, and a one-byte schema edit
  fails naming the type and both digests (FR-006-AC-2, AC-5, CON-2);
* TC-048 — on the published quire floor, ``Registry.load_from`` lists all eleven
  archetypes with the block and the ten references present, and
  ``validate_document`` passes every skeleton (FR-006-AC-3);
* TC-049 — the bundled FR-035 schema rejects an unknown ``semantic`` key naming
  it, an ambiguous ``data_schema``, a non-``<org>/<repo>`` package, and a target
  outside the registry (FR-006-AC-4).

Nothing here hand-computes a digest as an expected value: the digests are
produced by ``make manifest-digests`` (``scripts/manifest_digests.py``) and the
suite only ever recomputes them from the shipped bytes and compares.

No check in this module skips. FR-006's Inputs fix the engine floor at
``quire >= 0.33.0``, which loads this manifest, so a missing or too-old engine
is a failure and not a silent pass.
"""

from __future__ import annotations

import copy
import hashlib
import pathlib
import shutil

import pytest
import yaml
from jsonschema import Draft202012Validator

from spec_artifacts_iso import module_manifest_schema

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


def _schema_errors(manifest: dict) -> list[str]:
    validator = Draft202012Validator(module_manifest_schema())
    return [
        f"{'.'.join(str(p) for p in e.absolute_path)}: {e.message}"
        for e in validator.iter_errors(manifest)
    ]


def _derive_legacy(manifest: dict) -> dict:
    """Return the manifest with the ``semantic`` block and every ref removed.

    This is the FR-006-CON-1 consumer that predates the block: nothing it needs
    is expressed by either addition, so removing both must leave a manifest that
    validates and loads exactly as before.
    """
    legacy = copy.deepcopy(manifest)
    legacy.pop("semantic", None)
    for at in legacy.get("artifact_types") or []:
        at.pop("data_schema", None)
    for ot in legacy.get("object_types") or []:
        if isinstance(ot, dict):
            ot.pop("data_schema", None)
    return legacy


def _digest_findings(manifest: dict, pkg_root: pathlib.Path) -> list[str]:
    """Return one finding per artifact type whose recorded digest is stale.

    FR-006 Behavior: a mismatch fails the suite *naming the artifact type, the
    recorded digest, and the computed digest* — so the message carries all
    three, and TC-047's one-byte-edit check reads them back out of it.
    """
    findings: list[str] = []
    for name, at in _artifact_types(manifest).items():
        ref = at.get("data_schema")
        if not ref:
            continue
        target = pkg_root / ref["schema"]
        if not target.is_file():
            findings.append(
                f"{name}: data_schema.schema {ref['schema']} does not exist"
            )
            continue
        computed = "sha256:" + hashlib.sha256(target.read_bytes()).hexdigest()
        if computed != ref["digest"]:
            findings.append(
                f"{name}: {ref['schema']} digest mismatch — "
                f"recorded {ref['digest']}, computed {computed}"
            )
    return findings


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
    for extra in (
        "module-manifest.schema.json",
        "mappings.yaml",
        "mappings.schema.json",
    ):
        src = PKG_ROOT / extra
        if src.is_file():
            shutil.copy2(src, module / extra)
    return module


def _registry_archetypes(parent: pathlib.Path) -> set[str]:
    import quire

    registry = quire.Registry.load_from([str(parent)])
    return set(registry.archetype_names())


# ─── TC-046: the block, its key set, and the legacy fixture ──────────────


def test_tc046_manifest_validates_with_semantic_block() -> None:
    """TC-046: FR-006-AC-1: the manifest validates against the bundled FR-035
    schema with the ``semantic`` block present."""
    manifest = _manifest()
    assert "semantic" in manifest, "manifest declares no semantic block"
    assert not _schema_errors(manifest), _schema_errors(manifest)


def test_tc046_semantic_block_key_set_and_values() -> None:
    """TC-046: FR-006-AC-1: the block's key set is exactly the nine declared
    keys with the values of FR-006 Outputs; ``sweep_report`` stays absent."""
    semantic = _manifest()["semantic"]
    assert set(semantic) == SEMANTIC_KEYS, set(semantic) ^ SEMANTIC_KEYS
    assert "sweep_report" not in semantic
    assert semantic["contract_version"] == "1.0.0"
    assert semantic["semantic_core"] == "0.1.0"
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


def test_tc046_block_adds_no_required_key() -> None:
    """TC-046: FR-006-CON-1: neither ``semantic`` at the manifest root nor
    ``data_schema`` on an ArtifactTypeEntry is a required key, so a consumer
    that ignores the block reads the same contract as before."""
    schema = module_manifest_schema()
    assert "semantic" not in set(schema.get("required", []))
    entry = schema["$defs"]["ArtifactTypeEntry"]
    assert "data_schema" not in set(entry.get("required", []))


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


def test_tc046_legacy_fixture_validates_under_the_fr035_schema() -> None:
    """TC-046: FR-006-AC-7: the legacy fixture validates under the same bundled
    FR-035 schema as the current manifest."""
    fixture = yaml.safe_load(LEGACY_FIXTURE.read_text())
    assert not _schema_errors(fixture), _schema_errors(fixture)


def test_tc046_legacy_fixture_loads_under_quire(tmp_path: pathlib.Path) -> None:
    """TC-046: FR-006-AC-7: the legacy fixture loads under quire with the same
    eleven archetypes the current manifest lists."""
    _module_tree(tmp_path, LEGACY_FIXTURE.read_text())
    assert _registry_archetypes(tmp_path) == ARCHETYPE_NAMES


# ─── TC-047: the references, the digests, and the one-byte edit ──────────


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


def test_tc047_digests_equal_the_shipped_bytes() -> None:
    """TC-047: FR-006-AC-2: every ``data_schema.digest`` equals ``sha256:`` plus
    the hex SHA-256 of the named file's bytes, with no line-ending
    normalization. The expected values come from the files, never from a
    literal in this suite — ``make manifest-digests`` is their only producer."""
    findings = _digest_findings(_manifest(), PKG_ROOT)
    assert not findings, findings


def test_tc047_exports_equals_the_referencing_set() -> None:
    """TC-047: FR-006-AC-2: ``semantic.exports`` equals the set of artifact types
    carrying a ``data_schema`` reference — in both directions."""
    manifest = _manifest()
    referencing = {
        name for name, at in _artifact_types(manifest).items() if at.get("data_schema")
    }
    assert set(manifest["semantic"]["exports"]) == referencing


def test_tc047_no_inline_data_schema_remains() -> None:
    """TC-047: FR-006-CON-2: the reference form is the only form — every
    ``data_schema`` carries exactly ``schema`` and ``digest``."""
    for name, at in _artifact_types(_manifest()).items():
        ref = at.get("data_schema")
        if ref is None:
            continue
        assert set(ref) == {
            "schema",
            "digest",
        }, f"{name}: inline data_schema {set(ref)}"
        assert ref["digest"].startswith("sha256:")
        assert len(ref["digest"]) == len("sha256:") + 64


def test_tc047_one_byte_schema_edit_fails_naming_type_and_digests(
    tmp_path: pathlib.Path,
) -> None:
    """TC-047: FR-006-AC-5: a one-byte edit to an emitted schema with no digest
    update fails the suite, and the failure names the artifact type, the
    recorded digest, and the computed digest."""
    manifest = _manifest()
    module = _module_tree(tmp_path, MANIFEST_PATH.read_text())
    recorded = _artifact_types(manifest)["FR"]["data_schema"]["digest"]

    assert not _digest_findings(manifest, module), "unedited copy already stale"

    edited = module / "schemas" / "FR.json"
    original = edited.read_bytes()
    edited.write_bytes(original.replace(b'"description"', b'"Description"', 1))
    assert edited.read_bytes() != original, "the one-byte mutation did not apply"

    computed = "sha256:" + hashlib.sha256(edited.read_bytes()).hexdigest()
    findings = _digest_findings(manifest, module)
    assert len(findings) == 1, findings
    assert "FR" in findings[0]
    assert recorded in findings[0], findings[0]
    assert computed in findings[0], findings[0]


# ─── TC-048: the published quire floor still loads the module ────────────


def test_tc048_registry_lists_eleven_archetypes_with_the_block_present() -> None:
    """TC-048: FR-006-AC-3: at the published floor (quire >= 0.33.0),
    ``Registry.load_from`` over the module's parent directory lists all eleven
    archetypes with the ``semantic`` block and the ten ``data_schema``
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


# ─── TC-049: what the bundled FR-035 schema refuses ──────────────────────


def test_tc049_schema_rejects_an_unknown_semantic_key_naming_it() -> None:
    """TC-049: FR-006-AC-4: the bundled FR-035 schema rejects a ``semantic`` key
    outside the admitted ten, and the error names the key."""
    manifest = _manifest()
    manifest["semantic"] = manifest["semantic"] | {"foo": 1}
    errors = _schema_errors(manifest)
    assert errors, "schema accepted an undeclared semantic key"
    assert any("foo" in e for e in errors), errors


def test_tc049_schema_rejects_an_ambiguous_data_schema() -> None:
    """TC-049: FR-006-AC-4: a ``data_schema`` mixing ``schema``/``digest`` with
    any other key is ambiguous and is rejected."""
    manifest = _manifest()
    types = _artifact_types(manifest)
    ref = dict(types["FR"]["data_schema"])
    ref["type"] = "object"
    types["FR"]["data_schema"] = ref
    assert _schema_errors(manifest), "schema accepted an ambiguous data_schema"


def test_tc049_schema_rejects_a_non_org_repo_package() -> None:
    """TC-049: FR-006-AC-4: ``package`` is an IR package identity
    (``<org>/<repo>``), never a URL or an ``ix://`` identity."""
    manifest = _manifest()
    manifest["semantic"] = manifest["semantic"] | {"package": "ix://agent-ix/x"}
    errors = _schema_errors(manifest)
    assert errors, "schema accepted an ix:// package identity"
    assert any("package" in e for e in errors), errors


def test_tc049_schema_rejects_a_target_outside_the_registry() -> None:
    """TC-049: FR-006-AC-4: ``targets`` values come from the filament-core-data
    target registry; ``go`` is not one of them."""
    manifest = _manifest()
    manifest["semantic"] = manifest["semantic"] | {"targets": ["go"]}
    errors = _schema_errors(manifest)
    assert errors, "schema accepted an unregistered target"
    assert any("targets" in e for e in errors), errors
