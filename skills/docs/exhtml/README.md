# exhtml

[日本語](README_ja.md)

Explain a concept, mechanism, or research result as one self-contained HTML page. The page has a table of contents on the left and a glossary on the right, opens in the dark theme with a light toggle, and includes inline SVG or Mermaid figures and highlighted code. It needs no build step and opens directly in a browser.

The look is fixed by a bundled template; the agent writes only the content. For a Markdown version of the same kind of page, use [`exmd`](../exmd/README.md). To write down what the conversation already established, use [`chat-note`](../chat-note/README.md). It is not for standalone diagrams or slides.

## Usage

- 「HTMLで解説して」
- 「exhtmlで作って」
- 「解説ページにして」
- 「HTMLにまとめて」

## Behavior

- Fixes the subject (conversation content, a given file, or research results) and the intended reader, and plans the structure.
- The glossary is written after the body and holds only terms the intended reader does not know, in the order they first appear in the body. It has at most 20 entries, and every entry is linked from the body.
- Fills `assets/template.html`. The template part, the runtime block (theme toggle and table of contents generation), and page-specific `<style>` / `<script>` are not edited. Unused optional blocks (MathJax, Shiki, Mermaid) are removed.
- Runs `scripts/check_exhtml.py` and fixes the file until it reports `ok`. A file that has not passed is not reported as a result.
- Output goes to `/tmp/YYYY-MM-DD-<slug>.html`, overwriting a file with the same name. An existing exhtml page is updated in place: the file name stays and only the body, glossary, and `updated` change.
- On macOS it opens the file with `open`; if that fails the path is simply reported.
- Design rules: template tokens only for color, rounded corners only on chips, and no emoji, gradients, shadows, or external images. Figures use hand-drawn SVG for structure and Mermaid for branching, sequence, ER, and state diagrams. Simple one-way procedures are numbered lists, not figures.

## Dependencies

- The `japanese-tech-writing`, `cognitive-rhythm-writing`, and `stop-ai-slop-jp` skills are called for prose style when they are installed. exhtml defines only structure and appearance.
- `python3` runs the check script.

The full procedure lives in [SKILL.md](SKILL.md).
