# git-squash

[日本語](README_ja.md)

Squashes and tidies the commits on the current branch with minimal interaction, then pushes with `--force-with-lease` unless `--no-push` is given. By default commits are regrouped into logical units; with `--one` everything becomes a single commit.

New commit messages follow Conventional Commits and are written in the specified language.

## Usage

- "commitをsquashして"
- "commitを整理して"

```text
/git-squash
/git-squash ja --one
/git-squash --no-push
/git-squash --dry-run
```

## Arguments

| Argument      | Effect                                                                                   |
| ------------- | ---------------------------------------------------------------------------------------- |
| `language`    | Language of the commit messages and the report (`ja`, `en`). Defaults to English.        |
| `--one`, `-1` | Squash the target commits into one.                                                      |
| `--no-push`   | Do not push after squashing; report the required command instead.                        |
| `--dry-run`   | Show the squash plan (grouping and new commit messages) only. No reset, commit, or push. |

## Behavior

- Pre-checks the branch, base branch, number of target commits, working tree, and divergence from upstream.
- Stops without changes on the default branch, with zero target commits, with uncommitted changes (no automatic stash or commit), or when upstream has commits not yet fetched. With a single commit it exits as nothing to squash.
- Without `--one`, groups commits into logical units by type, changed files, and PR context. If grouping is unstable, or one file's changes cannot be safely split across groups, it falls back to a single commit.
- Generates Conventional Commits messages with a blank second line and a bulleted body.
- Runs `git reset --soft origin/<base-branch>` and recreates the commits.
- Pushes with `git push --force-with-lease` automatically. If that fails, it stops and never falls back to `--force`.
- It does not ask for confirmation; unsafe states are aborted with the reason reported.
- The report follows [references/summary_template.md](references/summary_template.md) (or [the Japanese variant](references/summary_template_ja.md)).

## Dependencies

- `git` and `gh` CLIs

The full procedure lives in [SKILL.md](SKILL.md).
