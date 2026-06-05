#!/usr/bin/env bash
# NFR-006 (filament-core-service) verification: per-artifact CLI extract
# p95 ≤ 50 ms. Requires `quire` (from agent-ix/quire-cli) and `hyperfine`
# in PATH.
#
# Render was removed (FR-002 CR, 2026-06-04): the per-archetype skeletons are
# the authoring source of truth and quire-rs enforces structure with no render
# step. The hot path is now `quire extract <doc.md> --module …`, so the bench
# exercises that against a filled skeleton.
#
# Usage: scripts/bench_quire_cli.sh
#
# Reports mean + stddev per archetype via hyperfine; CI gate stays
# enforced upstream in quire-cli's bench lane, not here.
#
# If `quire` is not installed, exit 0 with an informational message so
# developers without quire-cli can still run unrelated scripts.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MODULE="$ROOT/spec_artifacts_iso"

if ! command -v quire >/dev/null; then
  echo "quire not on PATH — install via 'cargo install --git https://github.com/agent-ix/quire-cli quire-cli'." >&2
  echo "Skipping bench (not a hard error; CI gate lives in quire-cli)." >&2
  exit 0
fi

if ! command -v hyperfine >/dev/null; then
  echo "hyperfine not on PATH — install via 'cargo install hyperfine'" >&2
  exit 1
fi

# The FR skeleton is a filled, conformant authoring document. extract reads
# its archetype from frontmatter and yields structured records + edges.
DOC_FR="$MODULE/skeletons/fr.md"

if [[ ! -f "$DOC_FR" ]]; then
  echo "FR skeleton not found at $DOC_FR" >&2
  exit 1
fi

# One bench run per archetype the original harness covered (fr). Extend
# by adding more archetype/document pairs below.
hyperfine -N --warmup 5 --runs 100 \
  --command-name "quire extract FR" \
  "quire extract $DOC_FR --module $MODULE"
