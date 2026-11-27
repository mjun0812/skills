#!/usr/bin/env python
"""Render a review report, inline comments, and review body from a findings JSON file.

Usage:
    render_review.py --pr-text <pr.md>
    render_review.py --pr-text <pr.md> --findings <findings.json> --out-dir <dir>
    render_review.py --pr-text <pr.md> --findings <findings.json> --out-dir <dir> \
        --posted <posted.json>

<pr.md> holds the PR title and body. Without --findings, prints the output
language (ja or en) decided from it. With --findings, writes <dir>/report.md
and <dir>/comments.json. report.md shows every finding in full for the chat;
comments.json holds the inline comments, which carry the same details on
GitHub. Adding --posted writes <dir>/body.md instead: the review body, which
lists the findings in tables that link to the inline comments in
<posted.json>. A finding without a posted inline comment keeps its details in
the body.

Each run prints the verdict (APPROVE or REQUEST_CHANGES) to stdout. Only
findings reproduced by running the code decide the verdict; findings that were
only traced through the code are listed as unproven. Validation errors,
including a language that does not match the PR text, are printed to stderr,
one per line, with exit code 2.

The findings JSON is documented in references/findings.md. Every layout
decision (ordering, numbering, field labels, footers) lives here so the
report, the inline comments, and the review body cannot disagree.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import NotRequired, TypedDict, cast

ORIGINS = ("finder", "claim")
PROOFS = ("reproduced", "traced")
SIDES = ("RIGHT", "LEFT")

# Code and URLs are English in both languages, so they do not count as prose.
_NON_PROSE = re.compile(r"```.*?```|`[^`\n]*`|https?://\S+", re.DOTALL)
_JAPANESE = re.compile(r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff]")
_LATIN = re.compile(r"[A-Za-z]")
# The heading render_comments writes: a mark, the finding number, a colon.
_COMMENT_NUMBER = re.compile(r"\S+ (\d+): ")


class Condition(TypedDict):
    """A completion condition with an optional note shown on the next line."""

    text: str
    note: NotRequired[str]


class Reproduction(TypedDict):
    """The command that showed the problem and what it printed."""

    command: str
    output: str


class Finding(TypedDict):
    """One confirmed finding as written by the reviewer."""

    origin: str
    proof: str
    reproduction: NotRequired[Reproduction]
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
        "unproven": "未証明の指摘",
        "unproven_note": "実行では再現できていない指摘。到達できることはコードで確かめている。判定には含めない。",
        "unproven_inline": "未証明: 実行では再現できていない",
        "none": "なし",
        "without_inline": "inline commentにできなかった指摘",
        "category": "種別",
        "finding": "指摘",
        "location": "場所",
        "problem": "問題",
        "execution_path": "発生経路",
        "reproduction": "再現",
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
        "unproven": "Unproven findings",
        "unproven_note": "Not reproduced by running the code. Reachability was confirmed by reading it. These do not affect the verdict.",
        "unproven_inline": "Unproven: not reproduced by running the code",
        "none": "N/A",
        "without_inline": "Findings without an inline comment",
        "category": "Category",
        "finding": "Finding",
        "location": "Location",
        "problem": "Problem",
        "execution_path": "Execution path",
        "reproduction": "Reproduction",
        "basis": "Basis",
        "other_locations": "Other locations",
        "notes": "Notes",
        "completion_conditions": "Completion condition",
    },
}


def detect_language(pr_text: str) -> str:
    """Decide the report language from the PR title and body.

    Japanese prose mixes in English identifiers, so the text counts as
    Japanese once Japanese characters make up a third of its letters.

    Args:
        pr_text: The PR title and body.

    Returns:
        ``ja`` when the prose is mainly Japanese, otherwise ``en``.
    """
    prose = _NON_PROSE.sub(" ", pr_text)
    japanese = len(_JAPANESE.findall(prose))
    latin = len(_LATIN.findall(prose))
    return "ja" if japanese and japanese * 2 >= latin else "en"


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


def validate(data: object, language: str) -> list[str]:
    """Check the findings document and return every violation found.

    Args:
        data: The parsed findings JSON.
        language: The language decided from the PR text.

    Returns:
        Human-readable violations, empty when the document is valid.
    """
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["document: must be a JSON object"]
    if data.get("language") != language:
        errors.append(
            f"language: must be {language!r}, decided from the PR title and body; "
            "rewrite every text field in that language"
        )
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
        proof = f.get("proof")
        if proof not in PROOFS:
            errors.append(f"{where}.proof: must be one of {list(PROOFS)}")
        if origin == "claim" and proof == "traced":
            errors.append(
                f"{where}.proof: must be reproduced for origin claim, "
                "a claim is confirmed only by command output"
            )
        reproduction = f.get("reproduction")
        if proof == "reproduced" and not (
            isinstance(reproduction, dict)
            and all(
                isinstance(reproduction.get(key), str) and reproduction[key].strip()
                for key in ("command", "output")
            )
        ):
            errors.append(
                f"{where}.reproduction: required for proof reproduced, "
                "an object with non-empty command and output"
            )
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
        if origin == "claim" and not (_is_str_list(f.get("basis")) and f["basis"]):
            errors.append(
                f"{where}.basis: required for origin claim, one item per entry"
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


def _conditions(finding: Finding) -> str:
    """Render the completion conditions of a finding as a bullet list.

    Args:
        finding: A validated finding.
    """
    lines: list[str] = []
    for raw in finding["completion_conditions"]:
        normalized = _condition(raw)
        if normalized is None:
            continue
        text, note = normalized
        lines.append(f"- {text}")
        if note:
            lines.append(f"  {note}")
    return "\n".join(lines)


def _reproduction(reproduction: Reproduction) -> str:
    """Render the command and its output as one fenced block.

    The fence is longer than any backtick run inside, so quoted output cannot
    close it early.

    Args:
        reproduction: The command and the output it printed.
    """
    text = f"$ {reproduction['command'].strip()}\n{reproduction['output'].strip()}"
    longest = max((len(run) for run in re.findall(r"`+", text)), default=0)
    fence = "`" * max(3, longest + 1)
    return f"{fence}text\n{text}\n{fence}"


def _location(finding: Finding) -> str:
    """Render the finding's location, marking LEFT-side lines.

    Args:
        finding: A validated finding.
    """
    loc = f"`{finding['path']}:{finding['line']}`"
    return f"{loc} (LEFT)" if finding.get("side") == "LEFT" else loc


def _details(finding: Finding, lb: dict[str, str]) -> list[str]:
    """Render every detail field of a finding, in the order all outputs share.

    Args:
        finding: A validated finding.
        lb: The labels of the output language.
    """
    parts = [f"**{lb['problem']}**:\n{finding['problem'].strip()}"]
    if finding["origin"] == "finder":
        hops = "\n".join(
            f"{i}. {hop}" for i, hop in enumerate(finding["execution_path"], start=1)
        )
        parts.append(f"**{lb['execution_path']}**:\n\n{hops}")
    else:
        parts.append(f"**{lb['basis']}**:\n\n{_bullets(finding['basis'])}")
    if finding["proof"] == "reproduced":
        parts.append(
            f"**{lb['reproduction']}**:\n\n{_reproduction(finding['reproduction'])}"
        )
    for key in ("other_locations", "notes"):
        if finding.get(key):
            parts.append(f"**{lb[key]}**:\n\n{_bullets(finding[key])}")
    parts.append(f"**{lb['completion_conditions']}**:\n\n{_conditions(finding)}")
    return parts


def _section(number: int, finding: Finding, lb: dict[str, str]) -> str:
    """Render one finding in full under its own heading.

    Args:
        number: The finding's number.
        finding: A validated finding.
        lb: The labels of the output language.
    """
    return "\n\n".join(
        [
            f"### {number}. [{finding['category']}] {finding['summary']}",
            f"**{lb['location']}**: {_location(finding)}",
            *_details(finding, lb),
        ]
    )


def _header(data: Document, verdict: str, lb: dict[str, str]) -> list[str]:
    """Render the title, summary, and verdict that open the report and the body.

    Args:
        data: The validated findings document.
        verdict: APPROVE or REQUEST_CHANGES.
        lb: The labels of the output language.
    """
    return [
        f"# {data['reviewer']} {lb['title']}",
        f"## {lb['summary']}",
        "\n".join([data["summary"].strip(), *data.get("notes", [])]),
        f"## {lb['verdict']}",
        verdict,
    ]


def _footer(data: Document) -> str:
    """Render the line that records the reviewer and the reviewed commit.

    Args:
        data: The validated findings document.
    """
    return f"---\n\nReviewed by {data['reviewer']} at `{data['commit'][:7]}`"


def render_report(data: Document, findings: list[Finding], verdict: str) -> str:
    """Render the full report shown in the chat, with every finding in detail.

    Args:
        data: The validated findings document.
        findings: Findings already ordered and numbered by position, with the
            reproduced ones first.
        verdict: APPROVE or REQUEST_CHANGES.

    Returns:
        The Markdown report.
    """
    lb = LABELS[data["language"]]
    parts = [*_header(data, verdict, lb), f"## {lb['findings']}"]
    if not any(f["proof"] == "reproduced" for f in findings):
        parts.append(lb["none"])
    unproven_started = False
    for n, f in enumerate(findings, start=1):
        if f["proof"] == "traced" and not unproven_started:
            parts.extend([f"## {lb['unproven']}", lb["unproven_note"]])
            unproven_started = True
        parts.append(_section(n, f, lb))
    parts.append(_footer(data))
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
        if f["proof"] == "reproduced":
            heading = [f"🔴 {n}: **[{f['category']}] {f['summary']}**"]
        else:
            heading = [
                f"🟡 {n}: **[{f['category']}] {f['summary']}**",
                f"_{lb['unproven_inline']}_",
            ]
        body = "\n\n".join(
            [*heading, *_details(f, lb), "---", f"Commented by {data['reviewer']}"]
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


def inline_urls(posted: list[dict[str, str]]) -> dict[int, str]:
    """Map finding numbers to the URLs of their posted inline comments.

    The number is read from the heading render_comments wrote, because the
    comments of a pending review carry no line to match on.

    Args:
        posted: The review comments the GitHub API returned.
    """
    urls: dict[int, str] = {}
    for comment in posted:
        match = _COMMENT_NUMBER.match(comment["body"])
        if match:
            urls[int(match[1])] = comment["html_url"]
    return urls


def _table(
    rows: list[tuple[int, Finding]], urls: dict[int, str], lb: dict[str, str]
) -> str:
    """Render findings as a table whose numbers link to their inline comments.

    Args:
        rows: Findings with their numbers.
        urls: Inline comment URLs by finding number.
        lb: The labels of the output language.
    """
    lines = [
        f"| # | {lb['category']} | {lb['location']} | {lb['finding']} |",
        "| --- | --- | --- | --- |",
    ]
    for n, f in rows:
        number = f"[{n}]({urls[n]})" if n in urls else str(n)
        # A pipe or a line break in a cell would end it early.
        category, summary = (
            " ".join(f[key].split()).replace("|", "\\|")
            for key in ("category", "summary")
        )
        lines.append(f"| {number} | {category} | {_location(f)} | {summary} |")
    return "\n".join(lines)


def render_body(
    data: Document, findings: list[Finding], verdict: str, urls: dict[int, str]
) -> str:
    """Render the review body posted to GitHub.

    Args:
        data: The validated findings document.
        findings: Findings already ordered and numbered by position, with the
            reproduced ones first.
        verdict: APPROVE or REQUEST_CHANGES.
        urls: Inline comment URLs by finding number. A finding missing here
            has no inline comment, so the body carries its details.

    Returns:
        The Markdown review body.
    """
    lb = LABELS[data["language"]]
    numbered = list(enumerate(findings, start=1))
    reproduced = [(n, f) for n, f in numbered if f["proof"] == "reproduced"]
    unproven = [(n, f) for n, f in numbered if f["proof"] == "traced"]
    parts = [
        *_header(data, verdict, lb),
        f"## {lb['findings']}",
        _table(reproduced, urls, lb) if reproduced else lb["none"],
    ]
    if unproven:
        parts.extend(
            [f"## {lb['unproven']}", lb["unproven_note"], _table(unproven, urls, lb)]
        )
    without_inline = [(n, f) for n, f in numbered if n not in urls]
    if without_inline:
        parts.append(f"## {lb['without_inline']}")
        parts.extend(_section(n, f, lb) for n, f in without_inline)
    parts.append(_footer(data))
    return "\n\n".join(parts) + "\n"


def main() -> int:
    """Parse arguments, validate the findings, and write the requested outputs."""
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--pr-text", required=True, type=Path, help="file with the PR title and body"
    )
    parser.add_argument("--findings", type=Path, help="findings JSON file")
    parser.add_argument("--out-dir", type=Path, help="directory for the outputs")
    parser.add_argument(
        "--posted",
        type=Path,
        help="review comments the GitHub API returned for the posted inline comments",
    )
    args = parser.parse_args()
    if (args.findings is None) != (args.out_dir is None):
        parser.error("--findings and --out-dir must be given together")
    if args.posted is not None and args.findings is None:
        parser.error("--posted requires --findings")

    try:
        language = detect_language(args.pr_text.read_text(encoding="utf-8"))
    except OSError as exc:
        print(f"{args.pr_text}: {exc}", file=sys.stderr)
        return 2
    if args.findings is None:
        print(language)
        return 0

    try:
        raw: object = json.loads(args.findings.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"{args.findings}: {exc}", file=sys.stderr)
        return 2
    errors = validate(raw, language)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 2
    data = cast(Document, raw)

    findings = sorted(
        data["findings"],
        key=lambda f: (PROOFS.index(f["proof"]), ORIGINS.index(f["origin"])),
    )
    reproduced = any(f["proof"] == "reproduced" for f in findings)
    verdict = "REQUEST_CHANGES" if reproduced else "APPROVE"
    args.out_dir.mkdir(parents=True, exist_ok=True)
    if args.posted is None:
        (args.out_dir / "report.md").write_text(
            render_report(data, findings, verdict), encoding="utf-8"
        )
        (args.out_dir / "comments.json").write_text(
            json.dumps(render_comments(data, findings), ensure_ascii=False, indent=2)
            + "\n",
            encoding="utf-8",
        )
    else:
        try:
            posted = cast(
                list[dict[str, str]],
                json.loads(args.posted.read_text(encoding="utf-8")),
            )
        except (OSError, ValueError) as exc:
            print(f"{args.posted}: {exc}", file=sys.stderr)
            return 2
        (args.out_dir / "body.md").write_text(
            render_body(data, findings, verdict, inline_urls(posted)), encoding="utf-8"
        )
    print(verdict)
    return 0


if __name__ == "__main__":
    sys.exit(main())
