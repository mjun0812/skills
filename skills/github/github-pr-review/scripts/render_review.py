#!/usr/bin/env python
"""Render a review body and inline comments from a findings JSON file.

Usage:
    render_review.py --findings <findings.json> --out-dir <dir>

Writes <dir>/body.md and <dir>/comments.json, then prints the verdict
(APPROVE or REQUEST_CHANGES) to stdout. Validation errors are printed to
stderr, one per line, with exit code 2.

The findings JSON is documented in references/findings.md. Every layout
decision (ordering, numbering, field labels, footers) lives here so the
review body and the inline comments cannot disagree.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import NotRequired, TypedDict, cast

ORIGINS = ("finder", "standards", "contract")
SIDES = ("RIGHT", "LEFT")


class Condition(TypedDict):
    """A completion condition with an optional note shown only in the body."""

    text: str
    note: NotRequired[str]


class Finding(TypedDict):
    """One confirmed finding as written by the reviewer."""

    origin: str
    path: str
    line: int
    side: NotRequired[str]
    category: str
    summary: str
    problem: str
    execution_path: NotRequired[list[str]]
    basis: NotRequired[list[str]]
    other_locations: NotRequired[list[str]]
    notes: NotRequired[list[str]]
    completion_conditions: list[str | Condition]


class Document(TypedDict):
    """The findings document, validated before rendering."""

    language: str
    reviewer: str
    commit: str
    summary: str
    notes: NotRequired[list[str]]
    findings: list[Finding]


LABELS = {
    "ja": {
        "title": "PR Review",
        "summary": "概要",
        "verdict": "判定",
        "findings": "指摘事項",
        "none": "なし",
        "location": "場所",
        "problem": "問題",
        "execution_path": "発生経路",
        "basis": "根拠",
        "other_locations": "他の該当箇所",
        "notes": "補足",
        "completion_conditions": "完了条件",
    },
    "en": {
        "title": "PR Review",
        "summary": "Summary",
        "verdict": "Verdict",
        "findings": "Findings",
        "none": "N/A",
        "location": "Location",
        "problem": "Problem",
        "execution_path": "Execution path",
        "basis": "Basis",
        "other_locations": "Other locations",
        "notes": "Notes",
        "completion_conditions": "Completion condition",
    },
}


def _is_str_list(value: object) -> bool:
    """Return whether value is a list of non-empty strings.

    Args:
        value: A parsed JSON value.
    """
    return isinstance(value, list) and all(
        isinstance(v, str) and v.strip() for v in value
    )


def _condition(value: object) -> tuple[str, str | None] | None:
    """Normalize one completion condition into (text, note).

    Args:
        value: A non-empty string, or an object with ``text`` and optional ``note``.

    Returns:
        The (text, note) pair, or None when the value is malformed.
    """
    if isinstance(value, str) and value.strip():
        return value, None
    if (
        isinstance(value, dict)
        and isinstance(value.get("text"), str)
        and value["text"].strip()
    ):
        note = value.get("note")
        if note is None or (isinstance(note, str) and note.strip()):
            return value["text"], note
    return None


def validate(data: object) -> list[str]:
    """Check the findings document and return every violation found.

    Args:
        data: The parsed findings JSON.

    Returns:
        Human-readable violations, empty when the document is valid.
    """
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["document: must be a JSON object"]
    if data.get("language") not in LABELS:
        errors.append(f"language: must be one of {sorted(LABELS)}")
    for key in ("reviewer", "commit", "summary"):
        if not (isinstance(data.get(key), str) and data[key].strip()):
            errors.append(f"{key}: must be a non-empty string")
    if "notes" in data and not _is_str_list(data["notes"]):
        errors.append("notes: must be a list of non-empty strings")
    findings = data.get("findings")
    if not isinstance(findings, list):
        return [*errors, "findings: must be a list"]

    for i, f in enumerate(findings):
        where = f"findings[{i}]"
        if not isinstance(f, dict):
            errors.append(f"{where}: must be an object")
            continue
        origin = f.get("origin")
        if origin not in ORIGINS:
            errors.append(f"{where}.origin: must be one of {list(ORIGINS)}")
        for key in ("path", "category", "summary", "problem"):
            if not (isinstance(f.get(key), str) and f[key].strip()):
                errors.append(f"{where}.{key}: must be a non-empty string")
        if not (isinstance(f.get("line"), int) and f["line"] >= 1):
            errors.append(f"{where}.line: must be an integer >= 1")
        if f.get("side", "RIGHT") not in SIDES:
            errors.append(f"{where}.side: must be RIGHT or LEFT")
        if origin == "finder" and not (
            _is_str_list(f.get("execution_path")) and f["execution_path"]
        ):
            errors.append(
                f"{where}.execution_path: required for origin finder, one hop per entry"
            )
        if origin in ("standards", "contract") and not (
            _is_str_list(f.get("basis")) and f["basis"]
        ):
            errors.append(
                f"{where}.basis: required for origin {origin}, one item per entry"
            )
        for key in ("other_locations", "notes"):
            if key in f and not _is_str_list(f[key]):
                errors.append(f"{where}.{key}: must be a list of non-empty strings")
        conditions = f.get("completion_conditions")
        if not (
            isinstance(conditions, list)
            and conditions
            and all(_condition(c) for c in conditions)
        ):
            errors.append(
                f"{where}.completion_conditions: must be a non-empty list of strings or {{text, note}} objects"
            )
    return errors


def _bullets(items: list[str]) -> str:
    """Render items as a Markdown bullet list.

    Args:
        items: Lines to render, one bullet each.
    """
    return "\n".join(f"- {item}" for item in items)


def _conditions(finding: Finding, with_notes: bool) -> str:
    """Render the completion conditions of a finding as a bullet list.

    Args:
        finding: A validated finding.
        with_notes: Whether to add each condition's note on the following line.
    """
    lines: list[str] = []
    for raw in finding["completion_conditions"]:
        normalized = _condition(raw)
        if normalized is None:
            continue
        text, note = normalized
        lines.append(f"- {text}")
        if with_notes and note:
            lines.append(f"  {note}")
    return "\n".join(lines)


def _location(finding: Finding) -> str:
    """Render the finding's location, marking LEFT-side lines.

    Args:
        finding: A validated finding.
    """
    loc = f"`{finding['path']}:{finding['line']}`"
    return f"{loc} (LEFT)" if finding.get("side") == "LEFT" else loc


def render_body(data: Document, findings: list[Finding], verdict: str) -> str:
    """Render the review body in the document's language.

    Args:
        data: The validated findings document.
        findings: Findings already ordered and numbered by position.
        verdict: APPROVE or REQUEST_CHANGES.

    Returns:
        The Markdown review body.
    """
    lb = LABELS[data["language"]]
    summary_lines = [data["summary"].strip(), *data.get("notes", [])]
    parts = [
        f"# {data['reviewer']} {lb['title']}",
        f"## {lb['summary']}",
        "\n".join(summary_lines),
        f"## {lb['verdict']}",
        verdict,
        f"## {lb['findings']}",
    ]
    if not findings:
        parts.append(lb["none"])
    for n, f in enumerate(findings, start=1):
        section = [
            f"### {n}. [{f['category']}] {f['summary']}",
            f"**{lb['location']}**: {_location(f)}",
            f"**{lb['problem']}**:\n{f['problem'].strip()}",
        ]
        if f["origin"] == "finder":
            hops = "\n".join(
                f"{i}. {hop}" for i, hop in enumerate(f["execution_path"], start=1)
            )
            section.append(f"**{lb['execution_path']}**:\n\n{hops}")
        else:
            section.append(f"**{lb['basis']}**:\n\n{_bullets(f['basis'])}")
        for key in ("other_locations", "notes"):
            if f.get(key):
                section.append(f"**{lb[key]}**:\n\n{_bullets(f[key])}")
        section.append(
            f"**{lb['completion_conditions']}**:\n\n{_conditions(f, with_notes=True)}"
        )
        parts.append("\n\n".join(section))
    parts.append(f"---\n\nReviewed by {data['reviewer']} at `{data['commit'][:7]}`")
    return "\n\n".join(parts) + "\n"


def render_comments(
    data: Document, findings: list[Finding]
) -> list[dict[str, str | int]]:
    """Build the inline comments payload for post_review.sh.

    Args:
        data: The validated findings document.
        findings: Findings already ordered and numbered by position.

    Returns:
        One entry per finding with path, line, side, and body.
    """
    lb = LABELS[data["language"]]
    comments: list[dict[str, str | int]] = []
    for n, f in enumerate(findings, start=1):
        body = "\n\n".join(
            [
                f"🔴 {n}: **[{f['category']}] {f['summary']}**",
                f"**{lb['problem']}**:\n{f['problem'].strip()}",
                f"**{lb['completion_conditions']}**:\n\n{_conditions(f, with_notes=False)}",
                "---",
                f"Commented by {data['reviewer']}",
            ]
        )
        comments.append(
            {
                "path": f["path"],
                "line": f["line"],
                "side": f.get("side", "RIGHT"),
                "body": body,
            }
        )
    return comments


def main() -> int:
    """Parse arguments, validate the findings, and write both outputs."""
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--findings", required=True, type=Path, help="findings JSON file"
    )
    parser.add_argument(
        "--out-dir",
        required=True,
        type=Path,
        help="directory for body.md and comments.json",
    )
    args = parser.parse_args()

    try:
        raw: object = json.loads(args.findings.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"{args.findings}: {exc}", file=sys.stderr)
        return 2
    errors = validate(raw)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 2
    data = cast(Document, raw)

    findings = sorted(data["findings"], key=lambda f: ORIGINS.index(f["origin"]))
    verdict = "REQUEST_CHANGES" if findings else "APPROVE"
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "body.md").write_text(
        render_body(data, findings, verdict), encoding="utf-8"
    )
    (args.out_dir / "comments.json").write_text(
        json.dumps(render_comments(data, findings), ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )
    print(verdict)
    return 0


if __name__ == "__main__":
    sys.exit(main())
