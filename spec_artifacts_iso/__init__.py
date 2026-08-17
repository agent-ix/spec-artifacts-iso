"""Filament Module: ISO-style spec artifacts.

Besides the manifest and skeletons this package ships the **FR-035 module
manifest JSON Schema** as package data (FR-001 CR-002). It lives here rather
than under ``tests/`` because it is not this repository's private fixture: every
module repository's manifest is gated by the same contract, and a copy per repo
is a copy that drifts — ``spec-artifacts-process`` shipped no copy at all and
its schema test skipped in silence as a result.
"""

import json
import pathlib
from typing import Any

MODULE_MANIFEST_SCHEMA_PATH = (
    pathlib.Path(__file__).resolve().parent / "module-manifest.schema.json"
)
"""Path to the bundled FR-035 module-manifest JSON Schema."""


def module_manifest_schema() -> dict[str, Any]:
    """Return the parsed FR-035 module-manifest schema (FR-001 CR-002).

    Any module repository validates its own ``manifest.yaml`` against this one
    source. Raises rather than returning ``None`` when the file is missing: a
    module contract that cannot be located is a packaging failure, and the
    caller must not be able to mistake it for "nothing to check".
    """
    if not MODULE_MANIFEST_SCHEMA_PATH.exists():  # pragma: no cover - packaging bug
        raise FileNotFoundError(
            f"FR-035 module-manifest schema missing from the installed package at "
            f"{MODULE_MANIFEST_SCHEMA_PATH}; the wheel was built without its "
            f"package data (see pyproject `include`)."
        )
    return json.loads(MODULE_MANIFEST_SCHEMA_PATH.read_text())


def hello():
    return "Hello, World!"
