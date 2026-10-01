#!/usr/bin/env node
/**
 * spec-artifacts-iso JSON Schema projection (FR-005).
 *
 * Runs the official `@typespec/json-schema` emitter through `tsp compile`,
 * keeps only the files whose `$id` sits under this module's base (the emitter
 * also writes the imported semantic-core models; those ship in the vendored
 * semantic-core bundle, never here), applies the filament-core-data issue #31
 * `$id` normalization (absolute `$id` for any schema the emitter left
 * relative), writes the files to
 * `spec_artifacts_iso/schemas/<Model>.json`.
 *
 *   node scripts/generate.mjs          # regenerate (make schemas)
 *   node scripts/generate.mjs --check  # fail on any byte difference (make schemas-check)
 *
 * Node built-ins only; no formatter dependency. Output is `JSON.stringify(schema, null, 2)`
 * plus one trailing newline, so two runs on one tree are byte-identical (NFR-001).
 */

import { execFileSync } from "node:child_process";
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
const SEMANTIC_CORE_BASE = "https://schemas.agent-ix.org/semantic-core/";

const INSTALL_HINT = "run `make semantic-install` first";

/** Turn a bare ENOENT under node_modules into the command that fixes it. */
function missingInstall(error, what) {
  if (error && error.code === "ENOENT") {
    return new Error(`${what} is not installed under ${packageRoot}/node_modules — ${INSTALL_HINT}`);
  }
  return error;
}

/** The `@jsonSchema` base declared in main.tsp (FR-005). */
function packageBase() {
  const source = readFileSync(resolve(packageRoot, "main.tsp"), "utf8");
  const base = source.match(/@jsonSchema\("([^"]+)"\)/)?.[1];
  if (!base) throw new Error("main.tsp declares no @jsonSchema base");
  return { base };
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
  const { base } = packageBase();
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
    // files dropped from the bundle without a word. An
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
    const files = new Map();
    for (const [name, schema] of all) {
      const id = typeof schema.$id === "string" ? schema.$id : "";
      if (id.startsWith(SEMANTIC_CORE_BASE)) {
        continue;
      }
      files.set(name, schema);
    }
    const rewritten = normalize(files, base);
    const rendered = new Map([...files].map(([name, schema]) => [name, render(schema)]));
    return { rendered };
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
  const { rendered } = emit();
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
    if (problems.length > 0) {
      console.error(`schema projection differs from the committed output:\n  ${problems.join("\n  ")}`);
      process.exit(1);
    }
    console.log(`schema projection is up to date (${rendered.size} files)`);
    return;
  }
  for (const name of readdirSync(outputDir).filter(isProjection)) rmSync(join(outputDir, name));
  for (const [name, text] of rendered) writeFileSync(join(outputDir, name), text);
  console.log(`schema projection written (${rendered.size} files)`);
}

main();
