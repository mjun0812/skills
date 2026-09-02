#!/usr/bin/env python3
"""exmd で生成した Markdown を機械的に検査する。

標準ライブラリだけで次を確認する。

- frontmatter (title / model / created / updated) とテンプレートの目印がある
- {{...}} プレースホルダーが残っていない
- h1 が 1 つだけで、見出しレベルが飛んでいない
- 要約が 1〜3 項目、用語の表が 2 列で 1 行以上ある
- 目次のリンクが GFM の見出し anchor と一致し、本文の h2/h3 がすべて目次にある
- 絵文字・矢印文字・生の HTML タグ・画像が本文にない
- コードブロックに言語があり、Mermaid 記法に色指定・HTML タグ・角丸ノードが無い

Usage:
    check_exmd.py <file.md>

Exit status: 0 = ok, 1 = 違反あり, 2 = 引数・ファイルの誤り
"""

from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

MARKER = "<!-- exmd template v1 -->"
FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
FENCE_RE = re.compile(r"^(```|~~~)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
TOC_LINK_RE = re.compile(r"\[([^\]]*)\]\(#([^)]+)\)")
# 絵文字と記号 (U+2600-27BF は ✅ ⚠ ❌ など)、矢印 (U+2190-21FF, 27F0-27FF, 2900-297F, 2B00-2BFF)
EMOJI_RE = re.compile(
    "[\U0001f000-\U0001faff\u2600-\u27bf\u2190-\u21ff\u27f0-\u27ff\u2900-\u297f\u2b00-\u2bff\ufe0f]"
)
HTML_TAG_RE = re.compile(r"</?[a-zA-Z][^>]*>")
IMAGE_RE = re.compile(r"!\[[^\]]*\]\(")
ROUNDED_NODE_RE = re.compile(r"(?m)(?:^|>|-|\|)\s*\w+\((?!\()")
FIXED_SECTIONS = ("要約", "目次", "用語")


def gfm_slug(text: str) -> str:
    """GitHub が見出しに付ける anchor を再現する。

    Args:
        text: 見出しのテキスト (Markdown の装飾を含んでよい)。

    Returns:
        anchor 文字列 (# を除く)。
    """
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"[*_]{1,2}([^*_]+)[*_]{1,2}", r"\1", text)
    out = []
    for ch in text.lower():
        if ch in " -_" or unicodedata.category(ch)[0] in ("L", "N", "M"):
            out.append(ch)
    return "".join(out).replace(" ", "-")


def split_blocks(
    lines: list[str],
) -> tuple[list[tuple[int, str]], list[tuple[str, str]]]:
    """コードブロックの外の行と、コードブロック (言語, 中身) を分ける。

    Args:
        lines: ファイルの行 (改行なし)。

    Returns:
        (本文の行の (行番号, 行), コードブロックの (言語, 中身) の一覧)。
    """
    prose: list[tuple[int, str]] = []
    blocks: list[tuple[str, str]] = []
    fence: str | None = None
    lang = ""
    buf: list[str] = []
    for i, line in enumerate(lines, 1):
        m = FENCE_RE.match(line)
        if fence is None and m:
            fence = line[:3]
            lang = line[3:].strip()
            buf = []
            continue
        if fence is not None and line.startswith(fence):
            blocks.append((lang, "\n".join(buf)))
            fence = None
            continue
        if fence is not None:
            buf.append(line)
        else:
            prose.append((i, line))
    return prose, blocks


def check(path: Path) -> list[str]:
    """1 ファイルを検査し、違反メッセージの一覧を返す。"""
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")

    fm = FRONTMATTER_RE.match(text)
    if not fm:
        errors.append("先頭に frontmatter (--- ... ---) が無い")
    else:
        fields = dict(re.findall(r"^(\w+):[ \t]*(.*)$", fm.group(1), re.MULTILINE))
        for key in ("title", "model"):
            if not fields.get(key, "").strip():
                errors.append(f"frontmatter の {key} が空")
        for key in ("created", "updated"):
            if not DATE_RE.match(fields.get(key, "").strip()):
                errors.append(
                    f"frontmatter の {key} が YYYY-MM-DD ではない: {fields.get(key)!r}"
                )
        if " " in fields.get("model", "").strip():
            errors.append("frontmatter の model に空白がある")
    if MARKER not in text:
        errors.append(f"テンプレートの目印 {MARKER} が無い")
    if "{{" in text:
        errors.append("{{...}} プレースホルダーが残っている")

    body_start = fm.end() if fm else 0
    lines = text[body_start:].split("\n")
    prose, blocks = split_blocks(lines)
    prose_text = "\n".join(line for _, line in prose)

    headings: list[tuple[int, str, str]] = []  # (level, text, slug)
    counts: dict[str, int] = {}
    prev_level = 0
    for _, line in prose:
        m = HEADING_RE.match(line)
        if not m:
            continue
        level, htext = len(m.group(1)), m.group(2)
        base = gfm_slug(htext)
        n = counts.get(base, 0)
        counts[base] = n + 1
        slug = base if n == 0 else f"{base}-{n}"
        if prev_level and level > prev_level + 1:
            errors.append(
                f"見出しレベルが飛んでいる: h{prev_level} の直後に h{level} ({htext})"
            )
        prev_level = level
        headings.append((level, htext, slug))

    h1 = [h for h in headings if h[0] == 1]
    if len(h1) != 1:
        errors.append(f"h1 は 1 つだけ (見つかった数: {len(h1)})")

    def section(name: str) -> list[str]:
        """## name の直下から次の見出しまでの行を返す。"""
        out: list[str] = []
        inside = False
        for _, line in prose:
            m = HEADING_RE.match(line)
            if m:
                inside = len(m.group(1)) == 2 and m.group(2) == name
                continue
            if inside:
                out.append(line)
        return out

    summary_items = [
        line for line in section("要約") if re.match(r"^\s*[-*]\s+\S", line)
    ]
    if not 1 <= len(summary_items) <= 3:
        errors.append(f"要約は 1〜3 項目 (見つかった数: {len(summary_items)})")

    toc_lines = section("目次")
    toc_targets = [slug for _, slug in TOC_LINK_RE.findall("\n".join(toc_lines))]
    if not toc_targets:
        errors.append("目次にリンクが無い")
    slugs = {slug for _, _, slug in headings}
    for target in toc_targets:
        if target not in slugs:
            errors.append(f"目次のリンク先 #{target} に対応する見出しが無い")
    for level, htext, slug in headings:
        if level in (2, 3) and htext not in FIXED_SECTIONS and slug not in toc_targets:
            errors.append(f"見出し「{htext}」が目次に無い (#{slug})")

    glossary_rows = [line for line in section("用語") if line.startswith("|")]
    data_rows = [r for r in glossary_rows[2:] if r.strip("| ").strip()]
    if len(glossary_rows) < 2:
        errors.append("用語の表が無い")
    elif not data_rows:
        errors.append("用語の表に行が無い")
    else:
        for row in data_rows:
            if row.strip().strip("|").count("|") != 1:
                errors.append(f"用語の表は 2 列にする: {row.strip()}")

    bad_chars = sorted(set(EMOJI_RE.findall(prose_text)))
    if bad_chars:
        errors.append(f"本文に絵文字または矢印文字がある: {' '.join(bad_chars)}")
    for tag in HTML_TAG_RE.findall(prose_text.replace(MARKER, "")):
        errors.append(f"本文に HTML タグがある (Markdown だけで書く): {tag}")
    if IMAGE_RE.search(prose_text):
        errors.append("画像は使わない。図は Mermaid で描く")

    mermaid_count = 0
    for i, (lang, src) in enumerate(blocks, 1):
        if not lang:
            errors.append(
                f"コードブロック #{i} に言語が無い (ハイライトしない場合は text)"
            )
            continue
        if lang != "mermaid":
            continue
        mermaid_count += 1
        if re.search(r"<\s*br|<[a-z]+>", src, re.IGNORECASE):
            errors.append(f"Mermaid #{mermaid_count} のラベルに HTML タグがある")
        if re.search(
            r"^\s*(classDef|style|linkStyle)\b|%%\{\s*init|\b(fill|stroke|color)\s*:",
            src,
            re.MULTILINE,
        ):
            errors.append(
                f"Mermaid #{mermaid_count} に色や style の指定がある (色は使わない)"
            )
        head = src.strip().split("\n", 1)[0]
        if head.startswith(("flowchart", "graph")) and ROUNDED_NODE_RE.search(src):
            errors.append(
                f"Mermaid #{mermaid_count} (flowchart) に角丸ノード id(...) がある。id[...] を使う"
            )

    return errors


def main(argv: list[str]) -> int:
    """引数の Markdown を検査し、結果を表示して終了コードを返す。"""
    if len(argv) != 2 or argv[1] in ("-h", "--help"):
        print("usage: check_exmd.py <file.md>", file=sys.stderr)
        return 2
    path = Path(argv[1])
    if not path.is_file():
        print(f"ファイルが見つからない: {path}", file=sys.stderr)
        return 2
    errors = check(path)
    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        print(f"{len(errors)} 件の違反: {path}")
        return 1
    print(f"ok: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
