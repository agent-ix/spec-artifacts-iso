#!/usr/bin/env python3
"""Corpus census over ISO spec bundles — the measurement FR-005 is drawn from.

FR-005 cites this script as the record of its census (re-measured 2026-09-04,
which corrected six figures the earlier hand count got wrong): it is the
source of every population the requirement's constraints admit (the status
spellings, the cardinality forms, the constraint categories, the empty
verification cells, the index link lines, and the rest). It therefore has to
be reproducible by someone who is not the author, so:

* the corpus root is an argument (``--root``), defaulting to the ``~/dev/*/spec``
  glob the recorded runs used, rather than one developer's absolute path;
* every number states its **unit**, its **population**, and its **method** —
  whether it was counted by document, by line, by table row, by relationship
  entry, or by directory — so a figure quoted in the spec can be traced back to
  what was actually counted;
* ``--json`` emits the same numbers machine-readably, so a later run is diffed
  against this one rather than re-read by eye.

The census is strictly read-only. It opens documents and writes nothing to any
corpus repository; a defect it finds is reported here and fixed elsewhere.

Usage::

    python scripts/corpus_census.py                    # ~/dev/*/spec
    python scripts/corpus_census.py --root 'path/*/spec'
    python scripts/corpus_census.py --json > census.json
"""

from __future__ import annotations

import argparse
import collections
import glob
import json
import os
import pathlib
import re
import sys
from typing import Any

import yaml

# The glob the recorded censuses ran over. Kept as the *default* only; the
# logic below never assumes it.
DEFAULT_ROOT_GLOB = "~/dev/*/spec"

#: Frontmatter ``type`` values this census recognises as ISO artifacts.
ARTIFACT_TYPES = frozenset(
    {
        "FR",
        "NFR",
        "StR",
        "US",
        "IT",
        "TC",
        "Glossary",
        "index",
        "log",
        "master-requirements",
    }
)

#: The requirement/test/glossary types that carry a prefixed identifier.
IDENTIFIED_TYPES = frozenset({"FR", "NFR", "StR", "US", "IT", "TC", "Glossary"})

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)
ROW_ID_RE = re.compile(r"^(?P<prefix>.+?)-(?P<kind>AC|CON|VC)-(?P<n>\d+)$")
STORY_BOLD_RE = re.compile(r"^\s*(?:[-*]\s+)?\*\*As an?\b", re.I)
STORY_PLAIN_RE = re.compile(r"^\s*(?:[-*]\s+)?As an?\b", re.I)
IT_SC_TOKEN_RE = re.compile(r"\bIT-\d+-SC-\d+\b")
INDEX_LINK_RE = re.compile(
    r"^\s*(?P<bullet>[*-])\s+\[(?P<title>[^\]]*)\]\((?P<href>[^)]*)\)(?P<rest>.*)$"
)
LOG_BULLET_RE = re.compile(r"^\s*(?P<bullet>[*-])\s+(?P<body>\S.*)$")
LOG_DATE_RE = re.compile(r"^\*\*(?P<date>\d{4}-\d{2}-\d{2})\*\*")
HEADING_RE = re.compile(r"^(?P<hashes>#{1,6})\s+(?P<text>.*?)\s*$")

#: The four verification methods the advisory ``ac-verification-method`` lint
#: rule admits. Every other spelling in the corpus is free text.
LINT_ADMITTED_METHODS = ("Test", "Analysis", "Inspection", "Demonstration")


class Metric:
    """One reported number, with the three things that make it readable."""

    def __init__(self, value: int, unit: str, population: str, method: str) -> None:
        self.value = value
        self.unit = unit
        self.population = population
        self.method = method

    def as_dict(self) -> dict[str, Any]:
        return {
            "value": self.value,
            "unit": self.unit,
            "population": self.population,
            "method": self.method,
        }


class Distribution:
    """A counted value set, reported alongside its distinct-value count."""

    def __init__(
        self, counter: collections.Counter, unit: str, population: str, method: str
    ) -> None:
        self.counter = counter
        self.unit = unit
        self.population = population
        self.method = method

    def as_dict(self) -> dict[str, Any]:
        return {
            "distinct": len(self.counter),
            "total": sum(self.counter.values()),
            "unit": self.unit,
            "population": self.population,
            "method": self.method,
            "counts": dict(
                sorted(self.counter.items(), key=lambda kv: (-kv[1], kv[0]))
            ),
        }


def expand_roots(patterns: list[str]) -> list[pathlib.Path]:
    """Expand the root glob patterns into the bundle directories they match.

    A "bundle" is one matched directory — a repository's ``spec/`` tree. The
    repository name is that directory's parent name, which is how the census
    attributes a finding to a repository without hard-coding a path depth.
    """
    roots: list[pathlib.Path] = []
    seen: set[pathlib.Path] = set()
    for pattern in patterns:
        expanded = os.path.expanduser(pattern)
        for match in sorted(glob.glob(expanded)):
            path = pathlib.Path(match).resolve()
            if path.is_dir() and path not in seen:
                seen.add(path)
                roots.append(path)
    return roots


def split_row(line: str) -> list[str] | None:
    """Split a Markdown table row into trimmed cells, or ``None`` if not a row."""
    stripped = line.strip()
    if not stripped.startswith("|"):
        return None
    cells = stripped.split("|")
    # A well-formed row has a leading and trailing pipe, hence empty ends.
    if cells and cells[0].strip() == "":
        cells = cells[1:]
    if cells and cells[-1].strip() == "":
        cells = cells[:-1]
    return [cell.strip() for cell in cells]


def section_lines(lines: list[str], heading: str) -> list[str]:
    """Return the body lines under ``## <heading>`` up to the next heading."""
    body: list[str] = []
    collecting = False
    for line in lines:
        match = HEADING_RE.match(line)
        if match:
            if collecting:
                break
            if (
                len(match.group("hashes")) == 2
                and match.group("text").strip().lower() == heading.lower()
            ):
                collecting = True
            continue
        if collecting:
            body.append(line)
    return body


def has_heading(lines: list[str], heading: str) -> bool:
    for line in lines:
        match = HEADING_RE.match(line)
        if match and match.group("text").strip().lower() == heading.lower():
            return True
    return False


class Census:
    """Accumulates the census over one or more bundle roots."""

    def __init__(self) -> None:
        self.bundles = 0
        self.repositories: set[str] = set()
        self.documents_scanned = 0
        self.documents_unreadable = 0
        self.documents_with_frontmatter = 0
        self.documents_typed = 0
        self.documents_identified = 0
        self.type_counts: collections.Counter = collections.Counter()

        self.status_documents = 0
        self.status: collections.Counter = collections.Counter()
        self.cardinality: collections.Counter = collections.Counter()
        self.id_patterns: collections.Counter = collections.Counter()

        self.constraint_rows = 0
        self.constraint_types: collections.Counter = collections.Counter()
        self.verification_cells = 0
        self.verification_cells_empty = 0
        self.verification_methods: collections.Counter = collections.Counter()

        self.fr_documents = 0
        self.fr_with_object = 0
        self.fr_prose_constraints = 0

        self.us_documents = 0
        self.us_story_bold = 0
        self.us_story_plain = 0
        self.us_story_neither = 0

        self.it_documents = 0
        self.it_with_success_criteria = 0

        self.index_documents = 0
        self.index_link_lines = 0
        self.index_dash_bullets = 0
        self.index_without_summary = 0

        self.log_documents = 0
        self.log_dated_entries = 0
        self.log_undated_entries = 0
        self.log_undated_repositories: set[str] = set()

        self.master_requirements_documents = 0
        self.depends_on_lists = 0
        self.depends_on_empty = 0

    # -- traversal ---------------------------------------------------------

    def run(self, roots: list[pathlib.Path]) -> None:
        for root in roots:
            self.bundles += 1
            self.repositories.add(root.parent.name)
            for path in sorted(root.rglob("*.md")):
                if path.is_file():
                    self.scan_document(path, root.parent.name)

    def scan_document(self, path: pathlib.Path, repository: str) -> None:
        self.documents_scanned += 1
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            self.documents_unreadable += 1
            return

        match = FRONTMATTER_RE.match(text)
        if not match:
            return
        try:
            frontmatter = yaml.safe_load(match.group(1)) or {}
        except yaml.YAMLError:
            return
        if not isinstance(frontmatter, dict):
            return
        self.documents_with_frontmatter += 1

        artifact_type = frontmatter.get("type")
        if artifact_type not in ARTIFACT_TYPES:
            return
        self.documents_typed += 1
        self.type_counts[artifact_type] += 1

        identifier = str(frontmatter.get("id") or "")
        if artifact_type in IDENTIFIED_TYPES and identifier:
            self.documents_identified += 1
            self.id_patterns[re.sub(r"\d+", "N", identifier)] += 1

        if "status" in frontmatter:
            self.status_documents += 1
            self.status[str(frontmatter["status"])] += 1

        for relationship in frontmatter.get("relationships") or []:
            if isinstance(relationship, dict) and "cardinality" in relationship:
                self.cardinality[str(relationship["cardinality"])] += 1

        lines = text.splitlines()
        if identifier:
            self.scan_tables(lines, identifier)

        if artifact_type == "FR":
            self.scan_fr(lines, frontmatter, identifier)
        elif artifact_type == "US":
            self.scan_us(lines)
        elif artifact_type == "IT":
            self.scan_it(text)
        elif artifact_type == "index":
            self.scan_index(lines)
        elif artifact_type == "log":
            self.scan_log(lines, repository)
        elif artifact_type == "master-requirements":
            self.scan_master_requirements(frontmatter)

    # -- per-type scans ----------------------------------------------------

    def scan_tables(self, lines: list[str], identifier: str) -> None:
        """Count constraint, acceptance-criterion, and validation rows.

        A row is attributed to this document only when its first cell is an
        identifier prefixed by the document's own id, which is the same
        anchoring the archetype ``table_row`` locators use.
        """
        for line in lines:
            cells = split_row(line)
            if not cells:
                continue
            row_match = ROW_ID_RE.match(cells[0])
            if not row_match or row_match.group("prefix") != identifier:
                continue
            kind = row_match.group("kind")
            if kind == "CON" and len(cells) >= 4:
                self.constraint_rows += 1
                self.constraint_types[cells[2]] += 1
                self.record_verification(cells[3])
            elif kind == "AC" and len(cells) >= 3:
                self.record_verification(cells[2])
            elif kind == "VC" and len(cells) >= 3:
                self.record_verification(cells[2])

    def record_verification(self, cell: str) -> None:
        self.verification_cells += 1
        if not cell:
            self.verification_cells_empty += 1
            return
        method = cell.split("(", 1)[0].strip()
        self.verification_methods[method] += 1

    def scan_fr(self, lines: list[str], frontmatter: dict, identifier: str) -> None:
        self.fr_documents += 1
        if "object" in frontmatter:
            self.fr_with_object += 1
        if not has_heading(lines, "Constraints"):
            return
        body = section_lines(lines, "Constraints")
        for line in body:
            cells = split_row(line)
            if cells:
                row_match = ROW_ID_RE.match(cells[0])
                if row_match and row_match.group("kind") == "CON":
                    return
        if any(line.strip() for line in body):
            self.fr_prose_constraints += 1

    def scan_us(self, lines: list[str]) -> None:
        self.us_documents += 1
        for line in lines:
            if STORY_BOLD_RE.match(line):
                self.us_story_bold += 1
                return
        for line in lines:
            if STORY_PLAIN_RE.match(line):
                self.us_story_plain += 1
                return
        self.us_story_neither += 1

    def scan_it(self, text: str) -> None:
        self.it_documents += 1
        if IT_SC_TOKEN_RE.search(text):
            self.it_with_success_criteria += 1

    def scan_index(self, lines: list[str]) -> None:
        self.index_documents += 1
        for line in section_lines(lines, "Contents"):
            match = INDEX_LINK_RE.match(line)
            if not match:
                continue
            self.index_link_lines += 1
            if match.group("bullet") == "-":
                self.index_dash_bullets += 1
            rest = match.group("rest").strip().lstrip("-—–").strip()
            if not rest:
                self.index_without_summary += 1

    def scan_log(self, lines: list[str], repository: str) -> None:
        self.log_documents += 1
        for line in section_lines(lines, "History"):
            match = LOG_BULLET_RE.match(line)
            if not match:
                continue
            if LOG_DATE_RE.match(match.group("body")):
                self.log_dated_entries += 1
            else:
                self.log_undated_entries += 1
                self.log_undated_repositories.add(repository)

    def scan_master_requirements(self, frontmatter: dict) -> None:
        self.master_requirements_documents += 1
        depends_on = frontmatter.get("dependsOn", frontmatter.get("depends_on"))
        if isinstance(depends_on, list):
            if depends_on:
                self.depends_on_lists += 1
            else:
                self.depends_on_empty += 1

    # -- reporting ---------------------------------------------------------

    def metrics(self) -> dict[str, Metric]:
        docs = "ISO artifact documents in the scanned bundles"
        return {
            "bundles": Metric(
                self.bundles,
                "spec bundles",
                "directories matched by the root glob",
                "by directory",
            ),
            "repositories": Metric(
                len(self.repositories),
                "repositories",
                "parent directory of each matched bundle",
                "by directory",
            ),
            "documents_scanned": Metric(
                self.documents_scanned,
                "documents",
                "every *.md file under the matched bundles",
                "by document",
            ),
            "documents_unreadable": Metric(
                self.documents_unreadable,
                "documents",
                "scanned documents that could not be decoded as UTF-8",
                "by document",
            ),
            "documents_with_frontmatter": Metric(
                self.documents_with_frontmatter,
                "documents",
                "scanned documents carrying a YAML frontmatter block",
                "by document",
            ),
            "documents_typed": Metric(
                self.documents_typed,
                "documents",
                "documents whose frontmatter type is an ISO artifact type",
                "by document",
            ),
            "documents_identified": Metric(
                self.documents_identified,
                "documents",
                "requirement, test and glossary documents carrying an id",
                "by document",
            ),
            "status_documents": Metric(
                self.status_documents,
                "documents",
                f"{docs} declaring a frontmatter status key",
                "by document",
            ),
            "constraint_rows": Metric(
                self.constraint_rows,
                "table rows",
                "constraint rows anchored to their own document id",
                "by table row",
            ),
            "verification_cells": Metric(
                self.verification_cells,
                "table cells",
                "verification/validation cells of AC, CON and VC rows",
                "by table row",
            ),
            "verification_cells_empty": Metric(
                self.verification_cells_empty,
                "table cells",
                "verification/validation cells whose content is empty",
                "by table row",
            ),
            "verification_methods_lint_admitted": Metric(
                sum(
                    count
                    for method, count in self.verification_methods.items()
                    if method in LINT_ADMITTED_METHODS
                ),
                "table cells",
                "verification cells whose method is one of "
                + ", ".join(LINT_ADMITTED_METHODS),
                "by table row",
            ),
            "fr_documents": Metric(
                self.fr_documents, "documents", "documents of type FR", "by document"
            ),
            "fr_with_object": Metric(
                self.fr_with_object,
                "documents",
                "FR documents declaring a frontmatter object key",
                "by document",
            ),
            "fr_prose_constraints": Metric(
                self.fr_prose_constraints,
                "documents",
                "FR documents whose ## Constraints section holds prose, no rows",
                "by document",
            ),
            "us_documents": Metric(
                self.us_documents, "documents", "documents of type US", "by document"
            ),
            "us_story_bold": Metric(
                self.us_story_bold,
                "documents",
                "US documents whose story opens with a bold **As a**",
                "by document",
            ),
            "us_story_plain": Metric(
                self.us_story_plain,
                "documents",
                "US documents whose story opens with a plain As a",
                "by document",
            ),
            "us_story_neither": Metric(
                self.us_story_neither,
                "documents",
                "US documents carrying neither story form",
                "by document",
            ),
            "it_documents": Metric(
                self.it_documents, "documents", "documents of type IT", "by document"
            ),
            "it_with_success_criteria": Metric(
                self.it_with_success_criteria,
                "documents",
                "IT documents carrying at least one IT-NNN-SC-NN token",
                "by document",
            ),
            "index_documents": Metric(
                self.index_documents,
                "documents",
                "documents of type index",
                "by document",
            ),
            "index_link_lines": Metric(
                self.index_link_lines,
                "lines",
                "bullet lines under ## Contents holding a Markdown link",
                "by line",
            ),
            "index_dash_bullets": Metric(
                self.index_dash_bullets,
                "lines",
                "index link lines whose bullet marker is -",
                "by line",
            ),
            "index_without_summary": Metric(
                self.index_without_summary,
                "lines",
                "index link lines carrying no trailing summary",
                "by line",
            ),
            "log_documents": Metric(
                self.log_documents, "documents", "documents of type log", "by document"
            ),
            "log_dated_entries": Metric(
                self.log_dated_entries,
                "lines",
                "bullet lines under ## History opening with **YYYY-MM-DD**",
                "by line",
            ),
            "log_undated_entries": Metric(
                self.log_undated_entries,
                "lines",
                "bullet lines under ## History carrying no leading bold date",
                "by line",
            ),
            "log_undated_repositories": Metric(
                len(self.log_undated_repositories),
                "repositories",
                "repositories holding at least one undated history entry",
                "by directory",
            ),
            "master_requirements_documents": Metric(
                self.master_requirements_documents,
                "documents",
                "documents of type master-requirements",
                "by document",
            ),
            "depends_on_lists": Metric(
                self.depends_on_lists,
                "documents",
                "master-requirements documents with a non-empty dependsOn list",
                "by document",
            ),
            "depends_on_empty": Metric(
                self.depends_on_empty,
                "documents",
                "master-requirements documents with an empty dependsOn list",
                "by document",
            ),
        }

    def distributions(self) -> dict[str, Distribution]:
        docs = "ISO artifact documents in the scanned bundles"
        return {
            "artifact_types": Distribution(
                self.type_counts, "documents", docs, "by document"
            ),
            "status_spellings": Distribution(
                self.status,
                "documents",
                f"{docs} declaring a frontmatter status key",
                "by document",
            ),
            "cardinality_forms": Distribution(
                self.cardinality,
                "relationship entries",
                "frontmatter relationship entries declaring a cardinality",
                "by relationship entry",
            ),
            "id_patterns": Distribution(
                self.id_patterns,
                "documents",
                "identified documents, digits folded to N",
                "by document",
            ),
            "constraint_types": Distribution(
                self.constraint_types,
                "table rows",
                "the Type cell of every constraint row",
                "by table row",
            ),
            "verification_methods": Distribution(
                self.verification_methods,
                "table cells",
                "the text before the first ( of a non-empty verification cell",
                "by table row",
            ),
        }

    def as_json(self, roots: list[pathlib.Path], patterns: list[str]) -> dict:
        return {
            "census_version": 1,
            "source": "scripts/corpus_census.py",
            "root_patterns": patterns,
            "roots": [str(root) for root in roots],
            "metrics": {
                name: metric.as_dict() for name, metric in self.metrics().items()
            },
            "distributions": {
                name: dist.as_dict() for name, dist in self.distributions().items()
            },
        }


def render_table(
    census: Census, roots: list[pathlib.Path], patterns: list[str], top: int
) -> str:
    out: list[str] = []
    out.append(f"Corpus census — root patterns: {', '.join(patterns)}")
    out.append(f"Bundles matched: {len(roots)}")
    out.append("")
    out.append("Every row states what it counts: the unit, the population it was")
    out.append("counted over, and the method (by document, by line, by table row,")
    out.append("by relationship entry, or by directory).")
    out.append("")
    metrics = census.metrics()
    width = max(len(name) for name in metrics)
    header = f"{'metric'.ljust(width)}  {'value':>8}  unit / population / method"
    out.append(header)
    out.append("-" * len(header))
    for name, metric in metrics.items():
        out.append(
            f"{name.ljust(width)}  {metric.value:>8}  "
            f"{metric.unit} / {metric.population} / {metric.method}"
        )
    out.append("")
    for name, dist in census.distributions().items():
        data = dist.as_dict()
        out.append(
            f"{name}: {data['distinct']} distinct value(s) over "
            f"{data['total']} {dist.unit} "
            f"({dist.population}; {dist.method})"
        )
        for value, count in list(data["counts"].items())[:top]:
            out.append(f"    {count:>8}  {value!r}")
        if len(data["counts"]) > top:
            out.append(f"    ... {len(data['counts']) - top} more value(s)")
        out.append("")
    return "\n".join(out)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="corpus_census.py",
        description=(
            "Census the ISO spec corpus. Read-only: no corpus file is written."
        ),
    )
    parser.add_argument(
        "--root",
        dest="roots",
        action="append",
        metavar="GLOB",
        help=(
            "glob matching the spec bundle directories to census "
            f"(repeatable; default {DEFAULT_ROOT_GLOB})"
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit the census as JSON instead of the human table",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=30,
        help="how many values of each distribution the table shows (default 30)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    patterns = args.roots or [DEFAULT_ROOT_GLOB]
    roots = expand_roots(patterns)
    if not roots:
        print(
            f"corpus_census: no bundle matched {', '.join(patterns)}",
            file=sys.stderr,
        )
        return 1
    census = Census()
    census.run(roots)
    if args.json:
        print(json.dumps(census.as_json(roots, patterns), indent=2, sort_keys=False))
    else:
        print(render_table(census, roots, patterns, args.top))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
