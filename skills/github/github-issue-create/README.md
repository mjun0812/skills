# github-issue-create

[日本語](README_ja.md)

Turn a todo, note, or bug report (plus the facts established in the current conversation) into one GitHub issue. Claims in the material are verified against the repository (and official docs for external tools) and classified as confirmed, inferred, or unverified before the draft is shown for approval. Related issues are searched first. The skill records facts and does not choose a solution.

The output is a single issue with a title, a body structured by an issue template, and labels. To rewrite an existing issue until it can be implemented from the text alone, use [`github-issue-polish`](../github-issue-polish/README.md) instead.

## Usage

- 「issue作って」
- 「これIssueにしといて」
- 「調べてからissueにして」
- 「バグ報告を起票して」
- 「Todoを起票して」

```text
/github-issue-create language=ja
```

## Arguments

| Argument   | Effect                                                               |
| ---------- | -------------------------------------------------------------------- |
| `language` | Language of the issue title and body (`ja`, `en`). Defaults to `en`. |

## Behavior

- Reads the request and conversation as draft material. If the request has no content, it asks for a free-text summary.
- Searches open and closed issues for duplicates. If an open issue covers the same problem, it stops and asks whether to create a new one anyway. Related issues are written as `Related to #N`.
- Verifies claims (files, functions, config keys, errors, causal statements) in the repository, and in official docs for external specs only. It checks only the area around each claim and does not dig into root causes or compare solutions.
- Picks the template automatically: `bug_report`, `test`, `feature_request`, `research`, or `task` (the fallback when unclear).
- Templates come from the repository's `.github/ISSUE_TEMPLATE/` when present, otherwise from `references/ISSUE_TEMPLATE/` (English) or `references/ISSUE_TEMPLATE_JA/` (Japanese). Labels are chosen only from labels that already exist in the repository.
- Sections without information are omitted. Inferred or unverified claims are written as hypotheses or open questions. Line numbers are not put in the body.
- Information from private repositories is not written into issues posted to public repositories.
- Diagrams, diffs, and tree-form file structure diffs are added where they help; see [references/visuals.md](references/visuals.md).
- The issue is created only after the user approves the title, body, type, and labels, together with the confirmed/inferred/unverified breakdown, web sources, and related issues. If the material is too thin to draft a title, it asks questions instead.
- After creation it re-fetches the issue and compares it with the draft, then reports the URL, template type, and labels. When open decisions remain, it suggests taking the issue to a specification step before implementation.

## Dependencies

- `gh` CLI (stops with guidance if `gh auth status` fails)

The full procedure lives in [SKILL.md](SKILL.md).
