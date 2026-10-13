# git

Skills for local git operations: committing, resolving conflicts, and tidying history. None of them run on the default branch, and the only forced push they ever use is `--force-with-lease`.

## Which skill to use

| Situation                                                  | Skill                                            |
| ---------------------------------------------------------- | ------------------------------------------------ |
| Commit the current changes with a generated message        | [`git-commit`](git-commit/README.md)             |
| Resolve conflicts from a merge, rebase, cherry-pick, or PR | [`git-fix-conflict`](git-fix-conflict/README.md) |
| Squash or regroup the commits on the current branch        | [`git-squash`](git-squash/README.md)             |
