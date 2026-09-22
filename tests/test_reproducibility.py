"""Reproducibility and offline resolution of the schema projection (NFR-001),
and the digest binding at load (FR-006-AC-8).

NFR-001 has three measurements and this module discharges two of them as tests
(byte reproducibility, wall time) and one as a manual gate (no network read).
FR-006-AC-8 (quire-rs FR-069, `agent-ix/quire-rs#390`) shipped in quire-rs
v0.47.0/0.47.1: a `data_schema.digest` mismatch is refused by *dropping* the
mismatched archetype from the registry rather than raising, so the assertion
is on `Registry.archetype_names()`, not on an exception — see
``test_tc063_...`` below.
"""

from __future__ import annotations

import hashlib
import pathlib
import shutil
import subprocess
import time

import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
PKG_ROOT = REPO_ROOT / "spec_artifacts_iso"
SCHEMAS_DIR = PKG_ROOT / "schemas"
MANIFEST_PATH = PKG_ROOT / "manifest.yaml"

#: NFR-001 metric 3: target 10 s, threshold 30 s. The threshold is the gate.
SCHEMAS_CHECK_THRESHOLD_SECONDS = 30.0


def _make(target: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["make", target], cwd=REPO_ROOT, capture_output=True, text=True
    )


def _emitted_bytes() -> dict[str, bytes]:
    return {
        path.name: path.read_bytes()
        for path in sorted(SCHEMAS_DIR.glob("*.json"))
        if not path.name.endswith("-frontmatter.schema.json")
    }


def _schemas_porcelain() -> str:
    """`git status --porcelain spec_artifacts_iso/schemas` — NFR-001 metric 1's
    declared instrument."""
    return subprocess.run(
        ["git", "-C", str(REPO_ROOT), "status", "--porcelain", str(SCHEMAS_DIR)],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def _on_disk_snapshot() -> dict[pathlib.Path, bytes]:
    """Every file under `schemas/`, so the tree can be put back exactly."""
    return {
        path: path.read_bytes()
        for path in sorted(SCHEMAS_DIR.rglob("*"))
        if path.is_file()
    }


def _restore(snapshot: dict[pathlib.Path, bytes]) -> None:
    for path in sorted(SCHEMAS_DIR.rglob("*")):
        if path.is_file() and path not in snapshot:
            path.unlink()
    for path, data in snapshot.items():
        if not path.is_file() or path.read_bytes() != data:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)


def test_tc056_two_schema_runs_reproduce_the_committed_bundle() -> None:
    """TC-056: NFR-001 metric 1: two consecutive `make schemas` runs on one tree
    produce byte-identical bundles for every emitted file, and that bundle is
    the **committed** one.

    Metric 1's target and threshold are both 0 files differing, and its declared
    method is `make schemas` twice plus
    `git status --porcelain spec_artifacts_iso/schemas` — so the comparison is
    against the committed bytes, not merely run 1 against run 2. Two runs
    agreeing with each other while both differ from what is committed is
    exactly the drift the manifest digests bind against, and comparing the runs
    only to each other would report that as a pass.

    The generator writes into the working tree, so the tree is snapshotted
    first and restored in a `finally`: a non-deterministic emitter fails this
    test without also leaving the checkout drifted for TC-047 and TC-061.
    """
    assert _schemas_porcelain() == "", (
        "`spec_artifacts_iso/schemas` is already dirty before the measurement; "
        "metric 1 compares a fresh projection to the committed bytes, so the "
        "tree must start clean"
    )
    snapshot = _on_disk_snapshot()
    committed = _emitted_bytes()
    assert committed, "there are no committed emitted schemas to reproduce"

    try:
        first = _make("schemas")
        assert first.returncode == 0, (
            f"`make schemas` failed: {first.stdout}\n{first.stderr}\n"
            "If the TypeSpec package is not installed, run `make semantic-install`."
        )
        after_first = _emitted_bytes()
        assert after_first, "the generator produced no emitted schema"

        second = _make("schemas")
        assert second.returncode == 0, f"second `make schemas` failed: {second.stderr}"
        after_second = _emitted_bytes()
        porcelain = _schemas_porcelain()
    finally:
        _restore(snapshot)

    differing = sorted(
        name
        for name in set(after_first) | set(after_second)
        if after_first.get(name) != after_second.get(name)
    )
    assert differing == [], (
        f"{len(differing)} file(s) differ between two consecutive `make schemas` "
        f"runs on one tree (metric 1 threshold is 0): {differing}"
    )

    drifted = sorted(
        name
        for name in set(committed) | set(after_second)
        if committed.get(name) != after_second.get(name)
    )
    assert drifted == [], (
        f"{len(drifted)} regenerated file(s) differ from the committed bundle "
        f"(metric 1 threshold is 0): {drifted}"
    )
    assert porcelain == "", (
        "`git status --porcelain spec_artifacts_iso/schemas` is not empty after "
        f"two `make schemas` runs: {porcelain}"
    )


def test_tc058_schemas_check_completes_within_the_threshold() -> None:
    """TC-058: NFR-001 metric 3: `make schemas-check` completes within 30 s on
    the reference machine.

    The assertion is on the threshold (30 s), not the target (10 s): a target
    missed is a report, a threshold missed is a defect. The measured duration is
    printed so a regression is visible in the run output before it crosses.
    """
    started = time.monotonic()
    result = _make("schemas-check")
    elapsed = time.monotonic() - started
    assert (
        result.returncode == 0
    ), f"`make schemas-check` failed: {result.stdout}\n{result.stderr}"
    print(f"NFR-001 metric 3: `make schemas-check` took {elapsed:.1f}s")
    assert elapsed < SCHEMAS_CHECK_THRESHOLD_SECONDS, (
        f"`make schemas-check` took {elapsed:.1f}s, over the "
        f"{SCHEMAS_CHECK_THRESHOLD_SECONDS:.0f}s threshold"
    )


def _module_copy_with_broken_digest(destination: pathlib.Path) -> pathlib.Path:
    """A copy of the module whose `FR` data_schema digest is off by one hex
    digit — everything else byte-identical."""
    module = destination / "spec_artifacts_iso"
    shutil.copytree(
        PKG_ROOT,
        module,
        ignore=shutil.ignore_patterns("semantic", "__pycache__", "*.pyc"),
    )
    manifest_path = module / "manifest.yaml"
    text = manifest_path.read_text(encoding="utf-8")

    manifest = yaml.safe_load(text)
    reference = next(
        entry["data_schema"]
        for entry in manifest["artifact_types"]
        if entry["name"] == "FR"
    )
    good = str(reference["digest"])
    tail = good[-1]
    broken = good[:-1] + ("0" if tail != "0" else "1")
    assert broken != good
    manifest_path.write_text(text.replace(good, broken), encoding="utf-8")

    # Sanity: the file the reference names is untouched, so the mismatch is
    # between the recorded digest and the shipped bytes, which is exactly what
    # FR-006-AC-8 asks the loader to refuse.
    shipped = (module / reference["schema"]).read_bytes()
    assert f"sha256:{hashlib.sha256(shipped).hexdigest()}" == good
    return destination


def test_tc063_a_broken_digest_drops_the_archetype_at_load(
    tmp_path: pathlib.Path,
) -> None:
    """TC-063: FR-006-AC-8: a copy of the module with one `data_schema.digest`
    altered by one hex digit is refused at load — the digest binding is real,
    not a no-op.

    quire-rs FR-069's loader half (`semantic.data-schema-digest-mismatch`,
    `src/semantic/resolver.rs`) does not raise on a mismatch: the loader
    (`src/loader/mod.rs`) records the failure internally and `continue`s past
    that archetype, so the registry loads with it *missing* rather than
    refusing to load at all. The `quire.Registry` Python binding exposes no
    diagnostics accessor — only `load_from`, `from_env`, `archetype_names`,
    `validate` (checked against the installed 0.47.1 wheel) — so
    `archetype_names()` is the only observable surface; the diagnostic code
    itself is not asserted here because nothing in the binding surfaces it.
    """
    import quire

    root = _module_copy_with_broken_digest(tmp_path)
    registry = quire.Registry.load_from([str(root)])
    assert "FR" not in registry.archetype_names(), (
        "the loader loaded FR despite its recorded digest not matching the "
        "shipped schema bytes — the digest binding is a no-op"
    )


def test_tc063_control_the_unmodified_module_still_loads(
    tmp_path: pathlib.Path,
) -> None:
    """Control for TC-063: the same copy, with its digests intact, loads with
    `FR` present.

    Without this the assertion above (`FR` absent) would be indistinguishable
    from a copy that never loaded anything at all — this pins the absence to
    the digest mismatch specifically, not to some unrelated breakage in the
    copy.
    """
    import quire

    module = tmp_path / "spec_artifacts_iso"
    shutil.copytree(
        PKG_ROOT,
        module,
        ignore=shutil.ignore_patterns("semantic", "__pycache__", "*.pyc"),
    )
    registry = quire.Registry.load_from([str(tmp_path)])
    assert "FR" in registry.archetype_names()
