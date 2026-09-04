#!/usr/bin/env python3
"""Rewrite every ``data_schema.digest`` in the module manifest (FR-006).

FR-006 binds each exported artifact type to the exact shipped bytes of its
emitted schema::

    data_schema:
      schema: schemas/FR.json
      digest: sha256:<64 hex>

The digest is the SHA-256 over the *raw bytes* of the file ``schema`` names,
resolved module-relative, with no line-ending normalization. This script is the
only producer of those values — FR-006 Outputs states outright that the suite
never hand-computes a digest, so ``make schemas`` is followed by
``make manifest-digests`` and the test suite only ever *checks*.

The rewrite is deliberately line-targeted rather than a YAML round-trip: the
manifest is hand-authored, carries block comments that document engine
decisions, and a ``yaml.safe_dump`` round-trip would drop every one of them and
reflow the rest of the file. Only the ``digest:`` line of each ``data_schema``
block is touched, so the script is idempotent and its diff is never wider than
the values that actually changed.

Usage::

    make manifest-digests          # rewrite in place
    python scripts/manifest_digests.py --check   # exit 1 on any stale digest
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import pathlib
import re
import sys

import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
PKG_ROOT = REPO_ROOT / "spec_artifacts_iso"
MANIFEST_PATH = PKG_ROOT / "manifest.yaml"
LEGACY_FIXTURE = REPO_ROOT / "tests" / "fixtures" / "manifest-legacy.yaml"

LEGACY_HEADER = """\
# FR-006 legacy-manifest fixture — GENERATED, do not hand-edit.
#
# spec_artifacts_iso/manifest.yaml with the `semantic` block and every
# `data_schema` reference removed: the form a consumer that predates the
# FR-006 additions reads. FR-006-CON-1 and FR-006-AC-7 use it to prove the
# additions break nothing — it validates under the same bundled FR-035
# schema and loads under quire with the same eleven archetypes.
#
# Regenerate with:
#   poetry run python scripts/manifest_digests.py --write-legacy-fixture
# tests/test_semantic_manifest.py fails if this file drifts from the real
# manifest, so it is never a second hand-maintained copy.
"""

_DATA_SCHEMA_RE = re.compile(r"^(?P<indent>\s*)data_schema:\s*$")
_SCHEMA_RE = re.compile(r"^(?P<indent>\s*)schema:\s*(?P<value>\S+)\s*$")
_DIGEST_RE = re.compile(r"^(?P<indent>\s*)digest:\s*(?P<value>\S+)\s*$")


def file_digest(path: pathlib.Path) -> str:
    """Return ``sha256:<hex>`` over the raw bytes of ``path``."""
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _indent_of(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def resolve_schema(
    pkg_root: pathlib.Path, schema_value: str, source: pathlib.Path
) -> pathlib.Path:
    """Resolve a manifest ``data_schema.schema`` value under ``pkg_root``.

    The value is manifest-supplied text being joined onto a filesystem path, so
    it is checked here rather than trusted: the bundled FR-035 schema forbids
    ``..`` in it, but this script never validates against that schema before
    joining, so ``../../..`` would otherwise resolve and be digested. Absolute
    paths, ``..`` segments and anything that escapes the module root are
    refused.
    """
    candidate = pathlib.PurePosixPath(schema_value)
    if candidate.is_absolute() or pathlib.PureWindowsPath(schema_value).is_absolute():
        raise SystemExit(
            f"{source}: data_schema.schema {schema_value!r} is an absolute path; "
            "it must be relative to the module root"
        )
    if ".." in candidate.parts:
        raise SystemExit(
            f"{source}: data_schema.schema {schema_value!r} contains a '..' "
            "segment; it must stay inside the module root"
        )
    root = pkg_root.resolve()
    target = (pkg_root / schema_value).resolve()
    if target != root and root not in target.parents:
        raise SystemExit(
            f"{source}: data_schema.schema {schema_value!r} resolves to {target}, "
            f"outside the module root {root}"
        )
    return target


def rewrite(
    text: str, pkg_root: pathlib.Path, source: pathlib.Path | None = None
) -> tuple[str, list[tuple[str, str, str]]]:
    """Return ``(new_text, changes)`` where each change is ``(schema, old, new)``.

    ``source`` names the file ``text`` came from and appears in every error
    message, so a failure against a fixture reports the fixture rather than the
    bundled manifest.
    """
    source = source if source is not None else MANIFEST_PATH
    lines = text.split("\n")
    changes: list[tuple[str, str, str]] = []
    i = 0
    while i < len(lines):
        block = _DATA_SCHEMA_RE.match(lines[i])
        if not block:
            i += 1
            continue
        outer = len(block.group("indent"))
        j = i + 1
        schema_value: str | None = None
        digest_index: int | None = None
        while j < len(lines):
            line = lines[j]
            if line.strip() and _indent_of(line) <= outer:
                break
            schema = _SCHEMA_RE.match(line)
            if schema:
                schema_value = schema.group("value")
            digest = _DIGEST_RE.match(line)
            if digest:
                digest_index = j
            j += 1
        if schema_value is None or digest_index is None:
            raise SystemExit(
                f"{source}: data_schema block at line {i + 1} lacks a "
                f"schema or digest key (schema={schema_value!r}, "
                f"digest_line={digest_index})"
            )
        target = resolve_schema(pkg_root, schema_value, source)
        if not target.is_file():
            raise SystemExit(
                f"{source}: data_schema.schema {schema_value!r} names no "
                f"file under {pkg_root}"
            )
        computed = file_digest(target)
        old = _DIGEST_RE.match(lines[digest_index]).group("value")
        if old != computed:
            indent = _DIGEST_RE.match(lines[digest_index]).group("indent")
            lines[digest_index] = f"{indent}digest: {computed}"
            changes.append((schema_value, old, computed))
        i = j
    return "\n".join(lines), changes


def derive_legacy(manifest: dict) -> dict:
    """Return the manifest with the ``semantic`` block and every ref removed."""
    legacy = copy.deepcopy(manifest)
    legacy.pop("semantic", None)
    for at in legacy.get("artifact_types") or []:
        at.pop("data_schema", None)
    for ot in legacy.get("object_types") or []:
        if isinstance(ot, dict):
            ot.pop("data_schema", None)
    return legacy


def write_legacy_fixture(manifest_path: pathlib.Path, fixture: pathlib.Path) -> None:
    """Regenerate the FR-006 legacy-manifest fixture from the real manifest."""
    legacy = derive_legacy(yaml.safe_load(manifest_path.read_text()))
    fixture.parent.mkdir(parents=True, exist_ok=True)
    body = yaml.safe_dump(legacy, sort_keys=False, allow_unicode=True, width=10000)
    fixture.write_text(LEGACY_HEADER + body)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--check",
        action="store_true",
        help="do not write; exit non-zero naming every stale digest",
    )
    parser.add_argument(
        "--manifest",
        type=pathlib.Path,
        default=MANIFEST_PATH,
        help="manifest to rewrite (default: the bundled module manifest)",
    )
    parser.add_argument(
        "--write-legacy-fixture",
        action="store_true",
        help=(
            "regenerate tests/fixtures/manifest-legacy.yaml (the manifest with "
            "the semantic block and every data_schema removed) and exit; only "
            "valid for the bundled module manifest"
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    manifest_path = args.manifest.resolve()

    if args.write_legacy_fixture:
        # The fixture is derived from *the* module manifest; deriving it from
        # some other file would overwrite the committed fixture from an
        # unrelated manifest, so the combination is refused rather than
        # silently ignoring --manifest.
        if manifest_path != MANIFEST_PATH.resolve():
            parser.error(
                "--write-legacy-fixture regenerates "
                f"{LEGACY_FIXTURE} from {MANIFEST_PATH}, so it cannot be "
                f"combined with --manifest {manifest_path}"
            )
        write_legacy_fixture(manifest_path, LEGACY_FIXTURE)
        print(f"wrote {LEGACY_FIXTURE}")
        return 0

    text = manifest_path.read_text()
    new_text, changes = rewrite(text, manifest_path.parent, manifest_path)

    if args.check:
        for schema, old, new in changes:
            print(f"stale digest for {schema}: recorded {old}, computed {new}")
        if changes:
            print(f"{len(changes)} stale digest(s); run `make manifest-digests`")
            return 1
        print("every data_schema.digest matches the shipped bytes")
        return 0

    if changes:
        manifest_path.write_text(new_text)
        for schema, old, new in changes:
            print(f"{schema}: {old} -> {new}")
        print(f"rewrote {len(changes)} digest(s) in {manifest_path}")
    else:
        print(f"{manifest_path}: every data_schema.digest already current")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    sys.exit(main())
