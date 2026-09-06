"""quire-rs#409: the schema owns shape; the engine owns vocabulary coherence."""

import copy
import hashlib
import pathlib

import pytest
from jsonschema import Draft202012Validator

from spec_artifacts_iso import module_manifest_schema


def validator():
    schema = module_manifest_schema()
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(
        {"$ref": "#/$defs/DocumentReference", "$defs": schema["$defs"]}
    )


def reference():
    return {
        "name": "functional-coverage",
        "archetype": "TestMatrix",
        "section": "Functional Requirement Coverage",
        "column": "Test Cases",
        "pattern": "(TC-[0-9]+)",
        "targets": ["test-case"],
    }


@pytest.mark.parametrize("column", ["Coverage Status", "Status", "État"])
def test_optional_nonblank_column_and_legacy_omission(column):
    """TC-064: FR-001-AC-1: no required key or schema default is introduced."""
    checker = validator()
    legacy = reference()
    before = copy.deepcopy(legacy)
    checker.validate(legacy)
    checker.validate(legacy | {"status_column": column})
    assert legacy == before
    definition = module_manifest_schema()["$defs"]["DocumentReference"]
    assert "status_column" not in definition["required"]
    assert "default" not in definition["properties"]["status_column"]


@pytest.mark.parametrize("column", ["", " ", "\t\n", "\u00a0", None, 17, True, [], {}])
def test_blank_and_nonstring_override_refused(column):
    """TC-064: FR-001-AC-1: malformed fields remain schema failures."""
    errors = list(validator().iter_errors(reference() | {"status_column": column}))
    assert errors


def test_only_the_additive_property_changes_the_parent_schema():
    """TC-065: FR-001-AC-1: exact parent 6686f112, not a refreshed expectation."""
    path = (
        pathlib.Path(__file__).resolve().parents[1]
        / "spec_artifacts_iso/module-manifest.schema.json"
    )
    text = path.read_text()
    addition = (
        '        "status_column": {\n'
        '          "type": "string",\n'
        '          "pattern": "\\\\S",\n'
        '          "description": "quire-rs#409: optional exact status-column '
        "override; omission inherits traceability.status.column. The engine "
        'requires a declared global status vocabulary."\n'
        "        },\n"
    )
    assert text.count(addition) == 1
    assert (
        hashlib.sha256(text.replace(addition, "").encode()).hexdigest()
        == "52bddd1c14e0df06e95322db45734925990a4472e6b4c980a5c14f00480bb874"
    )
