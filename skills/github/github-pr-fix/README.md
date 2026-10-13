# github-pr-fix

[日本語](README_ja.md)

Bring a PR back to a mergeable state. It detects merge conflicts, failing CI, and unresolved review comments, and runs only the sub-skills that match what it found. All work happens in a dedicated worktree created from the PR head, and the fixes are pushed to the PR head branch.

If only one kind of problem needs fixing, use that skill directly: [`git-fix-conflict`](../../git/git-fix-conflict/README.md), [`github-fix-ci`](../github-fix-ci/README.md), or [`github-resolve-pr-comment`](../github-resolve-pr-comment/README.md).

## Usage

- "PRの問題を全部直して"
- "PRをまとめて修正して"

```text
/github-pr-fix
/github-pr-fix 123
```

## Arguments

| Argument    | Effect                                          |
| ----------- | ----------------------------------------------- |
| `PR number` | PR to fix. Defaults to the current branch's PR. |

## Behavior

- Stops with an error when no PR is found, or when the PR comes from a fork the user cannot push to.
- Creates the worktree at `<repo-root>/.tmp/<repo-name>-worktrees/pr-<number>-fix` on a local branch `pr-fix/<number>`, taken from the fetched PR head ref. A leftover worktree with uncommitted changes aborts the run.
- The PR's language is detected once from its title and body (English when ambiguous) and passed to every sub-skill and the final summary.
- Detection runs in parallel. Conflicts are handled when the PR is `CONFLICTING`. CI is handled when any check is `FAILURE`, `CANCELLED`, or `TIMED_OUT`. Review comments are handled when there is at least one unresolved inline thread, counted with `scripts/fetch_review_threads.sh --only-unresolved`.
- Sub-skills run in this order, and a failure in one does not stop the next: `git-fix-conflict`, `github-fix-ci`, `github-resolve-pr-comment`. It asks the user before large changes.
- Pushes go explicitly to the PR head branch with `git push <push-remote> HEAD:<head-ref-name>`. For cross-repository PRs, the head repository is the push remote rather than `origin`.
- The original working tree is never edited. At the end, uncommitted changes and unpushed commits are checked, the PR's final state is shown with a summary (templates in `references/summary_template.md` and `_ja`), and the worktree, local branch, and temporary refs are removed, even after an error or cancellation.

## Dependencies

- Skills: [`git-fix-conflict`](../../git/git-fix-conflict/README.md), [`github-fix-ci`](../github-fix-ci/README.md), [`github-resolve-pr-comment`](../github-resolve-pr-comment/README.md)
- `git` and `gh` CLI

The full procedure lives in [SKILL.md](SKILL.md).
