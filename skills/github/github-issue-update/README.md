# github-issue-update

[日本語](README_ja.md)

Scan all open issues and propose three kinds of updates: closing (resolved, duplicate, stale), adding comments (extra information, or a body that no longer matches the code), and adding or removing labels. A summary is shown first and nothing is written until the user approves it.

Only open issues are inspected; closed issues and PRs are not. To rewrite a single issue in depth, use [`github-issue-polish`](../github-issue-polish/README.md).

## Usage

- 「issueを整理して」
- 「issueのラベルを整理して」

```text
/github-issue-update
/github-issue-update language=en --max 20
```

## Arguments

| Argument    | Effect                                                |
| ----------- | ----------------------------------------------------- |
| `language`  | Language of the comments posted. Defaults to `ja`.    |
| `--max <N>` | Cap on candidates applied per run. Defaults to `100`. |

## Behavior

- Close candidates: duplicates among open issues (the older one is kept), resolved issues (all completion checkboxes ticked, or referenced files/code gone), and stale issues (not updated for over 90 days and with no comments or only vague completion criteria).
- Label candidates use only labels that already exist in the repository. Labels are never created.
- Multiple actions on one issue are bundled. Candidates are prioritized: resolved close, duplicate close, stale close, label changes, comments. Candidates beyond `--max` are dropped from the lowest priority and the count is reported.
- The summary is grouped into close, comment, and label changes. Approval is asked in steps: apply all, select individually, cancel all, or inspect details of specific candidates first. Rejected candidates are only counted as skipped.
- Applying: actions on the same issue run serially, different issues in parallel in batches of 5 to 10 (no more than 20 in a row, to respect rate limits). A failure does not stop the others and is reported.
- An issue is always closed after posting a reason comment, using `gh issue comment` and `gh issue close` rather than `gh issue close --comment`.
- The final report lists closed, commented, relabeled, skipped, capped, and failed counts.

## Dependencies

- `gh` CLI (stops if not authenticated)

The full procedure lives in [SKILL.md](SKILL.md).
