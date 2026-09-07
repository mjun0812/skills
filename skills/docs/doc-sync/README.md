# doc-sync

Compare the documentation in a repository against the actual implementation, find the places that have drifted, and update them to match the code.

## When to use

- The user asks to "update the docs" or says "the README is out of date, fix it".
- Docstrings, OpenAPI specs, or example config files need to catch up with recent code changes.

## Arguments

| Argument    | Effect                                                                             |
| ----------- | ---------------------------------------------------------------------------------- |
| `--dry-run` | Detect drift and report before/after previews without editing any file.            |
| `<path>`    | Limit the scan to a directory or file. Defaults to the whole repository.           |
| `language`  | Language to write updates in. Defaults to the language the existing document uses. |

## What it checks

Four kinds of documents are in scope: Markdown files, docstrings and header comments, OpenAPI/Swagger specs, and example config files such as `.env.example`. Build output, dependency directories, and `.mjun/` are always excluded.

Typical drift it looks for includes renamed functions or CLI flags, moved files, changed API endpoints or config keys, removed features that are still documented, new features that are not, and outdated version requirements or install steps.

## How it works

1. Enumerate the target documents.
2. Cross-check each factual claim against the code. Style and wording differences are not treated as drift.
3. Present the detected drift grouped by file and section.
4. Apply the edits unless `--dry-run` is set. Ambiguous cases are skipped and listed at the end.
5. Report what was updated and what was skipped.

## Guarantees

- Nothing is written from guesswork. Every edit is backed by reading the relevant implementation.
- Edits are minimal and keep the original language, tone, structure, and formatting.
- The skill never commits. Reviewing and committing the result is left to the user.

## Files

- `SKILL.md`: the skill definition.
