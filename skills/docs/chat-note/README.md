# chat-note

[日本語](README_ja.md)

Write what the current conversation established into a single Japanese Markdown file, keeping facts, inferences, and open questions separate. The file starts with a table of contents and ends with reference links, so it can be read later without searching again.

No outside information is added. To explain a topic that was not covered in the conversation, or to start from research, use [`exmd`](../exmd/README.md) instead.

## Usage

- 「今の内容をメモにまとめて」
- 「ここまでの話をMarkdownにまとめて」

## Behavior

- Fixes the scope first: the whole conversation unless the user specifies otherwise.
- Writes only from information already in the conversation. Extra searches or external information are added only when the user explicitly asks.
- Output is one Markdown file with frontmatter (`title`, `model`, `created`, `updated`), a table of contents at the top, a short summary, free-form body, and reference links.
- Saved to the path the user gives. Otherwise saved to the current directory as `YYYY-MM-DD-<slug>.md`. Asks before overwriting an existing file.
- Before replying, checks that the table of contents is at the top, the note stands on its own, and the conclusion is in the first half. The reply states what was summarized and where it was saved, without repeating the body.

The full procedure lives in [SKILL.md](SKILL.md).
