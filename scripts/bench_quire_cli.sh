#!/usr/bin/env bash
# NFR-006 (filament-core-service) verification: per-artifact CLI render
# p95 ≤ 50 ms. Requires `quire` (from agent-ix/quire-cli) and `hyperfine`
# in PATH.
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

CTX_FR="$(mktemp --suffix=.json)"
trap 'rm -f "$CTX_FR"' EXIT

cat > "$CTX_FR" <<'JSON'
{
  "id": "FR-099",
  "title": "Performance benchmark sample",
  "artifact_type": "FR",
  "object": "core/scheduler",
  "description": "Auto-generated benchmark target.",
  "relationships": [
    {
      "target": "ix://agent-ix/filament-core-service/FR-035",
      "type": "implements",
      "cardinality": "1..1"
    }
  ]
}
JSON

# One bench run per archetype the original harness covered (fr). Extend
# by adding more archetype/context pairs below.
hyperfine -N --warmup 5 --runs 100 \
  --command-name "quire render FR" \
  "quire render FR --module $MODULE --data $CTX_FR"
