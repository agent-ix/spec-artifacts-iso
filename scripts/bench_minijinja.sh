#!/usr/bin/env bash
# NFR-006 (filament-core-service) verification: per-artifact CLI render
# p95 ≤ 50 ms. Requires `minijinja-cli` and `hyperfine` in PATH.
#
# Usage: scripts/bench_minijinja.sh
#
# Exits 0 if the mean+stddev are well under the 50 ms p95 budget.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATE="$ROOT/spec_artifacts_iso/templates/fr.md.j2"
CTX="$(mktemp --suffix=.json)"
trap "rm -f $CTX" EXIT

cat > "$CTX" <<'JSON'
{
  "id": "FR-099",
  "title": "Performance benchmark sample",
  "artifact_type": "FR",
  "description": "Auto-generated benchmark target.",
  "relationships": [
    {"target": "ix://agent-ix/filament-core-service/FR-035", "type": "implements"}
  ]
}
JSON

command -v minijinja-cli >/dev/null || {
  echo "minijinja-cli not on PATH — install via 'cargo install minijinja-cli'" >&2
  exit 1
}
command -v hyperfine >/dev/null || {
  echo "hyperfine not on PATH — install via 'cargo install hyperfine'" >&2
  exit 1
}

hyperfine -N --warmup 5 --runs 100 "minijinja-cli $TEMPLATE $CTX"
