# github-issue-resolve

[日本語](README_ja.md)

Take a GitHub issue number through investigation, implementation in a dedicated worktree, and PR creation in one run. Only changes that pass review and the repository's own verification commands are finalized, and the original working tree is not modified.

The output is a PR that references the issue (`Closes #N`). To sharpen an under-specified issue first, use [`github-issue-polish`](../github-issue-polish/README.md). To only open a PR from the current branch, use [`github-pr-create`](../github-pr-create/README.md).

## Usage

- 「#Nを解決して」
- 「issueから実装してPRまで」

```text
/github-issue-resolve 123
/github-issue-resolve #123 --draft
/github-issue-resolve 123 --dry-run
```

## Arguments

| Argument    | Effect                                                                      |
| ----------- | --------------------------------------------------------------------------- |
| `issue`     | Issue number (required). `#` prefix optional.                               |
| `--draft`   | Open the PR as a draft.                                                     |
| `--dry-run` | Stop after the investigation and proposed approach. No worktree is created. |

## Behavior

- Reads the issue and decides the output language (Japanese if the issue is mainly Japanese, otherwise English). Closed issues are rejected.
- If information needed to decide the approach is missing, it stops and asks specific questions with options or a recommendation, instead of guessing.
- Builds a task queue from the issue's `- [ ]` checklist, or splits into independently verifiable tasks only when needed. The queue lives in the conversation and is not written back to the issue. The approach and task list are shown briefly without asking for confirmation.
- Creates a worktree at `<repo-root>/.tmp/<repo-name>-worktrees/<branch>` on a `<type>/<issue-number>-<slug>` branch from the latest default branch.
- Implements one task per iteration with a fresh implementer subagent ([templates/implementer-prompt.md](templates/implementer-prompt.md)) and checks it with a fresh reviewer subagent ([templates/reviewer-prompt.md](templates/reviewer-prompt.md)). A rejected task is sent back at most twice, then the run stops and reports the unresolved findings. Results are judged from structured fields and command results, not from the subagents' claims.
- After all tasks, runs the repository's test, lint, and build commands (found from manifests, task runners, CI config, and README). Failures are sent back at most twice; if there are no such commands, this step is skipped and the report says so.
- Commits and opens the PR through `git-commit` and `github-pr-create`, then verifies that the PR body contains `Closes #N`.
- Reports the issue, branch, PR URL, and diff stat. The worktree and branch are removed afterwards, including on abort, except when PR creation failed (kept for manual fixes). No destructive reset runs during implementation, and nothing is committed or pushed before the PR phase.

## Dependencies

- Skills: [`git-commit`](../../git/git-commit/README.md), [`github-pr-create`](../github-pr-create/README.md)
- `gh` and `git` CLIs

The full procedure lives in [SKILL.md](SKILL.md).
