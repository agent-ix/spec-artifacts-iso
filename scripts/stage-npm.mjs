#!/usr/bin/env node
// Stage the Filament-module payload for npm packaging.
//
// Non-destructive: copies manifest.yaml + schemas/ + skeletons/ from the inner
// `spec_*` Python package dir up to the repo root, so the published npm tarball
// IS the module root (manifest.yaml at the top, schema refs resolve relative to
// it). The inner dir remains the single source of truth; the staged copies are
// gitignored. Runs automatically via the `prepack` script before `npm pack` /
// `npm publish`, and `--unstage` (the `postpack` script) removes the copies
// again.
//
// The cleanup is not cosmetic. A `manifest.yaml` at the repo root makes quire
// treat the root as a module root, which shadows archetype discovery and makes
// `quire validate` fail on documents whose archetype comes from another
// module. Leaving the staged copies behind after a pack breaks the repo's own
// spec gate, so packing always unstages.
// Node built-ins only, zero dependencies.
import {
  existsSync,
  readdirSync,
  statSync,
  rmSync,
  cpSync,
  mkdirSync,
  readFileSync,
  writeFileSync,
} from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");

// Locate the inner module dir: a `spec_*` directory containing manifest.yaml.
const inner = readdirSync(root).find(
  (name) =>
    /^spec_/.test(name) &&
    statSync(join(root, name)).isDirectory() &&
    existsSync(join(root, name, "manifest.yaml")),
);
if (!inner) {
  console.error("stage-npm: no inner spec_* dir with manifest.yaml found");
  process.exit(1);
}

const unstage = process.argv.includes("--unstage");

const PAYLOAD = [
  "manifest.yaml",
  "module-manifest.schema.json",
  "schemas",
  "skeletons",
  "mappings.yaml",
  "mappings.schema.json",
  "examples",
  "semantic/main.tsp",
  "semantic/generated",
];
for (const item of PAYLOAD) {
  const to = join(root, item);
  if (unstage) {
    if (existsSync(to)) {
      rmSync(to, { recursive: true, force: true });
      console.log(`stage-npm: unstaged ${item}`);
    }
    continue;
  }
  const from = join(root, inner, item);
  if (!existsSync(from)) continue;
  rmSync(to, { recursive: true, force: true });
  mkdirSync(dirname(to), { recursive: true });
  cpSync(from, to, { recursive: true });
  console.log(`stage-npm: ${inner}/${item} -> ${item}`);
}
if (unstage) {
  // `semantic/main.tsp` and `semantic/generated` leave an empty `semantic/`.
  const leftover = join(root, "semantic");
  if (existsSync(leftover) && readdirSync(leftover).length === 0) {
    rmSync(leftover, { recursive: true, force: true });
  }
  process.exit(0);
}

// Version sync: when packing from a CI tag (vX.Y.Z), stamp package.json so the
// tarball is named/published at the tag version. No-op locally (no env / no match).
const m = (process.env.GITHUB_REF_NAME ?? "").match(
  /^v?(\d+\.\d+\.\d+(?:[-+].+)?)$/,
);
if (m) {
  const pkgPath = join(root, "package.json");
  const pkg = JSON.parse(readFileSync(pkgPath, "utf8"));
  if (pkg.version !== m[1]) {
    pkg.version = m[1];
    writeFileSync(pkgPath, JSON.stringify(pkg, null, 2) + "\n");
    console.log(`stage-npm: version -> ${m[1]}`);
  }
}
