# github-fix-ci

[日本語](README_ja.md)

Check the CI status of a PR (or the current branch), fetch the failed logs, classify the errors (test, lint, build, type, other), fix them, and commit and push. Only workflow runs that match the PR head commit are considered, so stale runs are never used as evidence.

To fix conflicts, CI, and review comments together, use [`github-pr-fix`](../github-pr-fix/README.md), which calls this skill.

## Usage

- "CIを直して"
- "CIが落ちているので修正して"

```text
/github-fix-ci
/github-fix-ci 123 --dry-run
/github-fix-ci --no-commit
```

## Arguments

| Argument      | Effect                                                                          |
| ------------- | ------------------------------------------------------------------------------- |
| `PR number`   | PR to check. Defaults to the current branch's PR; without one, repository mode. |
| `--no-commit` | Fix the files but skip commit and push.                                         |
| `--dry-run`   | Stop after the analysis and proposed fix. No edits, commit, or push.            |

## Behavior

- PR mode applies when a PR is given or linked to the current branch. Without one it runs in repository mode, where nothing is committed or pushed and the user is told to commit manually.
- In PR mode the commit message follows the PR's language (English when ambiguous): `fix: resolve CI failures - <description>` or `fix: CI失敗を修正 - <説明>`.
- If all checks pass, it reports success and exits. If checks are still running, it reports the status and exits without waiting.
- Failed logs come from `gh run view --log-failed` for runs whose `headSha` equals the PR head. When several runs remain, it prefers the one matching the failed check name, or only the latest when unclear.
- Multiple failures are fixed in dependency order (for example build before test). Only the files it fixed are staged.
- It asks the user when a fix is unclear or risky. Suspected flaky tests and environment failures (missing secrets, permissions) are reported for manual handling, and a repeatedly failing CI gets a root-cause investigation suggestion.
- After pushing, it reports that CI will rerun and suggests rechecking once it finishes.

## Dependencies

- `git` and `gh` CLI

The full procedure lives in [SKILL.md](SKILL.md).
