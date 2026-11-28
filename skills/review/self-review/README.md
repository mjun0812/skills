# self-review

[日本語](README_ja.md)

Adversarially review changes you wrote yourself and return only verified findings to the chat. Use it to grade your own changes before or after opening a PR. It reviews the current branch's changes (commits since the merge-base with the base, plus uncommitted changes) by default, and without arguments it proposes the target from the branch's state. With a commit it reviews that one commit. The changes are pinned as a snapshot in a temporary worktree, and two Finder subagents with different focuses propose findings. When a PR exists, a Claim subagent checks the claims in the PR body against the real code. Every candidate is challenged by an independent Verifier subagent that runs the code. Findings it reproduces are reported as required changes, and findings it could neither reproduce nor refute are reported as unproven.

Even when a PR exists, nothing is posted to GitHub as a review or comment. To review a PR as a reviewer and post the review, use `github-pr-review` instead.

## Usage

- "自分の変更を厳しくレビューして"
- "PRを出す前にself reviewして"
- "このcommitをself reviewして"

```text
/self-review
/self-review --base origin/feat/parent
/self-review HEAD~1
```

## Arguments

| Argument       | Effect                                                                                                                                                                                                                                            |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `commit`       | Commit to review. No target is proposed when given.                                                                                                                                                                                               |
| `--base <ref>` | Starting point of the branch's changes. When given, no target is proposed and the branch's changes are reviewed. Defaults to the base branch of the current branch's open PR, or the default branch of the repository `gh` resolves without a PR. |

## Behavior

- Without `commit` or `--base`, the target is chosen from the number of commits ahead of the base and whether uncommitted changes exist. With one candidate it proceeds without asking; with several it shows the options with their size. The branch's changes are recommended.

  | Commits ahead of the base | Uncommitted changes | Target                                                                           |
  | ------------------------- | ------------------- | -------------------------------------------------------------------------------- |
  | 0                         | No                  | Exit with nothing to review                                                      |
  | 0                         | Yes                 | Uncommitted changes only                                                         |
  | 1                         | No                  | The branch's changes                                                             |
  | 2 or more                 | No                  | Choose: the branch's changes / the latest commit only                            |
  | 1 or more                 | Yes                 | Choose: the branch's changes / uncommitted changes only / the latest commit only |

  When HEAD is a merge commit, "the latest commit only" is left out so that changes merged from others are not reviewed.

- Without a commit, the commits from the merge-base of the base and HEAD up to HEAD are reviewed together with uncommitted changes. Without `--base`, the base branch is fetched from the remote that points to the PR's base repository, so a stale `origin/main` in a fork is not used as the base. In a fork with no PR yet and no `upstream` remote, however, `gh` resolves the fork itself and `origin/main` becomes the base. When the target is the branch's changes and an open PR exists, its title and body are passed to the subagents as the purpose of the change. If the base cannot be resolved, for example with no remote or offline, only uncommitted changes are reviewed when they exist; otherwise `--base` is requested.
- With a commit, only the diff between that commit and its first parent is reviewed. Root commits and branches or PRs that are not checked out are out of scope.
- `scripts/self_review_snapshot.sh` creates the snapshot worktree under `/tmp/self-review.*`. The review reads only this snapshot and never changes your working tree.
- First it restates the intent of the change in two or three sentences from the description, commits, and diff, and passes it to the subagents. Findings are judged by whether that intent is broken. When the intent cannot be pinned down, it asks the user.
- Finder, Claim, and Verifier may run tests and reproduction code. Each subagent runs them in its own copy exported from the snapshot to a temporary directory and never changes the snapshot. Finder attaches to each finding a reproduction that runs as is, with its output.
- Claim is launched only when the PR title and body are used as the purpose of the change. It runs the validation, scope, and blast radius statements in the PR body and proposes the mismatches it observes. It does not decide whether the description or the code is right.
- Candidates at the same location or with the same root cause are merged, then verified one by one. Verifier reruns the reproduction itself. `refuted` and `uncertain` candidates are discarded and only counted in the report. Confirmed findings that Verifier reproduced become required changes, and those it only traced through the code become unproven. Findings are confirmed in the order Finder, Claim, and Claim drops candidates that duplicate an already confirmed finding.
- If a subagent cannot start or returns no result, the review stops and reports the cause. It never falls back to reading the diff itself.
- Before reporting, it checks that no agent changed the snapshot. When the branch's changes or only uncommitted changes are reviewed, it also checks that the original repository's HEAD and working tree are unchanged since the snapshot was created. If either changed, the results are discarded and only the need for a re-review is reported.
- If `hunk` is available, findings are shown as notes on the reviewed diff. An open Hunk session for the repository is switched to the reviewed diff; without one, Hunk is launched in a Herdr pane. Only notes from a previous self-review are removed; notes from other agents and from you are kept. A previous note that has replies is also kept. Findings outside the diff's hunks are not shown in Hunk; only their count is reported. Without a Hunk session, the Hunk display is skipped when running outside Herdr or when there are no findings.
- The verdict is `CHANGES_REQUIRED` with one or more required changes and `PASS` with none. Unproven findings do not change the verdict. Findings are reported as one table followed by the details of each finding, and the table's "Reproduced" column shows whether each was reproduced. The header also names the reviewer and the model. Every finding goes to the chat even when shown in Hunk. Nothing is saved to a file or posted to GitHub.
- Snapshot cleanup is attempted at the end. Cleanup requires HEAD, file contents, and the index to match creation time and no new untracked files. The initial input copy is then restored inside the snapshot before removal with `git worktree remove`. Review edits, new commits, or denied removal preserve the worktree; its path and the reason are reported. Partial worktrees from creation failures, parent directories, and review artifacts are also kept. Denied deletion is never retried through another method. It never runs `reset`/`restore`/`stash`/`checkout`/`clean` on the original repository. The Hunk session, its notes, and the pane that runs Hunk are kept.

## Dependencies

- Agents: [`code-reviewer-finder`](../../../agents/.apm/agents/code-reviewer-finder.md), [`code-reviewer-claim`](../../../agents/.apm/agents/code-reviewer-claim.md), [`code-reviewer-verifier`](../../../agents/.apm/agents/code-reviewer-verifier.md). They ship through the Claude Code plugin and apm. `apm install -t codex` converts them to Codex agent format, dropping the `tools` restriction. On other install methods, the same prompts are given to generic subagents instead.
- `git`, `jq`, bash, and `gh` to resolve the base when `--base` is omitted and to read the PR
- Optional: [`hunk`](https://github.com/modem-dev/hunk), and [Herdr](https://github.com/herdrdev/herdr) to open a pane when no Hunk session exists

See [SKILL.md](SKILL.md) for the full procedure.
