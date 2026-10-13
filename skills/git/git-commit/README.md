# git-commit

[日本語](README_ja.md)

Reads the staged and unstaged changes, generates a Conventional Commits message that summarizes them, and commits. If nothing is staged, the current changes are staged first. It never pushes.

The message is written in the language you specify (English by default). The only output is the generated commit message.

## Usage

- Use when running `git commit`: "現在の変更を確認して、コミットする"

```text
/git-commit
/git-commit ja
```

## Arguments

| Argument   | Effect                                                            |
| ---------- | ----------------------------------------------------------------- |
| `language` | Language of the commit message (`ja`, `en`). Defaults to English. |

## Behavior

- Collects `git diff --cached`, `git diff`, `git status`, and the current branch before starting.
- If there are no staged or unstaged changes, it reports that there is nothing to commit and exits.
- If changes are already staged, it commits only those and does not stage anything more. If nothing is staged, it reviews and stages the current changes.
- The message format is `<type>: <description>` (no scope), a blank line, then a bulleted body with one change per line. The rules are in [references/conventional_commits.md](references/conventional_commits.md).
- Body style follows the language: Japanese ends lines with a noun phrase (no desu/masu form); English uses imperative fragments such as `- Add retry on login failure`.
- After committing, it prints only the generated message.
- Allowed tools are limited to `git status`, `add`, `branch`, `diff`, and `commit`.

The full procedure lives in [SKILL.md](SKILL.md).
