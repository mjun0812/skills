# exmd

Explain a concept, mechanism, or research result as a single GitHub-flavored Markdown page with a glossary table, a table of contents, Mermaid figures, and code.

## When to use

- The user asks to "explain this in Markdown", "make an exmd", or "write a Markdown article about X".
- The topic may not have been discussed yet. The skill researches it first and then explains it.

Do not use it to write out a conversation as-is (`chat-note`) or for an HTML explainer (`exhtml`).

## What it produces

One Markdown file that renders as-is on GitHub, in VS Code, and in Obsidian. The structure is fixed by the bundled template: frontmatter, summary, table of contents, glossary table, then the body starting with a background section. The agent fills in the content only.

By default the file is saved in the current directory as `YYYY-MM-DD-<english-slug>.md`. Existing exmd pages are updated in place, changing only the body, glossary, table of contents, and the `updated` date.

## How it works

1. Decide the subject from the conversation, a given file, or research results.
2. Plan the structure (background, main topic, examples, notes) and list the technical terms up front.
3. Copy `assets/template.md` and fill in the placeholders (`{{TITLE}}`, `{{TOC}}`, `{{GLOSSARY}}`, `{{BODY}}`, and so on).
4. Run `scripts/check_exmd.py` and fix the page until it reports `ok`. The checker verifies that the table of contents matches the headings.
5. Report what was written, where it was saved, and the check result.

## Writing rules

- Only GFM syntax. No raw HTML, images, or definition lists.
- No emoji, symbol characters, arrow characters, or ASCII art. Figures are drawn with Mermaid.
- Mermaid diagrams use square nodes only and carry no colors, so they render on both GitHub themes.
- Every technical term is defined in the glossary table in order of first appearance.
- Small changes to existing structures (file trees, call trees, pseudocode) are shown in `diff` fences.
- Table-of-contents anchors follow GitHub's heading-anchor rules.

## Files

- `SKILL.md`: the skill definition and the full set of structure, notation, figure, and code rules.
- `assets/template.md`: the page template with the fixed frontmatter and section layout.
- `scripts/check_exmd.py`: validator that checks the output against the template and the rules.

## Related skills

- `japanese-tech-writing` is used for prose style when it is installed. `exmd` only defines structure and notation.
