"""Packaging and TypeSpec-toolchain conformance (FR-005-CON-3, FR-005-AC-9).

Two payloads leave this repository — a Python sdist/wheel and an npm tarball —
and FR-005 Outputs requires them to carry the same module: ``schemas/``,
``skeletons/``, ``manifest.yaml``, ``module-manifest.schema.json``,
``mappings.yaml``, ``mappings.schema.json``, ``examples/``,
``semantic/main.tsp`` and ``semantic/generated/toolchain.json``, and none of the
TypeSpec toolchain (``node_modules``, ``package.json``, ``package-lock.json``,
``tspconfig.yaml``, ``scripts/``), which is a build input.

Nothing here skips. ``poetry`` and ``npm`` are the tools that build the two
payloads; if either is absent the build tests fail, because a packaging gate
that reports "passed" because it could not run asserts nothing.
"""

from __future__ import annotations

import json
import pathlib
import subprocess
import tarfile
import tomllib

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
PKG_ROOT = REPO_ROOT / "spec_artifacts_iso"
SEMANTIC_DIR = PKG_ROOT / "semantic"
SEMANTIC_PACKAGE_JSON = SEMANTIC_DIR / "package.json"
SEMANTIC_PACKAGE_LOCK = SEMANTIC_DIR / "package-lock.json"
NPM_PACKAGE_JSON = REPO_ROOT / "package.json"
PYPROJECT = REPO_ROOT / "pyproject.toml"
POETRY_LOCK = REPO_ROOT / "poetry.lock"

#: FR-005-CON-3: the three versions the reproducibility claim rests on.
PINNED_VERSIONS = {
    "@typespec/compiler": "1.15.0",
    "@typespec/json-schema": "1.15.0",
    "@agent-ix/semantic-core": "0.1.0",
}

#: FR-005 Outputs — the shipped payload, module-root relative.
PAYLOAD_ENTRIES = (
    "schemas/",
    "skeletons/",
    "manifest.yaml",
    "module-manifest.schema.json",
    "mappings.yaml",
    "mappings.schema.json",
    "examples/",
    "semantic/main.tsp",
    "semantic/generated/toolchain.json",
)

#: FR-005 Outputs — the TypeSpec toolchain, which is a build input and must not
#: appear in either shipping list.
TOOLCHAIN_ENTRIES = (
    "semantic/node_modules",
    "semantic/package.json",
    "semantic/package-lock.json",
    "semantic/tspconfig.yaml",
    "semantic/scripts",
)

#: The one source a committed ``poetry.lock`` of this repository may name.
INTERNAL_INDEX = "us-west1-python.pkg.dev/agent-ix/internal-pypi"


def _load_json(path: pathlib.Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _repo_package_jsons() -> list[pathlib.Path]:
    """Every ``package.json`` of the repository itself, toolchain tree excluded."""
    return [
        path
        for path in sorted(REPO_ROOT.rglob("package.json"))
        if "node_modules" not in path.parts and ".git" not in path.parts
    ]


def _covers(declared: str, entry: str) -> bool:
    """Does a shipping-list path ``declared`` name the payload ``entry``?

    Either direction counts. ``schemas/**/*.json`` names the ``schemas/`` entry
    from inside it, and ``semantic/generated/`` names the
    ``semantic/generated/toolchain.json`` entry by containing it.
    """
    declared = declared.strip().lstrip("./").rstrip("/")
    entry = entry.strip().lstrip("./").rstrip("/")
    if declared == entry:
        return True
    return declared.startswith(entry + "/") or entry.startswith(declared + "/")


def _pyproject_include_paths() -> list[str]:
    """The ``[tool.poetry] include`` paths, made module-root relative."""
    data = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    paths = []
    for item in data["tool"]["poetry"]["include"]:
        path = item["path"] if isinstance(item, dict) else item
        prefix = "spec_artifacts_iso/"
        paths.append(path[len(prefix) :] if path.startswith(prefix) else path)
    return paths


def _npm_files() -> list[str]:
    return list(_load_json(NPM_PACKAGE_JSON)["files"])


def _payload_members(names: list[str], strip: str) -> set[str]:
    """Reduce archive member names to the payload entries they belong to."""
    members = set()
    for name in names:
        _, _, rel = name.partition(strip)
        if not rel or name == rel:
            continue
        if any(_covers(rel, entry) for entry in PAYLOAD_ENTRIES):
            members.add(rel)
    return members


# --------------------------------------------------------------------------
# TC-054 — FR-005-CON-3: exact pins, a committed lockfile, no local references
# --------------------------------------------------------------------------


def test_typespec_package_pins_every_dependency_exactly() -> None:
    """TC-054: FR-005-CON-3: the three toolchain versions are pinned exactly.

    "Pinned exactly" means the literal version and nothing else: a ``^`` or
    ``~`` range, an ``x`` wildcard, a ``*``, or a comparator would let a fresh
    install resolve a different compiler and produce a different projection,
    which is the whole claim this constraint makes.
    """
    package = _load_json(SEMANTIC_PACKAGE_JSON)
    declared = {
        **package.get("dependencies", {}),
        **package.get("devDependencies", {}),
    }
    for name, version in PINNED_VERSIONS.items():
        assert name in declared, f"{name} is not declared by semantic/package.json"
        assert (
            declared[name] == version
        ), f"{name} is declared as {declared[name]!r}, not the exact pin {version!r}"
    for name, spec in declared.items():
        assert not any(
            char in spec for char in "^~<>|*x "
        ), f"{name} is declared as a range ({spec!r}), not an exact version"


def test_package_lock_is_committed_and_agrees_with_the_pins() -> None:
    """TC-054: FR-005-CON-3: ``package-lock.json`` is present, and not ignored."""
    assert SEMANTIC_PACKAGE_LOCK.is_file(), (
        f"{SEMANTIC_PACKAGE_LOCK} is missing: without it `npm ci` cannot "
        "reproduce the toolchain the projection was emitted with"
    )
    ignored = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "check-ignore", "-q", str(SEMANTIC_PACKAGE_LOCK)],
        check=False,
    )
    assert (
        ignored.returncode != 0
    ), f"{SEMANTIC_PACKAGE_LOCK} is gitignored, so it can never be committed"

    lock = _load_json(SEMANTIC_PACKAGE_LOCK)
    root = lock["packages"][""]
    declared = {**root.get("dependencies", {}), **root.get("devDependencies", {})}
    assert declared == PINNED_VERSIONS, (
        "the lockfile root records pins that differ from package.json: "
        f"{declared} != {PINNED_VERSIONS}"
    )
    for name, version in PINNED_VERSIONS.items():
        entry = lock["packages"].get(f"node_modules/{name}")
        assert entry is not None, f"{name} is not resolved by the lockfile"
        assert entry["version"] == version
        assert entry.get("integrity"), f"{name} is locked without an integrity hash"


def test_no_dependency_uses_a_file_or_link_reference() -> None:
    """TC-054: FR-005-CON-3: no ``file:`` or ``link:`` reference anywhere.

    A local reference makes the payload depend on one machine's directory
    layout, so a lockfile that carries one is not reproducible off that
    machine.
    """
    offenders: list[str] = []
    for path in _repo_package_jsons():
        package = _load_json(path)
        for field in (
            "dependencies",
            "devDependencies",
            "peerDependencies",
            "optionalDependencies",
        ):
            for name, spec in (package.get(field) or {}).items():
                if isinstance(spec, str) and spec.startswith(("file:", "link:")):
                    offenders.append(f"{path}: {field}.{name} = {spec}")

    lock = _load_json(SEMANTIC_PACKAGE_LOCK)
    for name, entry in lock.get("packages", {}).items():
        resolved = entry.get("resolved")
        if isinstance(resolved, str) and resolved.startswith(("file:", "link:")):
            offenders.append(f"{SEMANTIC_PACKAGE_LOCK}: {name!r} -> {resolved}")
        if entry.get("link") is True:
            offenders.append(f"{SEMANTIC_PACKAGE_LOCK}: {name!r} is a link")

    assert not offenders, offenders


def test_no_npmrc_exists_anywhere_in_the_repository() -> None:
    """TC-054: FR-005-CON-3: no ``.npmrc`` in the repository tree.

    Registry routing is the developer's npm configuration (FR-005 Inputs), not
    a file this repository ships; a committed ``.npmrc`` would pin the scope
    routing — and often a credential — into the payload.
    """
    found = [
        str(path.relative_to(REPO_ROOT))
        for path in REPO_ROOT.rglob(".npmrc")
        if ".git" not in path.parts
    ]
    assert not found, found


def test_poetry_lock_names_no_local_registry_source() -> None:
    """TC-054: the committed ``poetry.lock`` names only the published index.

    ``quire`` resolves from the internal index; ``pypi.ix`` is the local devpi
    that only exists on a developer's network, so a lockfile naming it cannot
    be installed by CI or by a consumer.
    """
    text = POETRY_LOCK.read_text(encoding="utf-8")
    assert "pypi.ix" not in text, (
        "poetry.lock names the local registry pypi.ix; switch the dependency "
        "back to the internal index before committing"
    )
    urls = [
        line.split("=", 1)[1].strip().strip('"')
        for line in text.splitlines()
        if line.startswith("url = ")
    ]
    assert urls, "poetry.lock declares no package source at all"
    for url in urls:
        assert INTERNAL_INDEX in url, f"poetry.lock names a foreign source: {url}"


# --------------------------------------------------------------------------
# TC-062 — FR-005-AC-9: the two shipping lists, and the two built payloads
# --------------------------------------------------------------------------


def test_pyproject_include_names_every_shipped_payload_entry() -> None:
    """TC-062: FR-005-AC-9: the sdist/wheel ``include`` list covers the payload."""
    declared = _pyproject_include_paths()
    missing = [
        entry
        for entry in PAYLOAD_ENTRIES
        if not any(_covers(path, entry) for path in declared)
    ]
    assert not missing, (
        f"pyproject [tool.poetry] include names no path covering {missing}; "
        f"declared: {declared}"
    )


def test_pyproject_include_names_no_typespec_toolchain_file() -> None:
    """TC-062: FR-005-AC-9: the toolchain is a build input and must not ship."""
    declared = _pyproject_include_paths()
    offenders = [
        path for path in declared for entry in TOOLCHAIN_ENTRIES if _covers(path, entry)
    ]
    assert not offenders, offenders


def test_npm_files_names_every_shipped_payload_entry() -> None:
    """TC-062: FR-005-AC-9: the npm ``files`` list covers the same payload."""
    declared = _npm_files()
    missing = [
        entry
        for entry in PAYLOAD_ENTRIES
        if not any(_covers(path, entry) for path in declared)
    ]
    assert (
        not missing
    ), f"package.json files names no path covering {missing}; declared: {declared}"


def test_npm_files_names_no_typespec_toolchain_file() -> None:
    """TC-062: FR-005-AC-9: the npm list carries no toolchain file either."""
    declared = _npm_files()
    offenders = [
        path for path in declared for entry in TOOLCHAIN_ENTRIES if _covers(path, entry)
    ]
    assert not offenders, offenders


def test_sdist_and_npm_tarball_carry_the_same_payload_entry_set(tmp_path) -> None:
    """TC-062: FR-005-AC-9: a built sdist and a packed tarball agree.

    Entry sets, not bytes: the sdist carries a ``PKG-INFO`` and a
    ``pyproject.toml`` the npm tarball does not, and comparing bytes would
    assert something neither FR-005-AC-9 nor any other requirement claims.
    """
    sdist_dir = tmp_path / "sdist"
    npm_dir = tmp_path / "npm"
    sdist_dir.mkdir()
    npm_dir.mkdir()

    subprocess.run(
        ["poetry", "build", "--format", "sdist", "--output", str(sdist_dir)],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    built = list(sdist_dir.glob("*.tar.gz"))
    assert len(built) == 1, f"expected one sdist, got {built}"
    with tarfile.open(built[0]) as archive:
        sdist_names = archive.getnames()
    sdist_payload = _payload_members(sdist_names, "/spec_artifacts_iso/")

    # `npm pack` runs scripts/stage-npm.mjs as `prepack`, which copies the
    # payload up to the repo root, and `postpack` removes it again. A failing
    # pack would leave the copies behind, and a `manifest.yaml` at the repo
    # root makes quire treat the root as a module root and shadows archetype
    # discovery — so unstage unconditionally, whatever the pack did.
    try:
        subprocess.run(
            ["npm", "pack", "--pack-destination", str(npm_dir)],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    finally:
        subprocess.run(
            ["node", "scripts/stage-npm.mjs", "--unstage"],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
    for staged in ("manifest.yaml", "schemas", "skeletons", "examples", "semantic"):
        assert not (
            REPO_ROOT / staged
        ).exists(), f"npm pack left {staged} staged at the repository root"

    packed = list(npm_dir.glob("*.tgz"))
    assert len(packed) == 1, f"expected one npm tarball, got {packed}"
    with tarfile.open(packed[0]) as archive:
        npm_names = archive.getnames()
    npm_payload = _payload_members(npm_names, "package/")

    assert sdist_payload, "the sdist carries no payload entry at all"
    assert npm_payload, "the npm tarball carries no payload entry at all"
    assert sdist_payload == npm_payload, {
        "only in sdist": sorted(sdist_payload - npm_payload),
        "only in npm tarball": sorted(npm_payload - sdist_payload),
    }

    for names, label in ((sdist_names, "sdist"), (npm_names, "npm tarball")):
        shipped_toolchain = [
            name
            for name in names
            for entry in TOOLCHAIN_ENTRIES
            if f"/{entry}" in name or name.endswith(f"/{entry}")
        ]
        assert (
            not shipped_toolchain
        ), f"{label} ships toolchain files: {shipped_toolchain}"
