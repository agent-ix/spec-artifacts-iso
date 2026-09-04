"""FR-007 — the reference mapping from authored Markdown to an FR-005 record.

This is a **test oracle**, not module code. The module ships data — the emitted
schemas, ``mappings.yaml``, and the golden records under ``examples/`` — and
this file is what proves that data is coherent. Nothing in the module builds a
record from Markdown, and nothing anywhere derives Markdown from a record
(FR-007-CON-3, pinned by TC-059).

The mapping is **driven by** ``spec_artifacts_iso/mappings.yaml``: the
published declaration says, per model and per property, which of the eight
mapping kinds applies, where it reads from, which named parse it uses, and
whether the projection is lossless. There is no per-model branch below — a
model this file has never heard of maps correctly the moment ``mappings.yaml``
declares it, which is what makes the published declaration the contract rather
than a second description of this Python.

Semantics implemented here, each from FR-007 ``## Behavior``:

* ``section`` — the byte-exact section slice (quire-rs FR-008: content starts
  on the line after the heading and runs to the line before the next heading of
  any level, CR bytes and blank lines preserved) with 1-based document
  ``startLine``/``endLine``;
* ``section`` + ``parse: story`` — the anchored As-a / I-want / So-that lines;
* ``table`` / ``typed-table`` — one object per data row in authored order,
  every cell trimmed (``\\r`` included), the ``Verification`` split, row-id
  patterns and uniqueness, and ``### <row id>`` detail subsections;
* ``list`` — index entries and log history;
* ``token`` — ``IT-XXX-SC-NN`` success criteria;
* ``ocl-clause`` — ``### <clauseId>`` clauses under ``## Invariants``, with the
  clause text carried beside the record in ``invariantsText`` and never parsed;
* ``frontmatter`` — the named keys only, every other key dropped by policy;
* ``provenance`` — the corpus-relative path, the SHA-256 of the bytes as read
  with no line-ending normalization, and the caller's ``sourceIdentity`` when
  the caller supplies one. A ``sourceIdentity`` is never synthesized.

Failure discipline (FR-007): every failure found is reported in one pass, and
no record is emitted when any failure is found. The mapping never validates the
record against the model — a record this builds and the schema then rejects is
a defect in the pair of requirements, and the suite reports the two layers
separately (TC-044, TC-045).
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import pathlib
import re
from typing import Any

import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PKG_ROOT = REPO_ROOT / "spec_artifacts_iso"
MAPPINGS_PATH = PKG_ROOT / "mappings.yaml"
MAPPINGS_SCHEMA_PATH = PKG_ROOT / "mappings.schema.json"


# --------------------------------------------------------------------------
# Failures
# --------------------------------------------------------------------------
@dataclasses.dataclass(frozen=True)
class Failure:
    """One mapping failure, always carrying the document line that caused it."""

    line: int
    message: str

    def __str__(self) -> str:
        return f"line {self.line}: {self.message}"


class MappingError(Exception):
    """Raised with *every* failure found in one pass; no record is emitted."""

    def __init__(self, failures: list[Failure]) -> None:
        unique = sorted(set(failures), key=lambda f: (f.line, f.message))
        self.failures = tuple(unique)
        super().__init__("; ".join(str(failure) for failure in self.failures))

    @property
    def lines(self) -> tuple[int, ...]:
        return tuple(failure.line for failure in self.failures)


@dataclasses.dataclass(frozen=True)
class MappingResult:
    """A record and its clause-text sidecar.

    ``invariants_text`` is the FR-007 sidecar: one entry per ``ClauseRef`` in
    the same order, each recording the fence's lines and body bytes. The record
    never carries clause text.
    """

    record: dict[str, Any]
    invariants_text: tuple[dict[str, Any], ...] = ()


# --------------------------------------------------------------------------
# The published declaration
# --------------------------------------------------------------------------
def load_mappings() -> dict[str, Any]:
    """The shipped ``mappings.yaml``, read fresh."""
    return yaml.safe_load(MAPPINGS_PATH.read_text(encoding="utf-8"))


def load_mappings_schema() -> dict[str, Any]:
    """The shipped ``mappings.schema.json``, read fresh."""
    return json.loads(MAPPINGS_SCHEMA_PATH.read_text(encoding="utf-8"))


def canonical_json(record: dict[str, Any]) -> str:
    """FR-007 Golden records: sorted keys, two-space indent, trailing newline."""
    return json.dumps(record, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


# --------------------------------------------------------------------------
# Document structure
# --------------------------------------------------------------------------
_FENCE_RE = re.compile(r"^(?P<indent> {0,3})(?P<fence>`{3,}|~{3,})(?P<info>.*)$")
_HEADING_RE = re.compile(r"^ {0,3}(?P<hashes>#{1,6})[ \t]+(?P<text>.*?)[ \t]*$")
_CLOSING_HASHES_RE = re.compile(r"[ \t]+#+[ \t]*$")


@dataclasses.dataclass(frozen=True)
class _Heading:
    level: int
    text: str
    index: int  # 0-based line index of the heading line
    content_start: int  # 0-based index of the first content line
    content_end: int  # 0-based index of the next heading of ANY level, or EOF
    block_end: int  # 0-based index of the next heading of level <= this, or EOF


@dataclasses.dataclass(frozen=True)
class _Fence:
    open_index: int
    close_index: int | None  # None when the fence is never terminated
    info: str
    indent: int


class Document:
    """A Markdown document sliced the way quire-rs slices one (FR-008)."""

    def __init__(self, text: str) -> None:
        self.text = text
        lines = text.split("\n")
        if lines and lines[-1] == "":
            lines.pop()
        self.lines = lines
        offsets: list[int] = []
        cursor = 0
        for line in lines:
            offsets.append(cursor)
            cursor += len(line) + 1
        offsets.append(len(text))
        self._offsets = offsets
        self.frontmatter, self._body_start = self._read_frontmatter()
        self.fences = self._scan_fences()
        self.headings = self._scan_headings()

    # -- construction ------------------------------------------------------
    def _read_frontmatter(self) -> tuple[dict[str, Any], int]:
        if not self.lines or self.lines[0].rstrip("\r") != "---":
            return {}, 0
        for index in range(1, len(self.lines)):
            if self.lines[index].rstrip("\r") == "---":
                block = "\n".join(line.rstrip("\r") for line in self.lines[1:index])
                loaded = yaml.safe_load(block) if block.strip() else {}
                return (loaded if isinstance(loaded, dict) else {}), index + 1
        return {}, 0

    def _scan_fences(self) -> list[_Fence]:
        fences: list[_Fence] = []
        opened: tuple[int, str, str, int] | None = None
        for index in range(self._body_start, len(self.lines)):
            line = self.lines[index].rstrip("\r")
            match = _FENCE_RE.match(line)
            if opened is None:
                if match:
                    opened = (
                        index,
                        match.group("fence"),
                        match.group("info").strip(),
                        len(match.group("indent")),
                    )
                continue
            if (
                match
                and match.group("fence")[0] == opened[1][0]
                and len(match.group("fence")) >= len(opened[1])
                and not match.group("info").strip()
            ):
                fences.append(_Fence(opened[0], index, opened[2], opened[3]))
                opened = None
        if opened is not None:
            fences.append(_Fence(opened[0], None, opened[2], opened[3]))
        return fences

    def _fenced_lines(self) -> set[int]:
        inside: set[int] = set()
        for fence in self.fences:
            end = (
                fence.close_index if fence.close_index is not None else len(self.lines)
            )
            inside.update(range(fence.open_index, end + 1))
        return inside

    def _scan_headings(self) -> list[_Heading]:
        fenced = self._fenced_lines()
        raw: list[tuple[int, str, int]] = []
        for index in range(self._body_start, len(self.lines)):
            if index in fenced:
                continue
            match = _HEADING_RE.match(self.lines[index].rstrip("\r"))
            if not match:
                continue
            text = _CLOSING_HASHES_RE.sub("", match.group("text")).strip()
            raw.append((len(match.group("hashes")), text, index))

        headings: list[_Heading] = []
        for position, (level, text, index) in enumerate(raw):
            following = raw[position + 1 :]
            content_end = following[0][2] if following else len(self.lines)
            block_end = next(
                (other[2] for other in following if other[0] <= level),
                len(self.lines),
            )
            headings.append(
                _Heading(level, text, index, index + 1, content_end, block_end)
            )
        return headings

    # -- access ------------------------------------------------------------
    def slice(self, start: int, end: int) -> str:
        """The byte-exact text of lines ``[start, end)``."""
        return self.text[self._offsets[start] : self._offsets[end]]

    def line_text(self, index: int) -> str:
        return self.lines[index]

    def doc_line(self, index: int) -> int:
        """The 1-based document line of a 0-based line index."""
        return index + 1

    def find(self, heading: str, level: int) -> list[_Heading]:
        return [h for h in self.headings if h.level == level and h.text == heading]

    def children(self, parent: _Heading, level: int) -> list[_Heading]:
        return [
            h
            for h in self.headings
            if h.level == level and parent.index < h.index < parent.block_end
        ]


# --------------------------------------------------------------------------
# Named parses (FR-007 `parses`)
# --------------------------------------------------------------------------
_EMPHASIS = ("**", "__", "*", "_")
_MARK = r"(?:\*\*|__|\*|_)"
_STORY_ANCHORS = {
    "asA": r"as an?",
    "iWant": r"i want",
    "soThat": r"so that",
}
_STORY_RES = {
    field: re.compile(
        rf"^[ \t]*{_MARK}?[ \t]*(?:{anchor})[ \t]*:?[ \t]*{_MARK}?[ \t]*:?[ \t]*"
        r"(?P<text>.*?)[ \t]*$",
        re.IGNORECASE,
    )
    for field, anchor in _STORY_ANCHORS.items()
}
_TEST_REF_RE = re.compile(r"TC-[0-9]+")
_INDEX_ENTRY_RE = re.compile(
    r"^(?P<bullet>[*-])[ \t]+\[(?P<title>[^\]]*)\]\((?P<href>[^)]*)\)"
    r"(?:[ \t]+[-–—][ \t]+(?P<summary>.*?))?[ \t]*$"
)
_BULLET_RE = re.compile(r"^(?P<bullet>[*-])[ \t]+(?P<rest>.*)$")
_LOG_DATE_RE = re.compile(
    r"^(?:\*\*|__)?(?P<date>[0-9]{4}-[0-9]{2}-[0-9]{2})(?:\*\*|__)?"
    r"[ \t]*(?:[-–—][ \t]*)?(?P<text>.*)$"
)
_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _strip_emphasis(value: str) -> str:
    text = value.strip()
    for marker in _EMPHASIS:
        if (
            text.startswith(marker)
            and text.endswith(marker)
            and len(text) > 2 * len(marker)
        ):
            return text[len(marker) : -len(marker)].strip()
    return text


def split_verification(cell: str) -> dict[str, Any]:
    """FR-005 `Verification`: ``<method> (<annotation>)``.

    ``method`` is the text before the first ``(`` trimmed; ``annotation`` is the
    text between the first ``(`` and the last ``)`` verbatim; ``testRefs`` are
    the ``TC-[0-9]+`` tokens of the annotation in order. A cell with no
    parenthesised remainder is ``method`` alone with ``testRefs: []`` and no
    ``annotation``, and no byte of the cell is dropped either way.
    """
    open_at = cell.find("(")
    close_at = cell.rfind(")")
    if open_at == -1 or close_at < open_at:
        return {"method": cell.strip(), "testRefs": []}
    annotation = cell[open_at + 1 : close_at]
    return {
        "method": cell[:open_at].strip(),
        "testRefs": _TEST_REF_RE.findall(annotation),
        "annotation": annotation,
    }


# --------------------------------------------------------------------------
# The mapping itself
# --------------------------------------------------------------------------
class _Mapper:
    def __init__(
        self,
        document: Document,
        model: str,
        declaration: dict[str, Any],
        *,
        path: str,
        digest: str,
        source_identity: str | None,
    ) -> None:
        self.doc = document
        self.model = model
        self.declaration = declaration
        self.path = path
        self.digest = digest
        self.source_identity = source_identity
        self.failures: list[Failure] = []
        self.invariants_text: list[dict[str, Any]] = []

    # -- helpers -----------------------------------------------------------
    def fail(self, index: int, message: str) -> None:
        self.failures.append(Failure(self.doc.doc_line(index), message))

    def heading(self, name: str, level: int) -> _Heading | None:
        """The single heading a mapping names, or ``None`` when it is absent.

        A heading the mapping names twice is a failure naming the second
        occurrence's line (FR-007 Failure discipline).
        """
        found = self.doc.find(name, level)
        for duplicate in found[1:]:
            self.fail(
                duplicate.index,
                f"heading {'#' * level} {name!r} is named by the "
                f"{self.model} mapping and appears more than once",
            )
        return found[0] if found else None

    def section_object(self, heading: _Heading) -> dict[str, Any]:
        return {
            "text": self.doc.slice(heading.content_start, heading.content_end),
            "startLine": self.doc.doc_line(heading.index),
            "endLine": max(heading.index + 1, heading.content_end),
        }

    # -- kinds -------------------------------------------------------------
    def frontmatter(self, entry: dict[str, Any]) -> Any:
        source = entry["source"]
        key = source["key"]
        if key not in self.doc.frontmatter:
            # A model-required array whose frontmatter key is absent takes the
            # declared default (an empty edge set); everything else is absent.
            return source.get("default")
        value = self.doc.frontmatter[key]
        item_keys = entry["source"].get("item_keys")
        if item_keys is None or not isinstance(value, list):
            return value
        return [
            {k: item[k] for k in item_keys if k in item}
            for item in value
            if isinstance(item, dict)
        ]

    def provenance(self, entry: dict[str, Any]) -> dict[str, Any]:
        del entry  # the shape is fixed; the declaration names the sources
        record: dict[str, Any] = {"path": self.path, "digest": self.digest}
        if self.source_identity is not None:
            record["sourceIdentity"] = self.source_identity
        return record

    def section(self, entry: dict[str, Any]) -> Any:
        source = entry["source"]
        heading = self.heading(source["heading"], source["level"])
        if heading is None:
            return None
        shape = entry["yield"]
        if shape == "HeadingText":
            return heading.text
        if shape == "HeadingRef":
            return {
                "heading": heading.text,
                "line": self.doc.doc_line(heading.index),
            }
        section = self.section_object(heading)
        if shape == "Section":
            return section
        return self.story(heading, section)

    def story(
        self, heading: _Heading, section: dict[str, Any]
    ) -> dict[str, Any] | None:
        story: dict[str, Any] = {}
        for index in range(heading.content_start, heading.content_end):
            line = self.doc.line_text(index).rstrip("\r")
            for field, pattern in _STORY_RES.items():
                if field in story:
                    continue
                match = pattern.match(line)
                if match:
                    story[field] = _strip_emphasis(match.group("text"))
        missing = [field for field in _STORY_RES if field not in story]
        if missing:
            self.fail(
                heading.index,
                f"`## {heading.text}` does not match the story grammar: no "
                + ", ".join(
                    {"asA": "`As a`", "iWant": "`I want`", "soThat": "`So that`"}[field]
                    for field in missing
                )
                + " line",
            )
            return None
        story["section"] = section
        return story

    def table(self, entry: dict[str, Any], typed: bool) -> Any:
        source = entry["source"]
        heading = self.heading(source["section"], 2)
        if heading is None:
            return None
        found = self._find_table(heading)
        if found is None:
            return None
        header_index, row_indices = found
        columns = self._columns(header_index)
        if columns != list(source["columns"]):
            self.fail(
                header_index,
                f"table under `## {heading.text}` has columns {columns}; the "
                f"{self.model}.{entry['_property']} mapping declares "
                f"{list(source['columns'])}",
            )
            return None

        rows: list[dict[str, Any]] = []
        seen_ids: dict[str, int] = {}
        for row_index in row_indices:
            cells = self._cells(row_index)
            if len(cells) != len(columns):
                self.fail(
                    row_index,
                    f"row under `## {heading.text}` has {len(cells)} cells; the "
                    f"table declares {len(columns)} columns",
                )
                continue
            row: dict[str, Any] = {}
            for column, cell in zip(columns, cells, strict=True):
                rule = entry["cells"][column]
                if rule.get("parse") == "verification":
                    row[rule["property"]] = split_verification(cell)
                else:
                    row[rule["property"]] = cell
            row["line"] = self.doc.doc_line(row_index)
            if typed:
                self._check_row_id(entry, heading, row_index, row, seen_ids)
            rows.append(row)

        if typed and entry.get("detail"):
            self._attach_details(entry, heading, rows)
        return rows

    def _check_row_id(
        self,
        entry: dict[str, Any],
        heading: _Heading,
        row_index: int,
        row: dict[str, Any],
        seen_ids: dict[str, int],
    ) -> None:
        rule = entry["row_id"]
        column_rule = entry["cells"][rule["column"]]
        row_id = row.get(column_rule["property"])
        document_id = self.doc.frontmatter.get("id", "")
        pattern = rule["pattern"].replace("{id}", re.escape(str(document_id)))
        if not isinstance(row_id, str) or not re.match(pattern, row_id):
            self.fail(
                row_index,
                f"row id {row_id!r} under `## {heading.text}` does not match "
                f"{rule['pattern'].replace('{id}', str(document_id))}",
            )
            return
        if row_id in seen_ids:
            self.fail(
                row_index,
                f"row id {row_id!r} is repeated in the table under "
                f"`## {heading.text}` (first at line {seen_ids[row_id]})",
            )
            return
        seen_ids[row_id] = self.doc.doc_line(row_index)

    def _attach_details(
        self, entry: dict[str, Any], heading: _Heading, rows: list[dict[str, Any]]
    ) -> None:
        rule = entry["detail"]
        id_property = entry["cells"][entry["row_id"]["column"]]["property"]
        by_id = {row[id_property]: row for row in rows if id_property in row}
        document_id = self.doc.frontmatter.get("id", "")
        pattern = entry["row_id"]["pattern"].replace(
            "{id}", re.escape(str(document_id))
        )
        for child in self.doc.children(heading, rule["heading_level"]):
            token = child.text.split(":", 1)[0].strip()
            if not re.match(pattern, token):
                continue
            row = by_id.get(token)
            if row is None:
                self.fail(
                    child.index,
                    f"`### {child.text}` names {token!r}, which matches no row "
                    f"of the table under `## {heading.text}`",
                )
                continue
            if rule["property"] in row:
                self.fail(
                    child.index,
                    f"`### {child.text}` supplements {token!r}, which already "
                    "carries a detail subsection",
                )
                continue
            row[rule["property"]] = self.doc.slice(
                child.content_start, child.content_end
            )

    def _find_table(self, heading: _Heading) -> tuple[int, list[int]] | None:
        header_index: int | None = None
        for index in range(heading.content_start, heading.content_end):
            if self.doc.line_text(index).strip().startswith("|"):
                header_index = index
                break
        if header_index is None or header_index + 1 >= heading.content_end:
            return None
        delimiter = self.doc.line_text(header_index + 1).strip()
        if not delimiter.startswith("|") or not re.fullmatch(
            r"[|:\- \t]*-[|:\- \t]*", delimiter
        ):
            return None
        rows: list[int] = []
        for index in range(header_index + 2, heading.content_end):
            if not self.doc.line_text(index).strip().startswith("|"):
                break
            rows.append(index)
        return header_index, rows

    def _columns(self, index: int) -> list[str]:
        return self._cells(index)

    def _cells(self, index: int) -> list[str]:
        line = self.doc.line_text(index).strip()
        if line.startswith("|"):
            line = line[1:]
        if line.endswith("|") and not line.endswith("\\|"):
            line = line[:-1]
        cells: list[str] = []
        buffer: list[str] = []
        position = 0
        while position < len(line):
            char = line[position]
            if char == "\\" and position + 1 < len(line) and line[position + 1] == "|":
                buffer.append("|")
                position += 2
                continue
            if char == "|":
                cells.append("".join(buffer))
                buffer = []
                position += 1
                continue
            buffer.append(char)
            position += 1
        cells.append("".join(buffer))
        return [cell.strip() for cell in cells]

    def list_(self, entry: dict[str, Any]) -> Any:
        source = entry["source"]
        heading = self.heading(source["section"], 2)
        if heading is None:
            return None
        if entry["parse"] == "index-entry":
            return self._index_entries(heading)
        return self._log_entries(heading)

    def _index_entries(self, heading: _Heading) -> list[dict[str, Any]]:
        entries: list[dict[str, Any]] = []
        for index in range(heading.content_start, heading.content_end):
            match = _INDEX_ENTRY_RE.match(self.doc.line_text(index).rstrip("\r"))
            if not match:
                continue  # prose, a nested bullet or a blank line: not an entry
            entry: dict[str, Any] = {
                "title": match.group("title").strip(),
                "href": match.group("href").strip(),
                "line": self.doc.doc_line(index),
            }
            summary = match.group("summary")
            if summary is not None:
                entry["summary"] = summary.strip()
            entries.append(entry)
        return entries

    def _log_entries(self, heading: _Heading) -> list[dict[str, Any]]:
        starts = [
            index
            for index in range(heading.content_start, heading.content_end)
            if _BULLET_RE.match(self.doc.line_text(index).rstrip("\r"))
        ]
        entries: list[dict[str, Any]] = []
        for position, start in enumerate(starts):
            end = (
                starts[position + 1]
                if position + 1 < len(starts)
                else heading.content_end
            )
            bullet = _BULLET_RE.match(self.doc.line_text(start).rstrip("\r"))
            assert bullet is not None
            match = _LOG_DATE_RE.match(bullet.group("rest"))
            if not match:
                self.fail(
                    start,
                    "history entry carries no `YYYY-MM-DD` date: "
                    f"{bullet.group('rest').strip()!r}",
                )
                continue
            # The entry extends to the next bullet at the same indentation.
            body = [match.group("text")]
            body.extend(
                self.doc.line_text(index).rstrip("\r")
                for index in range(start + 1, end)
            )
            entries.append(
                {
                    "date": match.group("date"),
                    "text": "\n".join(body).strip(),
                    "line": self.doc.doc_line(start),
                }
            )
        return entries

    def token(self, entry: dict[str, Any]) -> Any:
        source = entry["source"]
        heading = self.heading(source["section"], 2)
        if heading is None:
            return None
        pattern = re.compile(source["pattern"])
        found: list[dict[str, Any]] = []
        for index in range(heading.content_start, heading.content_end):
            line = self.doc.line_text(index).rstrip("\r")
            for match in pattern.finditer(line):
                remainder = line[match.end() :].lstrip()
                if remainder.startswith(":"):
                    remainder = remainder[1:]
                found.append(
                    {
                        "id": match.group(0),
                        "text": remainder.strip(),
                        "line": self.doc.doc_line(index),
                    }
                )
        return found

    def ocl_clause(self, entry: dict[str, Any]) -> Any:
        source = entry["source"]
        heading = self.heading(source["section"], 2)
        if heading is None:
            return None
        language = source["language"]
        level = source["clause_heading_level"]

        for fence in self.doc.fences:
            if heading.content_start <= fence.open_index < heading.content_end:
                if fence.info.split()[:1] == [language]:
                    self.fail(
                        fence.open_index,
                        f"fenced `{language}` block under `## {heading.text}` is "
                        f"owned by no `{'#' * level}` heading",
                    )

        clauses: list[dict[str, Any]] = []
        seen: dict[str, int] = {}
        for child in self.doc.children(heading, level):
            if not _IDENTIFIER_RE.match(child.text):
                self.fail(
                    child.index,
                    f"clause heading {child.text!r} is not an Identifier "
                    "(^[A-Za-z_][A-Za-z0-9_]*$)",
                )
                continue
            fences = [
                fence
                for fence in self.doc.fences
                if child.content_start <= fence.open_index < child.content_end
            ]
            if not fences:
                continue  # a prose clause heading yields no ClauseRef
            for extra in fences[1:]:
                self.fail(
                    extra.open_index,
                    f"clause {child.text!r} owns more than one fenced block",
                )
            fence = fences[0]
            tag = fence.info.split()[0] if fence.info.split() else ""
            if tag != language:
                self.fail(
                    fence.open_index,
                    f"clause {child.text!r} owns a fence tagged {tag!r}; the "
                    f"mapping declares {language!r}",
                )
                continue
            if fence.close_index is None:
                self.fail(
                    fence.open_index,
                    f"clause {child.text!r} owns an unterminated fence",
                )
                continue
            if child.text in seen:
                self.fail(
                    child.index,
                    f"clause id {child.text!r} is already used in this document "
                    f"(first at line {seen[child.text]})",
                )
                continue
            seen[child.text] = self.doc.doc_line(child.index)
            clauses.append(self._clause(child, fence, language))
        return clauses or None

    def _clause(self, child: _Heading, fence: _Fence, language: str) -> dict[str, Any]:
        assert fence.close_index is not None
        open_line = self.doc.doc_line(fence.open_index)
        close_line = self.doc.doc_line(fence.close_index)
        clause: dict[str, Any] = {"language": language, "clauseId": child.text}
        if self.source_identity is not None:
            opening = self.doc.line_text(fence.open_index).rstrip("\r")
            closing = self.doc.line_text(fence.close_index).rstrip("\r")
            clause["sourceSpan"] = {
                "sourceIdentity": self.source_identity,
                "path": self.path,
                "startLine": open_line,
                "startColumn": len(opening) - len(opening.lstrip()) + 1,
                "endLine": close_line,
                "endColumn": len(closing.rstrip()),
            }
        self.invariants_text.append(
            {
                "clauseId": child.text,
                "startLine": open_line,
                "endLine": close_line,
                "text": self.doc.slice(fence.open_index + 1, fence.close_index),
            }
        )
        return clause

    # -- driver ------------------------------------------------------------
    _KINDS = {
        "frontmatter": "frontmatter",
        "provenance": "provenance",
        "section": "section",
        "list": "list_",
        "token": "token",
        "ocl-clause": "ocl_clause",
    }

    def build(self) -> dict[str, Any]:
        record: dict[str, Any] = {}
        for name, entry in self.declaration["properties"].items():
            entry = dict(entry, _property=name)
            kind = entry["kind"]
            if kind in ("table", "typed-table"):
                value = self.table(entry, typed=kind == "typed-table")
            else:
                value = getattr(self, self._KINDS[kind])(entry)
            if value is not None:
                record[name] = value
        return record


# --------------------------------------------------------------------------
# Public entry points
# --------------------------------------------------------------------------
def model_for(data: bytes, declaration: dict[str, Any] | None = None) -> str:
    """The model name of a document, from its frontmatter ``type``."""
    declaration = declaration or load_mappings()
    return _model_of(Document(data.decode("utf-8")), declaration)


def _model_of(document: Document, declaration: dict[str, Any]) -> str:
    model = document.frontmatter.get("type")
    if model not in declaration["models"]:
        raise ValueError(
            f"frontmatter `type: {model!r}` names no model in mappings.yaml; "
            f"known models are {sorted(declaration['models'])}"
        )
    return str(model)


def map_bytes(
    data: bytes,
    *,
    path: str,
    model: str | None = None,
    source_identity: str | None = None,
    declaration: dict[str, Any] | None = None,
) -> MappingResult:
    """Build the record of one document from its bytes as read.

    ``path`` is the corpus-relative path recorded in ``provenance``;
    ``source_identity`` is caller data and is never synthesized. Raises
    :class:`MappingError` carrying *every* failure found, having emitted no
    record.
    """
    declaration = declaration or load_mappings()
    document = Document(data.decode("utf-8"))
    model = model or _model_of(document, declaration)
    digest = f"sha256:{hashlib.sha256(data).hexdigest()}"
    mapper = _Mapper(
        document,
        model,
        declaration["models"][model],
        path=path,
        digest=digest,
        source_identity=source_identity,
    )
    record = mapper.build()
    if mapper.failures:
        raise MappingError(mapper.failures)
    return MappingResult(record, tuple(mapper.invariants_text))


def map_file(
    file: pathlib.Path,
    *,
    path: str | None = None,
    model: str | None = None,
    source_identity: str | None = None,
    declaration: dict[str, Any] | None = None,
) -> MappingResult:
    """Read a document read-only and map it.

    ``read_bytes`` is the only file access this module performs: the mapping
    reads Markdown and writes nothing (FR-007-CON-3).
    """
    data = file.read_bytes()
    return map_bytes(
        data,
        path=path if path is not None else file.name,
        model=model,
        source_identity=source_identity,
        declaration=declaration,
    )
