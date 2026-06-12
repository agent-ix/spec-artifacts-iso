# 🐍 spec-artifacts-iso

> Filament Module: ISO-style spec artifacts (FR/NFR/StR/US/IT/TC/AC/CON) — unified-shape archetypes (frontmatter JSON Schemas + `body_extraction` asserts) with per-archetype authoring **skeletons** as the source of truth, validated by quire-rs. No render templates.

---

## ✍️ Authoring conventions (format-walkthrough decisions, 2026-06-11)

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

---

## 📐 Project Structure and Development Philosophy

- **Library Name:** `spec_artifacts_iso`
- **Layout:** Flat project layout (package at root, no `src/`)
- **Language:** Python 3.13+
- **Dependency Management:** [Poetry](https://python-poetry.org/)
- **Build and CI:** GitHub Actions
- **Publishing:** Google Artifact Registry (PyPI-compatible)

---

## 🛠 Prerequisites

- **Python 3.13+** installed on your system
- **Poetry 2.x** installed (`pip install poetry` or [official installer](https://python-poetry.org/docs/#installation))
- **devpi-client** (optional, for local publishing): `pip install devpi-client`

---

## 🚀 Quick Start

```bash
# Install dependencies and create venv
make install

# Run tests
make test

# Format code
make format

# Lint code
make lint

# Build distribution
make build
```

---

## 📦 Build Process

- **Local Development**:
  - `make install` - Install dependencies in Poetry venv
  - `make test` - Run tests
  - `make format` - Auto-format code (Black + Ruff)
  - `make lint` - Run linting checks
- **Artifact Building**:
  - `make build` - Build wheel and sdist under `dist/`
- **Artifact Upload**:
  - Artifacts uploaded via `twine upload` in CI

---

## 🚀 Continuous Integration (CI)

- **GitHub Actions Workflow**:
  - Triggers: `push`, `pull_request`, `tag v*.*.*`
  - Runs tests and lint checks
  - Builds artifacts with `poetry build`
  - Publishes to Google Artifact Registry using `twine upload -r internal-pypi`

---

## 🔑 Required GitHub Secrets

| Secret Name | Purpose |
|:------------|:--------|
| `GCP_SERVICE_ACCOUNT_KEY` | Raw JSON of GCP Service Account Key |

| Variable Name | Purpose |
|:------------|:--------|
| `GCP_REGION` | GCP Region for Artifact Registry (e.g., `us-west1`) |
| `GCP_PROJECT_NAME` | GCP Project ID (e.g., `agent-ix`) |
| `GCP_PYPI` | Artifact Registry repository name (e.g., `internal-pypi`) |

---

## 🐳 Makefile Targets

| Target | Description |
|:-------|:------------|
| `install` | Install dependencies in Poetry venv |
| `build` | Build wheel and sdist artifacts |
| `test` | Run tests |
| `lint` | Run linting (Ruff + Black check) |
| `format` | Auto-format code (Black + Ruff --fix) |
| `shell` | Open Poetry shell |
| `clean` | Remove all build artifacts |
| `version` | Show project version |
| `info` | Show Git and version info |
| `update-lock` | Update poetry.lock |
| `update-packages` | Update all dependencies |
| `add-package p=<name>` | Add a production dependency |
| `add-dev-package p=<name>` | Add a dev dependency |
| `local-publish` | Build and publish to local PyPI |

---

## 🏠 Local Development with Local PyPI

For local development and testing, you can publish packages to the local PyPI proxy.

### Prerequisites

1. **Local Kubernetes cluster** running with PyPI proxy:
   ```bash
   # In the local repo
   make up
   make pypi-up
   ```

2. **devpi-client** installed locally:
   ```bash
   pip install devpi-client
   ```

### Publishing Locally

```bash
make local-publish
```

### Installing from Local PyPI

```bash
pip install --index-url http://pypi.ix/root/dev/+simple/ spec_artifacts_iso
```

---

## 📜 Design Philosophy

- Native Poetry-based development (no Docker required for development)
- Isolated Poetry virtualenv (no global pip pollution)
- Direct uploads to Artifact Registry using correct PyPI-style authentication
- Always source-driven — no hand-editing built artifacts
- Dynamic, Git-tag-based versioning
- Clear Makefile and CI workflows matching production standards

---
