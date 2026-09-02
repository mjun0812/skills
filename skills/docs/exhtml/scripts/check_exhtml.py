#!/usr/bin/env python3
"""exhtml で生成した HTML を機械的に検査する。

ブラウザを使わず、標準ライブラリだけで次を確認する。

- テンプレートの目印と <style> がテンプレートと一致している (テンプレート部分の改変禁止)
- {{...}} プレースホルダーが残っていない
- h2/h3 に id があり、id が文書全体で一意
- 用語集の dt に term- で始まる id があり、#term- 参照先が存在する
- 冒頭要約が 1〜3 項目、メタ行が created/updated/model の形式
- 絵文字・矢印文字・外部画像・追加 <style>・追加 <script>・border-radius の混入がない
- SVG 属性や Mermaid 記法に生の色指定が無い (図の色は c1〜c4 クラスだけ)
- Mermaid / shiki / MathJax の任意ブロックが、使用有無と一致して残っている (削除されている)
- Mermaid 記法に <br> やタグ、flowchart の角丸ノードが無い
- 手描き SVG が .ex-figure-frame の中にあり viewBox を持つ

Usage:
    check_exhtml.py <file.html>

Exit status: 0 = ok, 1 = 違反あり, 2 = 引数・ファイルの誤り
"""

from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "template.html"
MARKER = "<!-- exhtml template v1 -->"
OPTIONAL_BLOCKS = ("mathjax", "shiki", "mermaid")
REQUIRED_BLOCKS = ("runtime",)
STYLE_RE = re.compile(r"<style>(.*?)</style>", re.DOTALL)
BLOCK_RE = {
    name: re.compile(rf"<!-- exhtml:{name}\b.*?<!-- /exhtml:{name} -->", re.DOTALL)
    for name in OPTIONAL_BLOCKS + REQUIRED_BLOCKS
}
META_RE = re.compile(
    r"^created \d{4}-\d{2}-\d{2} / updated \d{4}-\d{2}-\d{2} / model \S+"
)
# 絵文字と記号 (U+2600-27BF は ✅ ⚠ ❌ など)、矢印 (U+2190-21FF, 27F0-27FF, 2900-297F, 2B00-2BFF)
EMOJI_RE = re.compile(
    "[\U0001f000-\U0001faff\u2600-\u27bf\u2190-\u21ff\u27f0-\u27ff\u2900-\u297f\u2b00-\u2bff\ufe0f]"
)
# flowchart の行頭または矢印の直後にある id(...) 形式 (角丸ノード)。id((...)) の円は別扱い
ROUNDED_NODE_RE = re.compile(r"(?m)(?:^|>|-|\|)\s*\w+\((?!\()")
VOID_TAGS = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "source",
    "track",
    "wbr",
}
MATH_RE = re.compile(r"\$\$|\\\(|\\\[|\$[^$\n]+\$")
LANG_RE = re.compile(r"language-([\w-]+)")
# Mermaid 記法は HTMLParser を通すと <br/> がタグとして消えるため生テキストから取る
MERMAID_RE = re.compile(
    r'<pre[^>]*class="[^"]*\bmermaid\b[^"]*"[^>]*>(.*?)</pre>', re.DOTALL
)
PLAIN_LANGS = {"plaintext", "text"}


class Page(HTMLParser):
    """検査に必要な情報だけを集める最小の DOM 走査。"""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, dict[str, str | None]]] = []
        self.ids: list[str] = []
        self.headings: list[tuple[str, str | None]] = []
        self.anchors: list[str] = []
        self.glossary_dts: list[str | None] = []
        self.summary_items = 0
        self.meta_text = ""
        self.prose: list[str] = []
        self.code_langs: list[str | None] = []
        self.images: list[str] = []
        self.inline_radius = 0
        self.raw_colors: list[str] = []
        self.svgs: list[tuple[bool, bool]] = []  # (in .ex-figure-frame, has viewBox)
        self.html_lang: str | None = None
        self._capture: list[tuple[str, list[str]]] = []

    # -- helpers ---------------------------------------------------------
    def _classes(self, attrs: dict[str, str | None]) -> set[str]:
        return set((attrs.get("class") or "").split())

    def _inside(self, tag: str | None = None, cls: str | None = None) -> bool:
        for name, attrs in self.stack:
            if tag and name != tag:
                continue
            if cls and cls not in self._classes(attrs):
                continue
            return True
        return False

    # -- parser hooks ----------------------------------------------------
    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = dict(attrs)
        classes = self._classes(a)
        if tag == "html":
            self.html_lang = a.get("lang")
        if a.get("id"):
            self.ids.append(a["id"] or "")
        if tag in ("h2", "h3") and self._inside("main"):
            self.headings.append((tag, a.get("id")))
        if tag == "a" and (a.get("href") or "").startswith("#"):
            self.anchors.append((a.get("href") or "")[1:])
        if tag == "dt" and self._inside("aside", "ex-glossary"):
            self.glossary_dts.append(a.get("id"))
        if tag == "li" and self._inside("div", "ex-summary"):
            self.summary_items += 1
        if tag == "img":
            self.images.append(a.get("src") or "")
        if "border-radius" in (a.get("style") or ""):
            self.inline_radius += 1
        if self._inside("svg") and not self._inside("svg", "ex-defs"):
            for attr in ("fill", "stroke", "color"):
                value = (a.get(attr) or "").strip()
                if value and value not in ("none", "currentColor", "transparent"):
                    self.raw_colors.append(f'<{tag} {attr}="{value}">')
            if re.search(r"(fill|stroke|color)\s*:", a.get("style") or ""):
                self.raw_colors.append(f'<{tag} style="{a.get("style")}">')
        if (
            tag == "svg"
            and "ex-defs" not in classes
            and not self._inside("pre", "mermaid")
        ):
            self.svgs.append((self._inside(cls="ex-figure-frame"), "viewbox" in a))
        if tag == "code" and self._inside("pre"):
            m = LANG_RE.search(a.get("class") or "")
            self.code_langs.append(m.group(1) if m else None)
        if tag == "p" and "ex-meta" in classes:
            self._capture.append(("meta", []))
        if tag not in VOID_TAGS:
            self.stack.append((tag, a))

    def handle_endtag(self, tag: str) -> None:
        while self.stack:
            name, attrs = self.stack.pop()
            classes = self._classes(attrs)
            if (
                name == "p"
                and "ex-meta" in classes
                and self._capture
                and self._capture[-1][0] == "meta"
            ):
                self.meta_text = "".join(self._capture.pop()[1]).strip()
            if name == tag:
                break

    def handle_data(self, data: str) -> None:
        if self._capture:
            self._capture[-1][1].append(data)
        if (
            not self._inside("pre")
            and not self._inside("code")
            and not self._inside("script")
            and not self._inside("style")
        ):
            self.prose.append(data)


def check(path: Path) -> list[str]:
    """1 ファイルを検査し、違反メッセージの一覧を返す。"""
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    template = TEMPLATE.read_text(encoding="utf-8")

    if not text.startswith(MARKER):
        errors.append(f"先頭行がテンプレートの目印 {MARKER} ではない")
    if "{{" in text:
        errors.append("{{...}} プレースホルダーが残っている")

    styles = STYLE_RE.findall(text)
    template_style = STYLE_RE.findall(template)
    if len(styles) != 1:
        errors.append(f"<style> は 1 つだけ許可 (見つかった数: {len(styles)})")
    elif styles[0] != template_style[0]:
        errors.append(
            "<style> の内容がテンプレートと一致しない (テンプレート部分を書き換えない)"
        )

    rest = text
    for name, pattern in BLOCK_RE.items():
        found = pattern.findall(text)
        if name in REQUIRED_BLOCKS and len(found) != 1:
            errors.append(f"exhtml:{name} ブロックは必須 (見つかった数: {len(found)})")
        if len(found) > 1:
            errors.append(f"exhtml:{name} ブロックが重複している")
        rest = pattern.sub("", rest)
    if "<script" in rest:
        errors.append(
            "テンプレートのブロック以外に <script> がある (ページ固有の script は禁止)"
        )

    page = Page()
    page.feed(text)

    if page.html_lang != "ja":
        errors.append('<html lang="ja"> になっていない')

    duplicates = sorted({i for i in page.ids if page.ids.count(i) > 1})
    if duplicates:
        errors.append(f"id が重複している: {', '.join(duplicates)}")
    for tag, hid in page.headings:
        if not hid:
            errors.append(f"main 内の <{tag}> に id が無い")
    id_set = set(page.ids)
    for target in page.anchors:
        if target and target not in id_set:
            errors.append(f"リンク先 #{target} が存在しない")

    if not page.glossary_dts:
        errors.append("用語集 (aside.ex-glossary) に <dt> が 1 つも無い")
    for dt_id in page.glossary_dts:
        if not dt_id or not dt_id.startswith("term-"):
            errors.append(f"用語集の <dt> に term- で始まる id が無い (id={dt_id!r})")

    if not 1 <= page.summary_items <= 3:
        errors.append(
            f"冒頭要約 (.ex-summary) は 1〜3 項目 (見つかった数: {page.summary_items})"
        )
    if not META_RE.match(page.meta_text):
        errors.append(
            f"メタ行が 'created YYYY-MM-DD / updated YYYY-MM-DD / model <name>' の形式ではない: {page.meta_text!r}"
        )

    prose = "".join(page.prose)
    bad_chars = sorted(set(EMOJI_RE.findall(prose)))
    if bad_chars:
        errors.append(f"本文に絵文字または矢印文字がある: {' '.join(bad_chars)}")

    for src in page.images:
        if not src.startswith("data:"):
            errors.append(f"外部画像は禁止 (data: URI のみ許可): {src}")
    if page.inline_radius:
        errors.append(
            f"inline style に border-radius がある ({page.inline_radius} 箇所)"
        )
    for raw in page.raw_colors[:5]:
        errors.append(
            f"SVG に生の色指定がある。色は fig-node の c1〜c4 クラスで付ける: {raw}"
        )

    for lang in page.code_langs:
        if lang is None:
            errors.append(
                "<pre><code> に language-* クラスが無い (ハイライトしない場合は language-plaintext)"
            )

    mermaid_sources = MERMAID_RE.findall(text)
    for i, src in enumerate(mermaid_sources):
        if re.search(r"<\s*br|<\s*b\s*>|<[a-z]+>", src, re.IGNORECASE):
            errors.append(
                f"Mermaid #{i + 1} のラベルに HTML タグがある (securityLevel strict では描画されない)"
            )
        if re.search(
            r"^\s*(classDef|style|linkStyle)\b|%%\{\s*init|\b(fill|stroke|color)\s*:",
            src,
            re.MULTILINE,
        ):
            errors.append(
                f"Mermaid #{i + 1} に色や style の指定がある。色は class A c1 のように c1〜c4 を付ける"
            )
        head = src.strip().split("\n", 1)[0]
        if head.startswith(("flowchart", "graph")) and ROUNDED_NODE_RE.search(src):
            errors.append(
                f"Mermaid #{i + 1} (flowchart) に角丸ノード id(...) がある。角丸禁止なので id[...] を使う"
            )

    for in_frame, has_viewbox in page.svgs:
        if not in_frame:
            errors.append("手描き SVG が .ex-figure-frame の外にある")
        if not has_viewbox:
            errors.append("手描き SVG に viewBox が無い")

    uses = {
        "mermaid": bool(mermaid_sources),
        "shiki": any(lang and lang not in PLAIN_LANGS for lang in page.code_langs),
        "mathjax": bool(MATH_RE.search(prose)),
    }
    for name, used in uses.items():
        present = bool(BLOCK_RE[name].search(text))
        if used and not present:
            errors.append(f"{name} を使っているのに exhtml:{name} ブロックが無い")
        if present and not used:
            errors.append(f"{name} を使っていないので exhtml:{name} ブロックを削除する")

    return errors


def main(argv: list[str]) -> int:
    """引数の HTML を検査し、結果を表示して終了コードを返す。"""
    if len(argv) != 2 or argv[1] in ("-h", "--help"):
        print("usage: check_exhtml.py <file.html>", file=sys.stderr)
        return 2
    path = Path(argv[1])
    if not path.is_file():
        print(f"ファイルが見つからない: {path}", file=sys.stderr)
        return 2
    if not TEMPLATE.is_file():
        print(f"テンプレートが見つからない: {TEMPLATE}", file=sys.stderr)
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
