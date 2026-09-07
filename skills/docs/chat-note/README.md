# chat-note

Write what was researched and discussed in the current conversation into a single Japanese Markdown file, without adding outside information.

## When to use

- The user asks to "summarize what we have so far" or "put this discussion into a Markdown note".
- The material already exists in the conversation and only needs to be captured for later reading.

Do not use it to explain a topic that was not discussed, or for requests that start with research. Use `exmd` for those.

## What it produces

One Markdown file with a frontmatter block (`title`, `model`, `created`, `updated`), a table of contents at the top, a short summary, the body, and a list of reference links.

By default the file is saved in the current directory as `YYYY-MM-DD-<english-slug>.md`. The skill asks before overwriting an existing file.

## Rules the skill follows

- Facts, inferences, and unverified points are kept distinct.
- No additional searches or outside sources unless the user explicitly asks.
- The note must be readable on its own, without re-running the original research.
- The conclusion comes first; the note is a single file, not a set of documents.

## Files

- `SKILL.md`: the skill definition, including the output template.
