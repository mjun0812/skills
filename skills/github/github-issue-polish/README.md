# github-issue-polish

[日本語](README_ja.md)

Rewrite an existing GitHub issue until an implementer can start without further investigation. The skill investigates the codebase to find the root cause and the files to change, decides each design branch with a stated rationale, trials the approach in a temporary worktree, and then applies the result after approval. It rewrites the body of an issue the authenticated user opened, and proposes the polished body in a comment on an issue someone else opened, leaving that body unchanged.

The polished body contains: background, current behavior, root cause by `path:line`, chosen approach with rejected alternatives, files to change, test plan, out of scope, verification notes, a decision log, and completion criteria. Sections that cannot be filled are omitted. To file a new issue, use [`github-issue-create`](../github-issue-create/README.md). To implement an issue and open the PR, use [`github-issue-resolve`](../github-issue-resolve/README.md).

## Usage

- 「issueを磨いて」
- 「#Nをpolishして」
- 「issueを実装できるレベルに詰めて」

```text
/github-issue-polish 123
/github-issue-polish 123 language=en --skip-trial
/github-issue-polish #123 --dry-run
```

## Arguments

| Argument       | Effect                                                                   |
| -------------- | ------------------------------------------------------------------------ |
| `issue`        | Issue number (required). `#` prefix optional.                            |
| `language`     | Language of the polished body. Defaults to the issue's current language. |
| `--skip-trial` | Skip the trial implementation in a worktree.                             |
| `--dry-run`    | Stop after showing the polished body. Nothing is written to the issue.   |

## Behavior

- Stops if the issue is already closed or `gh` is not authenticated.
- Compares the issue body and comments with the target structure to list gaps; agreements in comments are folded into the body.
- Investigates the code and identifies causes and changes by `path:line`. Problems outside the issue's scope go to "out of scope" and a suggestion to file a separate issue, not into the body.
- Decides design branches itself instead of asking. Undecidable branches get a provisional decision with low confidence, flagged "needs confirmation" in the decision log (issue / decision / rationale / confidence).
- Trial implementation: creates a worktree on `polish/<issue-number>-trial`, implements a minimal version, runs the tests, and summarizes results as verification notes (no full diff in the issue). The worktree and branch are always deleted afterwards, including on error or cancellation.
- Shows the full polished body, a change summary, and where the result will go, then asks for approval (apply / revise and show again / cancel).
- The issue's author decides where the result goes.
  - If the authenticated user opened the issue, it overwrites the body via `gh issue edit --body-file` and posts one comment summarizing the changes.
  - If someone else opened it, it leaves the body and title unchanged and posts the polished body with the change summary as one proposal comment.
- The final report lists the changed sections, low-confidence items to confirm, and out-of-scope problems worth a separate issue.

## Dependencies

- `gh` and `git` CLIs

The full procedure lives in [SKILL.md](SKILL.md).
