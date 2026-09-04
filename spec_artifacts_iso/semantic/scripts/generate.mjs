#!/usr/bin/env node
/**
 * spec-artifacts-iso JSON Schema projection (FR-005).
 *
 * Runs the official `@typespec/json-schema` emitter through `tsp compile`,
 * keeps only the files whose `$id` sits under this module's base (the emitter
 * also writes the imported semantic-core models; those ship in the vendored
 * semantic-core bundle, never here), applies the filament-core-data issue #31
 * `$id` normalization (absolute `$id` for any schema the emitter left
 * relative; a recorded no-op when none is), writes the files to
 * `spec_artifacts_iso/schemas/<Model>.json`, and records
 * `generated/toolchain.json` with the compiler and emitter versions plus a
 * digest over the emitted files (name + newline + bytes, sorted).
 *
 *   node scripts/generate.mjs          # regenerate (make schemas)
 *   node scripts/generate.mjs --check  # fail on any byte difference (make schemas-check)
 *
 * Node built-ins only; no formatter dependency. Output is `JSON.stringify(schema, null, 2)`
 * plus one trailing newline, so two runs on one tree are byte-identical (NFR-001).
 */

import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import {
  existsSync,
  mkdtempSync,
  readdirSync,
  readFileSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const packageRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const moduleRoot = resolve(packageRoot, "..");
const repoRoot = resolve(moduleRoot, "..");
const outputDir = resolve(moduleRoot, "schemas");
const toolchainPath = resolve(packageRoot, "generated/toolchain.json");
const SEMANTIC_CORE_BASE = "https://schemas.agent-ix.org/semantic-core/";
const NORMALIZATION = {
  name: "issue-31-absolute-id",
  version: "1.0.0",
  issue: "https://github.com/agent-ix/filament-core-data/issues/31",
};

const INSTALL_HINT = "run `make semantic-install` first";

/** Turn a bare ENOENT under node_modules into the command that fixes it. */
function missingInstall(error, what) {
  if (error && error.code === "ENOENT") {
    return new Error(`${what} is not installed under ${packageRoot}/node_modules — ${INSTALL_HINT}`);
  }
  return error;
}

function version(name) {
  try {
    return JSON.parse(
      readFileSync(resolve(packageRoot, "node_modules", name, "package.json"), "utf8"),
    ).version;
  } catch (error) {
    throw missingInstall(error, name);
  }
}

/**
 * Digest of the resolved semantic-core's own `generated/toolchain.json`, so the
 * copy this module compiled against is identified by bytes rather than by a
 * version string two registries could disagree on (SR-006 FND-246).
 */
function semanticCoreDigest() {
  const path = resolve(
    packageRoot,
    "node_modules/@agent-ix/semantic-core/generated/toolchain.json",
  );
  try {
    return `sha256:${createHash("sha256").update(readFileSync(path)).digest("hex")}`;
  } catch (error) {
    throw missingInstall(error, "@agent-ix/semantic-core");
  }
}

/** The manifest `version` is the authority; the `@jsonSchema` base must embed it (FR-005). */
function packageBase() {
  const manifest = readFileSync(resolve(moduleRoot, "manifest.yaml"), "utf8");
  const manifestVersion = manifest.match(/^version:\s*["']?([0-9]+\.[0-9]+\.[0-9]+)["']?\s*$/m)?.[1];
  if (!manifestVersion) throw new Error("manifest.yaml declares no top-level semver version");
  const source = readFileSync(resolve(packageRoot, "main.tsp"), "utf8");
  const declared = source.match(/@jsonSchema\("([^"]+)"\)/)?.[1];
  if (!declared) throw new Error("main.tsp declares no @jsonSchema base");
  const expected = `https://schemas.agent-ix.org/agent-ix/spec-artifacts-iso/${manifestVersion}/`;
  if (declared !== expected) {
    throw new Error(
      `@jsonSchema base ${declared} does not match manifest version ${manifestVersion} (expected ${expected})`,
    );
  }
  return { base: expected, manifestVersion };
}

function normalize(files, base) {
  const rewritten = [];
  for (const [name, schema] of files) {
    if (typeof schema.$id === "string" && !/^https?:\/\//.test(schema.$id)) {
      schema.$id = `${base}${schema.$id}`;
      rewritten.push(name);
    }
  }
  return rewritten;
}

function render(schema) {
  return `${JSON.stringify(schema, null, 2)}\n`;
}

function emit() {
  const { base, manifestVersion } = packageBase();
  const tsp = resolve(packageRoot, "node_modules/.bin/tsp");
  if (!existsSync(tsp)) {
    throw new Error(`the TypeSpec compiler (${tsp}) is not installed — ${INSTALL_HINT}`);
  }
  const scratch = mkdtempSync(join(tmpdir(), "spec-artifacts-iso-emit-"));
  try {
    try {
      execFileSync(
        tsp,
        ["compile", packageRoot, "--option", `@typespec/json-schema.emitter-output-dir=${scratch}`],
        { cwd: packageRoot, stdio: "pipe" },
      );
    } catch (error) {
      throw missingInstall(error, "the TypeSpec compiler (node_modules/.bin/tsp)");
    }
    // Read the emitter's output explicitly rather than assuming it is flat: a
    // future emitter that writes into a subdirectory would otherwise have those
    // files dropped from both the bundle and the digest without a word. An
    // unexpected entry is a hard failure, never a silent omission.
    const entries = readdirSync(scratch, { withFileTypes: true }).sort((a, b) =>
      a.name < b.name ? -1 : a.name > b.name ? 1 : 0,
    );
    const unexpected = entries
      .filter((entry) => !(entry.isFile() && entry.name.endsWith(".json")))
      .map((entry) => `${entry.name}${entry.isDirectory() ? "/" : ""}`);
    if (unexpected.length > 0) {
      throw new Error(
        `the JSON Schema emitter wrote entries this script does not read:\n  ${unexpected.join("\n  ")}\n` +
          "generate.mjs bundles a flat directory of *.json files; update it before regenerating.",
      );
    }
    const all = entries.map((entry) => [
      entry.name,
      JSON.parse(readFileSync(join(scratch, entry.name), "utf8")),
    ]);
    const excluded = [];
    const files = new Map();
    for (const [name, schema] of all) {
      const id = typeof schema.$id === "string" ? schema.$id : "";
      if (id.startsWith(SEMANTIC_CORE_BASE)) {
        excluded.push(name);
        continue;
      }
      files.set(name, schema);
    }
    const rewritten = normalize(files, base);
    const rendered = new Map([...files].map(([name, schema]) => [name, render(schema)]));
    const digest = createHash("sha256");
    for (const [name, text] of rendered) digest.update(`${name}\n${text}`);
    const toolchain = {
      compiler: { name: "@typespec/compiler", version: version("@typespec/compiler") },
      emitter: { name: "@typespec/json-schema", version: version("@typespec/json-schema") },
      semanticCore: {
        name: "@agent-ix/semantic-core",
        version: version("@agent-ix/semantic-core"),
        toolchainDigest: semanticCoreDigest(),
      },
      normalization: {
        ...NORMALIZATION,
        applied: rewritten.length > 0,
        rewrittenFiles: rewritten,
        note: rewritten.length === 0 ? "no-op: the emitter produced no relative $id" : undefined,
      },
      base,
      manifestVersion,
      excludedImportedFiles: excluded,
      files: [...rendered.keys()],
      digest: `sha256:${digest.digest("hex")}`,
    };
    return { rendered, toolchain: render(toolchain) };
  } finally {
    rmSync(scratch, { recursive: true, force: true });
  }
}

/** Files under schemas/ that are not projections: the hand-authored frontmatter schemas. */
function isProjection(name) {
  return name.endsWith(".json") && !name.endsWith("-frontmatter.schema.json");
}

function main() {
  const check = process.argv.includes("--check");
  const { rendered, toolchain } = emit();
  if (check) {
    const problems = [];
    for (const [name, text] of rendered) {
      const path = join(outputDir, name);
      let current;
      try {
        current = readFileSync(path, "utf8");
      } catch {
        current = undefined;
      }
      if (current !== text) problems.push(relative(repoRoot, path));
    }
    let committed = [];
    try {
      committed = readdirSync(outputDir).filter(isProjection);
    } catch {
      problems.push(`${relative(repoRoot, outputDir)} (missing; run make schemas)`);
    }
    for (const name of committed)
      if (!rendered.has(name)) problems.push(`${relative(repoRoot, join(outputDir, name))} (stale)`);
    let currentToolchain;
    try {
      currentToolchain = readFileSync(toolchainPath, "utf8");
    } catch {
      currentToolchain = undefined;
    }
    if (currentToolchain !== toolchain) problems.push(relative(repoRoot, toolchainPath));
    if (problems.length > 0) {
      console.error(`schema projection differs from the committed output:\n  ${problems.join("\n  ")}`);
      process.exit(1);
    }
    console.log(`schema projection is up to date (${rendered.size} files)`);
    return;
  }
  for (const name of readdirSync(outputDir).filter(isProjection)) rmSync(join(outputDir, name));
  for (const [name, text] of rendered) writeFileSync(join(outputDir, name), text);
  writeFileSync(toolchainPath, toolchain);
  console.log(`schema projection written (${rendered.size} files)`);
}

main();
