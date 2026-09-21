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

// npm does not run `postpack` when `pack`/`publish` fails, so a failed pack can
// leave the staged copies behind — and a root `manifest.yaml` makes quire treat
// the repo root as a module, which breaks archetype discovery. Staging is
// therefore idempotent: it clears the previous staging before writing, so a
// leftover from a failed pack is cleaned by the next one rather than compounding.
// Every staged name is also gitignored, so a leftover is never an untracked
// surprise in `git status`.

const PAYLOAD = [
  "manifest.yaml",
  "schemas",
  "skeletons",
  "mappings.yaml",
  "mappings.schema.json",
  "examples",
  "semantic/main.tsp",
  "semantic/generated",
];
// The record of what THIS run staged, one payload path per line. `--unstage`
// removes only what the record names, so a repo-root path that legitimately
// carries a payload name — one this script never copied — is never deleted by
// a postpack. The name ends in `.log`, which the repo's .gitignore already
// covers, and is absent from package.json `files`, so it is neither committed
// nor packed.
const RECORD = join(root, "stage-npm-staged.log");

/** Drop the empty `semantic/` that removing its two payload entries leaves. */
function pruneEmptySemantic() {
  const leftover = join(root, "semantic");
  if (existsSync(leftover) && readdirSync(leftover).length === 0) {
    rmSync(leftover, { recursive: true, force: true });
  }
}

if (unstage) {
  if (!existsSync(RECORD)) {
    console.log(
      `stage-npm: no staging record (${"stage-npm-staged.log"}); nothing was staged by this script, leaving the repo root untouched`,
    );
    process.exit(0);
  }
  const staged = readFileSync(RECORD, "utf8")
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);
  for (const item of staged) {
    if (!PAYLOAD.includes(item)) {
      console.error(
        `stage-npm: staging record names ${item}, which is not a payload path; refusing to remove it`,
      );
      process.exit(1);
    }
    const to = join(root, item);
    if (existsSync(to)) {
      rmSync(to, { recursive: true, force: true });
      console.log(`stage-npm: unstaged ${item}`);
    }
  }
  pruneEmptySemantic();
  rmSync(RECORD, { force: true });
  process.exit(0);
}

const staged = [];
for (const item of PAYLOAD) {
  const to = join(root, item);
  const from = join(root, inner, item);
  if (!existsSync(from)) continue;
  rmSync(to, { recursive: true, force: true });
  mkdirSync(dirname(to), { recursive: true });
  cpSync(from, to, { recursive: true });
  staged.push(item);
  console.log(`stage-npm: ${inner}/${item} -> ${item}`);
}
writeFileSync(RECORD, staged.map((item) => `${item}\n`).join(""));

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
