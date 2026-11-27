"""The NFR-001 offline verifier isolates both measured commands."""

from __future__ import annotations

import os
import pathlib
import subprocess

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
VERIFIER = REPO_ROOT / "scripts" / "verify_offline.sh"


def _fake_tools(
    tmp_path: pathlib.Path, *, unshare_status: int = 0, make_status: int = 0
) -> tuple[pathlib.Path, pathlib.Path]:
    log = tmp_path / "commands.log"
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    unshare = bin_dir / "unshare"
    unshare.write_text(
        "#!/usr/bin/env python3\n"
        "import os, pathlib, subprocess, sys\n"
        "args = sys.argv[1:]\n"
        "with pathlib.Path(os.environ['OFFLINE_LOG']).open('a') as log:\n"
        "    log.write(' '.join(args) + '\\n')\n"
        f"if args == ['--net', '/bin/true'] and {unshare_status}:\n"
        f"    raise SystemExit({unshare_status})\n"
        "if args[:1] != ['--net']:\n"
        "    raise SystemExit(97)\n"
        "raise SystemExit(subprocess.run(args[1:]).returncode)\n",
        encoding="utf-8",
    )
    unshare.chmod(0o755)
    make = bin_dir / "make"
    make.write_text(
        "#!/usr/bin/env python3\n"
        "import os, pathlib, sys\n"
        "with pathlib.Path(os.environ['OFFLINE_LOG']).open('a') as log:\n"
        "    log.write('MAKE ' + ' '.join(sys.argv[1:]) + '\\n')\n"
        f"raise SystemExit({make_status} if sys.argv[1:] == ['test'] else 0)\n",
        encoding="utf-8",
    )
    make.chmod(0o755)
    return log, bin_dir


def _run_verifier(
    bin_dir: pathlib.Path, log: pathlib.Path
) -> subprocess.CompletedProcess[str]:
    env = {
        **os.environ,
        "PATH": f"{bin_dir}:/usr/bin:/bin",
        "OFFLINE_LOG": str(log),
    }
    return subprocess.run(
        ["bash", str(VERIFIER)],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.trace("TC-057", "NFR-001-M-2")
def test_tc057_offline_verifier_isolates_both_commands_and_propagates_failure(
    tmp_path: pathlib.Path,
) -> None:
    log, bin_dir = _fake_tools(tmp_path, make_status=23)

    result = _run_verifier(bin_dir, log)

    assert result.returncode == 23
    assert log.read_text(encoding="utf-8").splitlines() == [
        "--net /bin/true",
        "--net make schemas-check",
        "MAKE schemas-check",
        "--net make test",
        "MAKE test",
    ]


@pytest.mark.trace("TC-057", "NFR-001-M-2")
def test_tc057_offline_verifier_fails_closed_when_namespace_is_unavailable(
    tmp_path: pathlib.Path,
) -> None:
    log, bin_dir = _fake_tools(tmp_path, unshare_status=17)

    result = _run_verifier(bin_dir, log)

    assert result.returncode == 17
    assert log.read_text(encoding="utf-8").splitlines() == ["--net /bin/true"]
