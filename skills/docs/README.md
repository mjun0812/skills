# docs

Skills for writing and maintaining documents. Three of them turn a topic into a single readable page, and one keeps existing documentation in step with the code.

## Which skill to use

| Situation                                                   | Skill       |
| ----------------------------------------------------------- | ----------- |
| Write down what the current conversation established, as-is | `chat-note` |
| Explain a topic in Markdown, researching it first if needed | `exmd`      |
| Explain a topic as a self-contained HTML page               | `exhtml`    |
| Bring existing docs back in line with the implementation    | `doc-sync`  |

`chat-note` never adds outside information. `exmd` and `exhtml` may research the topic and share the same structure (summary, glossary, body, figures); they differ only in output format.

## chat-note

Write the facts, inferences, and open questions from the current conversation into one Japanese Markdown file with a table of contents and reference links. No extra research is done unless the user asks for it.

- Output: `YYYY-MM-DD-<slug>.md` in the current directory unless a path is given. Asks before overwriting.
- Trigger phrases: "今の内容をメモにまとめて", "ここまでの話をMarkdownにまとめて".

## doc-sync

Compare Markdown files, docstrings, OpenAPI specs, and example config files against the implementation, then rewrite the parts that are factually out of date. Style and wording differences are left alone, and the skill never commits.

| Argument    | Effect                                                                             |
| ----------- | ---------------------------------------------------------------------------------- |
| `--dry-run` | Report the drift and before/after previews without editing any file.               |
| `<path>`    | Limit the scan to a directory or file. Defaults to the whole repository.           |
| `language`  | Language for the updated text. Defaults to the language the document already uses. |

```text
/doc-sync                      # update the whole repository
/doc-sync --dry-run            # report only
/doc-sync docs/api/            # limit to one directory
/doc-sync README.md --dry-run  # preview a single file
```

Build output, dependency directories, and `.mjun/` are always excluded. Drift the skill cannot resolve with confidence is skipped and listed in the final report.

## exhtml

Explain a concept, mechanism, or research result as one self-contained HTML page: table of contents on the left, glossary on the right, dark theme with a light toggle, inline SVG or Mermaid figures, and highlighted code. The page layout comes from `exhtml/assets/template.html`; the agent fills in the content and runs `exhtml/scripts/check_exhtml.py` until it passes.

- Output: `/tmp/YYYY-MM-DD-<slug>.html` unless a path is given. Existing exhtml pages are updated in place.
- Trigger phrases: "HTMLで解説して", "exhtmlで作って", "解説ページにして".
- Uses the `japanese-tech-writing` skill for prose style when it is installed.

## exmd

The Markdown counterpart of `exhtml`. Produces one GitHub-flavored Markdown file with frontmatter, summary, table of contents, glossary table, and Mermaid figures, so it renders as-is on GitHub, in VS Code, and in Obsidian. The structure comes from `exmd/assets/template.md`; the agent fills in the content and runs `exmd/scripts/check_exmd.py`, which also verifies that the table of contents matches the headings.

- Output: `YYYY-MM-DD-<slug>.md` in the current directory unless a path is given. Existing exmd pages are updated in place.
- Trigger phrases: "Markdownで解説して", "exmdで作って", "〜についてMarkdownにまとめて".
- Uses the `japanese-tech-writing` skill for prose style when it is installed.

The rules each skill follows (structure, figures, notation, and design) live in its `SKILL.md`.
