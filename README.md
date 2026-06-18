# spec-artifacts-iso

> Filament Module: ISO-style spec artifacts (FR, NFR, StR, US, IT, TC) — unified-shape archetypes (frontmatter schema + body_extraction asserts) validated by quire-rs; per-archetype authoring skeletons are the source of truth (no render templates); iso-spec-core grammar

An Agent-IX Filament module loaded by [`quire-cli`](https://github.com/agent-ix/quire-cli) and [`ix-spec`](https://github.com/agent-ix/ix-spec). The module path is `spec_artifacts_iso`: a `manifest.yaml`, per-kind authoring `skeletons/`, and frontmatter `schemas/`. It contributes doc-backed `archetypes` and `artifact_types` (ISO-style requirement artifacts) — no embedded `object_types`.

## Installing quire-cli

This module is consumed by the `quire` binary from [`quire-cli`](https://github.com/agent-ix/quire-cli), published on the public npm registry, so no auth or registry config is needed:

```bash
npm install -g @agent-ix/quire-cli
```

See https://github.com/agent-ix/quire-cli#install for details.

## Artifact types provided

The `Spec` archetype (kind `spec`) is a doc-backed container that holds ISO-style requirement artifacts (its composition expects `StR`, `FR`, `NFR`, `US`, `IT`, `TC`). The artifact types below live inside it.

| Kind | ID pattern | Description |
|:-----|:-----------|:------------|
| `FR` | `FR-{next:03d}` | Functional Requirement (ISO/IEC/IEEE 29148): required `## Description` (normative shall/must language) + `## Acceptance Criteria` (`ID \| Criteria \| Verification` table, `{id}-AC-N`) + `## Dependencies`; optional `## Inputs`/`## Outputs`/`## Behavior` and a `## Constraints` table (`{id}-CON-N`). |
| `NFR` | `NFR-{next:03d}` | Non-Functional Requirement / quality constraint (ISO/IEC/IEEE 29148, attribute from ISO 25010): required `## Statement` + `## Measurement and Evaluation` (`Metric \| Target \| Threshold \| Method` table) + `## Verification`; `quality_attribute` is a frontmatter enum. |
| `StR` | `StR-{next:03d}` | Stakeholder Requirement (ISO/IEC/IEEE 29148 stakeholder triad): required `## Stakeholder Need` + `## Rationale` + `## Validation Criteria`; stakeholders, context, constraints, and traceability are optional. |
| `US` | `US-{next:03d}` | User Story (ISO/IEC/IEEE 29148): a single required `## Story` matching the "As a … / I want … / So that …" shape; all other sections are contextual and informative. |
| `IT` | `IT-{next:03d}` | Integration Test case (ISO/IEC/IEEE 29119): required six-section set — `## Objective`, `## Target Integration`, `## Preconditions`, `## Inputs`, `## Test Procedure`, `## Expected Results`. |
| `TC` | `TC-{next:03d}` | Test Case (ISO/IEC/IEEE 29119 essentials): required `## Description` + `## Test Procedure` + `## Expected Results`. |
| `master-requirements` | _(bundle root)_ | Master Requirements Specification: H1 fixed to "Master Requirements Specification"; required `## Purpose`, `## Scope`, `## System Overview`, `## Requirements Architecture`, `## References`; the repo-level `depends_on:` dependency manifest. |
| `index` | _(`index.md`)_ | OKF bundle directory index: required `## Contents` listing the artifacts in the directory via content-local relative links (not knowledge-graph edges). |
| `log` | _(`log.md`)_ | OKF bundle update log: required `## History` of dated, non-normative structural changes to the bundle. |

## How this module is used

### With ix-spec (recommended)

```bash
ix-spec plugin install path:../spec-artifacts-iso   # bundled root module; shown for completeness
ix-spec catalog list                                # list available artifact kinds
ix-spec catalog show FR                             # inspect the FR skeleton + schema
ix-spec write . --types FR,NFR                      # scaffold new artifacts
ix-spec review                                      # validate + review the spec
```

See https://github.com/agent-ix/ix-spec.

### With quire-cli directly

```bash
quire schema FR --module ./spec_artifacts_iso                    # show the FR authoring skeleton/schema
quire validate spec/**/*.md --module ./spec_artifacts_iso        # validate Markdown artifacts
quire extract spec/functional/FR-001.md --module ./spec_artifacts_iso --archetype FR
```

See https://github.com/agent-ix/quire-cli#usage-instructions.

## Authoring conventions

- **FR body**: required = `## Description` + `## Acceptance Criteria` (table).
  `## Inputs` / `## Outputs` / `## Behavior` / `## Constraints` /
  `## Dependencies` are optional, all at **level 2** — there is no
  `## Specification` umbrella. Object FRs carry their kind's anchor sections
  instead of I/O.
- **`object:` frontmatter** is the canonical object-kind field (never
  `object_type:`). It is optional for vanilla behavioral FRs and required for
  object FRs — kind anchors and extraction hang off it.
- **NFR body**: required = `## Statement` + `## Measurement and Evaluation`
  (`Metric|Target|Threshold|Method` table) + `## Verification`;
  `quality_attribute` is a frontmatter enum (ISO 25010), not a section.
- **AC Verification cells** use the ISO 29148 methods — `Inspection`,
  `Analysis`, `Demonstration`, `Test` — optionally annotated `Test (TC-035)`.
  Checked by the module's `ac-verification-method` lint rule (`quire lint`).
- **Relationships**: author the explicit `relationships:` array (typed verbs,
  incl. `specifies` for object FR → behavioral FR). Bare-ID sugar fields
  (`depends_on:` etc.) are read-side ingestion tolerance only — except in
  `spec.md` (master-requirements), where `depends_on:` is the repo-level
  dependency manifest.

## Development

This is a flat-layout Python 3.13+ package (`spec_artifacts_iso`, no `src/`) managed with Poetry, built and published via GitHub Actions to Google Artifact Registry (PyPI-compatible). All work goes through the Makefile:

```bash
make install                  # install dependencies into the Poetry venv
make test                     # run pytest
make lint                     # ruff + black --check
make format                   # auto-format (black + ruff --fix)
make build                    # build wheel + sdist under dist/
make update-lock              # update poetry.lock
make local-publish            # build + publish to local pypi.ix
```

| Target | Description |
|:-------|:------------|
| `install` | Install dependencies in the Poetry venv |
| `test` | Run tests |
| `lint` | Run linting (Ruff + Black check) |
| `format` | Auto-format code (Black + Ruff --fix) |
| `build` | Build wheel and sdist artifacts |
| `clean` | Remove all build artifacts |
| `version` / `info` | Show version / Git info |
| `update-lock` | Update `poetry.lock` |
| `add-package p=<name>` | Add a runtime dependency |
| `add-dev-package p=<name>` | Add a dev dependency |
| `use-local p=<name>` / `use-upstream p=<name>` | Switch a dep to/from local `pypi.ix` |
| `local-publish` | Build and publish to local PyPI |

CI runs on `push`, `pull_request`, and `v*.*.*` tags: it runs tests and lint, builds with `poetry build`, and publishes to Artifact Registry via `twine upload -r internal-pypi`. Versioning is dynamic from the Git tag. Required CI config: secret `GCP_SERVICE_ACCOUNT_KEY`; variables `GCP_REGION`, `GCP_PROJECT_NAME`, `GCP_PYPI`.

For local install from the cluster PyPI proxy (after `make local-publish`):

```bash
pip install --index-url http://pypi.ix/root/dev/+simple/ spec_artifacts_iso
```
