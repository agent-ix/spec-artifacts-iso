"""FR-005 — the emitted JSON Schema projection of the semantic data models.

The bundle under ``spec_artifacts_iso/schemas/<Model>.json`` is *generated* by
the official ``@typespec/json-schema`` emitter from
``spec_artifacts_iso/semantic/main.tsp`` (``make schemas``). Nothing here may be
hand-edited, and ``make schemas-check`` is the gate that says so.

These tests assert the properties a consumer relies on:

* the ten exported models exist, with the 2020-12 ``$schema`` and the
  version-embedded ``$id`` (TC-041);
* every ``$ref`` in the bundle resolves offline — to a shipped sibling, or to a
  file of the semantic-core 0.1.0 bundle (TC-041);
* every property is constrained, or is declared free text with a reason
  (TC-040), and every locator output has a property and vice versa (TC-039);
* no property models an execution result (TC-043);
* object schemas declare their properties inline, so the Python and Rust
  validators cannot disagree about ``unevaluatedProperties`` (TC-060);
* the file set and digest recorded in ``toolchain.json`` describe the committed
  bytes (TC-061);
* the drift gate actually fails on drift (TC-042).

There are no skip guards. A missing toolchain, a missing schema or a missing
golden record is a failure, not a reason to report green: this module's own
history (IT-002, 21 assertions that stood down on a stale wheel) is why.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import re
import subprocess

import pytest
import yaml
from jsonschema import Draft202012Validator

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
PKG_ROOT = REPO_ROOT / "spec_artifacts_iso"
SCHEMAS_DIR = PKG_ROOT / "schemas"
SEMANTIC_DIR = PKG_ROOT / "semantic"
TOOLCHAIN_PATH = SEMANTIC_DIR / "generated" / "toolchain.json"
MANIFEST_PATH = PKG_ROOT / "manifest.yaml"
EXAMPLES_DIR = PKG_ROOT / "examples"

MODULE_BASE = "https://schemas.agent-ix.org/agent-ix/spec-artifacts-iso/"
SEMANTIC_CORE_BASE = "https://schemas.agent-ix.org/semantic-core/"
SEMANTIC_CORE_VERSION = "0.1.0"

#: FR-005 Outputs: the export name a consumer writes, and the file it maps to.
EXPORT_TO_FILE = {
    "FR": "FR.json",
    "NFR": "NFR.json",
    "StR": "StR.json",
    "US": "US.json",
    "IT": "IT.json",
    "TC": "TC.json",
    "master-requirements": "MasterRequirements.json",
    "index": "Index.json",
    "log": "Log.json",
    "Glossary": "Glossary.json",
}

#: FR-005-CON-4 / AC-6: requirement definitions and execution results stay
#: distinct, so none of these may ever name a property.
EXECUTION_RESULT_PROPERTIES = frozenset(
    {"result", "outcome", "passed", "failed", "run", "executedAt", "evidence"}
)

#: FR-005-AC-3: the closed list of properties that may be free text. Anything
#: else must carry a real constraint. Widening this set is a spec change, not a
#: test change.
FREE_TEXT_PROPERTIES = frozenset(
    {
        "text",  # Section.text — the byte-exact section slice
        "detail",  # a supplementary `### <row id>` subsection body
        "summary",  # an index entry's trailing summary
        "description",  # the frontmatter description of index/log/Glossary
        "annotation",  # the parenthesized remainder of a verification cell
    }
)

CONSTRAINT_KEYWORDS = ("pattern", "minLength", "minimum", "enum", "const", "format")


def _load(path: pathlib.Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _projection_files() -> dict[str, pathlib.Path]:
    """The emitted files only — the hand-authored frontmatter schemas are not
    projections and are outside `make schemas` (FR-005 Outputs)."""
    return {
        p.name: p
        for p in sorted(SCHEMAS_DIR.glob("*.json"))
        if not p.name.endswith("-frontmatter.schema.json")
    }


def _manifest_version() -> str:
    return str(yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))["version"])


def _semantic_core_files() -> frozenset[str]:
    """The file list of the semantic-core bundle this module compiled against.

    Read from the resolved package's own ``generated/toolchain.json`` — the
    provenance FR-005-AC-2 names. Absent means `make semantic-install` was not
    run, which is a failure: the offline-closure claim cannot be checked
    without it.
    """
    path = (
        SEMANTIC_DIR
        / "node_modules"
        / "@agent-ix"
        / "semantic-core"
        / "generated"
        / "toolchain.json"
    )
    assert path.exists(), (
        f"{path} is missing; run `make semantic-install` — the semantic-core "
        "file list is what FR-005-AC-2 resolves imported $refs against, and "
        "without it this assertion would pass by checking nothing"
    )
    return frozenset(_load(path)["files"])


def _walk_refs(node: object) -> list[str]:
    found: list[str] = []
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "$ref" and isinstance(value, str):
                found.append(value)
            else:
                found.extend(_walk_refs(value))
    elif isinstance(node, list):
        for item in node:
            found.extend(_walk_refs(item))
    return found


def _walk_property_names(node: object) -> list[str]:
    found: list[str] = []
    if isinstance(node, dict):
        properties = node.get("properties")
        if isinstance(properties, dict):
            found.extend(properties)
        for value in node.values():
            found.extend(_walk_property_names(value))
    elif isinstance(node, list):
        for item in node:
            found.extend(_walk_property_names(item))
    return found


def _resolve(ref: str, bundle: dict[str, dict]) -> dict | None:
    """Resolve a bundle-internal ``$ref`` to its schema document."""
    if ref.startswith(MODULE_BASE):
        return bundle.get(ref.rsplit("/", 1)[-1])
    return None


def _free_text_reason(property_name: str, schema: dict) -> bool:
    """FR-005-AC-3's escape: declared free text, with a reason, from the closed
    list of names the requirement enumerates."""
    description = str(schema.get("description", ""))
    reason = description.partition("free text:")[2].strip()
    return (
        description.startswith("free text:")
        and bool(reason)
        and property_name in FREE_TEXT_PROPERTIES
    )


def _is_acceptable(
    property_name: str, schema: dict, bundle: dict[str, dict], seen: frozenset[str]
) -> bool:
    """FR-005-AC-3: a property is acceptable when, after following `$ref`, it is
    constrained — `pattern`, `minLength`, `minimum`, `enum`, `const` or
    `format`, or an object whose properties are all acceptable, or an array of
    such items, or `boolean`/`null` — or it is declared free text with a reason
    and its name is in the closed list.

    The free-text escape applies at every depth, not only at the top: `Section`
    is a shared model whose `text` is the byte-exact section slice, and every
    property typed `Section` inherits that.
    """
    if _free_text_reason(property_name, schema):
        return True

    ref = schema.get("$ref")
    if isinstance(ref, str):
        if ref.startswith(SEMANTIC_CORE_BASE):
            # semantic-core's models carry their own constraints; they are
            # verified in filament-core-data, not restated here.
            return True
        target_name = ref.rsplit("/", 1)[-1]
        if target_name in seen:  # a recursive model is not an escape hatch
            return True
        target = bundle.get(target_name)
        if target is None:
            return False
        return _is_acceptable(property_name, target, bundle, seen | {target_name})

    if any(keyword in schema for keyword in CONSTRAINT_KEYWORDS):
        return True

    declared = schema.get("type")
    types = declared if isinstance(declared, list) else [declared]
    if any(t in ("boolean", "null") for t in types if t):
        return True

    for composition in ("anyOf", "oneOf"):
        if composition in schema:
            return all(
                _is_acceptable(property_name, branch, bundle, seen)
                for branch in schema[composition]
            )

    if "object" in types:
        properties = schema.get("properties") or {}
        return bool(properties) and all(
            _is_acceptable(name, value, bundle, seen)
            for name, value in properties.items()
        )

    if "array" in types:
        items = schema.get("items")
        return isinstance(items, dict) and _is_acceptable(
            property_name, items, bundle, seen
        )

    return False


@pytest.fixture(scope="module")
def bundle() -> dict[str, dict]:
    files = _projection_files()
    assert files, (
        f"{SCHEMAS_DIR} carries no emitted schema; run `make semantic-install "
        "&& make schemas`"
    )
    return {name: _load(path) for name, path in files.items()}


def test_tc041_exported_schemas_exist_with_versioned_ids(
    bundle: dict[str, dict],
) -> None:
    """TC-041: FR-005-AC-1: the ten exported models ship as JSON Schema 2020-12
    documents whose `$id` embeds the manifest version, and whose `type` const is
    the archetype name — not the model name.
    """
    version = _manifest_version()
    for export, filename in EXPORT_TO_FILE.items():
        schema = bundle.get(filename)
        assert schema is not None, f"{filename} is not in the emitted bundle"
        assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        assert schema["$id"] == f"{MODULE_BASE}{version}/{filename}"
        type_property = schema["properties"]["type"]
        assert type_property.get("const") == export, (
            f"{filename} declares type const {type_property.get('const')!r}; "
            f"the archetype name is {export!r}"
        )


def test_tc041_every_ref_resolves_offline(bundle: dict[str, dict]) -> None:
    """TC-041: FR-005-AC-2, FR-005-CON-2: every `$ref` across the bundle points
    at a shipped sibling or at a file of the semantic-core 0.1.0 bundle, and no
    schema under the semantic-core base ships.
    """
    core_files = _semantic_core_files()
    version = _manifest_version()
    module_base = f"{MODULE_BASE}{version}/"
    core_base = f"{SEMANTIC_CORE_BASE}{SEMANTIC_CORE_VERSION}/"

    for name, schema in bundle.items():
        assert not str(schema.get("$id", "")).startswith(SEMANTIC_CORE_BASE), (
            f"{name} carries a semantic-core `$id`; imported models ship in the "
            "bundles quoin and quire vendor, never here"
        )

    for name, schema in bundle.items():
        for ref in _walk_refs(schema):
            if ref.startswith(module_base):
                target = ref[len(module_base) :]
                assert target in bundle, f"{name} refs unshipped sibling {target}"
            elif ref.startswith(core_base):
                target = ref[len(core_base) :]
                assert target in core_files, (
                    f"{name} refs {target}, which is not in the semantic-core "
                    f"{SEMANTIC_CORE_VERSION} bundle"
                )
            else:
                pytest.fail(
                    f"{name} carries `$ref` {ref!r}, which is outside the module "
                    "base and the semantic-core 0.1.0 base — a consumer would "
                    "have to read the network to resolve it"
                )


def test_tc040_every_property_is_constrained_or_declared_free_text(
    bundle: dict[str, dict],
) -> None:
    """TC-040: FR-005-AC-3, FR-005-CON-1: every property of every emitted object
    schema is constrained after following `$ref`, or is free text whose
    description says `free text:` and why, and whose name is in the closed list.
    """
    unconstrained: list[str] = []
    for name, schema in bundle.items():
        for property_name, property_schema in (schema.get("properties") or {}).items():
            if not _is_acceptable(
                property_name, property_schema, bundle, frozenset({name})
            ):
                unconstrained.append(f"{name}#{property_name}")
    assert not unconstrained, (
        "properties that are neither constrained nor declared free text with a "
        f"reason from the closed list: {sorted(unconstrained)}"
    )


def test_tc039_every_locator_output_has_a_property(bundle: dict[str, dict]) -> None:
    """TC-039: FR-005-CON-1: every `body_extraction` locator of every exported
    archetype has a property on its model, under the camelCase rule.

    The reverse direction — every property tracing back to a locator, a
    frontmatter key or a mapping entry — is TC-052's, which checks it against
    `mappings.yaml` where the trace is declared rather than inferred.
    """
    manifest = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    by_name = {a["name"]: a for a in manifest["artifact_types"]}

    missing: list[str] = []
    for export, filename in EXPORT_TO_FILE.items():
        archetype = by_name.get(export)
        if archetype is None:
            continue
        properties = set(bundle[filename].get("properties") or {})
        for locator, expected in _expected_properties(archetype).items():
            if expected is None:  # a section the typed rows already carry
                continue
            if expected not in properties:
                missing.append(f"{export}.{locator} -> {expected}")
    assert not missing, (
        "locator outputs with no property on their model (FR-005-CON-1): "
        f"{sorted(missing)}"
    )


def _locator_names(archetype: dict) -> list[str]:
    """The locator names of an archetype.

    The manifest nests them as ``body_extraction.yield_pattern.match.<name>``;
    ``yield_pattern`` and ``match`` are the DSL's own keys, not locators.
    """
    match = ((archetype.get("body_extraction") or {}).get("yield_pattern") or {}).get(
        "match"
    ) or {}
    return sorted(match)


def _camel(name: str) -> str:
    head, *rest = name.split("_")
    return head + "".join(part[:1].upper() + part[1:] for part in rest)


#: FR-005 Behavior: the single locator whose property name is not derived from
#: its own name, because the property is the list the section carries rather
#: than the section itself.
RENAMED_LOCATORS = {("index", "contents"): "entries"}


def _expected_properties(archetype: dict) -> dict[str, str | None]:
    """Locator name -> the property FR-005's naming rules require, or ``None``
    where the model deliberately carries no property for it.

    The rules, from FR-005 Behavior:

    * camelCase of the locator name, with a trailing ``_table`` dropped;
    * where one section carries both a ``section_body`` and a ``table_row``
      locator, the typed rows are that section's record form and the section
      body is not restated, so the ``section_body`` locator maps to nothing;
    * ``index.contents`` fills ``entries`` — the only rename.
    """
    match = ((archetype.get("body_extraction") or {}).get("yield_pattern") or {}).get(
        "match"
    ) or {}
    sections_with_rows = {
        spec.get("under_section")
        for spec in match.values()
        if spec.get("from") == "table_row" and spec.get("under_section")
    }
    expected: dict[str, str | None] = {}
    for name, spec in sorted(match.items()):
        renamed = RENAMED_LOCATORS.get((archetype["name"], name))
        if renamed is not None:
            expected[name] = renamed
            continue
        if (
            spec.get("from") == "section_body"
            and spec.get("after_heading") in sections_with_rows
        ):
            expected[name] = None
            continue
        base = name[: -len("_table")] if name.endswith("_table") else name
        expected[name] = _camel(base)
    return expected


def test_tc043_no_execution_result_property(bundle: dict[str, dict]) -> None:
    """TC-043: FR-005-AC-6, FR-005-CON-4: no emitted property models an
    execution result, and `TC.json` says so in words.
    """
    offenders = sorted(
        f"{name}#{prop}"
        for name, schema in bundle.items()
        for prop in _walk_property_names(schema)
        if prop in EXECUTION_RESULT_PROPERTIES
    )
    assert not offenders, f"execution-result properties: {offenders}"

    # The emitter carries the doc comment's own line wrapping into the
    # description, so compare on normalized whitespace: the requirement is that
    # the sentence is there, not that it is on one line.
    description = " ".join(str(bundle["TC.json"].get("description", "")).split())
    assert (
        "execution results (pass/fail, run time, evidence) are not modelled"
        in description
    ), "TC.json's description does not say that execution results are not modelled"


def test_tc060_object_schemas_declare_properties_inline(
    bundle: dict[str, dict],
) -> None:
    """TC-060: FR-005-AC-8: every emitted object schema declares its properties
    inline, so `unevaluatedProperties` and `additionalProperties` cannot mean
    different things to the Python and Rust validators.

    The only composition admitted at an object's top level is the `anyOf` of a
    nullable scalar.
    """
    offenders: list[str] = []
    for name, schema in bundle.items():
        if schema.get("type") != "object":
            continue
        for keyword in ("allOf", "oneOf", "$ref"):
            if keyword in schema:
                offenders.append(f"{name}: top-level {keyword}")
        if "anyOf" in schema:
            offenders.append(f"{name}: top-level anyOf on an object")
        assert schema.get("unevaluatedProperties") == {"not": {}}, (
            f"{name} is not sealed; FR-005 requires unevaluatedProperties: "
            "{{not: {{}}}} on every object schema"
        )
    assert not offenders, f"object schemas that are not declared inline: {offenders}"


def test_tc060_python_validator_accepts_every_golden_record(
    bundle: dict[str, dict],
) -> None:
    """TC-060: FR-005-AC-8: the Python `jsonschema` validator accepts every
    golden record the reference mapping produced.

    The rejection half lives with the mutations in ``test_mapping_failures.py``;
    this is the acceptance half, and it is the reason a golden record is a
    golden record.
    """
    goldens = sorted(EXAMPLES_DIR.glob("*.record.json"))
    assert len(goldens) == len(EXPORT_TO_FILE), (
        f"expected one golden record per exported type ({len(EXPORT_TO_FILE)}), "
        f"found {len(goldens)} in {EXAMPLES_DIR}"
    )
    for golden in goldens:
        record = _load(golden)
        filename = EXPORT_TO_FILE[record["type"]]
        validator = Draft202012Validator(bundle[filename], registry=_registry(bundle))
        errors = sorted(validator.iter_errors(record), key=lambda e: list(e.path))
        assert (
            not errors
        ), f"{golden.name} does not validate against {filename}: " + "; ".join(
            f"{list(e.path)}: {e.message}" for e in errors
        )


def _registry(bundle: dict[str, dict]):
    """A referencing registry over the shipped bundle and the semantic-core
    bundle, so validation resolves every `$ref` with no network read."""
    from referencing import Registry, Resource

    resources = [
        (schema["$id"], Resource.from_contents(schema)) for schema in bundle.values()
    ]
    core_dir = (
        SEMANTIC_DIR
        / "node_modules"
        / "@agent-ix"
        / "semantic-core"
        / "generated"
        / "json-schema"
    )
    for path in sorted(core_dir.glob("*.json")):
        schema = _load(path)
        resources.append((schema["$id"], Resource.from_contents(schema)))
    return Registry().with_resources(resources)


def test_tc061_toolchain_records_the_committed_bytes() -> None:
    """TC-061: FR-005-AC-7: the emitted file set equals `toolchain.json`'s
    `files`, and the digest recomputed over those bytes equals the recorded
    digest — computed from the committed tree, with no toolchain run.
    """
    toolchain = _load(TOOLCHAIN_PATH)
    files = _projection_files()
    assert sorted(files) == sorted(toolchain["files"])

    digest = hashlib.sha256()
    for name in sorted(files):
        digest.update(f"{name}\n".encode("utf-8"))
        digest.update(files[name].read_bytes())
    assert f"sha256:{digest.hexdigest()}" == toolchain["digest"]

    version = _manifest_version()
    assert toolchain["manifestVersion"] == version
    assert toolchain["base"] == f"{MODULE_BASE}{version}/"
    assert toolchain["semanticCore"]["version"] == SEMANTIC_CORE_VERSION
    assert re.fullmatch(
        r"sha256:[0-9a-f]{64}", toolchain["semanticCore"]["toolchainDigest"]
    ), "toolchain.json does not pin the semantic-core copy by digest"


def test_tc042_schemas_check_passes_clean_and_fails_on_drift(
    tmp_path: pathlib.Path,
) -> None:
    """TC-042: FR-005-AC-5: `make schemas-check` exits 0 on the committed tree
    and non-zero naming the file after a one-byte edit to an emitted schema.

    Shelling out to `make` is the point: the gate a developer runs is the gate
    under test. A missing TypeSpec install fails here with the command to run —
    it never skips, because a gate that reports green without running is the
    defect this suite exists to prevent.
    """
    clean = subprocess.run(
        ["make", "schemas-check"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert clean.returncode == 0, (
        "`make schemas-check` failed on the committed tree.\n"
        f"stdout: {clean.stdout}\nstderr: {clean.stderr}\n"
        "If the TypeSpec package is not installed, run `make semantic-install`."
    )

    victim = SCHEMAS_DIR / "FR.json"
    original = victim.read_bytes()
    try:
        victim.write_bytes(
            original.replace(b'"type": "object"', b'"type": "Object"', 1)
        )
        drifted = subprocess.run(
            ["make", "schemas-check"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        assert drifted.returncode != 0, "`make schemas-check` passed on a drifted tree"
        assert (
            "FR.json" in drifted.stdout + drifted.stderr
        ), "the drift report does not name the file that drifted"
    finally:
        victim.write_bytes(original)

    restored = subprocess.run(
        ["make", "schemas-check"], cwd=REPO_ROOT, capture_output=True, text=True
    )
    assert restored.returncode == 0, "the drifted file was not restored"
