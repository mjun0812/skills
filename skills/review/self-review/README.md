# self-review

[日本語](README_ja.md)

Adversarially review changes you wrote yourself and return only verified findings to the chat. Use it to grade your own changes before or after opening a PR. It reviews the current branch's changes (commits since the merge-base with the base, plus uncommitted changes) by default, and without arguments it proposes the target from the branch's state. With a commit it reviews that one commit. The changes are pinned as a snapshot in a temporary worktree, and two Finder subagents with different focuses and (when a spec is available) a Contract subagent propose findings. Every candidate is challenged by an independent Verifier subagent, and only confirmed findings are reported.

Even when a PR exists, nothing is posted to GitHub as a review or comment. To review a PR as a reviewer and post the review, use `github-pr-review` instead.

## Usage

- "自分の変更を厳しくレビューして"
- "PRを出す前にself reviewして"
- "このcommitをself reviewして"

```text
/self-review
/self-review --base origin/feat/parent
/self-review HEAD~1
/self-review --spec 45
/self-review --spec docs/specs/login/spec.md
```

## Arguments

| Argument          | Effect                                                                                                                                                                                                                                            |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `commit`          | Commit to review. No target is proposed when given.                                                                                                                                                                                               |
| `--base <ref>`    | Starting point of the branch's changes. When given, no target is proposed and the branch's changes are reviewed. Defaults to the base branch of the current branch's open PR, or the default branch of the repository `gh` resolves without a PR. |
| `--spec <source>` | Spec for the Contract axis: a GitHub issue number (its body plus maintainer comments), or the path to a Markdown file holding the contract. Defaults to the open PR body's `Closes #N` issue.                                                     |

## Behavior

- Without `commit` or `--base`, the target is chosen from the number of commits ahead of the base and whether uncommitted changes exist. With one candidate it proceeds without asking; with several it shows the options with their size. The branch's changes are recommended.

  | Commits ahead of the base | Uncommitted changes | Target                                                                           |
  | ------------------------- | ------------------- | -------------------------------------------------------------------------------- |
  | 0                         | No                  | Exit with nothing to review                                                      |
  | 0                         | Yes                 | Uncommitted changes only                                                         |
  | 1                         | No                  | The branch's changes                                                             |
  | 2 or more                 | No                  | Choose: the branch's changes / the latest commit only                            |
  | 1 or more                 | Yes                 | Choose: the branch's changes / uncommitted changes only / the latest commit only |

- Without a commit, the commits from the merge-base of the base and HEAD up to HEAD are reviewed together with uncommitted changes. Without `--base`, the base branch is fetched from the remote that points to the PR's base repository, so a stale `origin/main` in a fork is never used as the base. If an open PR exists, its title and body are passed to the subagents as the purpose of the change.
- With a commit, only the diff between that commit and its first parent is reviewed. Root commits and branches or PRs that are not checked out are out of scope.
- `scripts/self_review_snapshot.sh` creates the snapshot worktree under `/tmp/self-review.*`. The review reads only this snapshot and never changes your working tree.
- Finder only searches and reads the snapshot and runs no commands. Verifier may run the smallest relevant tests or reproduction code inside the snapshot.
- Candidates at the same location or with the same root cause are merged, then verified one by one. `refuted` and `uncertain` candidates are discarded. Findings are confirmed in the order Finder, Contract, and Contract drops candidates that duplicate an already confirmed finding.
- If a subagent cannot start or returns no result, the review stops and reports the cause. It never falls back to reading the diff itself.
- Before reporting, it checks that no agent changed the snapshot. When the branch's changes are reviewed, it also checks that the original repository's HEAD and working tree are unchanged since the snapshot was created. If either changed, the results are discarded and only the need for a re-review is reported.
- If `hunk` is available, findings are shown as notes on the reviewed diff. An open Hunk session for the repository is switched to the reviewed diff; without one, Hunk is launched in a Herdr pane. Only notes from a previous self-review are removed; notes from other agents and from you are kept. Findings outside the diff's hunks are not shown in Hunk; only their count is reported. Without a Hunk session and outside Herdr, the Hunk display is skipped.
- The verdict is `CHANGES_REQUIRED` with one or more confirmed findings and `PASS` with none. Every finding goes to the chat even when shown in Hunk. Nothing is saved to a file or posted to GitHub.
- The snapshot is removed at the end, including on interruption. It never runs `reset`/`restore`/`stash`/`checkout`/`clean` on the original repository. The Hunk session and pane are kept.

## Dependencies

- Agents: [`code-reviewer-finder`](../../../agents/code-reviewer-finder.md), [`code-reviewer-contract`](../../../agents/code-reviewer-contract.md), [`code-reviewer-verifier`](../../../agents/code-reviewer-verifier.md). They ship through the Claude Code plugin and apm. `apm install -t codex` converts them to Codex agent format, dropping the `tools` restriction. On other install methods, the same prompts are given to generic subagents instead.
- `git`, `jq`, bash, and `gh` to read the PR or a `--spec` issue
- Optional: [`hunk`](https://github.com/modem-dev/hunk), and [Herdr](https://github.com/herdrdev/herdr) to open a pane when no Hunk session exists

See [SKILL.md](SKILL.md) for the full procedure.
