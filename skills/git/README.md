# git

Skills for local git operations: committing, resolving conflicts, and tidying history. None of them run on the default branch, and the only forced push they ever use is `--force-with-lease`.

## Which skill to use

| Situation                                                  | Skill              |
| ---------------------------------------------------------- | ------------------ |
| Commit the current changes with a generated message        | `git-commit`       |
| Resolve conflicts from a merge, rebase, cherry-pick, or PR | `git-fix-conflict` |
| Squash or regroup the commits on the current branch        | `git-squash`       |

## git-commit

Read the staged and unstaged changes, generate a Conventional Commits message, and commit. If nothing is staged, the current changes are staged first. It never pushes.

| Argument   | Effect                                                            |
| ---------- | ----------------------------------------------------------------- |
| `language` | Language of the commit message (`ja`, `en`). Defaults to English. |

The message format is `<type>: <description>`, a blank line, then a bulleted body. The rules are in `git-commit/references/conventional_commits.md`. The only output is the generated message.

## git-fix-conflict

Detect and resolve conflicts from an in-progress merge, rebase, cherry-pick, revert, `am`, or `apply`. When nothing is in progress but the current branch's PR reports `CONFLICTING`, the skill merges the PR base branch and resolves the result.

| Argument    | Effect                                                                                        |
| ----------- | --------------------------------------------------------------------------------------------- |
| `--dry-run` | List the conflicting files and the proposed resolution. No edits, `git add`, commit, or push. |

After resolving, the skill continues the in-progress operation, runs the repository's test, lint, and build commands, and pushes when the PR branch needs it. It never starts a new rebase, and it asks before any push that rewrites history. Complex conflicts are shown to the user instead of being resolved automatically. The report follows `git-fix-conflict/references/summary_template.md` (or the `_ja` variant), in the language detected from the PR.

- Trigger phrases: "コンフリクトを直して", "マージコンフリクトを解消して".

## git-squash

Squash the commits on the current branch with minimal interaction. By default commits are regrouped into logical units; with `--one` everything becomes a single commit.

| Argument      | Effect                                                                   |
| ------------- | ------------------------------------------------------------------------ |
| `language`    | Language of the new commit messages and the report. Defaults to English. |
| `--one`, `-1` | Squash everything into one commit.                                       |
| `--no-push`   | Skip the push and print the command instead.                             |
| `--dry-run`   | Show the grouping plan and new messages. No reset, commit, or push.      |

The skill stops on its own when the situation is unsafe: default branch, uncommitted changes, unfetched upstream commits, or zero target commits. Pushes use `git push --force-with-lease` and never fall back to `--force`. The report follows `git-squash/references/summary_template.md` (or the `_ja` variant).

- Trigger phrases: "commitをsquashして", "commitを整理して".

The full procedure and safety checks for each skill live in its `SKILL.md`.
