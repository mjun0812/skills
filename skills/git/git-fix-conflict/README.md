# git-fix-conflict

[日本語](README_ja.md)

Detects and resolves conflicts from an in-progress merge, rebase, cherry-pick, revert, `am`, or `apply`. When nothing is in progress but the current branch's PR reports `CONFLICTING`, it merges the PR base branch and resolves the result.

It continues the in-progress operation, runs the repository's checks, and reports the result in the language detected from the PR (or from the request and recent commits when there is no PR).

## Usage

- "コンフリクトを直して"
- "マージコンフリクトを解消して"

```text
/git-fix-conflict
/git-fix-conflict --dry-run
```

## Arguments

| Argument    | Effect                                                                                        |
| ----------- | --------------------------------------------------------------------------------------------- |
| `--dry-run` | List the conflicting files and the proposed resolution. No edits, `git add`, commit, or push. |

## Behavior

- Checks the branch, Git state, in-progress operation, and unresolved files (`git diff --name-only --diff-filter=U`). If there are no conflicts, it reports that and exits.
- With unresolved files, it resolves the in-progress operation. Without them, if the PR is `CONFLICTING`, it fetches and runs `git merge origin/<base-branch>`. With `--dry-run` it detects conflicts non-destructively using `git merge-tree` instead of merging.
- Analyzes both sides of each conflict, keeping in mind that HEAD and theirs swap meaning depending on the operation, then applies a resolution and explains the reasoning.
- Stages the resolved files and completes the operation (merge commit, `rebase --continue`, `cherry-pick --continue`, `revert --continue`, or `am --continue`). For `apply`, it stages and commits as appropriate.
- Runs the repository's test, lint, and build commands, and revisits the resolution if they fail.
- Pushes when the PR branch needs it. It never starts a new rebase, and it asks before any push that rewrites history, using only `--force-with-lease`, never `--force`.
- Complex conflicts (large files, architectural changes) are shown to the user for a decision instead of being resolved automatically.
- The report follows [references/summary_template.md](references/summary_template.md) (or [the Japanese variant](references/summary_template_ja.md)).

## Dependencies

- `git` and `gh` CLIs

The full procedure lives in [SKILL.md](SKILL.md).
