# exmd

[日本語](README_ja.md)

Explain a concept, mechanism, or research result as one GitHub-flavored Markdown file with frontmatter, a summary, a table of contents, a glossary table, Mermaid figures, and code. It renders as-is on GitHub, in VS Code, and in Obsidian. Even for a topic that is not in the conversation, it researches the topic and then explains it.

It is the Markdown counterpart of [`exhtml`](../exhtml/README.md); use that one for an HTML page. To write out what the conversation already established without adding anything, use [`chat-note`](../chat-note/README.md).

## Usage

- 「Markdownで解説して」
- 「exmdで作って」
- 「解説記事をMarkdownで」
- 「〜についてMarkdownにまとめて」

## Behavior

- Fixes the subject, plans the structure (background, main body, examples, limits and related items), and lists the technical terms first.
- Fills `assets/template.md`. The fixed parts (frontmatter fields and the summary, table of contents, and glossary sections) are not changed. An existing exmd page is updated in place: the file name stays and only the body, glossary, table of contents, and `updated` change.
- Runs `scripts/check_exmd.py` and fixes the file until it reports `ok`. The script also checks that the table of contents matches the headings. A file that has not passed is not reported as a result.
- Output goes to the path the user gives, otherwise the current directory as `YYYY-MM-DD-<slug>.md`. Asks before overwriting an existing file.
- Notation rules: GFM only (no raw HTML, images, or definition lists), no emoji or arrow characters, and no colors in Mermaid. Figures are Mermaid, and small changes to a file tree or pseudocode are shown in `diff` fences. Simple one-way procedures are numbered lists, not figures.

## Dependencies

- The `japanese-tech-writing` skill is called for prose style when it is installed. exmd defines only structure and notation.
- `python3` runs the check script.

The full procedure lives in [SKILL.md](SKILL.md).
