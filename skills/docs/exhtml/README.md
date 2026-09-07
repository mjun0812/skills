# exhtml

Explain a concept, mechanism, or research result as a single self-contained HTML page with a glossary, a table of contents, figures, and code.

## When to use

- The user asks to "explain this in HTML", "make an exhtml", or "turn this into an explainer page".
- The reader should understand the topic without going back to the source material.

Do not use it for a Markdown summary (`chat-note`, `exmd`) or for a standalone diagram or slide.

## What it produces

One HTML file that opens directly in a browser with no build step. The layout is fixed by the bundled template: table of contents on the left, glossary on the right, dark theme by default with a light-theme toggle. The agent fills in the content only.

By default the file is saved as `/tmp/YYYY-MM-DD-<english-slug>.html`. Existing exhtml pages are updated in place, changing only the body and the `updated` date.

## How it works

1. Decide the subject from the conversation, a given file, or research results.
2. Plan the structure (terms, background, main topic, examples, notes) and list the technical terms up front.
3. Copy `assets/template.html` and fill in the placeholders (`{{TITLE}}`, `{{BODY}}`, `{{GLOSSARY}}`, and so on).
4. Remove unused optional blocks for MathJax, Shiki, and Mermaid.
5. Run `scripts/check_exhtml.py` and fix the page until it reports `ok`.
6. Report what was written, where it was saved, and the check result.

## Design rules

- The template's `<style>` and runtime script are never modified; the checker verifies they match the template.
- Colors come from the template tokens only. No emoji, symbol characters, gradients, shadows, or external images.
- Every technical term is defined in the glossary and linked from its first occurrence in the body.
- Figures are hand-drawn inline SVG for structures and relationships, Mermaid for branching flows, sequences, ER, and state diagrams, and numbered prose for linear steps.
- Small changes to existing structures (file trees, call trees, pseudocode) are shown as diffs.

## Files

- `SKILL.md`: the skill definition and the full set of structure, design, figure, code, and math rules.
- `assets/template.html`: the page template with the fixed stylesheet, runtime, and optional blocks.
- `scripts/check_exhtml.py`: validator that checks the output against the template and the rules.

## Related skills

- `japanese-tech-writing` is used for prose style when it is installed. `exhtml` only defines structure and appearance.
