# github-pr-create

[日本語](README_ja.md)

Push the current branch and open a Pull Request. The title and body are generated from the commits and diff against the base branch. The body always has an overview and validation; changes and design decisions appear only when there is something to say. Labels are chosen from the repository's existing ones, and the PR is always assigned to `@me`.

To file or polish an issue instead, use [`github-issue-create`](../github-issue-create/README.md). To implement an issue and open the PR in one run, use [`github-issue-resolve`](../github-issue-resolve/README.md), which calls this skill at the end.

## Usage

- "PR作って"
- "pull request作成して"

```text
/github-pr-create
/github-pr-create --dry-run
/github-pr-create language=ja
```

## Arguments

| Argument    | Effect                                                                                                                                    |
| ----------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| `language`  | Language of the PR title and body (`ja`, `en`). Defaults to the language of the repository's PR template, then the conversation language. |
| `spec`      | Issue number to treat as the primary `Closes` candidate. Passed by calling skills.                                                        |
| `--dry-run` | Show the generated title, body, base/head, and any diagram or image artifacts. No push, no attachment upload, no `gh pr create`.          |

## Behavior

- On the default branch or with uncommitted changes, it proposes a branch name and commit split, and after approval hands branch creation and commit to `git-commit`.
- The base branch is the one the user named in conversation, otherwise the default branch. If unrelated commits would be included, it picks the open PR head branch that HEAD is stacked on, or asks. The chosen base, the reason, and the commit list are reported so a wrong guess is visible.
- Stops and shows the URL and state when a PR already exists for the current branch.
- Uses the repository's PR template when present (headings and order kept as is), marking sections with nothing to say as `N/A`. Otherwise uses `references/pr_template.md` or `pr_template_ja.md`, omitting optional sections with nothing to say.
- Each fact is written under one heading only. Changes state what behaves differently, and design decisions give the reason wherever another approach could have been chosen.
- The body is written from the commit list and diff, not from memory. It does not invent facts and does not mention private repositories when posting to a public one.
- Validation and multiple design decisions go in tables, and logs in `<details>`. A breaking change goes on a line of the changes starting with "Breaking change:", and unvalidated scope in one sentence starting with "Not validated:" below the validation table.
- Where text alone is unclear, it follows `references/visuals.md` and adds a `diff` or tree block, Mermaid, or an image.
- Pushes with a normal push; `--force-with-lease` is used only after confirming with the user.
- The body is passed to `gh pr create` with `--body-file`. The result shows the PR URL, title, base and head, related issues, labels, and change size.

## Dependencies

- [`git-commit`](../../git/git-commit/README.md) for branch creation and commits
- `git` and `gh` CLI

The full procedure lives in [SKILL.md](SKILL.md).
