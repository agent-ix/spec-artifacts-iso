"""The emitted schema bundle, resolved offline, for the mapping suite.

Read-only: this loads the committed projection under
``spec_artifacts_iso/schemas/`` and the semantic-core bundle the module
compiled against, and builds a ``referencing`` registry so a record validates
with no network read. Nothing here writes.

There are no skip guards. A missing semantic-core install fails with the
command to run, because a validator that resolves nothing would report green
by checking nothing.
"""

from __future__ import annotations

import json
import pathlib
from typing import Any

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PKG_ROOT = REPO_ROOT / "spec_artifacts_iso"
SCHEMAS_DIR = PKG_ROOT / "schemas"
SEMANTIC_CORE_JSON_SCHEMA = (
    PKG_ROOT
    / "semantic"
    / "node_modules"
    / "@agent-ix"
    / "semantic-core"
    / "generated"
    / "json-schema"
)


def load_bundle() -> dict[str, dict[str, Any]]:
    """The emitted projection, keyed by file name.

    The hand-authored ``*-frontmatter.schema.json`` files are not projections
    and are not part of the bundle (FR-005 Outputs).
    """
    files = {
        path.name: json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(SCHEMAS_DIR.glob("*.json"))
        if not path.name.endswith("-frontmatter.schema.json")
    }
    assert files, (
        f"{SCHEMAS_DIR} carries no emitted schema; run `make semantic-install "
        "&& make schemas`"
    )
    return files


def registry(bundle: dict[str, dict[str, Any]]) -> Registry:
    """A registry over the shipped bundle and the semantic-core bundle."""
    assert SEMANTIC_CORE_JSON_SCHEMA.is_dir(), (
        f"{SEMANTIC_CORE_JSON_SCHEMA} is missing; run `make semantic-install` — "
        "without the semantic-core bundle every `ClauseRef` and `SemanticId` "
        "reference would resolve to nothing and this suite would pass by "
        "checking nothing"
    )
    resources = [
        (schema["$id"], Resource.from_contents(schema)) for schema in bundle.values()
    ]
    for path in sorted(SEMANTIC_CORE_JSON_SCHEMA.glob("*.json")):
        schema = json.loads(path.read_text(encoding="utf-8"))
        resources.append((schema["$id"], Resource.from_contents(schema)))
    return Registry().with_resources(resources)


def validation_errors(
    record: dict[str, Any], schema_file: str, bundle: dict[str, dict[str, Any]]
) -> list[str]:
    """Every schema error against ``schema_file``, each naming its JSON path.

    The path is what tells a reader which layer rejected the record: a schema
    failure names a JSON path, a mapping failure names a document line
    (FR-007, TC-045).
    """
    validator = Draft202012Validator(bundle[schema_file], registry=registry(bundle))
    return [
        f"{'/'.join(str(part) for part in error.absolute_path)}: {error.message}"
        for error in sorted(
            validator.iter_errors(record), key=lambda e: list(e.absolute_path)
        )
    ]
