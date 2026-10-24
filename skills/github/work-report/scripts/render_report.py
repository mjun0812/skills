#!/usr/bin/env python
"""Render the work report page from a report JSON file.

Usage:
    render_report.py <report.json> --out <report.html>

The report JSON is documented in references/report.md. The page layout and
styles live here so every report looks the same, and the JSON carries only the
content. Writes the page to --out and prints its path. Validation errors are
printed to stderr, one per line, with exit code 2.
"""

import argparse
import json
import sys
from html import escape
from pathlib import Path
from typing import Any

PILLS = {
    "merged": "merged",
    "open": "open",
    "closed": "closed",
    "draft": "draft",
    "approved": "approved",
    "changes_requested": "changes requested",
}

HEAD = """\
<meta charset="utf-8">
<title>{title}</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+JP:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
/* One-column work log: rows grouped by repository, numbers aligned on the left */
:root {{
  --bg: #f7f8fa; --surface: #ffffff; --fg: #1b2230; --muted: #5d6779; --line: #dfe3ea;
  --accent: #2f5fb3; --merged: #7a4fc2; --open: #1f8a4c; --closed: #8a5a1f; --changes: #b3372f;
  --sans: "IBM Plex Sans JP", "Hiragino Sans", "Noto Sans JP", system-ui, sans-serif;
  --mono: "IBM Plex Mono", ui-monospace, SFMono-Regular, Menlo, monospace;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --bg: #12161d; --surface: #1a1f28; --fg: #e4e8ef; --muted: #98a2b3; --line: #2b323e;
  --accent: #7fa6ec; --merged: #b291ec; --open: #5fc98b; --closed: #d5a35f; --changes: #ef8a80; color-scheme: dark }} }}
:root[data-theme="dark"] {{
  --bg: #12161d; --surface: #1a1f28; --fg: #e4e8ef; --muted: #98a2b3; --line: #2b323e;
  --accent: #7fa6ec; --merged: #b291ec; --open: #5fc98b; --closed: #d5a35f; --changes: #ef8a80; color-scheme: dark }}
body {{ margin: 0; background: var(--bg); color: var(--fg); font-family: var(--sans); font-size: 15px; line-height: 1.65;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); padding-block: 32px 64px; }}
main {{ max-width: 820px; margin: 0 auto; display: grid; gap: 36px; }}
header {{ display: grid; gap: 8px; }}
h1 {{ font-size: 1.6rem; margin: 0; text-wrap: balance; }}
.meta {{ color: var(--muted); font-size: .9rem; }}
.stats {{ display: flex; flex-wrap: wrap; gap: 8px 20px; font-size: .9rem; color: var(--muted); font-variant-numeric: tabular-nums; }}
.stats b {{ color: var(--fg); font-size: 1.1rem; margin-right: 4px; }}
h2 {{ font-size: 1.15rem; margin: 0 0 12px; padding-bottom: 6px; border-bottom: 1px solid var(--line); }}
h3 {{ font-size: .95rem; margin: 0 0 6px; display: flex; flex-wrap: wrap; gap: 4px 10px; align-items: baseline; }}
h3 .repo {{ font-family: var(--mono); font-weight: 500; color: var(--accent); }}
h3 .theme {{ color: var(--muted); font-weight: 400; font-size: .88rem; }}
section > div {{ display: grid; gap: 20px; }}
ul {{ list-style: none; margin: 0; padding: 0; background: var(--surface); border: 1px solid var(--line); border-radius: 6px; }}
li {{ display: grid; grid-template-columns: 4.2em 1fr auto; gap: 10px; padding: 8px 12px; border-top: 1px solid var(--line); align-items: baseline; }}
li:first-child {{ border-top: 0; }}
li > * {{ min-width: 0; }}
.num {{ font-family: var(--mono); font-size: .88rem; font-variant-numeric: tabular-nums; }}
a {{ color: var(--accent); text-decoration: none; }}
a:hover, a:focus-visible {{ text-decoration: underline; }}
a:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 2px; border-radius: 2px; }}
.date {{ font-family: var(--mono); font-size: .82rem; color: var(--muted); white-space: nowrap; }}
.pill {{ display: inline-block; font-size: .72rem; font-weight: 500; letter-spacing: .04em; padding: 0 6px; border-radius: 999px; border: 1px solid currentColor; margin-right: 6px; vertical-align: 1px; }}
.merged {{ color: var(--merged); }} .open, .approved {{ color: var(--open); }} .closed {{ color: var(--closed); }}
.changes_requested {{ color: var(--changes); }} .draft, .tag {{ color: var(--muted); }}
.note {{ color: var(--muted); font-size: .85rem; display: block; }}
.multi li {{ grid-template-columns: 1fr auto; }}
.repos {{ display: flex; flex-wrap: wrap; gap: 4px 12px; font-family: var(--mono); font-size: .85rem; margin-top: 4px; }}
footer {{ color: var(--muted); font-size: .82rem; }}
@media (max-width: 480px) {{ li {{ grid-template-columns: 3.6em 1fr; }} li .date {{ grid-column: 2; }} .multi li {{ grid-template-columns: 1fr; }} .multi li .date {{ grid-column: 1; }} }}
</style>
"""


def _text(value: object) -> bool:
    """Return whether value is a non-empty string.

    Args:
        value: A parsed JSON value.
    """
    return isinstance(value, str) and bool(value.strip())


def _link(value: object) -> bool:
    """Return whether value is an object with non-empty text and url.

    Args:
        value: A parsed JSON value.
    """
    return (
        isinstance(value, dict) and _text(value.get("text")) and _text(value.get("url"))
    )


def validate_item(item: object, where: str) -> list[str]:
    """Check one row of a group.

    Args:
        item: The parsed row.
        where: The row's location, used as the prefix of each violation.

    Returns:
        Human-readable violations, empty when the row is valid.
    """
    if not isinstance(item, dict):
        return [f"{where}: must be an object"]
    errors = [
        f"{where}.{key}: must be a non-empty string"
        for key in ("title", "date")
        if not _text(item.get(key))
    ]
    if "state" in item and item["state"] not in PILLS:
        errors.append(f"{where}.state: must be one of {list(PILLS)}")
    for key in ("note", "tag"):
        if key in item and not _text(item[key]):
            errors.append(f"{where}.{key}: must be a non-empty string when present")
    numbered = "number" in item or "url" in item
    if numbered and "links" in item:
        errors.append(f"{where}: needs number and url, or links, not both")
    elif numbered and not (
        isinstance(item.get("number"), int) and _text(item.get("url"))
    ):
        errors.append(f"{where}: number must be an integer and url a non-empty string")
    elif "links" in item and not (
        isinstance(item["links"], list)
        and item["links"]
        and all(_link(link) for link in item["links"])
    ):
        errors.append(f"{where}.links: must be a non-empty list of {{text, url}}")
    return errors


def validate(data: object) -> list[str]:
    """Check the report document and return every violation found.

    Args:
        data: The parsed report JSON.

    Returns:
        Human-readable violations, empty when the document is valid.
    """
    if not isinstance(data, dict):
        return ["document: must be a JSON object"]
    errors = [
        f"{key}: must be a non-empty string"
        for key in ("title", "heading", "meta", "footer")
        if not _text(data.get(key))
    ]
    stats = data.get("stats")
    if not isinstance(stats, list) or not all(
        isinstance(s, dict)
        and isinstance(s.get("value"), int)
        and _text(s.get("label"))
        for s in stats
    ):
        errors.append("stats: must be a list of {value: integer, label: string}")
    sections = data.get("sections")
    if not (isinstance(sections, list) and sections):
        return [*errors, "sections: must be a non-empty list"]
    for i, section in enumerate(sections):
        where = f"sections[{i}]"
        if not (isinstance(section, dict) and _text(section.get("heading"))):
            errors.append(f"{where}.heading: must be a non-empty string")
            continue
        groups = section.get("groups")
        if not (isinstance(groups, list) and groups):
            errors.append(f"{where}.groups: must be a non-empty list")
            continue
        for j, group in enumerate(groups):
            gwhere = f"{where}.groups[{j}]"
            if not isinstance(group, dict):
                errors.append(f"{gwhere}: must be an object")
                continue
            for key in ("label", "theme"):
                if key in group and not _text(group[key]):
                    errors.append(
                        f"{gwhere}.{key}: must be a non-empty string when present"
                    )
            items = group.get("items")
            if not (isinstance(items, list) and items):
                errors.append(f"{gwhere}.items: must be a non-empty list")
                continue
            item_errors = [
                e
                for k, item in enumerate(items)
                for e in validate_item(item, f"{gwhere}.items[{k}]")
            ]
            errors.extend(item_errors)
            if not item_errors and len({"number" in item for item in items}) > 1:
                errors.append(
                    f"{gwhere}.items: rows with a number and rows without one cannot share a group"
                )
    return errors


def render_item(item: dict[str, Any]) -> str:
    """Render one row.

    Args:
        item: A validated row.

    Returns:
        The row's <li> element.
    """
    body = ""
    if "state" in item:
        body += f'<span class="pill {item["state"]}">{PILLS[item["state"]]}</span>'
    if "tag" in item:
        body += f'<span class="pill tag">{escape(item["tag"])}</span>'
    body += escape(item["title"])
    if "note" in item:
        body += f'<span class="note">{escape(item["note"])}</span>'
    date = f'<span class="date">{escape(item["date"])}</span>'
    if "number" in item:
        number = f'<a class="num" href="{escape(item["url"])}">#{item["number"]}</a>'
        return f"<li>{number}<span>{body}</span>{date}</li>"
    if "links" in item:
        links = "".join(
            f'<a href="{escape(link["url"])}">{escape(link["text"])}</a>'
            for link in item["links"]
        )
        body += f'<span class="repos">{links}</span>'
    return f"<li><span>{body}</span>{date}</li>"


def render_group(group: dict[str, Any]) -> str:
    """Render one group of rows with its optional label and theme.

    Args:
        group: A validated group.

    Returns:
        The group's <div> element.
    """
    heading = ""
    if "label" in group:
        heading += f'<span class="repo">{escape(group["label"])}</span>'
    if "theme" in group:
        heading += f'<span class="theme">{escape(group["theme"])}</span>'
    if heading:
        heading = f"<h3>{heading}</h3>\n"
    multi = "" if "number" in group["items"][0] else ' class="multi"'
    rows = "\n".join(render_item(item) for item in group["items"])
    return f"<div>\n{heading}<ul{multi}>\n{rows}\n</ul>\n</div>"


def render(data: dict[str, Any]) -> str:
    """Render the whole page.

    Args:
        data: A validated report document.

    Returns:
        The page as HTML.
    """
    stats = "".join(
        f"<span><b>{s['value']}</b>{escape(s['label'])}</span>" for s in data["stats"]
    )
    header = (
        f"<header>\n<h1>{escape(data['heading'])}</h1>\n"
        f'<div class="meta">{escape(data["meta"])}</div>\n'
        + (f'<div class="stats">{stats}</div>\n' if stats else "")
        + "</header>"
    )
    sections = "\n".join(
        f"<section>\n<h2>{escape(section['heading'])}</h2>\n<div>\n"
        + "\n".join(render_group(group) for group in section["groups"])
        + "\n</div>\n</section>"
        for section in data["sections"]
    )
    return (
        HEAD.format(title=escape(data["title"]))
        + f'\n<main lang="{escape(data.get("lang", "ja"))}">\n{header}\n{sections}\n'
        + f"<footer>{escape(data['footer'])}</footer>\n</main>\n"
    )


def main() -> None:
    """Validate the report JSON and write the page."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("report", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    data = json.loads(args.report.read_text())
    errors = validate(data)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        sys.exit(2)
    args.out.write_text(render(data))
    print(args.out)


if __name__ == "__main__":
    main()
