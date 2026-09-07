# github

Skills for the GitHub side of a change: issues, pull requests, CI, and review. They all drive GitHub through the `gh` CLI, and the ones that write to a PR or issue detect the language from its title and body and reply in kind.

## Which skill to use

| Situation                                                                 | Skill                       |
| ------------------------------------------------------------------------- | --------------------------- |
| File one issue from a note, todo, or bug report                           | `github-issue-create`       |
| Sharpen an existing issue until it can be implemented from the text alone | `github-issue-polish`       |
| Implement an issue end to end and open the PR                             | `github-issue-resolve`      |
| Triage all open issues: close, comment, relabel in bulk                   | `github-issue-update`       |
| Open a PR from the current branch                                         | `github-pr-create`          |
| Review a PR and post findings                                             | `github-pr-review`          |
| Reply to and act on review comments                                       | `github-resolve-pr-comment` |
| Fix failing CI                                                            | `github-fix-ci`             |
| Fix everything blocking a PR (conflicts, CI, comments) in one go          | `github-pr-fix`             |

`github-pr-fix` orchestrates `git-fix-conflict`, `github-fix-ci`, and `github-resolve-pr-comment`, so use it only when more than one kind of problem needs fixing. `github-issue-resolve` chains into `git-commit` and `github-pr-create` for the final steps.

## Issues

### github-issue-create

Turn free-form input plus the current conversation into one GitHub issue. Claims in the material are verified against the repository (and official docs for external tools) and marked confirmed, inferred, or unverified before the draft is shown for approval. Duplicates are searched first, and the skill records facts without choosing a solution.

| Argument   | Effect                                                               |
| ---------- | -------------------------------------------------------------------- |
| `language` | Language of the issue title and body (`ja`, `en`). Defaults to `en`. |

Templates come from the repository's `.github/ISSUE_TEMPLATE/` when present, otherwise from `github-issue-create/references/ISSUE_TEMPLATE/` (or `ISSUE_TEMPLATE_JA/`): bug report, feature request, task, test, research. Labels are picked from the ones that already exist in the repository.

- Trigger phrases: "issue作って", "これIssueにしといて", "バグ報告を起票して".

### github-issue-polish

Rewrite an issue so that an implementer needs no further investigation: background, current behavior, root cause by `path:line`, chosen approach with rejected alternatives, files to change, test plan, out of scope, verification notes, decision log, and completion criteria. Design choices are made by the skill with a confidence level; a temporary worktree is used to trial the approach before the body is rewritten with approval.

| Argument       | Effect                                                                   |
| -------------- | ------------------------------------------------------------------------ |
| `issue`        | Issue number (required). `#` prefix optional.                            |
| `language`     | Language of the polished body. Defaults to the issue's current language. |
| `--skip-trial` | Skip the trial implementation in a worktree.                             |
| `--dry-run`    | Show the polished body without writing to the issue.                     |

- Trigger phrases: "issueを磨いて", "#Nをpolishして".

### github-issue-resolve

From an issue number, investigate, implement in a dedicated worktree, and open a PR. Implementation runs as a loop of implementer and reviewer subagents (prompts in `github-issue-resolve/templates/`), one task per iteration, with the repository's own test, lint, and build commands as the final gate. Commit and PR creation are delegated to `git-commit` and `github-pr-create`.

| Argument    | Effect                                                                      |
| ----------- | --------------------------------------------------------------------------- |
| `issue`     | Issue number (required). `#` prefix optional.                               |
| `--draft`   | Open the PR as a draft.                                                     |
| `--dry-run` | Stop after the investigation and proposed approach. No worktree is created. |

If the issue lacks information needed to decide the approach, the skill stops and asks instead of guessing. The worktree and branch are removed afterwards unless PR creation failed.

- Trigger phrases: "#N を解決して", "issueから実装してPRまで".

### github-issue-update

Scan every open issue and propose closes (resolved, duplicate, stale), comments, and label additions or removals. Nothing is written until the user approves the summary; approval can be all, individual, or none.

| Argument    | Effect                                                |
| ----------- | ----------------------------------------------------- |
| `language`  | Language of the comments posted. Defaults to `ja`.    |
| `--max <N>` | Cap on candidates applied per run. Defaults to `100`. |

Closed issues always receive a reason comment first. Labels that do not exist in the repository are never created.

- Trigger phrases: "issueを整理して", "issueのラベルを整理して".

## Pull requests

### github-pr-create

Push the current branch and open a PR whose body explains overview and background, related issues, approach, changes, impact, and validation results. The base branch is inferred from merge-base distance and reported with the commit list so a wrong guess is visible; the user's explicit choice in conversation wins. Refuses to run on the default branch or when a PR already exists.

| Argument    | Effect                                                                             |
| ----------- | ---------------------------------------------------------------------------------- |
| `language`  | Language of the PR title and body (`ja`, `en`). Defaults to English.               |
| `spec`      | Issue number to treat as the primary `Closes` candidate. Passed by calling skills. |
| `--dry-run` | Show the generated title, body, and base/head. No push, no `gh pr create`.         |

The repository's PR template is used when present, otherwise `github-pr-create/references/pr_template.md` (or `_ja`). The PR is always assigned to `@me`.

- Trigger phrases: "PR作って", "pull request作成して".

### github-pr-review

Adversarial review of a PR. Finder, Standards, and (when a spec is available) Contract subagents propose findings from a snapshot worktree; every candidate is challenged by a Verifier subagent, and only confirmed findings reach the report and inline comments. Earlier reviews by the same reviewer are dismissed and their threads resolved once the new review is posted.

| Argument         | Effect                                                                                 |
| ---------------- | -------------------------------------------------------------------------------------- |
| `PR number`      | PR to review. Defaults to the current branch's PR, or asks when there is none.         |
| `--spec <issue>` | Issue whose body is the spec for the Contract axis. Overrides the PR's `Closes` issue. |
| `--dry-run`      | Print the report only. Nothing is posted, dismissed, or resolved.                      |

Posting goes through `github-pr-review/scripts/post_review.sh`, which also drops inline comments whose `(path, line, side)` is not in the diff. Reports use `github-pr-review/references/report-en.md` or `report-ja.md`. The reviewer agents are defined in the repository's `agents/` directory; on install methods that cannot ship agents, generic subagents receive the same prompts.

- Trigger phrases: "このPRをレビューして".

### github-resolve-pr-comment

Collect all three kinds of PR comments (inline review threads, review summary bodies, PR-level issue comments), classify each as Must Fix, Should Fix, question, or information, apply the fixes, commit and push, and reply to every unresolved thread. A single summary comment is posted at PR level.

| Argument    | Effect                                                                            |
| ----------- | --------------------------------------------------------------------------------- |
| `PR number` | PR to handle. Defaults to the current branch's PR.                                |
| `--dry-run` | Show the classification and planned response. No edits, commit, push, or replies. |

Unresolved threads are the unit of work, regardless of review state or `isOutdated`. Replies and comments are posted through the scripts in `github-resolve-pr-comment/scripts/` with bodies passed as files.

- Trigger phrases: "レビューコメントに対応して", "PRコメントに返信して".

## CI and combined fixes

### github-fix-ci

Read the failing checks for a PR (or the current branch), fetch the failed logs, classify the errors (test, lint, build, type, other), fix them, and commit and push. Only workflow runs matching the PR head commit are considered.

| Argument      | Effect                                                                          |
| ------------- | ------------------------------------------------------------------------------- |
| `PR number`   | PR to check. Defaults to the current branch's PR; without one, repository mode. |
| `--no-commit` | Fix the files but skip commit and push.                                         |
| `--dry-run`   | Stop after the analysis and proposed fix. No edits, commit, or push.            |

In repository mode (no PR) nothing is committed. Still-running checks are reported and the skill exits rather than waiting. Flaky tests and environment failures (missing secrets, permissions) are reported for manual handling.

- Trigger phrases: "CIを直して", "CIが落ちているので修正して".

### github-pr-fix

Bring a PR back to a mergeable state. A dedicated worktree is created from the PR head, the three problem kinds are detected in parallel, and only the matching sub-skills run, in order: `git-fix-conflict`, `github-fix-ci`, `github-resolve-pr-comment`. Pushes go explicitly to the PR head branch, including for cross-repository PRs when the user can push there.

| Argument    | Effect                                          |
| ----------- | ----------------------------------------------- |
| `PR number` | PR to fix. Defaults to the current branch's PR. |

The original working tree is never edited. The worktree, local branch, and temporary refs are removed at the end, even after an error or cancellation.

- Trigger phrases: "PRの問題を全部直して", "PRをまとめて修正して".

The phase-by-phase procedure, exact `gh` invocations, and safety rules for each skill live in its `SKILL.md`.
